from willitlink.base.graph import MultiGraph, ResultsGraph

# TODO: Do this in a smarter way or preprocess this somehow.  This is related to
# the ingestion code, so once we get better scons integration we'll be better at
# determing the types of things at that point.

from willitlink.ingestion.parse_scons_dependency_tree import detect_type

# TODO: Do this in a smarter way.  This function's purpose is to basically clean
# up names from the user, so that they can type libmongocommon.a rather than the
# full path.

# TODO: Doing queries on things like "mongod" result in an infinite loop, since
# multiple targets end with "mongod"

def get_full_filenames(g, file_names):

    full_file_names = []

    if isinstance(file_names, list):
        for i in g.files:
            for file_name in file_names:
                # If we have an exact match just return a single element to reduce noise
                # TODO: find a more elegant way to do this and document how it works.
                if i == file_name:
                    full_file_names = [ file_name ]
                    break
                if i.endswith(file_name):
                    full_file_names.append(i)
    else:
        for i in g.files:
            # If we have an exact match just return a single element to reduce noise
            # TODO: find a more elegant way to do this and document how it works.
            if i == file_names:
                full_file_names = [ file_names ]
                break
            if i.endswith(file_names):
                full_file_names.append(i)


    return full_file_names

# Get the set of symbols either used or defined at a certain depth
#
# Return object format:
#
# [{
#     'symbol' : '<name>',
#     'type' : 'dependency/definition',
#     'object' : '<name>',
#     'path' : {
#         '<object_name>' : '<object_parent>',
#         '<object_parent>' : '<object_parent_parent>',
#         ...
#     }
# },
# ...
# ]
#

# python2 wil.py tree --leak libmongocommon.a
def get_symbol_info(g, build_object_names, search_depth=None, symbol_type='dependency'):

    queue = get_full_filenames(g, build_object_names)

    current_level_children = len(queue)
    next_level_children = 0

    parents = None

    for full_build_object_name in queue:
        if isinstance(full_build_object_name, tuple):
            parents = full_build_object_name[0]
            full_build_object_name = full_build_object_name[1]
        else:
            if parents is None:
                parents = [ full_build_object_name ]

        if detect_type(full_build_object_name) == "object":
            if symbol_type == "dependency":
                for symbol_needed in g.get('file_to_symbol_dependencies', full_build_object_name):
                    yield { 'symbol' : symbol_needed,
                            'type' : 'dependency',
                            'object' : full_build_object_name,
                            'parents': parents
                        }
            elif symbol_type == "definition":
                for symbol_defined in g.get('file_to_symbol_definitions', full_build_object_name):
                    yield { 'symbol' : symbol_defined,
                            'type' : 'definition',
                            'object' : full_build_object_name,
                            'parents': parents
                        }
        else:
            for object_file in g.get('archives_to_components', full_build_object_name):
                if symbol_type == "dependency":
                    for symbol_needed in g.get('file_to_symbol_dependencies', object_file):
                        yield { 'symbol' : symbol_needed,
                                'type' : 'dependency',
                                'object' : object_file,
                                'archive' : full_build_object_name,
                                'parents': parents
                              }
                elif symbol_type == "definition":
                    for symbol_defined in g.get('file_to_symbol_definitions', object_file):
                        yield { 'symbol' : symbol_defined,
                                'type' : 'definition',
                                'object' : object_file,
                                'archive' : full_build_object_name,
                                'parents': parents
                              }

        def add_path_info(item):
            if full_build_object_name is not parents[-1]:
                parents.append(full_build_object_name)
            return list(parents), item

        next_level_nodes = map(add_path_info, g.get('target_to_dependencies', full_build_object_name))
        next_level_nodes_count = len(queue)
        queue.extend(next_level_nodes)
        next_level_nodes_count = len(queue) - next_level_nodes_count

        next_level_children += next_level_nodes_count
        current_level_children -= 1

        if current_level_children == 0:
            if search_depth is not None:
                search_depth -= 1

                if search_depth == 0:
                    raise StopIteration

            current_level_children = next_level_children
            next_level_children = 0

# Okay, so this should be the general case.  We should be able to provide a general way to diff two
# sets of symbols.  The theory is that you give it a set of file names, and we provide a way to take
# any pair of the following sets:
#
# - The set of symbols (defined/used) in the archives and libdeps up to a certain depth.  The
#   "direct leak check" would then be a special case of this with depth of one.
# - The set of symbols (defined/used) outside the first set
#def diff_symbol_sets(build_object_names, )

#

# for symbol in symbols:
#     tmp = list(parents)
#     p = [{object_file:  full_build_object_name}]

#     while tmp:
#         if len(tmp) == 1:
#             p.append({tmp.pop(): None})
#         else:
#             p.append({tmp.pop(): tmp.pop()})

#     yield { 'symbol' : symbol_needed,
#             'type' : 'dependency',
#             'object' : object_file,
#            #'path' : p,
#             'parents': parents
#           }

def get_symbol_map(symbol_info):
    o = dict()

    for node in symbol_info:
        symbol = node['symbol']
        del node['symbol']
        o[symbol] = node

    return o
