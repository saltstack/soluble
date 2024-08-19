
async def accept_keys(hub, targets: list[str]):
    """Accept the ephemeral minion keys on the Salt master."""
    for target in targets:
        minion_id = await hub.soluble.minion.get_id(target)
        await hub.soluble.ssh.run_command(f"salt-key -a {minion_id} -y", escalate=True)

async def run_salt_command(hub, salt_command: str, salt_options: list[str]):
    """Run the specified Salt command targeting all ephemeral minions."""
    await hub.soluble.ssh.run_command(f"salt 'ephemeral-node-*' {salt_command} {' '.join(salt_options)}", escalate=True)
