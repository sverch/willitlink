#!/usr/bin/python

import json
import sys

from willitlink.base.graph import MultiGraph

def process_dep(line, results):
    buildElement = {}

    try:
        buildElement = json.loads(line)
    except ValueError, e:
        print("Failed to parse line as JSON: " + str(e))
        print(line)
        sys.exit(-1)

    for result in results:
        if result['_id'] == buildElement['_id']:
            if 'libdeps' in buildElement:
                result['deps'] = buildElement["libdeps"]
            else:
                print("Dude, we have an special without libdeps, you screwed up")
                sys.exit(-1)

def ingest_deps(filename, results):
    with open(filename, 'r') as f:
        for line in f:
            process_dep(line, results)
