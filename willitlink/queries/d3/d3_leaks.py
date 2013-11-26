from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer
from willitlink.queries.tree_leaks import find_direct_leaks
from willitlink.queries.d3.utils import dedupe_edges_d3
from willitlink.base.jobs import runner
from willitlink.base.dev_tools import Timer


# Pseudocode:
# for each archive or executable:
#    for each component in archive:
#         for each symbol dep in component:
#               if not leaky:
#                       for each symbol source in symbol dep
#                              for each source archive in symbol_source
#                                      link source archive to dest archive

def add_leaks_d3(g, d3_graph_object):
    # Get any symbols that are leaking from this archive
    # Iterate all the symbols leaking from this archive

    jobs = (
        { 'job': find_direct_leaks, 'args': [g, fn_obj] }
        for fn_obj
        in d3_graph_object['nodes']
    )

    with Timer('find direct leaks for edges', True):
        leak_objects = runner(jobs, parallel='threads')

    with Timer('resolve direct leak edges', True):
        map(d3_graph_object['edges'].extend,
            runner(symbol_resolving_jobs(g, leak_objects), parallel='threads') )

    return dedupe_edges_d3(d3_graph_object)

def symbol_resolving_jobs(g, leak_objects):
    for leak_object in leak_objects:

        if 'symbol' not in leak_object and isinstance(leak_object, list):
            leak_objects.extend(leak_object)
            continue

        yield { 'job': symbol_resolver, 'args': [g, leak_object]}

def symbol_resolver(g, leak_object):
    o = []
    # Get the files this symbol is defined
    for symbol_source in g.get('symbol_to_file_sources', leak_object['symbol']):

        # Get the archives this file is in
        for archive_source in g.get('dependency_to_targets', symbol_source):

            # Finally, for each archive, add an edge
            # XXX: Ignore the client_build for now, since we will get edges going there that we
            # don't really care about.
            # TODO: Actually get the client build out of the data so that we can analyze it
            # separately (it is logically separate and just adds more noise to our data)
            if archive_source.find("client_build") == -1:
                o.append( { 'to' : archive_source,
                            'from' : leak_object['parents'][-1],
                            'type' : 'symbol',
                            'symbol' : leak_object['symbol'] })

    return o
