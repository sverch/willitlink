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

def get_symbol_info(g, build_object_names, search_depth=None, symbol_type='dependency', parent=None):

    if search_depth is not None and search_depth == 0:
        return []

    # Get the full names of this file
    full_build_object_names = get_full_filenames(g, build_object_names)

    symbol_info_objects = []

    for full_build_object_name in full_build_object_names:

        if detect_type(full_build_object_name) == "object":
            if symbol_type == "dependency":
                for symbol_needed in g.get('file_to_symbol_dependencies', full_build_object_name):
                    symbol_info_objects.append({ 'symbol' : symbol_needed,
                                                    'type' : 'dependency',
                                                    'object' : full_build_object_name,
                                                    'path' : {} })
            elif symbol_type == "definition":
                for symbol_defined in g.get('file_to_symbol_definitions', full_build_object_name):
                    symbol_info_objects.append({ 'symbol' : symbol_defined,
                                                    'type' : 'definition',
                                                    'object' : full_build_object_name,
                                                    'path' : {} })
            else:
                print "Unrecognized symbol_type: " + symbol_type + " expected 'dependency' or 'definition'"
                return []

        else:

            object_files = g.get('archives_to_components', full_build_object_name)

            for object_file in object_files:
                if symbol_type == "dependency":
                    for symbol_needed in g.get('file_to_symbol_dependencies', object_file):
                        symbol_info_objects.append({ 'symbol' : symbol_needed,
                                                        'type' : 'dependency',
                                                        'object' : object_file,
                                                        'path' : {
                                                            object_file : full_build_object_name
                                                        } })
                elif symbol_type == "definition":
                    for symbol_defined in g.get('file_to_symbol_definitions', object_file):
                        symbol_info_objects.append({ 'symbol' : symbol_defined,
                                                        'type' : 'definition',
                                                        'object' : object_file,
                                                        'path' : {
                                                            object_file : full_build_object_name
                                                        } })
                else:
                    print "Unrecognized symbol_type: " + symbol_type + " expected 'dependency' or 'definition'"
                    return []

            # Now, we have to get all archive dependencies of this archive
            archive_dependencies = g.get('target_to_dependencies', full_build_object_name)

            # Recursively search all libdeps
            new_search_depth = None
            if search_depth is not None:
                new_search_depth = search_depth - 1

            if len(archive_dependencies) > 0:
                dependency_symbol_info_objects = get_symbol_info(g, archive_dependencies,
                                                                search_depth=new_search_depth,
                                                                symbol_type=symbol_type,
                                                                parent=full_build_object_name)

                symbol_info_objects.extend(dependency_symbol_info_objects)

            # If we have a parent, append info for that now
            if parent is not None:
                for symbol_info_object in symbol_info_objects:
                    symbol_info_object['path'][full_build_object_name] = parent

    return symbol_info_objects

# Okay, so this should be the general case.  We should be able to provide a general way to diff two
# sets of symbols.  The theory is that you give it a set of file names, and we provide a way to take
# any pair of the following sets:
#
# - The set of symbols (defined/used) in the archives and libdeps up to a certain depth.  The
#   "direct leak check" would then be a special case of this with depth of one.
# - The set of symbols (defined/used) outside the first set
#def diff_symbol_sets(build_object_names, )
