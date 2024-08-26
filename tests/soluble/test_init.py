from unittest import mock


def test_cli(hub):
    with mock.patch("sys.argv", ["soluble"]):
        hub.soluble.init.cli()
