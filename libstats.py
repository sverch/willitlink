#!/usr/bin/python

import os
import sys
import json

import dep_graph
from helpers.dev_tools import Timer
import family_tree
import tree_leaks

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
        g = dep_graph.MultiGraph().load(data_file)

    with Timer('leak detection query operation', True):
        leak_objects = []
        for leak in tree_leaks.find_direct_leaks(g, sys.argv[1]):
            leak_object = {}
            leak_object['leak'] = leak
            leak_object['sources'] = family_tree.symbol_family_tree(g, leak['symbol'], 2)
            leak_objects.append(leak_object)

        print(json.dumps(leak_objects, indent=3))

if __name__ == '__main__':
    main()
