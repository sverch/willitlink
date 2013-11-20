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

            # Iterate over all the object files in this archive
            for archive_component in archive_components:

                # Iterate over all the symbols needed by the object files in this archive
                for symbol_needed in g.get('file_to_symbol_dependencies', archive_component):

                    # Only add an edge for this if we are leaking this symbol
                    if symbol_needed not in leaks:

                        # Get the files this symbol is defined
                        for symbol_source in g.get('symbol_to_file_sources', symbol_needed):

                            # Get the archives this file is in
                            for archive_source in g.get('dependency_to_targets', symbol_source):

                                # Finally, for each archive, add an edge
                                d3_graph_object['edges'].append({ 'to' : archive_source,
                                                                  'from' : archive_or_executable,
                                                                  'type' : 'symdep',
                                                                  'symbol' : symbol_needed })
        except KeyError:
            pass

    return d3_graph_object
