def dedupe_edges_d3(d3_graph_object):

    edges_found = []
    current_edges = d3_graph_object['edges']

    for current_edge in current_edges:
        current_edge_items = current_edge.items()
        current_edge_items.sort()

        if current_edge_items not in edges_found:
            edges_found.append(current_edge_items)

    d3_graph_object['edges'] = map(dict, edges_found)

    return d3_graph_object


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
