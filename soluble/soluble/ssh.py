async def get_targets(hub, name: str) -> list[str]:
    """Get the target minions from the salt-ssh test.ping output."""
    output = await hub.soluble.ssh.run_command(name, "test.ping --out json")
    try:
        hosts = hub.lib.json.loads(output)
    except hub.lib.json.decoder.JSONDecodeError:
        hosts = {}
    return list(hosts.keys())


async def run_command(hub, name: str, command: str) -> str:
    """Run a salt-ssh command asynchronously, handle all prompts, and return the output."""
    target = hub.soluble.RUN[name].ssh_target
    roster = hub.soluble.RUN[name].roster_file
    escalate = hub.soluble.RUN[name].escalate
    options = " ".join(x.strip('"') for x in hub.soluble.RUN[name].salt_ssh_options)
    cmd = hub.lib.shutil.which("salt-ssh")
    assert cmd, "Could not find salt-ssh"

    full_command = f'{cmd} "{target}" --askpass --roster-file={roster} {command} -l {hub.OPT.pop_config.log_level} --log-file={hub.OPT.pop_config.log_file} --hard-crash {options}'
    if escalate:
        sudo = hub.lib.shutil.which("sudo")
        if sudo:
            full_command = f"{sudo} -E {full_command}"

    hub.log.info(f"Running salt-ssh command: {full_command}")

    process = await hub.lib.asyncio.create_subprocess_shell(
        full_command,
        stdout=hub.lib.asyncio.subprocess.PIPE,
        stderr=hub.lib.asyncio.subprocess.PIPE,
    )

    stdout, stderr = b"", b""

    # Read stderr in real-time and handle it
    while True:
        err_line = await process.stderr.readline()

        if err_line:
            print(err_line.decode("utf-8"), end="", file=hub.lib.sys.stderr)
            stderr += err_line

        if not err_line and process.stderr.at_eof():
            break

    # Wait for the process to complete and capture stdout at the end
    stdout, _ = await process.communicate()

    returncode = await process.wait()

    if returncode != 0:
        raise ChildProcessError(
            f"Command failed: {full_command}\nError: {stderr.decode('utf-8')}"
        )

    return stdout.decode("utf-8")
