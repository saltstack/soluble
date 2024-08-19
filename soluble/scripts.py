#!/usr/bin/env python3
import pop.hub


def start():
    hub = pop.hub.Hub()
    hub.pop.sub.add(dyne_name="soluble")
    hub.soluble.init.cli()
