from unittest import mock


def test_help(hub):
    with mock.patch("sys.argv", ["soluble", "master", "--help"]):
        hub.pop.config.load(["soluble"], cli="soluble")


async def test_cli(hub):
    ...
