from unittest import mock

import pop.hub
import pytest


@pytest.fixture(scope="session", name="hub")
def integration_hub():
    hub = pop.hub.Hub()
    hub.pop.sub.add(dyne_name="soluble")

    with mock.patch("sys.argv", ["soluble"]):
        hub.pop.config.load(["soluble"], cli="soluble")

    yield hub
