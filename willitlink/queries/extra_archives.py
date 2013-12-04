from willitlink.base.graph import MultiGraph, ResultsGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.symbol_diff import get_symbol_info

def get_full_filenames(graph, file_name):
    for i in graph.files:
        if i.endswith(file_name):
            yield i

def find_extra_archives(graph, archive_name):
    o = []

    symbols_defined = [ s['symbol']
                        for s in get_symbol_info(graph,
                                                 [ archive_name ],
                                                 search_depth=1,
                                                 symbol_type='definition') ]
    # loop over full names of this file
    for full_archive_name in get_full_filenames(graph, archive_name):
        # Get all symbols needed by this archive
        symbols_needed = get_symbol_info(graph,
                                         [ full_archive_name ],
                                         search_depth=1,
                                         symbol_type='dependency')

        extra_archives = []

        symbols_needed_set =  set([s['symbol'] for s in symbols_needed])

        for archive_dependency in graph.get('target_to_dependencies', full_archive_name):
            need_archive = False
            for symbol_defined in symbols_defined:

                if symbol_defined in symbols_needed_set:
                    need_archive = True

            if need_archive is False:
                extra_archives.append(archive_dependency)

        result = { 'archive': full_archive_name,
                   'extras': extra_archives }

        o.append(result)

    return o

def find_all_extra_archives(graph):
    r = ResultsGraph(relationships=['unneeded_archives'])
    for archive in graph.slice('archives_to_components').keys():
        for i in find_extra_archives(graph, archive):
            extras = i['extras']
            if len(extras) == 0:
                continue
            elif len(extras) == 1:
                r.add(relationship='unneeded_archives',
                      source=archive,
                      target=extras[0],
                      edge=None)
            else:
                for extra in extras:
                    r.add(relationship='unneeded_archives',
                          source=archive,
                          target=extra,
                          edge=None)

    return r
