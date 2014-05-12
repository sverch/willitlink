#!/usr/bin/python

import argparse
import os

from willitlink.base.dev_tools import Timer

import willitlink.ingestion as ingestion
from willitlink.ingestion.collector import data_collector

from willitlink.cli.basic import get_relationship_node, get_list, get_symbol_location, get_relationship_types
from willitlink.cli.leaks import get_leaks, get_unneeded_libdeps
from willitlink.cli.interface import get_interface
from willitlink.cli.trees import get_tree, get_tree_types
from willitlink.cli.d3 import get_file_family_tree_d3, get_file_family_tree_with_leaks_d3, get_file_family_relationship_d3
from willitlink.cli.libs_needed import get_required_libs, get_circle_deps
from willitlink.cli.file_graph import get_file_graph
from willitlink.cli.executables import get_executables

from willitlink.web.api import start_app

operations = {
    'collect': data_collector,
    'ingest': ingestion.command,
    'web': start_app,

    'basic': get_relationship_node,
    'tree': get_tree,
    'list': get_list,
    'libs-needed': get_required_libs,
    'libs-cycle': get_circle_deps,

    'leaks': get_leaks,

    'd3-file-family': get_file_family_tree_d3,
    'd3-file-family-with-leaks': get_file_family_tree_with_leaks_d3,
    'd3-file-relationship': get_file_family_relationship_d3,

    'interface': get_interface,
    'symbol': get_symbol_location,
    'extra-libdeps': get_unneeded_libdeps,

    'file-graph' : get_file_graph,

    'executables' : get_executables
}

def main():
    default_cwd = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    default_data_file = os.path.join(default_cwd, 'data', "dep_graph.json")

    parser = argparse.ArgumentParser(prog='wil.py', usage='wil.py [command] [arguments]', add_help='[wil]: a dependency analysis toolkit')
    parser.set_defaults(cwd=default_cwd)
    parser.add_argument('--timers', '-t', default=False, action='store_true')
    parser.add_argument('--data', '-d', default=default_data_file)
    subparsers = parser.add_subparsers(dest='command', title='commands', metavar='')

    ingest_parser = subparsers.add_parser('ingest', help='process collected data')
    ingest_parser = ingestion.argparser(default_cwd, ingest_parser)

    collector_parser = subparsers.add_parser('collect', help='generate and collect data from the build system')
    collector_parser.add_argument('--mongo', '-m', default=os.path.join(default_cwd, '..', 'mongo'))
    collector_parser.add_argument('--scons', '-s', nargs='*', default=[])

    web_api_parser = subparsers.add_parser('web', help='start a simple json api to')

    get_list_parser = subparsers.add_parser('list', help='a list of all symbols or files.')
    get_list_parser.add_argument('type', choices=['symbols', 'files'], help='kind of object')
    get_list_parser.add_argument('--filter', help='a prefix limiting expression', default="")

    relationship_parser = subparsers.add_parser('basic', help='return basic single relationships')
    relationship_subparsers = relationship_parser.add_subparsers(dest='relationship')

    for k,v in get_relationship_types().items():
        relationship_subparsers.add_parser(k, help=v[2]).add_argument('name')

    tree_parser = subparsers.add_parser('tree', help='return relationships rendered as trees')
    tree_parser.add_argument('--depth', type=int, default=2)

    for tree in get_tree_types().keys():
        tree_parser.add_argument('--' + tree, nargs='*', help='render tree of {0} for an object'.format(tree))

    for query_parser in [ 'leaks', 'symbol', 'extra-libdeps' ]:
        sp = subparsers.add_parser(query_parser, help='query for ' + query_parser)
        sp.add_argument('name')

        if query_parser is 'leaks':
            sp.add_argument('--source_names', '-s', nargs='*', help='names of files to look up symbols in but not check for leaks of', default=[])
            sp.add_argument('--depth', type=int, help='how many parents in the build graph to show for the sources of the symbols', default=2)

    sp = subparsers.add_parser('interface', help='query for interface')
    sp.add_argument('names', nargs='+', help="list of libraries or objects to get interface of")

    sp = subparsers.add_parser('executables', help='query for the executables a file is built into')
    sp.add_argument('name', help="file to check the executable list for")

    for query_parser in [ 'libs-needed', 'libs-cycle' ]:
        sp = subparsers.add_parser(query_parser, help='query for ' + query_parser)
        sp.add_argument('names', nargs='+', help="list of libraries or objects to check deps of")

    file_graph_parser = subparsers.add_parser('file-graph', help='return a structure that represents a weighted graph of dependencies between files')

    args = parser.parse_args()
    args.g = None

    with Timer('complete operation time', args.timers):
        operations[args.command](args)


if __name__ == '__main__':
    main()
