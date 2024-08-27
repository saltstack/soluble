import shutil

CONFIG = {
    "minion_config": {
        "default": "/etc/salt/minion",
        "help": "Path to the minion configuration template. Defaults to '/etc/salt/minion'",
        "dyne": "soluble",
    },
    "salt_bin": {
        "default": shutil.which("salt"),
        "help": "Path to the salt command",
        "dyne": "soluble",
    },
    "salt_key_bin": {
        "default": shutil.which("salt-key"),
        "help": "Path to the salt-key command",
        "dyne": "soluble",
    },
}

CLI_CONFIG = {
    "minion_config": {"subcommands": ["minion"]},
    "salt_bin": {
        "subcommands": ["minion"],
    },
    "salt_key_bin": {
        "subcommands": ["minion"],
    },
    "salt_command": {
        "positional": True,
        "display_priority": 2,
        "subcommands": ["minion"],
        "help": "The salt command to run on the ephemeral nodes",
        "dyne": "soluble"
    },
    "salt_options": {
        "positional": True,
        "display_priority": 3,
        "nargs": "...",
        "subcommands": ["minion"],
        "help": "Additional options to be passed to the salt command",
        "dyne": "soluble"
    },
}


SUBCOMMANDS = {
    "minion": {
        "help": "Create an ephemeral minion",
        "dyne": "soluble"
    }
}

DYNE = {"soluble": ["soluble"]}
