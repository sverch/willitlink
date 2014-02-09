from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer

from willitlink.queries.find_interface import find_interface
from willitlink.queries.libstats import resolve_leak_info
from willitlink.queries.executables import get_executable_list

import sys
import json
import os
import re

def dbgprint(my_object):
    print json.dumps(my_object, indent=4)

# The modules have files listed in "groups".  This returns a list of all files for the module.
def get_module_files(single_module_data):
    module_files = []
    for module_group in single_module_data['groups']:
        module_files.extend(module_group['files'])
    return module_files

# The modules have files listed in "groups".  This adds a 'files_flat' entry to each module that has
# a list of all files for the module.
def add_files_list(project_data):
    for system_name in project_data.keys():
        for module_object in project_data[system_name]['modules']:
            module_object['files_flat'] = get_module_files(module_object)

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

def add_interface_data(graph, project_data):
    for system_name in project_data.keys():
        for module_object in project_data[system_name]['modules']:
            module_object['interface'] = find_interface(graph, source_files_to_object_files(graph, module_object['files_flat']))
            for interface_object in module_object['interface']:
                interface_object['object'] = object_files_to_source_files(graph, [interface_object['object']])[0]
                interface_object['used_by'] = object_files_to_source_files(graph, interface_object['used_by'])

def add_leak_data(graph, project_data):
    for system_name in project_data.keys():
        for module_object in project_data[system_name]['modules']:
            module_object['leaks'] = resolve_leak_info(graph, source_files_to_object_files(graph, module_object['files_flat']), 1, None, [])
            for leak_object in module_object['leaks']:
                leak_object['object'] = object_files_to_source_files(graph, [leak_object['object']])[0]
                leak_object['sources'] = list(set(object_files_to_source_files(graph, leak_object['sources'].keys())))

def add_executable_data(graph, project_data):
    for system_name in project_data.keys():
        for module_object in project_data[system_name]['modules']:
            module_object['files_with_exec'] = []
            for source_file in module_object['files_flat']:
                executable_list = []
                executable_list = get_executable_list(graph, source_file)
                module_object['files_with_exec'].append({ "name" : source_file, "execs" : executable_list })

def add_willitlink_data(graph, project_data):
    add_files_list(project_data)
    add_interface_data(graph, project_data)
    add_leak_data(graph, project_data)
    add_executable_data(graph, project_data)
