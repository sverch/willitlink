from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
import os

cwd = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
data_file = os.path.join(cwd, 'data', "dep_graph.json")

def get_test_graph():
    with Timer('loading graph {0}'.format(data_file), True):
        g = MultiGraph(timers=True).load(data_file)

    return g
