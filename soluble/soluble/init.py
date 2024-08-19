def cli(hub):
    hub.pop.config.load(["soluble"], cli="soluble")
    # Your app's options can now be found under hub.OPT.soluble
    kwargs = dict(hub.OPT.soluble)

    # Initialize the asyncio event loop
    hub.pop.loop.create()

    # Start the async code
    coroutine = hub.soluble.init.run(**kwargs)
    hub.pop.Loop.run_until_complete(coroutine)


import pprint


async def run(hub, **kwargs):
    """
    This is the entrypoint for the async code in your project
    """
    print("soluble works!")
    pprint.pprint(hub.OPT.soluble)
