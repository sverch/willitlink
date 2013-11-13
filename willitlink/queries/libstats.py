#!/usr/bin/python

import os
import sys
import json

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.family_tree import symbol_family_tree
from willitlink.queries.tree_leaks import  find_direct_leaks

def resolve_leak_info(g, name):
    o = []

    for leak in find_direct_leaks(g, name):

        leak_object = {
            'leak': leak,
            'sources': symbol_family_tree(g, leak['symbol'], 2)
        }

        o.append(leak_object)

    return o

def main():
    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " <archive name>")
        exit(1)

    pkl_file = os.path.join(os.path.dirname(__file__), "dep_graph.pickle")

    if os.path.exists(pkl_file):
        data_file = pkl_file
        print('[wil]: using pickle store')
    else:
        data_file = os.path.join(os.path.dirname(__file__), "dep_graph.json")
        print('[wil]: using json store')

    with Timer('loading data file', True):
        g = MultiGraph().load(data_file)

    with Timer('leak detection query operation', True):
        leak_objects = resolve_leak_info(g, sys.argv[1])
        
        print(json.dumps(leak_objects, indent=3))

if __name__ == '__main__':
    main()
