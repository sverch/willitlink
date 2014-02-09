#!/usr/bin/python

import sys
import os
import re
import json
import yaml

from data_access import read_project_structure_file, load_willitlink_graph, write_project_structure_file

def get_all_project_files(project_data):
    all_files = []
    for system_object in project_data:
        for module_object in system_object['system_modules']:
            for module_group in module_object['groups']:
                all_files.extend(module_group['files'])
    return all_files

def diff_files(graph, project_data):
    # First remove things from our project data that we no longer have
    for system_object in project_data:
        for module_object in system_object['system_modules']:
            for module_group in module_object['groups']:
                module_group['files'] = [ file_name for file_name in module_group['files'] if file_name in graph.files ]

    # Now add things to "uncategorized_system/uncategorized_module" if they aren't in our project,
    # but are in the file list we are comparing against
    all_project_files = get_all_project_files(project_data)

    # TODO: Actually preserve order of the whole thing by loading as OrderedDict
    uncategorized_system_object = OrderedDict()
    uncategorized_system_object['name'] = "uncategorized_system"
    uncategorized_system_object['title'] = "Uncategorized System"
    for file_name in graph.files:
        file_name = str(file_name)
        # If this file is not in our project and it's a source file
        if file_name not in all_project_files and (file_name.endswith('.cc') or file_name.endswith('.cpp') or file_name.endswith('.h') or file_name.endswith('.hpp') or file_name.endswith('.js') or file_name.endswith('.py')):
            if 'uncategorized_system' not in project_data:
                uncategorized_system_object = {}
                uncategorized_system_object['description'] = 'Files that have not yet been categorized into a particular system'
                uncategorized_system_object['system_modules'] = []

            found_uncategorized_module = False
            for uncategorized_module in uncategorized_system_object['system_modules']:
                if 'uncategorized_module' == uncategorized_module['name']:
                    found_uncategorized_module = True
                    for uncategorized_group in uncategorized_module['groups']:
                        uncategorized_group['files'].append(file_name)
                        break # only put this file in the first "uncategorized group", whatever it is

            if not found_uncategorized_module:
                uncategorized_system_object['modules'].append({"name":"uncategorized_module",
                    "groups":[{"files":[file_name], "comments" : "uncategorized group"}]})

    project_data.append(uncategorized_system_object)

    return project_data

# TODO: This doesn't actually work at all now, since it is assuming the old schema
def main():

    if len(sys.argv) != 2:
        print "Usage: <base_directory>"
        exit(1)

    base_directory = sys.argv[1]

    project_data = read_project_structure_file(base_directory)
    graph = load_willitlink_graph(base_directory)

    diff_files(graph, project_data)

    write_project_structure_file(base_directory, project_data)

if __name__ == '__main__':
    main()
