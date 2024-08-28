import contextlib


def __init__(hub):
    hub.test.TARGETS = {}


def next_free_port(hub, host, port: int = 2222) -> int:
    for i in range(1000):
        with hub.lib.socket.socket(
            hub.lib.socket.AF_INET, hub.lib.socket.SOCK_STREAM
        ) as sock:
            sock.settimeout(2)
            try:
                sock.bind((host, port))
                break
            except OSError:
                port += 2
    else:
        raise RuntimeError(f"Unable to find an available port on {host}")

    return port


async def create_ssh_target(
    hub, host: str, username: str = "user", password: str = "pass"
):
    client = hub.lib.docker.from_env()
    port = hub.test.container.next_free_port(host)
    target_name = f"soluble_test_{hub.lib.uuid.uuid4()}"
    pugid = "0" if username == "root" else "1000"

    container = client.containers.run(
        "linuxserver/openssh-server:latest",
        command=["/bin/sh", "-c", "while true; do sleep 1; done"],
        detach=True,
        ports={"2222/tcp": port},
        hostname=target_name,
        network="bridge",
        environment={
            "PUID": pugid,
            "PGID": pugid,
            "TZ": "Etc/UTC",
            "SUDO_ACCESS": "true",
            "PASSWORD_ACCESS": "true",
            "USER_NAME": username,
            "USER_PASSWORD": password,
        },
    )

    # Enable SSH Tunneling
    container.exec_run(
        cmd="sed -i 's/^AllowTcpForwarding no/AllowTcpForwarding yes/' /etc/ssh/sshd_config",
        privileged=True,
        detach=True,
    )
    if username == "root":
        container.exec_run(
            cmd="sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config",
            privileged=True,
            detach=True,
        )

    # Wait for SSH service to be available
    for _ in range(60):
        try:
            async with hub.lib.asyncssh.connect(
                host=host,
                port=port,
                username=username,
                password=password,
                known_hosts=None,
            ):
                break
        except:
            await hub.lib.asyncio.sleep(1)
    else:
        container.stop()
        container.remove()
        raise RuntimeError("Could not connect to container")

    hub.test.TARGETS[target_name] = {
        "name": target_name,
        "port": port,
        "username": username,
        "password": password,
        "container": container,
    }

    return hub.test.TARGETS[target_name]


@contextlib.contextmanager
def roster(hub):
    """
    Return roster file for all created containers
    """
    roster = hub.test.TARGETS
    with hub.lib.tempfile.NamedTemporaryFile(suffix=".yaml") as fh:
        hub.lib.yaml.safe_dump(roster, fh)
        yield fh.name
