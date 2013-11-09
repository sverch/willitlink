#!/usr/bin/python

import json
import sys
import pymongo
client = pymongo.MongoClient()

def usage ():
    print("Usage: %s <json file>" % sys.argv[0])

def main():
    if len(sys.argv) != 2:
        usage()
        sys.exit(1)

    filename = sys.argv[1]
    f = open(filename)
    for line in f:
        buildElement = json.loads(line)
        print(buildElement)

        try:
            client['test'].deps.insert(buildElement)
        except pymongo.errors.DuplicateKeyError:
            # If this is an archive, we may have to do special resolution (since our info about archives
            # comes from different places)
            if buildElement['type'] == 'special':
                if 'libdeps' in buildElement:
                    client['test'].deps.update({ "_id" : buildElement["_id"] }, { "$set" : { "deps" : buildElement["libdeps"] } })
                else:
                    print("Dude, we have an special without libdeps, you screwed up")
                    sys.exit(-1)
            print("Duplicate Key!")

main()
