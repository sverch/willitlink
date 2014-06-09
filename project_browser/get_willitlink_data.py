from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer

from willitlink.queries.find_interface import find_interface
from willitlink.queries.tree_leaks import resolve_leak_info
from willitlink.queries.executables import get_executable_list

import sys
import json
import os
import re

from collections import OrderedDict

def dbgprint(my_object):
    print json.dumps(my_object, indent=4)

# The following four *_file_to_*_file(s) functions convert to/from *.o and *.cpp files.
# TODO:  If we use the "client_build" and the server build, this function will return more than one
# value for what the object file is.  However, the data in this repo is currently generated from
# both.  We should have only the server objects or only the client objects, since they are
# essentially two completely independent builds.
def source_file_to_object_file(graph, source_file):
    # TODO: Make this an assertion or something more obvious
    object_files = graph.get('source_to_file', source_file)
    if (len(object_files)) > 1:
        print object_files
    return object_files

def source_files_to_object_files(graph, source_files):
    object_files = []
    for source_file in source_files:
        object_files.extend(source_file_to_object_file(graph, source_file))
    return object_files

def object_file_to_source_file(graph, object_file):
    source_files = graph.get('file_to_source', object_file)
    if (len(source_files)) > 1:
        print source_files
    return source_files

def object_files_to_source_files(graph, object_files):
    source_files = []
    for object_file in object_files:
        source_files.extend(object_file_to_source_file(graph, object_file))
    return source_files

# Args:
# graph - willitlink graph object
# source_file - name of source file to query for
#
# Returns:
# List of executable names
def get_file_executables(graph, source_file):
    # XXX: I don't know why I have to convert everything back to strings.  It gets output as a
    # python unicode type in the result map if I don't do this.
    return [ str(executable) for executable in get_executable_list(graph, source_file) ]

# Args:
# graph - willitlink graph object
# source_file - name of source file to query for
#
# Returns:
# List of header names
def get_file_headers(graph, source_file):
    # XXX: When I figure out how to nicely handle the whole "duplicate object files per source file"
    # thing, this should not return a list
    object_files = source_file_to_object_file(graph, source_file)
    if (len(object_files) < 1):
        return []
    return [ str(header_include) for header_include in graph.get('file_to_header_includes', object_files[0]) ]

# Args:
# graph - willitlink graph object
# source_file - name of source file to query for
#
# Returns:
# List of symbols in the interface and where they are used in an object of the format:
# {
#     "symbol_name" : <name>,
#     "symbol_uses" : [ <files symbol is used in> ]
# }
def get_file_interface(graph, source_file):
    file_interface = find_interface(graph, source_file_to_object_file(graph, source_file))
    file_interface_result = []
    for file_interface_object in file_interface:
        file_interface_result_object = OrderedDict()
        file_interface_result_object['symbol_name'] = str(file_interface_object['symbol'])
        file_interface_result_object['symbol_uses'] = [ str(use_file) for use_file in object_files_to_source_files(graph, file_interface_object['used_by']) ]
        file_interface_result.append(file_interface_result_object)
    return file_interface_result

# Args:
# graph - willitlink graph object
# source_file - name of source file to query for
#
# Returns:
# List of symbols in the interface and where they are used in an object of the format:
# {
#     "symbol_name" : <name>,
#     "symbol_sources" : [ <files symbol is defined in> ]
# }
def get_file_dependencies(graph, source_file):
    file_dependencies = resolve_leak_info(graph, source_file_to_object_file(graph, source_file), 1, None, [])
    file_dependencies_result = []
    for file_dependencies_object in file_dependencies:
        file_dependencies_result_object = OrderedDict()
        file_dependencies_result_object['symbol_name'] = str(file_dependencies_object['symbol'])
        file_dependencies_result_object['symbol_sources'] = [ str(source_file) for source_file in list(set(object_files_to_source_files(graph, file_dependencies_object['sources'].keys()))) ]
        file_dependencies_result.append(file_dependencies_result_object)
    return file_dependencies_result



# Args:
# graph - willitlink graph object
#
# Returns:
# Object that contains build and version information.  Currently this is stored in the willitoink
# graph as "extra info".  This should eventually be in part of a "project data" datastructure, that
# contains both metadata about the project, as well as the graph with all the dependency
# information.
def get_version_and_build_info(graph):
    # Get version and build info from willitlink
    return graph.get_extra_info()
