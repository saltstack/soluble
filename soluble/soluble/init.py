import sys
import uuid

from dict_tools.data import NamespaceDict

def __init__(hub):
    hub.soluble.RUN = {}


def cli(hub):
    hub.pop.config.load(["soluble"], cli="soluble")
    kwargs = dict(hub.OPT.soluble)

    hub.pop.loop.create()

    coroutine = hub.soluble.init.run(**kwargs)
    retcode = hub.pop.Loop.run_until_complete(coroutine)
    sys.exit(retcode)


async def run(hub, **kwargs) -> int:
    """
    This is the entrypoint for the async code in your project
    """
    if not hub.SUBPARSER:
        print(hub.args.parser.help())
        return 2

    run_name = uuid.uuid4()
    hub.soluble.RUN[run_name] = NamespaceDict(**kwargs)
    return await hub.soluble[hub.SUBPARSER].run(run_name)
