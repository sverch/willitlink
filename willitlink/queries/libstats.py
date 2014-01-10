#!/usr/bin/python

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.family_tree import symbol_family_tree
from willitlink.queries.tree_leaks import  find_direct_leaks

# names are the files or archives we are checking the leaks of, whereas source_names are files or
# archives that we want to ignore in the output.
#
# For example, if a file "database.o" depeneds on "assert_util.o", we probably don't care about
# seeing that, but we also don't want to add the dependencies of "assert_util.o" to the output
def resolve_leak_info(g, names, depth, timers, source_names):
    with Timer('generating direct leak list', timers):
        direct_leaks = find_direct_leaks(g, names, source_names)

    for leak in direct_leaks:
        del leak['parents']
        del leak['type']
        leak['sources'] = symbol_family_tree(g, leak['symbol'], depth)

    return direct_leaks
