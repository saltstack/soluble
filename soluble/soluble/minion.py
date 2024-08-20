import pathlib
import socket
import tempfile

import yaml


async def run(hub, name: str) -> int:
    # Run Setup
    await hub.soluble.minion.setup(name)

    hub.log.info("Getting target minions...")
    targets = await hub.soluble.ssh.get_targets(name)

    hub.log.info("Accepting minion key(s) on Salt master...")
    await hub.soluble.master.accept_keys(name, targets)

    hub.log.info("Running specified Salt command on ephemeral minions...")
    command = hub.soluble.RUN[name].salt_command
    command += " ".join(hub.soluble.RUN[name].salt_options)
    retcode = await hub.soluble.master.run_command(name, command)

    # Run Teardown
    if not hub.soluble.RUN[name].bootstrap:
        hub.log.info("Running teardown on target(s)...")
        await hub.soluble.minion.teardown(
            name,
        )

    return retcode


async def get_id(hub, name: str, target: str = None) -> str:
    node_prefix = hub.soluble.RUN[name].node_prefix
    if not target:
        target = socket.gethostname()

    minion_id = f"{node_prefix}{target}"
    return minion_id


async def setup(hub, name: str):
    """Setup the ephemeral minion by generating and applying the SLS file."""
    config = hub.soluble.RUN[name]

    # Load the minion config, modify it, and save it
    try:
        with open(config.minion_config) as f:
            minion_config = yaml.safe_load(f) or {}
    except FileNotFoundError:
        minion_config = {}

    # Update the minion ID with a unique identifier
    minion_id = await hub.soluble.minion.get_id(name)
    minion_config["id"] = minion_id

    # Dump the updated minion config back to a file
    with tempfile.NamedTemporaryFile("w+", suffix="_config.yaml", delete=True) as cfg:
        cfg.write(yaml.safe_dump(minion_config))

        # Create the setup SLS content
        sls_content = {
            "copy_minion_config": {
                "file.managed": [
                    {"name": "/etc/salt/minion"},
                    {"source": f"file://{cfg.name}"},
                    {"user": "root"},
                    {"group": "root"},
                    {"mode": "644"},
                ]
            },
            "install_salt": {"pkg.installed": [{"name": "salt-minion"}]},
            "start_minion_service": {
                "service.running": [
                    {"name": "salt-minion"},
                    {"enable": True},
                    {"watch": [{"pkg": "install_salt"}]},
                ]
            },
        }

        with tempfile.NamedTemporaryFile("w+", suffix=".sls", delete=True) as fh:
            fh.write(yaml.safe_dump(sls_content))
            fh.flush()
            p = pathlib.Path(fh.name)

            hub.log.info("Running setup on target(s)...")
            await hub.soluble.ssh.run_command(name, f"state.apply {p.stem}")


async def teardown(hub, name: str):
    """Teardown the ephemeral minion by generating and applying the SLS file."""
    # Create the teardown SLS content
    sls_content = {
        "stop_minion_service": {"service.dead": [{"name": "salt-minion"}]},
        "uninstall_salt": {"pkg.purged": [{"name": "salt-minion"}]},
        "remove_minion_config": {
            "file.absent": [
                {"name": "/etc/salt/minion"},
                {
                    "require": [
                        {"service": "stop_minion_service"},
                        {"pkg": "uninstall_salt"},
                    ]
                },
            ]
        },
    }

    with tempfile.NamedTemporaryFile("w+", suffix=".sls", delete=True) as fh:
        fh.write(yaml.safe_dump(sls_content))
        fh.flush()

        p = pathlib.Path(fh.name)

        hub.log.info("Running teardown on target(s)...")
        await hub.soluble.ssh.run_command(name, f"state.apply {p.stem}")
