#!/usr/bin/python

import json
import sys

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from dep_graph import MultiGraph

def usage ():
    print("Usage: %s <json file>" % sys.argv[0])

def process_dep(line, results):
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
        if buildElement in results:
            if 'libdeps' in buildElement:
                idx = results.index(buildElement)
                buildElement['deps'] = buildElement["libdeps"]
                results[idx] = buildElement
            else:
                print("Dude, we have an special without libdeps, you screwed up")
                sys.exit(-1)
        else:
            results.append(results)

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
