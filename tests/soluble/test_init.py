from unittest import mock


def test_help(hub):
    with mock.patch("sys.argv", ["soluble"]):
        hub.soluble.init.cli()


async def test_cli(hub, salt_master):
    print("creating container")
    await hub.test.container.create()
    print("running command")
    await hub.test.cmd.run("init")
