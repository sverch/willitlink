#!/usr/bin/python

import os
import sys
import json

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.symbol_diff import get_symbol_info

def get_full_filenames(g, file_names):

    full_file_names = []

    if not isinstance(file_names, basestring):
        for i in g.files:
            for file_name in file_names:
                if i.endswith(file_name):
                    full_file_names.append(i)
    else:
        for i in g.files:
            if i.endswith(file_names):
                full_file_names.append(i)


    return full_file_names

# Find all symbols defined in this archive and in all archives that this archive lists as
# dependencies in scons
def find_symbol_definitions_recursive(g, full_archive_name):

    # First, we have to get all components of this archive
    archive_components = g.get('archives_to_components', full_archive_name)

    # Iterate this archive looking at all the symbols we define directly
    symbols_defined = set()
    for archive_component in archive_components:
        try:
            for symbol_defined in g.get('file_to_symbol_definitions', archive_component):
                symbols_defined.add(symbol_defined)
        except KeyError:
            pass

    # Now, we have to get all archive dependencies of this archive
    archive_dependencies = []
    try:
        archive_dependencies = g.get('target_to_dependencies', full_archive_name)
    except KeyError:
        pass

    # Now, recursively call this function on each archive we depend on, aggregating the results in
    # the symbols found set
    for archive_dependency in archive_dependencies:
        for symbol_defined in find_symbol_definitions_recursive(g, archive_dependency):
            symbols_defined.add(symbol_defined)

    # Return all our symbol definitions for this archive and sub archives
    return list(symbols_defined)

# Find all symbols needed be this archive, and include the file name
def find_symbol_dependencies_with_file(g, full_archive_name):

    # First, we have to get all components of this archive
    archive_components = g.get('archives_to_components', full_archive_name)

    # Iterate this archive looking at all the symbols we depend on directly
    symbols_needed = set()
    for archive_component in archive_components:
        try:
            for symbol_needed in g.get('file_to_symbol_dependencies', archive_component):
                symbols_needed.add((symbol_needed, archive_component))
        except KeyError:
            pass

    # Return all our symbol dependencies for this archive
    return list(symbols_needed)

def find_symbol_dependencies(g, full_archive_name):
    return [ symbol_needed for (symbol_needed, file_needing) in find_symbol_dependencies_with_file(g, full_archive_name) ]

def find_direct_leaks(g, archive_name):

    # Get the full names of this file
    full_archive_names = get_full_filenames(g, archive_name)

    for full_archive_name in full_archive_names:
        # Get all symbols needed by this archive
        symbols_needed = get_symbol_info(g, [ full_archive_name ], search_depth=1, symbol_type='dependency')

        # Get all symbols provided by this archive and archives listed as dependencies
        symbols_found = get_symbol_info(g, [ full_archive_name ], search_depth=None, symbol_type='definition')

        # Diff these lists to get the "leaks"
        leaks = []
        symbols_found_set = set()
        for symbol_found in symbols_found:
            symbols_found_set.add(symbol_found['symbol'])

        for symbol_needed in symbols_needed:

            if symbol_needed['symbol'] not in symbols_found_set:
                leaks.append(symbol_needed)

        o = []
        for leak_object in leaks:
            try:
                if (len(g.get('symbol_to_file_sources', leak_object['symbol'])) > 0):
                    o.append(leak_object)
            except KeyError:
                pass

    return o
