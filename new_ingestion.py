import os.path
import argparse

from generate_new_format import generate_edges
from parse_scons_dependency_tree import parse_tree
from import_dep_info import ingest_deps
from dev_tools import Timer

def main():
    parser = argparse.ArgumentParser("willitlink Ingestion.")

    parser.add_argument('--timers', '-t', default=False, action='store_true')
    parser.add_argument('input_tree', default=os.path.join(os.path.dirname(__file__), "dependency_tree.txt"))
    parser.add_argument('dep_info', default=os.path.join(os.path.dirname(__file__), "deps.json"))
    parser.add_argument('output_deps', default=os.path.join(os.path.dirname(__file__), "dep_graph.json"))

    args = parser.parse_args()

    with Timer('parsing', args.timers):
        results = parse_tree(args.input_tree,
                             list())

    with Timer('importing dep info', args.timers):
        ingest_deps(args.dep_info, results)

    with Timer('generating graph', args.timers):
        g = generate_edges(results)

    with Timer('writing output file', args.timers):
        g.export(args.output_deps)

    print('[wil]: generated dependency MultiGraph at {0}'.format(args.output_deps))


if __name__ == '__main__':
    main()
