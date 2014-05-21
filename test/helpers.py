from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
import os, shutil

cwd = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
data_dir = os.path.join(cwd, 'data')
data_file = os.path.join(data_dir, 'dep_graph.json')
temp_data_dir = os.path.join(cwd, 'data_tmp')
temp_data_file = os.path.join(cwd, 'data_tmp', 'dep_graph.json')

def get_test_graph():
    with Timer('loading graph {0}'.format(data_dir), True):
        g = MultiGraph(timers=True).load(data_dir)

    return g

def export_temporary_test_graph(graph):
    if not os.path.exists(temp_data_dir):
        os.mkdir(temp_data_dir)

    with Timer('exporting graph {0}'.format(temp_data_file), True):
        graph.export(temp_data_file)

def load_temporary_test_graph():
    with Timer('loading graph {0}'.format(temp_data_file), True):
        g = MultiGraph(timers=True).load(temp_data_file)

    return g

def cleanup_temporary_test_graph():
    if os.path.exists(temp_data_dir):
        shutil.rmtree(temp_data_dir)
