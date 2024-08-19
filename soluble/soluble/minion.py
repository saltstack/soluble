import os


async def run(hub, name: str) -> int:
    await hub.soluble.minion.get_config(name)

    hub.log.info("Copying minion configuration to target(s)...")
    await hub.soluble.minion.copy_config(name)

    hub.log.info("Installing Salt on target(s)...")
    await hub.soluble.minion.install_salt(name)

    hub.log.info("Starting salt-minion service on target(s)...")
    await hub.soluble.minion.start_service(name)

    hub.log.info("Getting target minions...")
    targets = await hub.soluble.ssh.get_targets(name)

    hub.log.info("Accepting minion key(s) on Salt master...")
    await hub.soluble.master.accept_keys(name, targets)

    hub.log.info("Running specified Salt command on ephemeral minions...")
    retcode = await hub.soluble.master.run_command(name)

    hub.log.info("Tearing down the ephemeral minions on target(s)...")
    await hub.soluble.minion.teardown(name)

    return retcode


async def get_config(hub, name: str):
    """Fetch the minion config from the Salt master if it's not found locally."""
    template = hub.soluble.RUN[name].minion_config
    if not os.path.exists(template):
        hub.log.info("Fetching minion config from Salt master...")
        await hub.soluble.master.run_command(
            f"salt-call --local cp.get_file salt://minion {template}"
        )


async def copy_config(hub, name: str):
    """Copy the minion config to the targets using salt-ssh."""
    template = hub.soluble.RUN[name].minion_config
    await hub.soluble.ssh.run_command(
        name,
        f"state.apply copy_minion_config pillar=\"{{'minion_config_template':'{template}'}}\"",
    )


async def install_salt(hub, name: str):
    """Install Salt on the targets using salt-ssh."""
    await hub.soluble.ssh.run_command(name, "state.apply install_salt")


async def start_service(hub, name: str):
    """Start the salt-minion service on the targets using salt-ssh."""
    await hub.soluble.ssh.run_command(name, "state.apply start_minion_service")


async def teardown(hub, name: str):
    """Teardown the ephemeral minions using salt-ssh."""
    await hub.soluble.ssh.run_command(name, "state.apply teardown_minion")
