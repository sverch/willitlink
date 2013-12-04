from willitlink.base.graph import MultiGraph, ResultsGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.symbol_diff import get_symbol_info, get_symbol_map

def get_full_filenames(g, file_names):

    full_file_names = []

    if isinstance(file_names, list):
        for i in g.files:
            for file_name in file_names:
                if i.endswith(file_name):
                    full_file_names.append(i)
    else:
        for i in g.files:
            if i.endswith(file_names):
                full_file_names.append(i)


    return full_file_names

def find_direct_leaks(graph, archive_names):
    # Get all symbols needed by this archive
    symbols_needed = get_symbol_info(graph,
                                     archive_names,
                                     search_depth=None,
                                     symbol_type='dependency')

    # Get all symbols provided by this archive and archives listed as dependencies
    # this "set-comprehension "makes us python2.7+

    symbols_found = { s['symbol']
                      for s in get_symbol_info(graph,
                                               archive_names,
                                               search_depth=None,
                                               symbol_type='definition') }


    leaks = ( symbol_needed
              for symbol_needed
              in symbols_needed
              if symbol_needed ['symbol'] not in symbols_found
            )

    return [ leak
             for leak
             in leaks
             if len(graph.get('symbol_to_file_sources', leak['symbol'])) > 0
           ]

# Get paths from the given list of archive sources to the given target.  Returns a list of objects
# that have the source and the paths to the target.
#
# Example:
# [{
#    "source" : "liba.a",
#    "target" : "libd.a",
#    "paths" : [
#       [
#       "liba.a",
#       "libc.a",
#       "libd.a"
#       ],
#       [
#       "liba.a",
#       "libb.a",
#       "libd.a"
#       ]
#    ]
# }]
def get_paths(g, archive_target, archive_sources):

    queue = get_full_filenames(g, archive_sources)
    traversed = []
    traversed.extend(queue)

    full_archive_targets = get_full_filenames(g, archive_target)

    if len(full_archive_targets) != 1:
        print "Error: did not get exactly one valid archive target"
        print archive_target
        print full_archive_targets
        raise StopIteration

    full_archive_target = full_archive_targets[0]

    current_level_children = len(queue)
    next_level_children = 0

    parents = None

    for parent_archive in queue:
        if isinstance(parent_archive, tuple):
            parents = parent_archive[0]
            parent_archive = parent_archive[1]
        else:
            if parents is None:
                parents = [ parent_archive ]

        # Check to see if we've reached the end of our path.  If so, return an object and continue
        # iteration
        if parent_archive == full_archive_target:
            yield { 'target' : full_archive_target,
                    'source' : parent_archive,
                    'parents': parents }

        def add_path_info(item):
            if parent_archive is not parents[-1]:
                parents.append(parent_archive)
            return list(parents), item

        next_level_libs_needed = find_libraries_needed(g, parent_archive)
        next_level_libs_needed = [ lib for lib in next_level_libs_needed if lib not in traversed ]
        traversed.extend(next_level_libs_needed)
        next_level_nodes = map(add_path_info, next_level_libs_needed)
        next_level_nodes_count = len(queue)
        queue.extend(next_level_nodes)
        next_level_nodes_count = len(queue) - next_level_nodes_count

        next_level_children += next_level_nodes_count
        current_level_children -= 1

        if current_level_children == 0:

            current_level_children = next_level_children
            next_level_children = 0

def find_libraries_needed(graph, archive_names):
    # Get all symbols needed by this archive
    symbols_needed = get_symbol_info(graph,
                                     archive_names,
                                     search_depth=1,
                                     symbol_type='dependency')

    # GOAL: Get list of archives needed
    # STEP1: Get object files for each symbol

    # Basic object files needed
    objects_needed = []

    # Object files that we need that has some problem (in this case multiple definitions)
    bad_objects_needed = []

    for symbol_needed in symbols_needed:
        symbol_locations = graph.get('symbol_to_file_sources', symbol_needed['symbol'])

        symbol_locations = [ symbol_location for symbol_location in symbol_locations if symbol_location.find("client_build") == -1 ]

        # If this symbol was defined in more than one place, add the objects as a dict with a
        # description
        if len(symbol_locations) > 1:
            for i in symbol_locations:
                bad_objects_needed.append({ "objects" : symbol_locations, "multiple_definitions" : True })
        elif len(symbol_locations) != 0:
            objects_needed.append(symbol_locations[0])

    # STEP2: Get archives containing each object file
    archives_needed = []
    for object_needed in objects_needed:
        archives_needed.extend(graph.get('dependency_to_targets', object_needed))

    return list(set(archives_needed))

def find_libraries_needed_full(graph, archive_names):
    # Get all symbols needed by this archive
    symbols_needed = get_symbol_info(graph,
                                     archive_names,
                                     search_depth=1,
                                     symbol_type='dependency')

    # GOAL: Get list of archives needed
    # STEP1: Get object files for each symbol

    # Basic object files needed
    objects_needed = []

    # Object files that we need that has some problem (in this case multiple definitions)
    bad_objects_needed = []

    for symbol_needed in symbols_needed:
        symbol_locations = graph.get('symbol_to_file_sources', symbol_needed['symbol'])

        symbol_locations = [ symbol_location for symbol_location in symbol_locations if symbol_location.find("client_build") == -1 ]

        # If this symbol was defined in more than one place, add the objects as a dict with a
        # description
        if len(symbol_locations) > 1:
            bad_objects_needed.append({ "objects" : symbol_locations, "multiple_definitions" : True })
        elif len(symbol_locations) != 0:
            objects_needed.append(symbol_locations[0])

    # STEP2: Get archives containing each object file
    archives_needed = []
    for object_needed in objects_needed:
        archives_needed.extend(graph.get('dependency_to_targets', object_needed))

    results = []
    for archive_name in get_full_filenames(graph, archive_names):
        results.extend(get_paths(graph, archive_name, list(set(archives_needed))))

    return results

def find_libraries_needed_multi(graph, archive_names):
    # Get all symbols needed by this archive
    symbols_needed = get_symbol_info(graph,
                                     archive_names,
                                     search_depth=1,
                                     symbol_type='dependency')

    # GOAL: Get list of archives needed
    # STEP1: Get object files for each symbol

    # Basic object files needed
    objects_needed = []

    # Object files that we need that has some problem (in this case multiple definitions)
    bad_objects_needed = []

    for symbol_needed in symbols_needed:
        symbol_locations = graph.get('symbol_to_file_sources', symbol_needed['symbol'])

        symbol_locations = [ symbol_location for symbol_location in symbol_locations if symbol_location.find("client_build") == -1 ]

        # If this symbol was defined in more than one place, add the objects as a dict with a
        # description
        if len(symbol_locations) > 1:
            bad_objects_needed.append(symbol_locations)
        elif len(symbol_locations) != 0:
            objects_needed.append(symbol_locations[0])

    # STEP2: Get archives containing each object file
    archives_needed = []
    for object_needed in objects_needed:
        archives_needed.extend(graph.get('dependency_to_targets', object_needed))

    bad_archives_needed = []
    for bad_objects_needed_list in bad_objects_needed:
        bad_archives_needed_single = []
        for bad_object_needed in bad_objects_needed_list:
            bad_archives_needed_single.extend(graph.get('dependency_to_targets', bad_object_needed))
        bad_archives_needed.append(bad_archives_needed_single)

    return { 'good' : list(set(archives_needed)), 'bad' : bad_archives_needed }
