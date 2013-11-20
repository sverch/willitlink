#!/usr/bin/python

import os
import sys
import json

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.d3.d3_utils import dedupe_edges_d3

def detect_type(line):
    if line.endswith('.h'):
        return "header"

    if line.endswith('.o'):
        return "object"

    if line.endswith('.a'):
        return "archive"

    if line.endswith('.js'):
        return "javascript"

    # Assume it's a system file if it starts with a '/'
    if line.startswith('/'):
        return "system"

    return "target"

def get_full_filenames(g, file_names):

    full_file_names = []

    for i in g.files:
        for file_name in file_names:
            # If we have an exact match just return a single element to reduce noise
            # TODO: find a more elegant way to do this and document how it works.
            if i == file_name:
                full_file_names = [ file_name ]
                break
            if i.endswith(file_name):
                full_file_names.append(i)

    return full_file_names

def file_family_tree_d3(g, file_names, get_parents=True, get_children=True, parent_node=None, child_node=None, is_full_file_name=False):

    family_tree = {}
    family_tree['nodes'] = set()
    family_tree['edges'] = []

    if len(file_names) == 0:
        return family_tree

    # Resolve the full file names if just the end was specified
    if not is_full_file_name:
        full_file_names = get_full_filenames(g, file_names)
    else:
        full_file_names = file_names


    for full_file_name in full_file_names:

        # Add this node
        family_tree['nodes'].add(full_file_name)

        # Add this edge if we came from somewhere
        if parent_node is not None:
            family_tree['edges'].append({ 'from' : parent_node, 'to' : full_file_name, 'type' : 'file' })

        if child_node is not None:
            family_tree['edges'].append({ 'from' : full_file_name, 'to' : child_node, 'type' : 'file' })

        if get_parents is True:
            parents = []
            try:
                parents = g.get('dependency_to_targets', full_file_name)
            except KeyError:
                pass

            parent_tree = file_family_tree_d3(g,
                                                parents,
                                                get_parents=True,
                                                get_children=False,
                                                child_node=full_file_name,
                                                is_full_file_name=True)

            family_tree['nodes'] = family_tree['nodes'].union(set(parent_tree['nodes']))
            family_tree['edges'].extend(parent_tree['edges'])

        if get_children is True:
            children = []
            try:
                children = g.get('target_to_dependencies', full_file_name)
            except KeyError:
                pass

            child_tree = file_family_tree_d3(g,
                                                children,
                                                get_parents=False,
                                                get_children=True,
                                                parent_node=full_file_name,
                                                is_full_file_name=True)

            family_tree['nodes'] = family_tree['nodes'].union(set(child_tree['nodes']))
            family_tree['edges'].extend(child_tree['edges'])

    family_tree['nodes'] = list(family_tree['nodes'])
    return dedupe_edges_d3(family_tree)
