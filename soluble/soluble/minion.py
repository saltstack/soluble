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


async def setup(hub, name: str):
    """Setup the ephemeral minion using raw Salt execution modules."""
    config = hub.soluble.RUN[name]

    # Load the minion config, modify it, and save it
    try:
        with open(config.minion_config) as f:
            minion_config = hub.lib.yaml.safe_load(f) or {}
    except FileNotFoundError:
        minion_config = {}

    # Dump the updated minion config back to a file
    with hub.lib.tempfile.NamedTemporaryFile(
        "w+", suffix="_config.yaml", delete=True
    ) as cfg:
        hub.lib.yaml.safe_dump(minion_config, cfg)

        # Copy the minion config to the target
        hub.log.info("Copying minion configuration to target(s)...")
        # await hub.soluble.ssh.run_command(
        #    name, f"cp.get_file file://{cfg.name} /etc/salt/minion"
        # )

    # Create the minion config file
    node_prefix = hub.soluble.RUN[name].node_prefix
    hub.log.info("Setting minion ids")
    await hub.soluble.ssh.run_command(
        name,
        f'state.single cmd.run name="echo {node_prefix}$(hostname) > /etc/salt/minion_id"',
    )

    # Install Salt on the target
    hub.log.info("Installing Salt on target(s)...")
    await hub.soluble.ssh.run_command(name, "pkg.install name=salt-minion")

    # Start the Salt minion service
    hub.log.info("Starting salt-minion service on target(s)...")
    await hub.soluble.ssh.run_command(name, "service.start name=salt-minion")

    # Enable the service to start on boot
    await hub.soluble.ssh.run_command(name, "service.enable name=salt-minion")


async def teardown(hub, name: str):
    """Teardown the ephemeral minion using raw Salt execution modules."""
    # Stop the Salt minion service
    hub.log.info("Stopping salt-minion service on target(s)...")
    await hub.soluble.ssh.run_command(name, "service.stop name=salt-minion")

    # Uninstall Salt from the target
    hub.log.info("Uninstalling Salt from target(s)...")
    await hub.soluble.ssh.run_command(name, "pkg.remove name=salt-minion")

    # Remove the minion configuration file
    hub.log.info("Removing minion configuration from target(s)...")
    await hub.soluble.ssh.run_command(name, "file.remove /etc/salt/minion")
