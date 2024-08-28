from unittest import mock

import pytest


@pytest.fixture(scope="session", name="hub")
def integration_hub(hub):
    hub.pop.sub.add("tests.helpers", subname="test")
    hub.pop.sub.add(dyne_name="soluble")

    hub.pop.sub.add(python_import="asyncio", sub=hub.lib)
    hub.pop.sub.add(python_import="asyncssh", sub=hub.lib)
    hub.pop.sub.add(python_import="docker", sub=hub.lib)
    hub.pop.sub.add(python_import="pytest", sub=hub.lib)
    hub.pop.sub.add(python_import="uuid", sub=hub.lib)
    hub.pop.sub.add(python_import="sys", sub=hub.lib)
    hub.pop.sub.add(python_import="socket", sub=hub.lib)
    hub.pop.sub.add(python_import="tempfile", sub=hub.lib)

    with mock.patch("sys.argv", ["soluble"]):
        hub.pop.config.load(["soluble"], cli="soluble", parse_cli=False)

    yield hub
