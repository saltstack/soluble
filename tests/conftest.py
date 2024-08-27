from unittest import mock

import pytest


@pytest.fixture(scope="session", name="hub")
def integration_hub(hub):
    hub.pop.sub.add(dyne_name="soluble")

    with mock.patch("sys.argv", ["soluble"]):
        hub.pop.config.load(["soluble"], cli="soluble", parse_cli=False)

    yield hub
