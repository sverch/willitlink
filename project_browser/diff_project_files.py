#!/usr/bin/python

import sys
import os
import re
import json
import yaml

from process_module_files import read_modules_file, dump_modules_file
from get_willitlink_data import load_graph

def get_project_data(base_directory):
    return read_modules_file(os.path.join(base_directory, "modules.yaml"))

def dump_project_data(base_directory, project_data):
    return dump_modules_file(base_directory, project_data)

def get_all_project_files(project_data):
    all_files = []
    for system_name in project_data.keys():
        for module_object in project_data[system_name]['modules']:
            for module_group in module_object['groups']:
                all_files.extend(module_group['files'])
    return all_files

def diff_files(graph, project_data):
    # First remove things from our project data that we no longer have
    for system_name in project_data.keys():
        for module_object in project_data[system_name]['modules']:
            for module_group in module_object['groups']:
                module_group['files'] = [ file_name for file_name in module_group['files'] if file_name in graph.files ]

    # Now add things to "uncategorized_system/uncategorized_module" if they aren't in our project,
    # but are in the file list we are comparing against
    all_project_files = get_all_project_files(project_data)
    for file_name in graph.files:
        file_name = str(file_name)
        # If this file is not in our project and it's a source file
        if file_name not in all_project_files and (file_name.endswith('.cc') or file_name.endswith('.cpp') or file_name.endswith('.h') or file_name.endswith('.hpp')):
            if 'uncategorized_system' not in project_data:
                project_data['uncategorized_system'] = {}
                project_data['uncategorized_system']['description'] = 'Files that have not yet been categorized into a particular system'
                project_data['uncategorized_system']['modules'] = []

            found_uncategorized_module = False
            for uncategorized_module in project_data['uncategorized_system']['modules']:
                if 'uncategorized_module' == uncategorized_module['name']:
                    found_uncategorized_module = True
                    for uncategorized_group in uncategorized_module['groups']:
                        uncategorized_group['files'].append(file_name)
                        break # only put this file in the first "uncategorized group", whatever it is

            if not found_uncategorized_module:
                project_data['uncategorized_system']['modules'].append({"name":"uncategorized_module",
                    "groups":[{"files":[file_name], "comments" : "uncategorized group"}]})

    return project_data

def main():

    if len(sys.argv) != 2:
        print "Usage: <base_directory>"
        exit(1)

    base_directory = sys.argv[1]

    project_data = get_project_data(base_directory)
    graph = load_graph(base_directory)

    diff_files(graph, project_data)

    dump_project_data(base_directory, project_data)

if __name__ == '__main__':
    main()
