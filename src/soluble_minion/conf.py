CONFIG = {
    "minion_config": {
        "default": "/etc/salt/minion",
        "help": "Path to the minion configuration template. Defaults to '/etc/salt/minion'",
        "dyne": "soluble",
    },
}

GROUP = "Soluble Minion"

CLI_CONFIG = {
    "minion_config": {"subcommands": ["minion"]},
    "salt_command": {
        "positional": True,
        "display_priority": 2,
        "subcommands": ["minion"],
        "help": "The salt command to run on the ephemeral nodes",
        "dyne": "soluble",
        "group": GROUP,
    },
    "salt_options": {
        "positional": True,
        "display_priority": 3,
        "nargs": "...",
        "subcommands": ["minion"],
        "help": "Additional options to be passed to the salt command",
        "dyne": "soluble",
        "group": GROUP,
    },
}

DYNE = {"soluble": ["soluble"]}
