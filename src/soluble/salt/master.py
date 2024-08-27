async def run_command(
    hub, name: str, salt_command: str, *, capture_output: bool = False
) -> int:
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

    kwargs = {}
    if capture_output:
        # Capture output so that nothing gets preinted to stdout
        kwargs["stdout"] = hub.lib.asyncio.subprocess.PIPE

    process = await hub.lib.asyncio.create_subprocess_shell(command, **kwargs)

    if capture_output:
        stdout, _ = await process.communicate()
        for line in stdout.splitlines():
            hub.log.debug(line)

    return await process.wait()
