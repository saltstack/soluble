import shutil

import salt.utils.parsers as salt_parsers


ssh_parser = salt_parsers.SaltSSHOptionParser()
all_opts = {
    str(opt.dest): opt
    for opt in ssh_parser._get_all_options()
    if opt.dest
    and not any(key in opt.dest for key in ("log", "out", "crash", "version", "color"))
}

CONFIG = {
    "bootstrap": {
        "default": False,
        "help": "Don't tear down the minion",
    },
    "escalate": {
        "default": False,
        "help": "Run salt commands as root",
    },
    "minion_config": {
        "default": all_opts["config_dir"].default + "/minion",
        "help": "Path to the minion configuration template. Defaults to '/etc/salt/minion' or the master's default minion config",
    },
    "salt_config_dir": {
        "default": all_opts["config_dir"].default,
        "help": all_opts["config_dir"].help.replace("%", ""),
    },
    "node_prefix": {
        "default": "ephemeral-node-",
        "help": "A prefix to add to the ephemeral minion id",
    },
    "roster_file": {
        "default": all_opts["roster_file"].default,
        "help": all_opts["roster_file"].help,
    },
    "salt_bin": {
        "default": shutil.which("salt"),
        "help": "Path to the salt command",
    },
    "salt_key_bin": {
        "default": shutil.which("salt-key"),
        "help": "Path to the salt-key command",
    },
}

CLI_CONFIG = {
    "bootstrap": {
        "action": "store_true",
        "subcommands": ["minion"],
    },
    "escalate": {
        "action": "store_true",
        "subcommands": ["minion"],
    },
    "minion_config": {"subcommands": ["minion"]},
    "roster_file": {"options": ["-R"]},
    "ssh_target": {
        "positional": True,
        "display_priority": 1,
        "subcommands": ["minion"],
        "help": "Target for the salt-ssh command. This is typically a minion ID, wildcard, or grain.",
    },
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
    },
    "salt_config_dir": {},
    "salt_options": {
        "positional": True,
        "display_priority": 3,
        "nargs": "...",
        "subcommands": ["minion"],
        "help": "Additional options to be passed to the salt command",
    },
}

SALT_SSH_OPTIONS = {}
for name, opt in all_opts.items():
    if name in CLI_CONFIG:
        continue
    if name in SALT_SSH_OPTIONS:
        continue
    if name in ("config_dir",):
        continue
    SALT_SSH_OPTIONS[name] = dict(
        dest=opt.dest,
        default=opt.default,
        help=str(opt.help).replace("%", " "),
        metavar=opt.metavar,
        choies=opt.choices,
        action=opt.action if "store" in opt.action else None,
        nargs=opt.nargs,
        options=opt._long_opts + opt._short_opts,
        group="Salt-SSH",
    )

CLI_CONFIG.update(SALT_SSH_OPTIONS)

SUBCOMMANDS = {
    "minion": {
        "help": "Create an ephemeral minion",
    }
}

DYNE = {"soluble": ["soluble"]}
