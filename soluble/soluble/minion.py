import pprint


async def run(
    hub,
    ssh_target: str,
    salt_command: str,
    *,
    roster_file: str,
    minion_config: str,
    salt_options: list[str],
    salt_ssh_options: list[str],
    **kwargs
) -> int:
    pprint.pprint(locals())
    return 0
