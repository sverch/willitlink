from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.symbol_diff import get_symbol_info

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
