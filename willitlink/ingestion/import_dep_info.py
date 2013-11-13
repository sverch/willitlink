#!/usr/bin/python

import json
import sys

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from willitlink.base.graph import MultiGraph

def usage ():
    print("Usage: %s <json file>" % sys.argv[0])

def process_dep(line, results):

    buildElement = {}

    try:
        buildElement = json.loads(line)
    except ValueError, e:
        print "Failed to parse line as JSON: " + str(e)
        print line
        sys.exit(-1)

    if isinstance(results, MongoClient):
        try:
            results['test'].deps.insert(buildElement)
        except DuplicateKeyError:
            # If this is an archive, we may have to do special resolution (since our info about archives
            # comes from different places)
            if buildElement['type'] == 'special':
                if 'libdeps' in buildElement:
                    results['test'].deps.update( { "_id" : buildElement["_id"] },
                                                { "$set" : { "deps" : buildElement["libdeps"] } } )
                else:
                    print("Dude, we have an special without libdeps, you screwed up")
                    sys.exit(-1)
            print("Duplicate Key!")
    elif isinstance(results, list):
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

def main():
    if len(sys.argv) != 2:
        usage()
        sys.exit(1)

    ingest_deps(filename=sys.argv[1],
                results=MongoClient())

if __name__ == '__main__':
    main()
