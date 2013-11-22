from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.symbol_diff import get_symbol_info

def get_full_filenames(graph, file_name):

    full_file_names = []

    for i in graph.files:
        if i.endswith(file_name):
            full_file_names.append(i)

    return full_file_names

def find_extra_archives(graph, archive_name):
    o = []

    # loop over full names of this file
    for full_archive_name in get_full_filenames(graph, archive_name):
        # Get all symbols needed by this archive
        symbols_needed = set([ s['symbol']
                               for s in get_symbol_info(graph,
                                                        [ full_archive_name ],
                                                        search_depth=1,
                                                        symbol_type='dependency') ])

        extra_archives = []

        for archive_dependency in graph.get('target_to_dependencies', full_archive_name):
            need_archive = False
            symbols_defined = [ s['symbol']
                                for s in get_symbol_info(graph,
                                                         [ archive_name ],
                                                         search_depth=1,
                                                         symbol_type='definition') ]
            for symbol_defined in symbols_defined:
                if symbol_defined in symbols_needed:
                    print symbol_defined
                    print archive_dependency
                    need_archive = True
            if need_archive == False:
                extra_archives.append(archive_dependency)

        result = { 'archive': full_archive_name,
                   'extras': extra_archives }

        o.append(result)

    return o
