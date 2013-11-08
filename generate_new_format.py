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
#    "symbol_sources" : { // symbol_to_file_sources
#         "mongo::inShutdown()" : [
#             "shutdown.o",
#         ],
#         ...
#    }
#    "symbol_dependents" : {  // symbol_to_file_dependencies
#         "mongo::inShutdown()" : [
#             "file_that_uses_shutdown.o",
#         ],
#         ...
#    }
#    "symbols_provided" : { // file_to_symbol_definitions
#         "shutdown.o" : [
#             "mongo::inShutdown()",
#         ],
#         ...
#    }
#    "symbols_needed" : { // files_to_symbol_dependencies
#         "file_that_uses_shutdown.o" : [
#             "mongo::inShutdown()",
#         ],
#         ...
#    }
#    "children" : { // target_to_dependencies
#         "libshutdown.a" : [
#             "libstringutils.a",
#         ],
#         "all" : [
#             "alltools",
#         ],
#         ...
#    }
#    "members" : { // archives_to_components
#         "libshutdown.a" : [
#             "shutdown.o",
#         ],
#         ...
#    }
#    "parents" : { // dependency_to_targets
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
    relationships = [
                      'symbol_to_file_sources', 'symbol_to_file_sources',
                      'file_to_symbol_definitions', 'file_to_symbol_dependencies',
                      'target_to_dependencies', 'archives_to_components', 'dependency_to_targets'
                    ]

    g = dep_graph.MultiGraph(relationships)
    g.make_lists(['symbols', 'files'])

    # Track how many nodes we've processed so far
    count = 0

    for buildObject in build_objects:
        count += 1

        # Add this file
        g.files.append(buildObject['_id'])

        # Add the symbol dependency information for this file
        if buildObject['type'] == 'object':

            # Iterate the symbol dependencies of this object, if applicable
            if 'symdeps' in buildObject:
                for symdep in buildObject['symdeps']:

                    # Add this symbol to the set of all symbols
                    g.symbols.append(symdep)

                    # Add an edge to indicate that a file depends on these symbols
                    g.add(relationship='files_to_symbol_dependencies',
                          item=buildObject['_id'],
                          deps=symdep)

                    # Add an edge to indicate that this symbol is needed by this file
                    g.add(relationship='symbol_to_file_dependencies',
                          item=symdep,
                          deps=buildObject['_id'])

            if 'symdefs' in buildObject:
                for symdef in buildObject['symdefs']:

                    # Add this symbol to the set of all symbols
                    g.symbols.append(symdef)

                    # Add an edge to indicate that this file provides this symbol
                    g.add(relationship='file_to_symbol_definitions',
                          item=buildObject['_id'],
                          deps=symdef)

                    # Add an edge to indicate that this symbol is provided by this file
                    g.add(relationship='symbol_to_file_sources',
                          item=symdef,
                          deps=buildObject['_id'])

        # Add the file dependency information for this file
        else:
            # Iterate the library dependencies of this build object, if applicable
            if 'deps' in buildObject:
                for libdep in buildObject['deps']:

                    # Add this symbol to the set of all files
                    g.files.append(lidep)

                    # Add an edge to indicate that this file provides this symbol
                    g.add(relationship='target_to_dependencies',
                          item=buildObject['_id'],
                          deps=libdep)

                    # Add an edge to indicate that this symbol is provided by this file
                    g.add(relationship='dependency_to_targets',
                          item=libdep,
                          deps=buildObject['_id'])

            # TODO: I believe we want to distinguish between objects and archives, but this treats
            # them all the same.
            # Iterate the object dependencies of this build object, if applicable
            if 'objects' in buildObject:
                for objdep in buildObject['objects']:

                    # Add this symbol to the set of all files
                    g.files.append(objdep)

                    # Add an edge to indicate that this file provides this symbol
                    g.add(relationship='archives_to_components',
                          item=buildObject['_id'],
                          deps=objdep)

                    # Add an edge to indicate that this symbol is provided by this file
                    g.add(relationship='dependency_to_targets',
                          item=objdep,
                          deps=buildObject['_id'])

        print(count)

    g.dedupe_lists()

    return g

def main():
    client = pymongo.MongoClient()

    try:
        out_fn = sys.argv[0]
    except IndexError:
        out_fn = 'new_format_deps.json'

    graph = generateEdges(client['test'].deps.find())

    graph.export(out_fn)

if __name__ == '__main__':
    main()
