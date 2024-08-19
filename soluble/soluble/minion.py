import os


async def run(
    hub,
    ssh_target: str,
    salt_command: str,
    *,
    roster_file: str,
    minion_config: str,
    salt_options: list[str],
    salt_ssh_options: list[str],
    **kwargs,
) -> int:
    await hub.soluble.minion.get_config(minion_config)

    hub.log.info("Copying minion configuration to target(s)...")
    await hub.soluble.minion.copy_config(salt_ssh_options, minion_config)

    hub.log.info("Installing Salt on target(s)...")
    await hub.soluble.minion.install_salt(salt_ssh_options)

    hub.log.info("Starting salt-minion service on target(s)...")
    await hub.soluble.minion.start_service(salt_ssh_options)

    hub.log.info("Getting target minions...")
    targets = await hub.soluble.ssh.get_targets(salt_ssh_options)

    hub.log.info("Accepting minion key(s) on Salt master...")
    await hub.soluble.master.accept_keys(targets)

    hub.log.info("Running specified Salt command on ephemeral minions...")
    await hub.soluble.master.run_salt_command(salt_command, salt_options)

    hub.log.info("Tearing down the ephemeral minions on target(s)...")
    await hub.soluble.minion.teardown(salt_ssh_options)

    hub.log.info("Done.")
    return 0


async def get_config(hub, minion_config_template: str):
    """Fetch the minion config from the Salt master if it's not found locally."""
    if not os.path.exists(minion_config_template):
        hub.log.info("Fetching minion config from Salt master...")
        await hub.soluble.ssh.run_command(
            f"salt-call --local cp.get_file salt://minion {minion_config_template}"
        )


async def get_id(hub, target: str) -> str:
    """Generate an ephemeral minion ID."""
    return f"ephemeral-node-{target}"


async def copy_config(hub, ssh_options: list[str], minion_config_template: str):
    """Copy the minion config to the targets using salt-ssh."""
    await hub.soluble.ssh.run_command(
        f"salt-ssh {' '.join(ssh_options)} state.apply copy_minion_config pillar=\"{{'minion_config_template':'{minion_config_template}'}}\""
    )


async def install_salt(hub, ssh_options: list[str]):
    """Install Salt on the targets using salt-ssh."""
    await hub.soluble.ssh.run_command(
        f"salt-ssh {' '.join(ssh_options)} state.apply install_salt"
    )


async def start_service(hub, ssh_options: list[str]):
    """Start the salt-minion service on the targets using salt-ssh."""
    await hub.soluble.ssh.run_command(
        f"salt-ssh {' '.join(ssh_options)} state.apply start_minion_service"
    )


async def teardown(hub, ssh_options: list[str]):
    """Teardown the ephemeral minions using salt-ssh."""
    await hub.soluble.ssh.run_command(
        f"salt-ssh {' '.join(ssh_options)} state.apply teardown_minion"
    )
