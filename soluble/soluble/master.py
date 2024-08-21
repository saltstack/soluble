async def accept_keys(hub, name: str) -> int:
    """Accept the ephemeral minion keys on the Salt master."""
    escalate = hub.soluble.RUN[name].escalate
    config_dir = hub.soluble.RUN[name].salt_config_dir
    cmd = hub.soluble.RUN[name].salt_key_bin
    assert cmd, "Could not find salt-key, is this a salt-master?"

    node_prefix = hub.soluble.RUN[name].node_prefix

    command = f"{cmd} -a '{node_prefix}*' -y"
    if config_dir:
        command += f" --config-dir={config_dir}"
    if escalate:
        sudo = hub.lib.shutil.which("sudo")
        if sudo:
            command = f"{sudo} -E {command}"

    process = await hub.lib.asyncio.create_subprocess_shell(
        command,
        stdout=hub.lib.asyncio.subprocess.PIPE,
    )

    stdout, _ = await process.communicate()
    retcode = await process.wait()
    if retcode != 0:
        raise ChildProcessError(f"Failed to accept minion keys")
    hub.log.error(stdout)
    return retcode


async def run_command(hub, name: str, salt_command: str) -> int:
    """Run a command on the Salt master, handling stdout, stderr, and error code."""
    salt_options = hub.soluble.RUN[name].salt_options
    node_prefix = hub.soluble.RUN[name].node_prefix
    cmd = hub.soluble.RUN[name].salt_bin

    escalate = hub.soluble.RUN[name].escalate
    command = f"{cmd} '{node_prefix}*' {salt_command} {' '.join(salt_options)}"
    config_dir = hub.soluble.RUN[name].salt_config_dir
    if config_dir:
        command += f" --config-dir={config_dir}"
    if escalate:
        command = f"sudo -E {command}"

    process = await hub.lib.asyncio.create_subprocess_shell(
        command,
    )

    return await process.wait()
