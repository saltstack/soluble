from unittest import mock


def test_help(hub):
    with mock.patch("sys.argv", ["soluble", "--help"]):
        hub.pop.config.load(["soluble"], cli="soluble")


def test_sub_help(hub):
    with mock.patch("sys.argv", ["soluble", "init", "--help"]):
        hub.pop.config.load(["soluble"], cli="soluble")


async def test_cli(hub, salt_master):
    await hub.test.container.create()
    await hub.test.cmd.run("init")
