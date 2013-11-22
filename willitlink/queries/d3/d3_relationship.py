#!/usr/bin/python

import os
import sys
import json

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.symbol_diff import get_symbol_info
from willitlink.queries.d3.d3_utils import dedupe_edges_d3

def get_full_filenames(g, file_names):

    full_file_names = []

    for i in g.files:
        for file_name in file_names:
            # If we have an exact match just return a single element to reduce noise
            # TODO: find a more elegant way to do this and document how it works.
            if i == file_name:
                full_file_names = [ file_name ]
                break
            if i.endswith(file_name):
                full_file_names.append(i)

    return full_file_names

def relationship_info_d3(g, file_names):

    full_file_names = get_full_filenames(g, file_names)

    d3_graph_object = { 'nodes': set(full_file_names),
                        'edges': [] }

    # For each node in our graph, we want to get symbol dependency information
    for archive_or_executable in d3_graph_object['nodes']:

        # First, we have to get all symbols directly needed by this archive or executable
        # Iterate all the symbols needed by this archive
        for dependency in get_symbol_info(g, [ archive_or_executable ], search_depth=1, symbol_type='dependency'):

            # Get the files this symbol is defined
            for symbol_source in g.get('symbol_to_file_sources', dependency['symbol']):

                # Get the archives this file is in
                for archive_source in g.get('dependency_to_targets', symbol_source):

                    # Finally, for each archive, add an edge, but only if it's in our list of
                    # file names and it's not ourself
                    if archive_source in full_file_names and archive_source != archive_or_executable:
                        d3_graph_object['edges'].append({ 'to' : archive_source,
                                                          'from' : archive_or_executable,
                                                          'type' : 'symbol',
                                                          'symbol' : dependency['symbol'] })

    d3_graph_object['nodes'] = list(d3_graph_object['nodes'])

    return dedupe_edges_d3(d3_graph_object)
