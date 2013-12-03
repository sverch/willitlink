from willitlink.cli.tools import get_graph, render

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer

from willitlink.queries.tree_leaks import find_libraries_needed, find_libraries_needed_full, find_libraries_needed_multi

# Given a list of file names, gets all the libraries required for this library to link.
# TODO: First pass - Just get the names of the libraries
# TODO: Second pass - Mark circular dependencies
# TODO: Third pass - Mark multiple declarations
def get_circle_deps(args):
    if args.g is None:
        g = get_graph(args)
    else:
        g = args.g

    with Timer('get libs needed query', args.timers):
        render(find_libraries_needed_full(g, args.names))

def get_required_libs(args):
    if args.g is None:
        g = get_graph(args)
    else:
        g = args.g

    with Timer('get libs needed query', args.timers):
        render(find_libraries_needed_multi(g, args.names))
