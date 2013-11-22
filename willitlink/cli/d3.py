from willitlink.cli.tools import get_graph, render

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer

from willitlink.queries.d3.d3_family_tree import file_family_tree_d3
from willitlink.queries.d3.d3_relationship import relationship_info_d3
from willitlink.queries.d3.d3_leaks import add_leaks_d3

def get_file_family_tree_d3(args):
    g = get_graph(args)

    with Timer('get file family tree query', args.timers):
        render(file_family_tree_d3(g, [args.name]))

def get_file_family_tree_with_leaks_d3(args):
    g = get_graph(args)

    family_tree = {}

    with Timer('get file family tree query', args.timers):
        family_tree = file_family_tree_d3(g, [args.name])

    with Timer('add leaks query', args.timers):
        render(add_leaks_d3(g, family_tree))

def get_file_family_relationship_d3(args):
    g = get_graph(args)

    args.files.append(args.first_file)
    with Timer('relationship info query', args.timers):
        render(relationship_info_d3(g, args.files))
