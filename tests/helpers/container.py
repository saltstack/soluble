import contextlib


def __init__(hub):
    hub.test.ROSTER = {}
    hub.test.CONTAINER = {}


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


async def create(hub, username: str = "root", password: str = "pass"):
    host = "localhost"
    client = hub.lib.docker.from_env()
    port = hub.test.container.next_free_port("localhost")
    target_name = f"soluble_agent_{hub.lib.uuid.uuid4()}"

    container = client.containers.run(
        "python:3.10-slim",
        command=[
            "/bin/sh",
            "-c",
            f"""
        apt-get update && \
        apt-get install -y openssh-server && \
        echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
        service ssh restart && \
        echo 'root:{password}' | chpasswd && \
        while true; do sleep 1; done
    """,
        ],
        detach=True,
        ports={"22/tcp": port},
        hostname=target_name,
        network="bridge",
        environment={
            "user": username,
            "USER_PASSWORD": password,
        },
    )
    print(f"Created container: {container.id}")

    # Wait for SSH service to be available
    print(f"Trying to connect to container: {container.id}", end="")
    for _ in range(60):
        print(".", end="")
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
    print("\nSuccess!")

    hub.test.ROSTER[target_name] = container
    hub.test.ROSTER[target_name] = {
        "host": "localhost",
        "port": port,
        "user": username,
        "passwd": password,
        "minion_opts": {"master": "localhost"},
    }

    return hub.test.ROSTER[target_name]


@contextlib.contextmanager
def roster(hub):
    """
    Return roster file for all created containers
    """
    roster = hub.test.ROSTER.copy()
    with hub.lib.tempfile.NamedTemporaryFile("w+", suffix=".yaml", delete=False) as fh:
        hub.lib.yaml.safe_dump(roster, fh)
        yield fh.name
