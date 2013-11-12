#!/usr/bin/python

import argparse
import os
import json

import helpers.ingestion as ingestion
import dep_graph

from find_leaks import find_direct_leaks
from helpers.dev_tools import Timer

def get_graph(args):
    with Timer('loading graph {0}'.format(args.data), args.timers):
        g = dep_graph.MultiGraph(timers=args.timers).load(args.data)

    return g

def render_data_for_cli(g, name, rel):
    return json.dumps( { rel: { name: g.get_endswith(rel, name)}}, indent=3)

def get_relationship_node(args):
    g = get_graph(args)

    try:
        print(render_data_for_cli(g, args.name, args.relationship))
    except KeyError:
        print('[wil]: there is no {0} named {1}'.format(args.thing, args.name))

def get_list(args):
    g = get_graph(args)

    print(json.dumps(getattr(g, args.name)))

def get_leaks(args):
    g = get_graph(args)

    with Timer('leaks query', args.timers):
        leaks = find_direct_leaks(g, args.name)

    print(json.dumps( { 'archive': args.name, 'leaks': leaks }, indent=3))

def main():
    default_data_file = os.path.join(os.path.dirname(__file__), "dep_graph.json")
    relationships = { 'symdep':('symbol_to_file_sources', 'symbol'),
                      'symsrc':('symbol_to_file_dependencies', 'symbol'),
                      'filedef':('file_to_symbol_definitions', 'file'),
                      'filedep':('file_to_symbol_dependencies', 'file'),
                      'targetdep':('target_to_dependencies', 'target'),
                      'deptarget':('dependency_to_targets', 'dependency'),
                      'arc':('archives_to_components', 'archive'),
                    }

    parser = argparse.ArgumentParser()
    parser.add_argument('--timers', '-t', default=False, action='store_true')
    subparsers = parser.add_subparsers(dest='command')

    ingest_parser = subparsers.add_parser('ingest')
    ingest_parser = ingestion.argparser(ingest_parser)

    for k,v in relationships.items():
        sp = subparsers.add_parser(k)
        sp.set_defaults(relationship=v[0], thing=v[1])
        sp.add_argument('name')
        sp.add_argument('--data', '-d', default=default_data_file)

    get_list_parser = subparsers.add_parser('list')
    get_list_parser.add_argument('name', choices=['symbols', 'files'])
    get_list_parser.add_argument('--data', '-d', default=default_data_file)

    get_leaks_parser = subparsers.add_parser('leaks')
    get_leaks_parser.add_argument('name')
    get_leaks_parser.add_argument('--data', '-d', default=default_data_file)

    args = parser.parse_args()

    operations = {
        'ingest': ingestion.command,
        'symdep': get_relationship_node,
        'symsrc': get_relationship_node,
        'filedef': get_relationship_node,
        'filedep': get_relationship_node,
        'targetdep': get_relationship_node,
        'arc': get_relationship_node,
        'deptarget': get_relationship_node,
        'list': get_list,
        'leaks': get_leaks,
    }

    with Timer('complete operation time', args.timers):
        operations[args.command](args)

if __name__ == '__main__':
    main()
