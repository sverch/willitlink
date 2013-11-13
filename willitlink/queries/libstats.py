#!/usr/bin/python

import os
import sys
import json

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.family_tree import symbol_family_tree
from willitlink.queries.tree_leaks import  find_direct_leaks

def resolve_leak_info(g, name, depth, timers):
    with Timer('generating direct leak list'):
        direct_leaks = find_direct_leaks(g, name)

    return [ {
               'leak': leak,
               'sources': symbol_family_tree(g, leak['symbol'], depth)
             }
             for leak in direct_leaks
           ]
