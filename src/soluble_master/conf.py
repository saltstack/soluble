CONFIG = {
    "master_config": {
        "default": "/etc/salt/master",
        "help": "Path to the master configuration template. Defaults to '/etc/salt/master'",
        "dyne": "soluble",
    },
}

CLI_CONFIG = {
    "master_config": {"subcommands": ["master"]},
}

DYNE = {"soluble": ["soluble"]}
