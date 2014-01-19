from willitlink.base.graph import MultiGraph, ResultsGraph
from willitlink.base.jobs import ThreadPool
from willitlink.base.dev_tools import Timer
from willitlink.queries.symbol_diff import get_symbol_info
from willitlink.queries.fullnames import get_full_filenames

def find_extra_archives(graph, archive_name):
    symbols_defined = { s['symbol']
                        for s in get_symbol_info(graph,
                                                 [ archive_name ],
                                                 search_depth=1,
                                                 symbol_type='definition') }

    # loop over full names of this file
    for full_archive_name in get_full_filenames(graph, archive_name):
        # Get all symbols needed by this archive
        symbols_needed = { s['symbol'] for s in get_symbol_info(graph,
                                         [ full_archive_name ],
                                         search_depth=1,
                                         symbol_type='dependency') }

        extra_archives = list()
        for archive_dependency in graph.get('target_to_dependencies', full_archive_name):
            if not symbols_defined.issubset(symbols_needed):
                extra_archives.append(archive_dependency)

        yield { 'archive': full_archive_name,
                'extras': extra_archives }

def find_all_extra_archives(graph):
    r = ResultsGraph(relationships=['unneeded_archives'])

    def add_results(archive):
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

    archives = graph.slice('archives_to_components').keys()
    map(add_results, archives)

    return r
