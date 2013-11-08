#!/usr/bin/env python

import re
import json
import pymongo
import subprocess
import sys
import dep_graph

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
#    "symbol_sources" : { // symbol2file_sources
#         "mongo::inShutdown()" : [
#             "shutdown.o",
#         ],
#         ...
#    }
#    "symbol_dependents" : {  // symbol2file_dependencies
#         "mongo::inShutdown()" : [
#             "file_that_uses_shutdown.o",
#         ],
#         ...
#    }
#    "symbols_provided" : { // file2symbol_definitions
#         "shutdown.o" : [
#             "mongo::inShutdown()",
#         ],
#         ...
#    }
#    "symbols_needed" : { // files2symbol_dependencies
#         "file_that_uses_shutdown.o" : [
#             "mongo::inShutdown()",
#         ],
#         ...
#    }
#    "children" : { // target2dependencies
#         "libshutdown.a" : [
#             "libstringutils.a",
#         ],
#         "all" : [
#             "alltools",
#         ],
#         ...
#    }
#    "members" : { // archives2components
#         "libshutdown.a" : [
#             "shutdown.o",
#         ],
#         ...
#    }
#    "parents" : { // dependency2targets
#         "shutdown.o" : [
#             "libshutdown.a",
#         ],
#         "libstringutils.a" : [
#             "libshutdown.a"
#         ],
#         ...
#    }
# }

def generateEdges(build_objects):
    edgesObject = {}
    edgesObject["symbols"] = set()
    edgesObject["files"] = set()
    edgesObject["symbol_sources"] = {}
    edgesObject["symbol_dependents"] = {}
    edgesObject["symbols_provided"] = {}
    edgesObject["symbols_needed"] = {}
    edgesObject["children"] = {}
    edgesObject["members"] = {}
    edgesObject["parents"] = {}

    # Track how many nodes we've processed so far
    count = 0

    for buildObject in build_objects:
        count += 1

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
                    if buildObject['_id'] not in edgesObject["children"]:
                        edgesObject["children"][buildObject['_id']] = set()

                    # Add an edge to indicate that this file provides this symbol
                    edgesObject["children"][buildObject['_id']].add(libdep)

                    # Ensure we have an entry for this symbol
                    if libdep not in edgesObject["parents"]:
                        edgesObject["parents"][libdep] = set()

                    # Add an edge to indicate that this symbol is provided by this file
                    edgesObject["parents"][libdep].add(buildObject['_id'])

            # TODO: I believe we want to distinguish between objects and archives, but this treats
            # them all the same.
            # Iterate the object dependencies of this build object, if applicable
            if 'objects' in buildObject:
                for objdep in buildObject['objects']:

                    # Add this symbol to the set of all files
                    edgesObject["files"].add(objdep)

                    # Ensure we have an entry for this file
                    if buildObject['_id'] not in edgesObject["members"]:
                        edgesObject["members"][buildObject['_id']] = set()

                    # Add an edge to indicate that this file provides this symbol
                    edgesObject["members"][buildObject['_id']].add(objdep)

                    # Ensure we have an entry for this symbol
                    if objdep not in edgesObject["parents"]:
                        edgesObject["parents"][objdep] = set()

                    # Add an edge to indicate that this symbol is provided by this file
                    edgesObject["parents"][objdep].add(buildObject['_id'])

        print(count)

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
    for k,v in edgesObject["children"].iteritems():
        edgesObject["children"][k] = list(v)
    for k,v in edgesObject["members"].iteritems():
        edgesObject["members"][k] = list(v)
    for k,v in edgesObject["parents"].iteritems():
        edgesObject["parents"][k] = list(v)

    return edgesObject

def main():
    client = pymongo.MongoClient()

    try: 
        out_fn = sys.argv[0]
    except IndexError: 
        out_fn = 'new_format_deps.json'

    edgesObject = generateEdges(client['test'].deps.find())

    with open(out_fn, 'w') as f: 
        f.write(json.dumps(edgesObject))

if __name__ == '__main__':
    main()
