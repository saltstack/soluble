from unittest import mock

import pop.hub
import pytest


@pytest.fixture(scope="function", name="hub")
def integration_hub():
    hub = pop.hub.Hub()
    hub.pop.sub.add("tests.helpers", subname="test")
    hub.pop.sub.add(dyne_name="soluble")

    hub.pop.sub.add(python_import="asyncio", sub=hub.lib)
    hub.pop.sub.add(python_import="asyncssh", sub=hub.lib)
    hub.pop.sub.add(python_import="docker", sub=hub.lib)
    hub.pop.sub.add(python_import="pathlib", sub=hub.lib)
    hub.pop.sub.add(python_import="pytest", sub=hub.lib)
    hub.pop.sub.add(python_import="pwd", sub=hub.lib)
    hub.pop.sub.add(python_import="uuid", sub=hub.lib)
    hub.pop.sub.add(python_import="sys", sub=hub.lib)
    hub.pop.sub.add(python_import="socket", sub=hub.lib)
    hub.pop.sub.add(python_import="tempfile", sub=hub.lib)

    with mock.patch("sys.argv", ["soluble"]):
        hub.pop.config.load(["soluble"], cli="soluble", parse_cli=False)

    yield hub


@pytest.fixture(scope="function", autouse=True)
def cleanup_containers(hub):
    # Yield first, after the test, clean up the containers
    try:
        yield
    finally:
        for container in hub.test.CONTAINER.values():
            container.stop()
            container.remove()


@pytest.fixture(scope="function", autouse=True)
def salt_config_dir(hub):
    # Create a temporary directory for the configuration files
    tempdir = hub.lib.tempfile.TemporaryDirectory()

    # Get the current user's username
    user = hub.lib.pwd.getpwuid(hub.lib.os.getuid()).pw_name

    # Define the paths within the temp directory
    config_dir = tempdir.name
    root_dir = hub.lib.os.path.join(config_dir, "salt")
    pki_dir_master = hub.lib.os.path.join(root_dir, "pki", "master")
    pki_dir_minion = hub.lib.os.path.join(root_dir, "pki", "minion")
    cachedir_master = hub.lib.os.path.join(root_dir, "cache", "master")
    cachedir_minion = hub.lib.os.path.join(root_dir, "cache", "minion")
    logs_master = hub.lib.os.path.join(root_dir, "logs", "master.log")
    logs_minion = hub.lib.os.path.join(root_dir, "logs", "minion.log")

    # Ensure all necessary directories exist
    hub.lib.os.makedirs(pki_dir_master, exist_ok=True)
    hub.lib.os.makedirs(pki_dir_minion, exist_ok=True)
    hub.lib.os.makedirs(cachedir_master, exist_ok=True)
    hub.lib.os.makedirs(cachedir_minion, exist_ok=True)
    hub.lib.os.makedirs(hub.lib.os.path.dirname(logs_master), exist_ok=True)
    hub.lib.os.makedirs(hub.lib.os.path.dirname(logs_minion), exist_ok=True)

    # Master configuration
    master_config = {
        "user": user,
        "root_dir": root_dir,
        "pki_dir": pki_dir_master,
        "cachedir": cachedir_master,
        "log_file": logs_master,
    }

    # Minion configuration
    minion_config = {
        "user": user,
        "master": "localhost",
        "root_dir": root_dir,
        "pki_dir": pki_dir_minion,
        "cachedir": cachedir_minion,
        "log_file": logs_minion,
    }

    # Write the master and minion configs to files
    master_config_path = hub.lib.os.path.join(config_dir, "master")
    minion_config_path = hub.lib.os.path.join(config_dir, "minion")

    with open(master_config_path, "w") as f:
        hub.lib.yaml.safe_dump(master_config, f)

    with open(minion_config_path, "w") as f:
        hub.lib.yaml.safe_dump(minion_config, f)

    # Store this on the nub
    hub.test.SALT_CONFIG_DIR = config_dir

    # Yield the config directory for use in other fixtures
    yield config_dir

    # Cleanup the temporary directory after the session
    tempdir.cleanup()


@pytest.fixture(scope="function")
async def salt_master(hub, salt_config_dir):
    # Start the Salt master using the configuration
    process = await hub.lib.asyncio.create_subprocess_exec(
        "salt-master",
        "-c",
        salt_config_dir,
        "-ldebug",
    )

    await hub.lib.asyncio.sleep(5)

    print("Done setting salt master")
    yield

    # Stop the Salt master after tests are done
    process.terminate()

    try:
        # Wait for the process to terminate gracefully
        await process.wait()
    except hub.lib.asyncio.CancelledError:
        # Ensure the process is fully stopped if wait fails
        process.kill()
        await process.wait()
