import os.path
import argparse

from willitlink.ingestion.build_graph import generate_edges
from willitlink.ingestion.parse_scons_dependency_tree import parse_tree
from willitlink.ingestion.import_dep_info import ingest_deps
from willitlink.base.dev_tools import Timer

output_formats = ['json', 'pickle', 'pkl', 'jsn']

def worker(input_tree, dep_info, output_dep_file, mongo_path, timer=False):
    with Timer('parsing', timer):
        results = parse_tree(input_tree, mongo_path)
        
    with Timer('importing dep info', timer):
        ingest_deps(dep_info, results)

    with Timer('generating graph', timer):
        g = generate_edges(results)

    with Timer('writing output file', timer):
        g.export(output_dep_file)

def argparser(cwd, parser):
    parser.add_argument('--timers', '-t', default=False, action='store_true')
    parser.add_argument('--format', '-f', default='json', action='store', choices=output_formats)
    parser.add_argument('--input_tree', default=os.path.join(cwd, 'data', "dependency_tree.txt"))
    parser.add_argument('--dep_info', default=os.path.join(cwd, 'data', "deps.json"))
    parser.add_argument('--mongo', '-m', default=os.path.join(cwd, '..', 'mongo'))
    parser.add_argument('--output_dep_name', default=os.path.join(cwd, 'data', "dep_graph.json"))

    return parser

def command(args):
    if os.path.splitext(args.output_dep_name)[1][1:] in output_formats:
        output_fn = args.output_dep_name
    else:
        output_fn = args.output_dep_name + '.' + args.format

    worker(args.input_tree, args.dep_info, output_fn, args.mongo, args.timers)

def main():
    parser = argparser(argparse.ArgumentParser("[wil]: willitlink ingestion"))
    args = parser.parse_args()

    command(args)
    print('[wil]: generated dependency MultiGraph at {0}'.format(args.output_deps))

if __name__ == '__main__':
    main()
