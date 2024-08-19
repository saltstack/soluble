import asyncio
import subprocess
import json
import sys

async def get_targets(hub, ssh_options: list[str]) -> list[str]:
    """Get the target minions from the salt-ssh test.ping output."""
    output = await hub.soluble.ssh.run_command(f"salt-ssh {' '.join(ssh_options)} test.ping --out json")
    return list(json.loads(output).keys())

async def run_command(hub, target:str, roster:str, *args, escalate: bool = False) -> str:
    """Run a shell command asynchronously and return the output."""
    command = f'"{target}" --roster={roster} {" ".join(args)}'
    if escalate:
        command = f"sudo {command}"
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        hub.log.info(f"Command failed: {command}\nError: {stderr.decode('utf-8')}")
        sys.exit(1)
    return stdout.decode('utf-8')
