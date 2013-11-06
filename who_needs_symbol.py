#!/usr/bin/env python

import re
import json
import pymongo
import subprocess
import sys
client = pymongo.MongoClient()

def locate_symbol_dependency(symbol):
    build_objects = list(client['test'].deps_cleaned.find({ "symdeps" : symbol }))
    for build_object in build_objects:
        build_archive = client['test'].deps_cleaned.find_one({ "objects" : build_object['_id'] })
        if build_archive is not None:
            print "Object: " + build_object['_id']
            print "Archive: " + build_archive['_id']
            print
        else:
            print "Object: " + build_object['_id']
            print

def main():
    if len(sys.argv) != 2:
        print "Usage: " + sys.argv[0] + " <symbol>"
        sys.exit(1)

    symbol = sys.argv[1]
    locate_symbol_dependency(symbol)

main()
