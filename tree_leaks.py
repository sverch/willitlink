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

def locate_symbol_definition(symbol):
    print "LOCATED IN: "
    build_objects = list(client['test'].deps_cleaned.find({ "symdefs" : symbol }))
    for build_object in build_objects:
        build_archive = client['test'].deps_cleaned.find_one({ "objects" : build_object['_id'] })
        if build_archive is not None:
            print "..." + build_object['_id'][-30:] + " [..." + build_archive['_id'][-30:] + "]"
        else:
            print "..." + build_object['_id'][-30:]

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
                        print
                        print "LEAK: "
                        print "..." + buildObject['_id'][-30:] + " -> " + leak
                        locate_symbol_definition(leak)
            if 'symdefs' in buildObject:
                for symdef in buildObject['symdefs']:
                    if symdef == leak:
                        print
                        print "LEAK: "
                        print "..." + buildObject['_id'][-30:] + " -> " + leak
                        locate_symbol_definition(leak)

def main():
    if len(sys.argv) < 2:
        print "Usage: " + sys.argv[0] + " <libraries...>"
        sys.exit(1)

    find_leaks(list(get_all_objects(sys.argv[1:])))

main()
