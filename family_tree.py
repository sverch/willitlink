#!/usr/bin/python

import os
import sys
import json

import dep_graph
from helpers.dev_tools import Timer

def get_full_filenames(g, file_name):

    full_file_names = []

    for i in g.files:
        if i.endswith(file_name):
            full_file_names.append(i)

    return full_file_names

def file_family_tree_recursive(g, full_file_name, depth):

    family_tree_hash = {}

    if depth is not None:
        if depth == 0:
            return {}
        depth = depth - 1

    parents = []
    try:
        parents = g.get('dependency_to_targets', full_file_name)
    except KeyError:
        pass

    for parent in parents:
        family_tree_hash[parent] = file_family_tree_recursive(g, parent, depth)

    return family_tree_hash

def file_family_tree(g, file_name, depth = None):

    family_tree_hash = {}

    if depth is not None:
        if depth == 0:
            return {}
        depth = depth - 1

    full_file_names = get_full_filenames(g, file_name)

    for full_file_name in full_file_names:
        family_tree_hash[full_file_name] = file_family_tree_recursive(g, full_file_name, depth)

    return family_tree_hash

def symbol_family_tree(g, symbol_name, depth = None):

    family_tree_hash = {}

    if depth is not None:
        if depth == 0:
            return {}
        depth = depth - 1

    try:
        file_sources =  g.get('symbol_to_file_sources', symbol_name)
    except KeyError:
        pass

    for file_source in file_sources:
        family_tree_hash[file_source] = file_family_tree_recursive(g, file_source, depth)

    return family_tree_hash

def usage():
        print("Usage: " + sys.argv[0] + " <symbol/file> <name> [<depth>]")

def main():

    depth = None

    if len(sys.argv) == 4:
        depth = sys.argv[3]
    elif len(sys.argv) != 3:
        usage()
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

    if sys.argv[1] == "symbol":
        with Timer('family tree query operation', True):
            print json.dumps(symbol_family_tree(g, sys.argv[2], int(depth)), indent=4)
    elif sys.argv[1] == "file":
            print json.dumps(file_family_tree(g, sys.argv[2], int(depth)), indent=4)
    else:
        usage()
        exit(1)

if __name__ == '__main__':
    main()
