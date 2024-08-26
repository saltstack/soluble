from soluble.conf import CLI_CONFIG


def __init__(hub):
    hub.soluble.RUN = {}
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
    hub.pop.config.load(["soluble"], cli="soluble")
    kwargs = dict(hub.OPT.soluble)
    salt_ssh_opts = []

    # Turn salt-ssh opts into a string
    for name, opts in CLI_CONFIG.items():
        if opts.get("group", "").lower() != "salt-ssh":
            continue

        value = kwargs.pop(name, None)
        if value is None:
            continue

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

    coroutine = hub.soluble.init.run(plugin=hub.SUBPARSER, **kwargs)
    retcode = hub.pop.Loop.run_until_complete(coroutine)
    hub.lib.sys.exit(retcode)


async def run(hub, plugin: str = "minion", **kwargs) -> int:
    """
    This is the entrypoint for the project
    """
    run_name = str(hub.lib.uuid.uuid4())
    hub.soluble.RUN[run_name] = hub.lib.ddata.NamespaceDict(**kwargs)
    await hub.soluble[plugin].run(run_name)
    return run_name
