import os.path
import argparse

from helpers.generate_new_format import generate_edges
from helpers.parse_scons_dependency_tree import parse_tree
from helpers.import_dep_info import ingest_deps
from helpers.dev_tools import Timer

def worker(input_tree, dep_info, output_dep_file, timer=False):
    with Timer('parsing', timer):
        results = parse_tree(input_tree, list())

    with Timer('importing dep info', timer):
        ingest_deps(dep_info, results)

    with Timer('generating graph', timer):
        g = generate_edges(results)

    with Timer('writing output file', timer):
        g.export(output_dep_file)

def argparser(parser):
    parser.add_argument('--timers', '-t', default=False, action='store_true')
    parser.add_argument('--format', '-f', default='json', action='store', choices=['json', 'pickle', 'pkl', 'jsn'])
    parser.add_argument('input_tree', default=os.path.join(os.path.dirname(__file__), "dependency_tree.txt"))
    parser.add_argument('dep_info', default=os.path.join(os.path.dirname(__file__), "deps.json"))
    parser.add_argument('output_dep_name', default=os.path.join(os.path.dirname(__file__), "dep_graph"))

    return parser

def command(args):
    output_fn = args.output_dep_name + '.' + args.format

    worker(args.input_tree, args.dep_info, outpu_fn, args.timers)

def main():
    parser = argparser(argparse.ArgumentParser("[wil]: willitlink ingestion"))
    args = parser.parse_args()

    command(args)
    print('[wil]: generated dependency MultiGraph at {0}'.format(args.output_deps))

if __name__ == '__main__':
    main()
