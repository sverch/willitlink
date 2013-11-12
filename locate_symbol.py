#!/usr/bin/python

import os
import sys
import json

import dep_graph

def locate_symbol(g, symbol_name):

    for containing_file in g.get('symbol_to_file_sources', symbol_name):
        for containing_archive in g.get('dependency_to_targets', containing_file):
            print "..." + containing_file[-30:] + " [..." + containing_archive[-30:] + "]"
            for next_containing_archive in g.get('dependency_to_targets', containing_archive):
                print "[..." + next_containing_archive[-30:] + "]"

def main():
    data_file = os.path.join(os.path.dirname(__file__), "dep_graph.json")
    pkl_file = os.path.join(os.path.dirname(__file__), "dep_graph.pkl")

    g = dep_graph.MultiGraph()

    if len(sys.argv) != 2:
        print "Usage: " + sys.argv[0] + " <symbol name>"
        exit(1)

    if os.path.exists(pkl_file):
        print "pickle!"
        g.load_pickle(pkl_file)
        print "pickle done!"
    else:
        print "json!"
        g.load(data_file)
        print "json done!"

    g.export_pickle(pkl_file)

    g = dep_graph.MultiGraph().load(data_file)

    locate_symbol(g, sys.argv[1])

if __name__ == '__main__':
    main()
