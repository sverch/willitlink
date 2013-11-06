#!/usr/bin/env python

import re
import json
import pymongo
import subprocess
import sys
client = pymongo.MongoClient()

def get_all_objects(archive_names):
    objects = []

    for archive_name in archive_names:

        # Get the archive object for this archive name
        buildObjects = list(client['test'].deps_cleaned.find({ "_id" : { "$regex" : archive_name } }))

        for buildObject in buildObjects:

            if buildObject['type'] == 'archive':

                # Find all objects for this archive object
                if 'objects' in buildObject:
                    objects += list(client['test'].deps_cleaned.find({ "_id" : { "$in" : buildObject['objects'] } }))

                # Now iterate this archive's dependencies recursively and add the results to the objects array
                if 'deps' in buildObject:
                    objects += get_all_objects(buildObject['deps'])

            elif buildObject['type'] == 'object':
                objects += [ buildObject ]
            else:
                print "Unsupported type found: " + buildObject['type']

    return objects

def find_leaks(objects):
    symdeps = []
    symdefs = []
    leaks = []
    for buildObject in objects:
        if 'symdeps' in buildObject:
            symdeps += buildObject['symdeps']
        if 'symdefs' in buildObject:
            symdefs += buildObject['symdefs']
    symdeps = list(set(symdeps))
    symdefs = list(set(symdefs))
    for symdep in symdeps:
        if symdep not in symdefs:
            leaks += [ symdep ]
    for leak in leaks:
        for buildObject in objects:
            if 'symdeps' in buildObject:
                for symdep in buildObject['symdeps']:
                    if symdep == leak:
                        print "Object: " + buildObject['_id']
                        print "Leak: " + leak
                        print
            if 'symdefs' in buildObject:
                for symdef in buildObject['symdefs']:
                    if symdef == leak:
                        print "Object: " + buildObject['_id']
                        print "Leak: " + leak
                        print

def main():
    if len(sys.argv) < 2:
        print "Usage: " + sys.argv[0] + " <libraries...>"
        sys.exit(1)

    find_leaks(list(get_all_objects(sys.argv[1:])))

main()
