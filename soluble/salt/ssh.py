async def run_command(hub, name: str, command: str) -> dict[str, object]:
    """Run a salt-ssh command asynchronously, handle all prompts, and return the output."""
    target = hub.soluble.RUN[name].ssh_target
    roster = hub.soluble.RUN[name].roster_file
    escalate = hub.soluble.RUN[name].escalate
    config_dir = hub.soluble.RUN[name].salt_config_dir
    options = " ".join(x.strip('"') for x in hub.soluble.RUN[name].salt_ssh_options)

    cmd = hub.lib.shutil.which("salt-ssh")
    assert cmd, "Could not find salt-ssh"

    full_command = f'{cmd} "{target}" --roster-file={roster} {command} --log-level=quiet --hard-crash {options} --no-color --out=json'
    if config_dir:
        full_command += f" --config-dir={config_dir}"
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

    # Wait for the process to complete and capture stdout at the end
    stdout, _ = await process.communicate()

    # Report the output of the salt-ssh commands
    data = hub.lib.json.loads(stdout.decode("utf-8"))
    for target, running in data.items():
        if isinstance(running, list):
            for comment in running:
                hub.log.error(comment)
            continue
        if not isinstance(running, dict):
            continue
        for state_name, state in running.items():
            if not isinstance(state, dict):
                hub.log.debug(f"{state_name}: {state}")
                continue
            hub.log.debug(
                f"{state_name}: {'success' if state['result'] else 'failure'}"
            )
            if state["comment"]:
                hub.log.debug(state["comment"])

            if state["changes"]:
                hub.log.debug(target + ":" + hub.lib.pprint.pformat(state["changes"]))

    returncode = await process.wait()
    if returncode != 0:
        raise ChildProcessError(f"Command failed: {full_command}")

    return data
