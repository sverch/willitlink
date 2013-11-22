#!/usr/bin/python

import os
import sys
import json

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.tree_leaks import find_direct_leaks
from willitlink.queries.d3.d3_utils import dedupe_edges_d3

# Pseudocode:
# for each archive or executable:
#    for each component in archive:
#         for each symbol dep in component:
#               if not leaky:
#                       for each symbol source in symbol dep
#                              for each source archive in symbol_source
#                                      link source archive to dest archive

def add_leaks_d3(g, d3_graph_object):

    # For each node in our graph, we want to get symbol dependency information
    for archive_or_executable in d3_graph_object['nodes']:

        # Get any symbols that are leaking from this archive
        # Iterate all the symbols leaking from this archive
        for leak_object in find_direct_leaks(g, archive_or_executable):

            # Get the files this symbol is defined
            for symbol_source in g.get('symbol_to_file_sources', leak_object['symbol']):

                # Get the archives this file is in
                for archive_source in g.get('dependency_to_targets', symbol_source):

                    # Finally, for each archive, add an edge
                    d3_graph_object['edges'].append({ 'to' : archive_source,
                                                      'from' : archive_or_executable,
                                                      'type' : 'symbol',
                                                      'symbol' : leak_object['symbol'] })

    return dedupe_edges_d3(d3_graph_object)
