import argparse

from generate_new_format import generate_edges
from parse_scons_dependency_tree import parse_tree
from dev_tools import Timer

def main():
    parser = argparse.ArgumentParser("willitlink Ingestion.")

    parser.add_argument('--timers', '-t', default=False, action='store_true')
    parser.add_argument('input_tree')
    parser.add_argument('output_deps')

    args = parser.parse_args()

    with Timer('parsing', args.timers):
        results = parse_tree(args.input_tree,
                             list())

    with Timer('generating graph', args.timers):
        g = generate_edges(results)

    with Timer('writing output file', args.timers):
        g.export(args.output_deps)

    print('[wil]: generated dependency MultiGraph at {0}'.format(args.output_deps))


if __name__ == '__main__':
    main()
