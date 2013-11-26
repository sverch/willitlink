from willitlink.cli.tools import render, get_graph

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer

from willitlink.queries.libstats import resolve_leak_info
from willitlink.queries.tree_leaks import find_direct_leaks
from willitlink.queries.extra_archives import find_extra_archives

def get_leaks(args):
    if args.g is None:
        g = get_graph(args)

    with Timer('leaks query', args.timers):
        leaks = find_direct_leaks(g, args.name)

    render({ 'archive': args.name, 'leaks': leaks })

def get_leak_check(args):
    if args.g is None:
        g = get_graph(args)
    else:
        g = args.g

    with Timer('leaks tree query', args.timers):
        render(resolve_leak_info(g, args.name, args.depth, args.timers))

def get_direct_leaks(args):
    g = get_graph(args)

    with Timer('direct leak query', args.timers):
        render(find_direct_leaks(g, args.name))

def get_unneeded_libdeps(args):
    g = get_graph(args)

    archives = []
    for filename in g.files:
        if filename.endswith(".a"):
            archives.append(filename)
    print('[wil]: total number of archives: ' + str(len(archives)))

    with Timer('find unneeded libdeps', args.timers):
        render(find_extra_archives(g, args.name))
