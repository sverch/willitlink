from willitlink.cli.tools import get_graph, render

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer

from willitlink.queries.file_graph_generator import generate_file_graph

def get_file_graph(args):
    g = get_graph(args)

    with Timer('get file graph query', args.timers):
        render(generate_file_graph(g))
