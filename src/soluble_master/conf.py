CONFIG = {
    "master_config": {
        "default": "/etc/salt/master",
        "help": "Path to the master configuration template. Defaults to '/etc/salt/master'",
        "dyne": "soluble",
    },
}
GROUP = "Soluble Master"

CLI_CONFIG = {
    "master_config": {"subcommands": ["master"], "group": GROUP},
}

DYNE = {"soluble": ["soluble"]}
