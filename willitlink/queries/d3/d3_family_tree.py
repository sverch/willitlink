from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer

from willitlink.ingestion.parse_scons_dependency_tree import detect_type
from willitlink.queries.d3.utils import dedupe_edges_d3
from willitlink.queries.fullnames import get_full_filenames

def file_family_tree_d3(g, file_names, get_parents=True, get_children=True,
                        parent_node=None, child_node=None, is_full_file_name=False):

    family_tree = { 'nodes': set(),
                    'edges': [] }

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
            family_tree['edges'].append({ 'from' : parent_node,
                                          'to' : full_file_name,
                                          'type' : 'file' })

        if child_node is not None:
            family_tree['edges'].append({ 'from' : full_file_name,
                                          'to' : child_node,
                                          'type' : 'file' })

        if get_parents is True:
            parents = g.get('dependency_to_targets', full_file_name)

            parent_tree = file_family_tree_d3(g,
                                              parents,
                                              get_parents=True,
                                              get_children=False,
                                              child_node=full_file_name,
                                              is_full_file_name=True)

            family_tree['nodes'] = family_tree['nodes'].union(parent_tree['nodes'])
            family_tree['edges'].extend(parent_tree['edges'])

        if get_children is True:
            children = g.get('target_to_dependencies', full_file_name)

            child_tree = file_family_tree_d3(g,
                                             children,
                                             get_parents=False,
                                             get_children=True,
                                             parent_node=full_file_name,
                                             is_full_file_name=True)

            family_tree['nodes'] = family_tree['nodes'].union(child_tree['nodes'])
            family_tree['edges'].extend(child_tree['edges'])

    family_tree['nodes'] = list(family_tree['nodes'])
    return dedupe_edges_d3(family_tree)
