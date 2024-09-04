from soluble.conf import CLI_CONFIG
from soluble.conf import SALT_SSH_GROUP
from soluble.conf import SUBCOMMANDS


def __init__(hub):
    hub.soluble.RUN = {}
    hub.pop.sub.add(dyne_name="salt")
    hub.pop.sub.add(dyne_name="lib")
    hub.pop.sub.add(python_import="asyncio", sub=hub.lib)
    hub.pop.sub.add(python_import="json", sub=hub.lib)
    hub.pop.sub.add(python_import="os", sub=hub.lib)
    hub.pop.sub.add(python_import="pathlib", sub=hub.lib, subname="path")
    hub.pop.sub.add(python_import="pprint", sub=hub.lib)
    hub.pop.sub.add(python_import="random", sub=hub.lib)
    hub.pop.sub.add(python_import="shutil", sub=hub.lib)
    hub.pop.sub.add(python_import="salt", sub=hub.lib)
    hub.pop.sub.add(python_import="socket", sub=hub.lib)
    hub.pop.sub.add(python_import="tempfile", sub=hub.lib)
    hub.pop.sub.add(python_import="typing", sub=hub.lib)
    hub.pop.sub.add(python_import="shlex", sub=hub.lib)
    hub.pop.sub.add(python_import="sys", sub=hub.lib)
    hub.pop.sub.add(python_import="uuid", sub=hub.lib)
    hub.pop.sub.add(python_import="yaml", sub=hub.lib)
    hub.pop.sub.add(python_import="warnings", sub=hub.lib)
    hub.pop.sub.add(
        python_import="dict_tools.data", subname="ddata", sub=hub.lib, omit_class=False
    )


def cli(hub):
    """
    Parse the config data and pass it to the actual runtime
    """
    soluble_plugins = list(hub.soluble._loaded.keys())

    # Dynamically add ssh_target to every subcommand
    CLI_CONFIG["ssh_target"]["subcommands"] = soluble_plugins

    # Dynamically create a subcommand for every soluble plugin
    for plugin in soluble_plugins:
        if plugin in SUBCOMMANDS:
            continue
        SUBCOMMANDS[plugin] = {"help": f"Create an ephemeral {plugin}"}

    hub.pop.config.load(["soluble"], cli="soluble")
    kwargs = dict(hub.OPT.soluble)
    salt_ssh_opts = []

    # Turn salt-ssh opts into a string
    for name, opts in CLI_CONFIG.items():
        if opts.get("group") != SALT_SSH_GROUP:
            continue

        value = kwargs.pop(name, None)
        if value is None:
            continue

        if isinstance(value, tuple):
            for v in value:
                salt_ssh_opts.append(opts["options"][0])
                if " " in v:
                    v = f"'{v}'"
                salt_ssh_opts.append(str(v))
        else:
            salt_ssh_opts.append(opts["options"][0])

            # This is a flag
            if isinstance(value, bool):
                continue

            salt_ssh_opts.append(str(value))

    kwargs["salt_ssh_options"] = salt_ssh_opts

    if not hub.SUBPARSER:
        print(hub.args.parser.help())
        return 2

    hub.pop.loop.create()

    coroutine = hub.soluble.init.apply(plugin=hub.SUBPARSER, **kwargs)
    retcode = hub.pop.Loop.run_until_complete(coroutine)
    hub.lib.sys.exit(retcode)


async def apply(hub, plugin: str = "minion", run_name: str = None, **kwargs) -> int:
    """
    Any valid "soluble" plugin must have a "setup", "run", and "teardown" function.
    """
    if run_name is None:
        run_name = str(hub.lib.uuid.uuid4())
    hub.soluble.RUN[run_name] = hub.lib.ddata.NamespaceDict(**kwargs)

    retcode = 0
    try:
        hub.log.info("Running setup on target(s)...")
        await hub.soluble[plugin].setup(run_name)
        retcode = await hub.soluble[plugin].run(run_name)
    finally:
        if not hub.soluble.RUN[run_name].bootstrap:
            hub.log.info("Running teardown on target(s)...")
            await hub.soluble[plugin].teardown(
                run_name,
            )

    return retcode


# Boilerplate code for creating a soluble plugin


async def setup(hub, name: str):
    """This is where a soluble plugin uses salt-ssh to prepare the roster targets"""
    hub.log.info("Soluble setup")
    await hub.salt.ssh.run_command(
        name,
        f"-H",
    )


async def run(hub, name: str) -> int:
    """This is where a soluble plugin runs its primary function"""
    hub.log.info("Soluble run")
    # TODO do a salt-ssh --raw
    await hub.salt.ssh.run_command(name, f"test.ping", capture_output=False)
    return 0


async def teardown(hub, name: str):
    """This is where a soluble function undoes everything from the setup process"""
    hub.log.info("Soluble teardown")
    await hub.salt.ssh.run_command(
        name,
        f"test.ping",
    )
