import json

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer

def get_graph(args):
    with Timer('loading graph {0}'.format(args.data), args.timers):
        g = MultiGraph(timers=args.timers).load(args.data)

    return g

def render(data):
    print(json.dumps(data, indent=3))
