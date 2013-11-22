from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.symbol_diff import get_full_filenames

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

def get_paths(source_map):

    # Base case is empty map
    if len(source_map) == 0:
        return []

    # Otherwise, iterate the keys, and recursively call
    path_list = []
    for k in source_map.keys():
        paths = get_paths(source_map[k])
        if len(paths) == 0:
            path_list.append([ k ])
        else:
            path_list.extend([ [ k ] + p for p in paths ])

    return path_list

def reverse_lists(lists):
    return [ lst.reverse()
             for lst in lists ]

def flip_tree(source_map):
    dest_map = {}
    paths = get_paths(source_map)
    reverse_lists(paths)
    add_paths(dest_map, paths)
    return dest_map

def file_family_tree(g, file_name, depth=None):
    return family_tree_base(graph=g,
                            relations=get_full_filenames(g, file_name),
                            depth=depth,
                            flipped=True)

def symbol_family_tree(g, symbol_name, depth=None):
    return family_tree_base(graph=g,
                            relations=g.get('symbol_to_file_sources', symbol_name),
                            depth=depth,
                            flipped=True)

def family_tree_base(graph, relations, depth, flipped=True):
    o = {}

    if depth is not None and depth > 0:
        depth = depth - 1

        for obj in relations:
            o[obj] = family_tree_base(graph, graph.get('dependency_to_targets', obj), depth)

        if flipped is True:
            return flip_tree(o)
        else:
            return o
    else:
        return o
