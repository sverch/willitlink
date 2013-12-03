#!/usr/bin/python

import argparse
import os

from willitlink.base.dev_tools import Timer

import willitlink.ingestion as ingestion
from willitlink.ingestion.collector import data_collector

from willitlink.cli.basic import get_relationship_node, get_list, get_symbol_location, get_relationship_types
from willitlink.cli.leaks import get_leaks, get_direct_leaks, get_unneeded_libdeps, get_leak_check
from willitlink.cli.trees import get_tree, get_tree_types
from willitlink.cli.d3 import get_file_family_tree_d3, get_file_family_tree_with_leaks_d3, get_file_family_relationship_d3

from willitlink.web.api import start_app

operations = {
    'collect': data_collector,
    'ingest': ingestion.command,
    'web': start_app,

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

    web_api_parser = subparsers.add_parser('web', help='start a simple json api to')
    web_api_parser.add_argument('--data', '-d', default=default_data_file)

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
    tree_parser.add_argument('--depth', type=int, default=2)

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
        sp.add_argument('--data', '-d', default=default_data_file)
        # two arguments are used below to ensure two or more files as arguments
        sp.add_argument('first_file', help="file to relate")
        sp.add_argument('files', nargs='+', help="list of other files to relate")

    args = parser.parse_args()
    args.g = None

    with Timer('complete operation time', args.timers):
        operations[args.command](args)


if __name__ == '__main__':
    main()
