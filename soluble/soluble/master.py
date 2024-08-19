import asyncio.subprocess


async def accept_keys(hub, targets: list[str]) -> int:
    """Accept the ephemeral minion keys on the Salt master."""
    retcode = 0
    for target in targets:
        minion_id = await hub.soluble.minion.get_id(target)
        command = f"salt-key -a {minion_id} -y"

        process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        # Log the stdout and stderr
        hub.log.info(stdout.decode("utf-8"))
        if process.returncode != 0:
            hub.log.error(stderr.decode("utf-8"))

        # Update the retcode if any command fails
        retcode = retcode or process.returncode

    return retcode


async def run_command(hub, name: str, salt_command: str) -> int:
    """Run a command on the Salt master, handling stdout, stderr, and error code."""
    salt_options = hub.soluble.RUN[name].salt_options
    node_prefix = hub.soluble.RUN[name].node_prefix

    command = f"salt '{node_prefix}*' {salt_command} {' '.join(salt_options)}"

    process = await asyncio.create_subprocess_shell(
        command,
    )

    return await process.wait()
