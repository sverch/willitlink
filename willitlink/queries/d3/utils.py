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
