#!/usr/bin/env python

import re
import json
import pymongo
import subprocess
import sys
client = pymongo.MongoClient()

# Strucutre of new format
# {
#    "symbols" : [
#        "mongo::inShutdown()",
#        ...
#    ],
#    "files" : [
#        "src/mongo/db/shutdown.o",
#        ...
#    ],
#    "symbol_sources" : {
#         "mongo::inShutdown()" : [
#             "shutdown.o",
#         ],
#         ...
#    }
#    "symbol_dependents" : {
#         "mongo::inShutdown()" : [
#             "file_that_uses_shutdown.o",
#         ],
#         ...
#    }
#    "symbols_provided" : {
#         "shutdown.o" : [
#             "mongo::inShutdown()",
#         ],
#         ...
#    }
#    "symbols_needed" : {
#         "file_that_uses_shutdown.o" : [
#             "mongo::inShutdown()",
#         ],
#         ...
#    }
#    "file_children" : {
#         "file_that_uses_shutdown.o" : [
#             "shutdown.o",
#         ],
#         ...
#    }
#    "file_parents" : {
#         "shutdown.o" : [
#             "file_that_uses_shutdown.o",
#         ],
#         ...
#    }
# }
def generateEdges():
    edgesObject = {}
    edgesObject["symbols"] = set()
    edgesObject["files"] = set()
    edgesObject["symbol_sources"] = {}
    edgesObject["symbol_dependents"] = {}
    edgesObject["symbols_provided"] = {}
    edgesObject["symbols_needed"] = {}
    edgesObject["file_children"] = {}
    edgesObject["file_parents"] = {}

    # Track how many nodes we've processed so far
    count = 0

    for buildObject in client['test'].deps.find():

        print count
        count = count + 1

        # Add this file
        edgesObject["files"].add(buildObject['_id'])

        # Add the symbol dependency information for this file
        if buildObject['type'] == 'object':

            # Iterate the symbol dependencies of this object, if applicable
            if 'symdeps' in buildObject:
                for symdep in buildObject['symdeps']:

                    # Add this symbol to the set of all symbols
                    edgesObject["symbols"].add(symdep)

                    # Ensure we have an entry for this file
                    if buildObject['_id'] not in edgesObject["symbols_needed"]:
                        edgesObject["symbols_needed"][buildObject['_id']] = set()

                    # Add an edge to indicate that this file needs this symbol
                    edgesObject["symbols_needed"][buildObject['_id']].add(symdep)

                    # Ensure we have an entry for this symbol
                    if symdep not in edgesObject["symbol_dependents"]:
                        edgesObject["symbol_dependents"][symdep] = set()

                    # Add an edge to indicate that this symbol is needed by this file
                    edgesObject["symbol_dependents"][symdep].add(buildObject['_id'])

            if 'symdefs' in buildObject:
                for symdef in buildObject['symdefs']:

                    # Add this symbol to the set of all symbols
                    edgesObject["symbols"].add(symdef)

                    # Ensure we have an entry for this file
                    if buildObject['_id'] not in edgesObject["symbols_provided"]:
                        edgesObject["symbols_provided"][buildObject['_id']] = set()

                    # Add an edge to indicate that this file provides this symbol
                    edgesObject["symbols_provided"][buildObject['_id']].add(symdef)

                    # Ensure we have an entry for this symbol
                    if symdef not in edgesObject["symbol_sources"]:
                        edgesObject["symbol_sources"][symdef] = set()

                    # Add an edge to indicate that this symbol is provided by this file
                    edgesObject["symbol_sources"][symdef].add(buildObject['_id'])

        # Add the file dependency information for this file
        else:

            # Iterate the library dependencies of this build object, if applicable
            if 'deps' in buildObject:
                for libdep in buildObject['deps']:

                    # Add this symbol to the set of all files
                    edgesObject["files"].add(libdep)

                    # Ensure we have an entry for this file
                    if buildObject['_id'] not in edgesObject["file_children"]:
                        edgesObject["file_children"][buildObject['_id']] = set()

                    # Add an edge to indicate that this file provides this symbol
                    edgesObject["file_children"][buildObject['_id']].add(libdep)

                    # Ensure we have an entry for this symbol
                    if libdep not in edgesObject["file_parents"]:
                        edgesObject["file_parents"][libdep] = set()

                    # Add an edge to indicate that this symbol is provided by this file
                    edgesObject["file_parents"][libdep].add(buildObject['_id'])

            # TODO: I believe we want to distinguish between objects and archives, but this treats
            # them all the same.
            # Iterate the object dependencies of this build object, if applicable
            if 'objects' in buildObject:
                for objdep in buildObject['objects']:

                    # Add this symbol to the set of all files
                    edgesObject["files"].add(objdep)

                    # Ensure we have an entry for this file
                    if buildObject['_id'] not in edgesObject["file_children"]:
                        edgesObject["file_children"][buildObject['_id']] = set()

                    # Add an edge to indicate that this file provides this symbol
                    edgesObject["file_children"][buildObject['_id']].add(objdep)

                    # Ensure we have an entry for this symbol
                    if objdep not in edgesObject["file_parents"]:
                        edgesObject["file_parents"][objdep] = set()

                    # Add an edge to indicate that this symbol is provided by this file
                    edgesObject["file_parents"][objdep].add(buildObject['_id'])

    edgesObject["symbols"] = list(edgesObject["symbols"])
    edgesObject["files"] = list(edgesObject["files"])
    for k,v in edgesObject["symbol_sources"].iteritems():
        edgesObject["symbol_sources"][k] = list(v)
    for k,v in edgesObject["symbol_dependents"].iteritems():
        edgesObject["symbol_dependents"][k] = list(v)
    for k,v in edgesObject["symbols_provided"].iteritems():
        edgesObject["symbols_provided"][k] = list(v)
    for k,v in edgesObject["symbols_needed"].iteritems():
        edgesObject["symbols_needed"][k] = list(v)
    for k,v in edgesObject["file_children"].iteritems():
        edgesObject["file_children"][k] = list(v)
    for k,v in edgesObject["file_parents"].iteritems():
        edgesObject["file_parents"][k] = list(v)

    f = open('new_format_deps.json', 'w')
    f.write(json.dumps(edgesObject))

def main():
    generateEdges()

main()
