async def run(hub, subcommand: str, target: str = "*", *args):
    with hub.test.container.roster() as rf:
        command = f"{hub.lib.sys.executable} -m soluble --ssh-option='-o StrictHostKeyChecking=no' --log-level=debug --salt-config-dir {hub.test.SALT_CONFIG_DIR} -R {rf} {subcommand} '{target}' {' '.join(args)}"

        # Run the command asynchronously
        process = await hub.lib.asyncio.create_subprocess_shell(
            command,
            stdout=hub.lib.asyncio.subprocess.PIPE,
        )

        await hub.lib.asyncio.sleep(2)

        # Capture the stdout and stderr
        stdout, _ = await process.communicate()

    # Decode the output
    stdout = stdout.decode()
    print(stdout)
    assert not await process.wait(), "Command failed"

    # Return the captured stdout
    return stdout
