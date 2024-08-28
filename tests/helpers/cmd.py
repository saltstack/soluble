async def run(hub, subcommand: str, target: str = "*", *args):
    with hub.test.container.roster() as rf:
        command = f"{hub.lib.sys.executable} -m soluble -R {rf} {subcommand} '{target}' {' '.join(args)}"

        # Run the command asynchronously
        process = await hub.lib.asyncio.create_subprocess_shell(
            command,
            stdout=hub.lib.asyncio.subprocess.PIPE,
            stderr=hub.lib.asyncio.subprocess.PIPE,
        )

        # Capture the stdout and stderr
        stdout, stderr = await process.communicate()

    # Decode the output
    stdout = stdout.decode()
    stderr = stderr.decode()

    # Assert the process was successful
    assert (
        process.returncode == 0
    ), f"Command failed with code {process.returncode}: {stderr}"

    # Return the captured stdout
    return stdout
