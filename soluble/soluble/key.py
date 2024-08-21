from typing import Literal


async def accept(hub, name: str) -> int:
    """Accept the ephemeral minion keys on the Salt master."""
    return await hub.soluble.key.command(name, action="-a")


async def destroy(hub, name: str) -> int:
    """Destroy the ephemeral minion keys on the Salt master."""
    return await hub.soluble.key.command(name, action="-d")


async def command(hub, name: str, action: Literal["-a", "-d"]):
    escalate = hub.soluble.RUN[name].escalate
    config_dir = hub.soluble.RUN[name].salt_config_dir
    cmd = hub.soluble.RUN[name].salt_key_bin
    assert cmd, "Could not find salt-key, is this a salt-master?"

    node_prefix = hub.soluble.RUN[name].node_prefix

    command = f"{cmd} {action} '{node_prefix}*' -y --out=json --no-color"
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
    for line in stdout.splitlines():
        hub.log.debug(line)
    return retcode
