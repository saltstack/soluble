async def run(hub, name: str) -> int:
    retcode = 0
    try:
        # Run Setup
        await hub.soluble.minion.setup(name)

        hub.log.info("Accepting minion key(s) on Salt master...")
        await hub.soluble.master.accept_keys(name)

        # Waiting for minion to be ready
        await hub.lib.asyncio.sleep(30)

        hub.log.info("Running specified Salt command on ephemeral minions...")
        command = hub.soluble.RUN[name].salt_command
        command += " ".join(hub.soluble.RUN[name].salt_options)
        retcode = await hub.soluble.master.run_command(name, command)
    finally:
        # Run Teardown
        if not hub.soluble.RUN[name].bootstrap:
            hub.log.info("Running teardown on target(s)...")
            await hub.soluble.minion.teardown(
                name,
            )

    return retcode


async def setup(hub, name: str):
    """Setup the ephemeral minion using raw Salt execution modules."""
    config = hub.soluble.RUN[name]

    # Copy the minion config to the target
    minion_config = hub.lib.path.Path(config.minion_config)

    if minion_config.exists():
        hub.log.info("Copying minion configuration to target(s)...")
        await hub.soluble.ssh.run_command(
            name,
            f"state.single file.managed source=file://{config.minion_config} name=/etc/salt/minion",
        )

    # Create the minion id file
    node_prefix = hub.soluble.RUN[name].node_prefix
    hub.log.info("Setting minion ids")
    await hub.soluble.ssh.run_command(
        name,
        f'state.single cmd.run name="echo {node_prefix}$(hostname) > /etc/salt/minion_id"',
    )

    # Install Salt on the target
    hub.log.info("Installing Salt on target(s)...")
    await hub.soluble.ssh.run_command(
        name, "state.single pkg.installed name=salt-minion"
    )

    # Start the Salt minion service
    hub.log.info("Starting salt-minion service on target(s)...")
    await hub.soluble.ssh.run_command(
        name, "state.single service.running name=salt-minion"
    )

    # Enable the service to start on boot
    await hub.soluble.ssh.run_command(name, "service.enabled name=salt-minion")


async def teardown(hub, name: str):
    """Teardown the ephemeral minion using raw Salt execution modules."""
    # Stop the Salt minion service
    hub.log.info("Stopping salt-minion service on target(s)...")
    await hub.soluble.ssh.run_command(
        name, "state.single service.disabled name=salt-minion"
    )
    await hub.soluble.ssh.run_command(
        name, "state.single service.dead name=salt-minion"
    )

    # Uninstall Salt from the target
    hub.log.info("Uninstalling Salt from target(s)...")
    await hub.soluble.ssh.run_command(name, "state.single pkg.removed name=salt-minion")

    # Remove the minion configuration file
    hub.log.info("Removing minion configuration from target(s)...")
    await hub.soluble.ssh.run_command(
        name, "state.single file.absent name=/etc/salt/minion"
    )
    await hub.soluble.ssh.run_command(
        name, "state.single file.absent name=/etc/salt/minion_id"
    )
