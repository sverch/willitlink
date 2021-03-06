from willitlink.cli.tools import render, get_graph

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer

from willitlink.queries.tree_leaks import resolve_leak_info
from willitlink.queries.extra_archives import find_extra_archives

def get_leaks(args):
    if args.g is None:
        g = get_graph(args)
    else:
        g = args.g

    with Timer('leaks tree query', args.timers):
        render(resolve_leak_info(g, args.names, args.depth, args.timers, args.source_names))

def get_unneeded_libdeps(args):
    g = get_graph(args)


    ct = 0
    for filename in g.files:
        if filename.endswith(".a"):
            ct += 1
    print('[wil]: total number of archives: ' + str(ct))

    with Timer('find unneeded libdeps', args.timers):
        render(list(find_extra_archives(g, args.name)))
