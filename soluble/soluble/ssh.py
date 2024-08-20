import asyncio.subprocess
import json
import sys
import shutil


async def get_targets(hub, name: str) -> list[str]:
    """Get the target minions from the salt-ssh test.ping output."""
    output = await hub.soluble.ssh.run_command(name, "test.ping --out json")
    return list(json.loads(output).keys())


async def run_command(hub, name: str, command: str) -> str:
    """Run a salt-ssh command asynchronously and return the output."""
    target = hub.soluble.RUN[name].ssh_target
    roster = hub.soluble.RUN[name].roster_file
    escalate = hub.soluble.RUN[name].escalate
    cmd = shutil.which("salt-ssh")
    assert cmd, "Could not find salt-ssh"
    
    full_command = f"{cmd} {target} --roster={roster} {command} --log-file={hub.OPT.pop_config.log_file}"
    if escalate:
        full_command = f"sudo -E {full_command}"

    process = await asyncio.create_subprocess_shell(
        full_command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        hub.log.info(f"Command failed: {full_command}\nError: {stderr.decode('utf-8')}")
        sys.exit(1)
    return stdout.decode("utf-8")
