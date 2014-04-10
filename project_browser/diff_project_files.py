#!/usr/bin/python

import sys
import os
import re
import json
import yaml

from data_access import read_project_structure_file, load_willitlink_graph, write_project_structure_file, validate_project_structure_file_schema, validate_processed_project_structure_file_schema
from data_manipulation import get_all_project_files

def diff_files(graph, project_data):
    # First remove things from our project data that we no longer have
    for system_object in project_data:
        for module_object in system_object['system_modules']:
            for module_group in module_object['module_groups']:
                new_group_files = []
                for file_name in module_group['group_files']:
                    if file_name in graph.files:
                        new_group_files.append(file_name)
                    else:
                        print "File name: " + file_name + " was deleted!"
                module_group['group_files'] = new_group_files

    # Now add things to "uncategorized_system/uncategorized_module" if they aren't in our project,
    # but are in the file list we are comparing against
    all_project_files = get_all_project_files(project_data)

    uncategorized_system_object = {}
    uncategorized_system_object['system_name'] = "uncategorized_system"
    uncategorized_system_object['system_title'] = "Uncategorized System"
    uncategorized_system_object['system_description'] = "Uncategorized System"
    uncategorized_system_object['system_modules'] = []
    uncategorized_module_object = {}
    uncategorized_module_object['module_name'] = "uncategorized_module"
    uncategorized_module_object['module_title'] = "Uncategorized Module"
    uncategorized_module_object['module_description'] = "Uncategorized Module"
    uncategorized_module_object['module_groups'] = []
    uncategorized_system_object['system_modules'].append(uncategorized_module_object)
    uncategorized_group_object = {}
    uncategorized_group_object['group_title'] = "Uncategorized Group"
    uncategorized_group_object['group_description'] = "Uncategorized Group"
    uncategorized_group_object['group_files'] = []
    uncategorized_module_object['module_groups'].append(uncategorized_group_object)

    for file_name in graph.files:
        file_name = str(file_name)
        # If this file is not in our project and it's a source file
        if file_name not in all_project_files and (file_name.endswith('.cc') or file_name.endswith('.cpp') or file_name.endswith('.h') or file_name.endswith('.hpp') or file_name.endswith('.js') or file_name.endswith('.py')):
            uncategorized_group_object['group_files'].append(file_name)

    project_data.append(uncategorized_system_object)

    return project_data

def main():

    if len(sys.argv) != 2:
        print "Usage: <base_directory>"
        exit(1)

    base_directory = sys.argv[1]

    project_data = read_project_structure_file(base_directory)
    graph = load_willitlink_graph(base_directory)

    diff_files(graph, project_data)

    write_project_structure_file(base_directory, project_data)

    validate_project_structure_file_schema(base_directory)

if __name__ == '__main__':
    main()
