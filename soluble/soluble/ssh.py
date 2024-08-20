import asyncio.subprocess
import json.decoder
import shutil
import sys


async def get_targets(hub, name: str) -> list[str]:
    """Get the target minions from the salt-ssh test.ping output."""
    output = await hub.soluble.ssh.run_command(name, "test.ping --out json")
    try:
        hosts = json.loads(output)
    except json.decoder.JSONDecodeError:
        hosts = {}
    return list(hosts.keys())


async def run_command(hub, name: str, command: str) -> str:
    """Run a salt-ssh command asynchronously, handle all prompts, and return the output."""
    target = hub.soluble.RUN[name].ssh_target
    roster = hub.soluble.RUN[name].roster_file
    escalate = hub.soluble.RUN[name].escalate
    options = " ".join(x.strip('"') for x in hub.soluble.RUN[name].salt_ssh_options)
    cmd = shutil.which("salt-ssh")
    assert cmd, "Could not find salt-ssh"

    full_command = f'{cmd} "{target}" --roster-file={roster} {command} -l {hub.OPT.pop_config.log_level} --log-file={hub.OPT.pop_config.log_file} --hard-crash {options}'
    if escalate:
        full_command = f"sudo -E {full_command}"

    hub.log.info(f"Running salt-ssh command: {full_command}")

    process = await asyncio.create_subprocess_shell(
        full_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,  # Enable stdin for interactive input
    )

    stdout, stderr = b"", b""

    async def handle_input():
        """Continuously send user input to the process's stdin."""
        while True:
            user_input = await asyncio.to_thread(input, "")
            process.stdin.write(user_input.encode("utf-8") + b"\n")
            await process.stdin.drain()

    t  = asyncio.create_task(handle_input())

    # Read stderr in real-time and handle it
    while True:
        err_line = await process.stderr.readline()

        if err_line:
            print(err_line.decode("utf-8"), end="", file=sys.stderr)
            stderr += err_line

        if not err_line and process.stderr.at_eof():
            break

    # Wait for the process to complete and capture stdout at the end
    stdout, _ = await process.communicate()

    returncode = await process.wait()
    t.cancel()

    if returncode != 0:
        raise ChildProcessError(
            f"Command failed: {full_command}\nError: {stderr.decode('utf-8')}"
        )

    return stdout.decode("utf-8")
