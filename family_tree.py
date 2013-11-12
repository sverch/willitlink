#!/usr/bin/python

import os
import sys
import json

import dep_graph
from helpers.dev_tools import Timer

def add_path(result_map, path):
    if len(path) == 0:
        result_map = {}
        return

    if path[0] not in result_map:
        result_map[path[0]] = {}
    add_path(result_map[path[0]], path[1:])

def add_paths(result_map, path_list):
    for path in path_list:
        add_path(result_map, path)

def dict_is_empty(D):
    for k in D:
        return False
    return True

def get_paths(source_map):

    # Base case is empty map
    if dict_is_empty(source_map):
        return []

    # Otherwise, iterate the keys, and recursively call
    path_list = []
    for k in source_map.keys():
        paths = get_paths(source_map[k])
        if len(paths) == 0:
            path_list.append([ k ])
        else:
            for path in get_paths(source_map[k]):
                path_list.append([ k ] + path)

    return path_list

def reverse_lists(lists):
    for to_reverse in lists:
        to_reverse.reverse()
    return lists

def flip_tree(source_map):
    dest_map = {}
    paths = get_paths(source_map)
    reverse_lists(paths)
    add_paths(dest_map, paths)
    return dest_map

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

    return flip_tree(family_tree_hash)

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

    return flip_tree(family_tree_hash)

def usage():
        print("Usage: " + sys.argv[0] + " <symbol/file> <name> [<depth>]")

def main():

    depth = None

    if len(sys.argv) == 4:
        depth = int(sys.argv[3])
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
            print json.dumps(symbol_family_tree(g, sys.argv[2], depth), indent=4)
    elif sys.argv[1] == "file":
            print json.dumps(file_family_tree(g, sys.argv[2], depth), indent=4)
    else:
        usage()
        exit(1)

if __name__ == '__main__':
    main()
