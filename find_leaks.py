#!/usr/bin/python

import os
import sys
import json

import dep_graph
from helpers.dev_tools import Timer

# Find all symbols defined in this archive and in all archives that this archive lists as
# dependencies in scons
def find_symbol_definitions_recursive(g, archive_name):

    # First, we have to get all components of this archive
    archive_components = g.get_endswith('archives_to_components', archive_name)

    # Iterate this archive looking at all the symbols we define directly
    symbols_defined = set()
    for archive_component in archive_components:
        try:
            for symbol_defined in g.get('file_to_symbol_definitions', archive_component):
                symbols_defined.add(symbol_defined)
        except KeyError:
            pass

    # Now, we have to get all archive dependencies of this archive
    archive_dependencies = g.get_endswith('target_to_dependencies', archive_name)

    # Now, recursively call this function on each archive we depend on, aggregating the results in
    # the symbols found set
    for archive_dependency in archive_dependencies:
        for symbol_defined in find_symbol_definitions_recursive(g, archive_dependency):
            symbols_defined.add(symbol_defined)

    # Return all our symbol definitions for this archive and sub archives
    return list(symbols_defined)

# Find all symbols needed be this archive
def find_symbol_dependencies(g, archive_name):

    # First, we have to get all components of this archive
    archive_components = g.get_endswith('archives_to_components', archive_name)

    # Iterate this archive looking at all the symbols we depend on directly
    symbols_needed = set()
    for archive_component in archive_components:
        try:
            for symbol_needed in g.get('file_to_symbol_dependencies', archive_component):
                symbols_needed.add(symbol_needed)
        except KeyError:
            pass

    # Return all our symbol dependencies for this archive
    return list(symbols_needed)

def find_direct_leaks(g, archive_name):

    # Get all symbols needed by this archive
    symbols_needed = find_symbol_dependencies(g, archive_name)

    # Get all symbols provided by this archive and archives listed as dependencies
    symbols_found = find_symbol_definitions_recursive(g, archive_name)

    # Diff these lists to get the "leaks"
    leaks = set()
    for symbol_needed in symbols_needed:
        if symbol_needed not in symbols_found:
            leaks.add(symbol_needed)

    # Iterate and print all leaks, but _only_ if they are defined somewhere in our project
    for leak in leaks:
        try:
            if (len(g.get('symbol_to_file_sources', leak)) > 0):
                print leak
        except KeyError:
            pass

def main():
    data_file = os.path.join(os.path.dirname(__file__), "dep_graph.json")
    pkl_file = os.path.join(os.path.dirname(__file__), "dep_graph.pickle")

    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " <archive name>")
        exit(1)

    if os.path.exists(pkl_file):
        data_file = pkl_file
        print('[wil]: using pickle rather than json')

    with Timer('loading data file', True):
        g = dep_graph.MultiGraph().load(data_file)

    with Timer('leak detection query operation', True):
        find_direct_leaks(g, sys.argv[1])

if __name__ == '__main__':
    main()
