# Anything higher than 20 is assumed to be ubuntu, lower than 20 is debian
DEBIAN_UBUNTU_MAJOR_RELEASE_CUTTOFF = 18

DEBIAN_REPO = "deb http://repo.saltproject.io/py3/ubuntu/{{ grains['osmajorrelease'] }}/amd64/latest {{ grains['oscodename'] }} main"
DEBIAN_KEY = "https://repo.saltproject.io/py3/ubuntu/{{ grains['osmajorrelease'] }}/amd64/latest/SALTSTACK-GPG-KEY.pub"
DEBIAN_TARGET = (
    f"os_family:Debian|osmajorrelease:>={DEBIAN_UBUNTU_MAJOR_RELEASE_CUTTOFF}"
)

UBUNTU_REPO = "deb http://repo.saltproject.io/py3/debian/{{ grains['osmajorrelease'] }}/amd64/latest {{ grains['oscodename'] }} main"
UBUNTU_KEY = "https://repo.saltproject.io/py3/debian/{{ grains['osmajorrelease'] }}/amd64/latest/SALTSTACK-GPG-KEY.pub"
UBUNTU_TARGET = (
    f"os_family:Debian|osmajorrelease:<{DEBIAN_UBUNTU_MAJOR_RELEASE_CUTTOFF}"
)

REDHAT_REPO = "https://repo.saltproject.io/py3/redhat/el{{ grains['osmajorrelease'] }}/x86_64/latest/"
REDHAT_KEY = "https://repo.saltproject.io/py3/redhat/el{{ grains['osmajorrelease'] }}/x86_64/latest/SALTSTACK-GPG-KEY.pub"
REDHAT_TARGET = "os_family:RedHat"

AMAZON_REPO = "https://repo.saltproject.io/py3/amazon/2/x86_64/latest/"
AMAZON_KEY = (
    "https://repo.saltproject.io/py3/amazon/2/x86_64/latest/SALTSTACK-GPG-KEY.pub"
)
AMAZON_TARGET = "os:Amazon"


async def setup(hub, name: str):
    """
    Add the SaltStack repository and install Salt based on the target OS.
    First, target Ubuntu-based systems, then fall back to other Debian-based systems (e.g., Debian, SteamOS).
    """
    # TODO this functionality is not quite ready
    return
    hub.log.info("Setting up SaltStack repository on target(s)...")

    # Handle Ubuntu-based systems (Pop!_OS, etc.)
    await hub.salt.ssh.run_command(
        name,
        "state.single",
        "pkgrepo.managed",
        f'name="{DEBIAN_REPO}"',
        f'key_url="{DEBIAN_KEY}"',
        "refresh=True",
        "--delimiter='|'",
        target=DEBIAN_TARGET,
        target_type="grain_pcre",
    )

    # Fallback to other Debian-based systems
    await hub.salt.ssh.run_command(
        name,
        "state.single",
        "pkgrepo.managed",
        f'name="{UBUNTU_REPO}"',
        f'key_url="{UBUNTU_KEY}"',
        "refresh=True",
        "--delimiter='|'",
        target=UBUNTU_TARGET,
        target_type="grain_pcre",
    )

    # Target RedHat/CentOS systems
    await hub.salt.ssh.run_command(
        name,
        "state.single",
        "pkgrepo.managed",
        f'name="{REDHAT_REPO}"',
        f'gpgkey="{REDHAT_KEY}"',
        "gpgcheck=1",
        "refresh=True",
        target=REDHAT_TARGET,
        target_type="grain",
    )

    # Target Amazon Linux systems
    await hub.salt.ssh.run_command(
        name,
        "state.single",
        "pkgrepo.managed",
        f'name="{AMAZON_REPO}"',
        f'gpgkey="{AMAZON_KEY}"',
        "gpgcheck=1",
        "refresh=True",
        target=AMAZON_TARGET,
        target_type="grain",
    )

    hub.log.info("SaltStack repository set up successfully.")


async def teardown(hub, name: str):
    """
    Remove the SaltStack repository based on the target OS.
    First, target Ubuntu-based systems, then fall back to other Debian-based systems (e.g., Debian, SteamOS).
    Finally, handle RedHat-based and Amazon Linux systems.
    """
    # TODO this functionality is not quite ready
    return
    hub.log.info("Removing SaltStack repository from target(s)...")

    # Handle Ubuntu-based systems (Pop!_OS, etc.)
    await hub.salt.ssh.run_command(
        name,
        "state.single",
        "pkgrepo.absent",
        f'name="{UBUNTU_REPO}"',
        "--delimiter='|'",
        target=UBUNTU_TARGET,
        target_type="grain_pcre",
    )

    # Fallback to other Debian-based systems
    await hub.salt.ssh.run_command(
        name,
        "state.single",
        "pkgrepo.absent",
        f'name="{DEBIAN_REPO}"',
        "--delimiter='|'",
        target=DEBIAN_TARGET,
        target_type="grain_pcre",
    )

    # Remove repository for RedHat/CentOS systems
    await hub.salt.ssh.run_command(
        name,
        "state.single",
        "pkgrepo.absent",
        f'name="{REDHAT_REPO}"',
        target=REDHAT_TARGET,
        target_type="grain",
    )

    # Remove repository for Amazon Linux systems
    await hub.salt.ssh.run_command(
        name,
        "state.single",
        "pkgrepo.absent",
        f'name="{AMAZON_REPO}"',
        target=AMAZON_TARGET,
        target_type="grain",
    )

    hub.log.info("SaltStack repository removed successfully.")
    return 0
