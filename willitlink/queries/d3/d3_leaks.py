#!/usr/bin/python

import os
import sys
import json

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.tree_leaks import find_direct_leaks

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

        try:
            # First, we have to get all object files directly built into this archive or executable
            archive_components = g.get('archives_to_components', archive_or_executable)

            # Get any symbols that are leaking from this archive
            leaks = find_direct_leaks(g, archive_or_executable)

            # Iterate all the symbols leaking from this archive
            for leak_object in leaks:
                leak_object['symbol']
                leak_object['file']

                # Get the files this symbol is defined
                for symbol_source in g.get('symbol_to_file_sources', leak_object['symbol']):

                    # Get the archives this file is in
                    for archive_source in g.get('dependency_to_targets', symbol_source):

                        # Finally, for each archive, add an edge
                        d3_graph_object['edges'].append({ 'to' : archive_source,
                                                          'from' : archive_or_executable,
                                                          'type' : 'symdep',
                                                          'symbol' : leak_object['symbol'] })
        except KeyError:
            pass

    return d3_graph_object
