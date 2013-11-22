from willitlink.base.graph import MultiGraph

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

    if not isinstance(file_names, basestring):
        for i in g.files:
            for file_name in file_names:
                if i.endswith(file_name):
                    full_file_names.append(i)
    else:
        for i in g.files:
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


def get_symbol_info(g, build_object_names, search_depth=None, symbol_type='dependency'):
    l = get_full_filenames(g, build_object_names)

    current_level_children = len(l)
    next_level_children = 0

    paths = dict()

    for full_build_object_name in l:
        if isinstance(full_build_object_name, tuple):
            print full_build_object_name
            parent = full_build_object_name[0]
            full_build_object_name = full_build_object_name[1]
        else:
            parent = None

        if detect_type(full_build_object_name) == "object":
            if symbol_type == "dependency":
                for symbol_needed in g.get('file_to_symbol_dependencies', full_build_object_name):
                    yield { 'symbol' : symbol_needed,
                                                    'type' : 'dependency',
                                                    'object' : full_build_object_name,
                                                    'path' : {} }
            elif symbol_type == "definition":
                for symbol_defined in g.get('file_to_symbol_definitions', full_build_object_name):
                    yield { 'symbol' : symbol_defined,
                                                    'type' : 'definition',
                                                    'object' : full_build_object_name,
                                                    'path' : {} }

        else:
            for object_file in g.get('archives_to_components', full_build_object_name):
                if symbol_type == "dependency":
                    for symbol_needed in g.get('file_to_symbol_dependencies', object_file):
                        r = { 'symbol' : symbol_needed,
                                'type' : 'dependency',
                                'object' : object_file,
                                'path' : {
                                    object_file : full_build_object_name,
                              } }

                        if parent is not None:
                            r[full_build_object_name] = parent

                        yield r
                elif symbol_type == "definition":
                    for symbol_defined in g.get('file_to_symbol_definitions', object_file):
                        r = { 'symbol' : symbol_defined,
                                'type' : 'definition',
                                'object' : object_file,
                                'path' : {
                                    object_file : full_build_object_name,
                            } }

                        if parent is not None:
                            r[full_build_object_name] = parent

                        yield r

            def add_path_info(item):
                return full_build_object_name, item

            next_level_nodes = map(add_path_info, g.get('target_to_dependencies', full_build_object_name))
            l.extend(next_level_nodes)

            next_level_children += len(next_level_nodes)
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
