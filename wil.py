#!/usr/bin/python

import argparse
import os
import json

import willitlink.ingestion as ingestion
from willitlink.ingestion.collector import data_collector
from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer

from willitlink.queries.leaks import find_direct_leaks
from willitlink.queries.libstats import resolve_leak_info
from willitlink.queries.family_tree import symbol_family_tree, file_family_tree
from willitlink.queries.tree_leaks import find_direct_leaks
from willitlink.queries.symbols import locate_symbol
from willitlink.queries.extra_archives import find_extra_archives

# d3 code
# TODO: actually make this general
from willitlink.queries.d3.d3_family_tree import file_family_tree_d3
from willitlink.queries.d3.d3_relationship import relationship_info_d3
from willitlink.queries.d3.d3_leaks import add_leaks_d3

def get_graph(args):
    with Timer('loading graph {0}'.format(args.data), args.timers):
        g = MultiGraph(timers=args.timers).load(args.data)

    return g

def render(data):
    print(json.dumps(data, indent=3))

def get_relationship_node(args):
    g = get_graph(args)

    try:
        name = args.name

        rel = None
        for rel_type in get_relationship_types().keys():
            if getattr(args, rel_type) is not None:
                rel = rel_type
                break

        if rel is None:
            raise Exception('invalid relationship type.')

        render({ rel: { name: g.get_endswith(rel, name)}})
    except KeyError:
        print('[wil]: there is no {0} named {1}'.format(args.thing, args.name))

def get_tree(args):
    g = get_graph(args)

    for tree_type in get_tree_types().keys():
        if getattr(args, tree_type) is not None:
            tree = tree_type
            args.name = getattr(args, tree)
            break

    if tree is None:
        raise Exception('invalid tree type.')

    get_tree_types()[tree](args)

def get_list(args):
    g = get_graph(args)

    render([ i for i in getattr(g, args.type) if i.endswith(args.filter)])

def get_leaks(args):
    g = get_graph(args)

    with Timer('leaks query', args.timers):
        leaks = find_direct_leaks(g, args.name)

    render({ 'archive': args.name, 'leaks': leaks })

def get_leak_check(args):
    g = get_graph(args)

    with Timer('leaks tree query', args.timers):
        render(resolve_leak_info(g, args.name, args.depth, args.timers))

def get_file_family_tree(args):
    g = get_graph(args)

    with Timer('get file family tree query', args.timers):
        render(file_family_tree(g, args.name, args.depth))

def get_file_family_tree_d3(args):
    g = get_graph(args)

    with Timer('get file family tree query', args.timers):
        render(file_family_tree_d3(g, [args.name]))

def get_file_family_tree_with_leaks_d3(args):
    g = get_graph(args)

    family_tree = {}

    with Timer('get file family tree query', args.timers):
        family_tree = file_family_tree_d3(g, [args.name])

    with Timer('add leaks query', args.timers):
        render(add_leaks_d3(g, family_tree))

def get_file_family_relationship_d3(args):
    g = get_graph(args)

    with Timer('relationship info query', args.timers):
        render(relationship_info_d3(g, [ args.name1, args.name2 ]))

def get_symbol_family_tree(args):
    g = get_graph(args)

    with Timer('get symbol family tree query', args.timers):
        render(symbol_family_tree(g, args.name, args.depth))

def get_direct_leaks(args):
    g = get_graph(args)

    with Timer('direct leak query', args.timers):
        render(find_direct_leaks(g, args.name))

def get_symbol_location(args):
    g = get_graph(args)

    with Timer('find symbol location', args.timers):
        render(locate_symbol(g, args.name))

def get_unneeded_libdeps(args):
    g = get_graph(args)

    archives = []
    for filename in g.files:
        if filename.endswith(".a"):
            archives.append(filename)
    print('[wil]: number of unneeded libdeps: ' + str(len(archives)))

    with Timer('find unneeded libdeps', args.timers):
        render(find_extra_archives(g, args.name))

def get_tree_types():
    return {
        'leak': get_leak_check,
        'symbol': get_symbol_family_tree,
        'file': get_file_family_tree,
    }

def get_relationship_types():
    return { 'symbol_dep':('symbol_to_file_sources', 'symbol', 'the file sources for a symbol'),
             'symbol_src':('symbol_to_file_dependencies', 'symbol', 'the file(s) that a symbol depends on'),
             'file_def':('file_to_symbol_definitions', 'file', 'the files that define a symbol'),
             'file_dep':('file_to_symbol_dependencies', 'file', 'the files that a symbol depends on'),
             'target_dep':('target_to_dependencies', 'target', 'the dependencies for a build target'),
             'dep_target':('dependency_to_targets', 'dependency', 'the build targets for a dependency'),
             'archive':('archives_to_components', 'archive', 'the components of an archive'),
    }

def main():
    default_cwd = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    default_data_file = os.path.join(default_cwd, 'data', "dep_graph.json")

    parser = argparse.ArgumentParser(prog='wil.py', usage='wil.py [command] [arguments]', add_help='[wil]: a dependency analysis toolkit')
    parser.set_defaults(cwd=default_cwd)
    parser.add_argument('--timers', '-t', default=False, action='store_true')
    subparsers = parser.add_subparsers(dest='command', title='commands', metavar='')


    ingest_parser = subparsers.add_parser('ingest', help='process collected data')
    ingest_parser = ingestion.argparser(default_cwd, ingest_parser)


    collector_parser = subparsers.add_parser('collect', help='generate and collect data from the build system')
    collector_parser.set_defaults(data_dir=os.path.join(default_cwd, 'data'))
    collector_parser.add_argument('--tree_name', default='dependency_tree.txt')
    collector_parser.add_argument('--data', '-d', default='deps.json')
    collector_parser.add_argument('--mongo', '-m', default=os.path.join(default_cwd, '..', 'mongo'))
    collector_parser.add_argument('--scons', '-s', nargs='*', default=[])


    get_list_parser = subparsers.add_parser('list', help='a list of all symbols or files.')
    get_list_parser.add_argument('type', choices=['symbols', 'files'], help='kind of object')
    get_list_parser.add_argument('filter', help='a prefix limiting expression')
    get_list_parser.add_argument('--data', '-d', default=default_data_file)


    relationship_parser = subparsers.add_parser('relationship', help='return direct single relationships')
    relationship_parser.add_argument('--data', '-d', default=default_data_file)

    for k,v in get_relationship_types().items():
        relationship_parser.add_argument('--' + k, action='store_const', const=v[1], help=v[2] )

    relationship_parser.add_argument('name', help='the name of object.')


    tree_parser = subparsers.add_parser('tree', help='return relationships rendered as trees')
    tree_parser.add_argument('--data', '-d', default=default_data_file)
    tree_parser.add_argument('--depth', type=int, default=1)

    for tree in get_tree_types().keys():
        tree_parser.add_argument('--' + tree, nargs='*', help='render tree of {0} for an object'.format(tree))

    for query_parser in [ 'leaks', 'direct-leaks', 'symbol',
                          'extra-libdeps', 'd3-file-family',
                          'd3-file-family-with-leaks']:
        sp = subparsers.add_parser(query_parser, help='query for ' + query_parser)
        sp.add_argument('name')
        sp.add_argument('--data', '-d', default=default_data_file)

    for query_parser in [ 'd3-file-relationship' ]:
        sp = subparsers.add_parser(query_parser, help='query for ' + query_parser)
        sp.add_argument('name1')
        sp.add_argument('name2')
        sp.add_argument('--data', '-d', default=default_data_file)

    args = parser.parse_args()

    operations = {
        'collect': data_collector,
        'ingest': ingestion.command,

        'relationship': get_relationship_node,
        'tree': get_tree,
        'list': get_list,

        'leaks': get_leaks,

        'd3-file-family': get_file_family_tree_d3,
        'd3-file-family-with-leaks': get_file_family_tree_with_leaks_d3,
        'd3-file-relationship': get_file_family_relationship_d3,

        'direct-leaks': get_direct_leaks,
        'symbol': get_symbol_location,
        'extra-libdeps': get_unneeded_libdeps,
    }

    with Timer('complete operation time', args.timers):
        operations[args.command](args)

if __name__ == '__main__':
    main()
