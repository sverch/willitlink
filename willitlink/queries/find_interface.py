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

def find_interface(graph, archive_names):
    # Get all symbols defined by this archive
    symbols_defined = list(get_symbol_info(graph,
                                           archive_names,
                                           search_depth=1,
                                           symbol_type='definition'))


    files_in_archive = set()
    for symbol_defined in symbols_defined:
        files_in_archive.add(symbol_defined['object'])

    interface = []

    for symbol_defined in symbols_defined:

        # Removing these right now because they are not useful (or incorrect)
        del symbol_defined['parents']
        del symbol_defined['type']

        files_requiring_symbol = []
        for file_requiring_symbol in graph.get('symbol_to_file_dependencies', symbol_defined['symbol']):
            if file_requiring_symbol in files_in_archive or "_test.o" in file_requiring_symbol:
                continue
            else:
                files_requiring_symbol.append(file_requiring_symbol)

        if len(files_requiring_symbol) > 0:
            symbol_defined['used_by'] = files_requiring_symbol
            interface.append(symbol_defined)

    return interface
