CONFIG = {
    "roster_file": {
        "default": "/srv/salt/roster",
        "help": "Path to the roster file for salt-ssh",
    },
    "minion_config": {
        "default": "/etc/salt/minion",
        "help": "Path to the minion configuration template. Defaults to '/etc/salt/minion' or the master's default minion config",
    },
    "node_prefix": {
        "default": "ephemeral-node-",
        "help": "A prefix to add to the ephemeral minion id",
    },
    "bootstrap": {
        "default": False,
        "help": "Don't tear down the minion",
    },
    "escalate": {
        "default": False,
        "help": "Run salt commands as root",
    },
}

CLI_CONFIG = {
    "roster_file": {"options": ["-R"]},
    "minion_config": {"subcommands": ["minion"]},
    "ssh_target": {
        "positional": True,
        "display_priority": 1,
        "subcommands": ["minion"],
        "help": "Target for the salt-ssh command. This is typically a minion ID, wildcard, or grain.",
    },
    "salt_command": {
        "positional": True,
        "display_priority": 2,
        "subcommands": ["minion"],
        "help": "The salt command to run on the ephemeral nodes",
    },
    "salt_options": {
        "positional": True,
        "display_priority": 3,
        "nargs": "...",
        "subcommands": ["minion"],
        "help": "Additional options to be passed to the salt command",
    },
    "salt_ssh_options": {
        "options": ["-O"],
        "action": "append",
        "help": "Additional options to be forwarded to salt-ssh",
    },
    "bootstrap": {
        "action": "store_true",
        "subcommands": ["minion"],
    },
    "escalate": {
        "action": "store_true",
        "subcommands": ["minion"],
    },
}

SUBCOMMANDS = {
    "minion": {
        "help": "",
        "desc": "",
    }
}


DYNE = {"soluble": ["soluble"]}
