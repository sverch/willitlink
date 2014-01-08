from willitlink.cli.tools import get_graph, render

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer

from willitlink.queries.executables import get_executable_list

def get_executables(args):
    if args.g is None:
        g = get_graph(args)
    else:
        g = args.g

    with Timer('get executables query', args.timers):
        render(get_executable_list(g, args.name))
