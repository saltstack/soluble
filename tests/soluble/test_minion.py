from unittest import mock


def test_help(hub):
    with mock.patch("sys.argv", ["soluble", "minion", "--help"]):
        hub.pop.config.load(["soluble"], cli="soluble")


async def test_cli(hub, salt_master):
    await hub.test.container.create()
    await hub.test.cmd.run("minion", "test.ping")
