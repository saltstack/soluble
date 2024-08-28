from unittest import mock


def test_help(hub):
    with mock.patch("sys.argv", ["soluble"]):
        hub.soluble.init.cli()


async def test_cli(hub):
    await hub.test.container.create()
    assert await hub.test.cmd.run("init")
