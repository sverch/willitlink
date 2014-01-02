from willitlink.cli.tools import render, get_graph

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer

from willitlink.queries.find_interface import find_interface

def get_interface(args):
    g = get_graph(args)

    with Timer('direct leak query', args.timers):
        render(find_interface(g, args.name))
