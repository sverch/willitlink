import os.path
import argparse
import json

from willitlink.ingestion.build_graph import generate_edges
from willitlink.ingestion.parse_scons_dependency_tree import parse_tree
from willitlink.ingestion.import_dep_info import ingest_deps
from willitlink.ingestion.version_info import get_version_info
from willitlink.base.dev_tools import Timer

output_formats = ['json', 'pickle', 'pkl', 'jsn']

def worker(input_tree, dep_info, build_info_file, output_dep_file, mongo_path, timer=False, client_build=False):
    with Timer('parsing', timer):
        results = parse_tree(input_tree, mongo_path)

    with Timer('importing dep info', timer):
        ingest_deps(dep_info, results)

    with Timer('generating graph', timer):
        g = generate_edges(results, client_build)

    with Timer('adding version and build info', timer):
        version_and_build_info = {}
        version_and_build_info['version_info'] = get_version_info(mongo_path)
        with open(build_info_file) as build_info:
            version_and_build_info['build_info'] = json.loads(build_info.read())
        g.set_extra_info(version_and_build_info)

    with Timer('writing output file', timer):
        g.export(output_dep_file)

def argparser(cwd, parser):
    parser.add_argument('--timers', '-t', default=False, action='store_true')
    parser.add_argument('--format', '-f', default='json', action='store', choices=output_formats)
    parser.add_argument('--mongo', '-m', default=os.path.join(cwd, '..', 'mongo'))
    parser.add_argument('--client', '-c', default=False, action='store_true',
            help='Use the C++ driver build objects instead of the server build objects')

    return parser

def command(args):
    # Output of scons dependency tree
    input_tree = os.path.join(args.data, 'dependency_tree.txt')

    # Scons flags we used to build
    build_info_file = os.path.join(args.data, 'build_info.json')

    # Output from our libdeps patch
    dep_info = os.path.join(args.data, 'deps.json')

    # Final output for graph result
    output_dep_file = os.path.join(args.data, 'dep_graph.json')

    for fn in [ output_dep_file ]:
        if os.path.exists(fn):
            os.remove(fn)

    if os.path.splitext(output_dep_file)[1][1:] in output_formats:
        output_fn = output_dep_file
    else:
        output_fn = output_dep_file + '.' + args.format

    worker(input_tree, dep_info, build_info_file, output_fn, args.mongo, args.timers, args.client)

def main():
    parser = argparser(argparse.ArgumentParser("[wil]: willitlink ingestion"))
    args = parser.parse_args()

    command(args)
    print('[wil]: generated dependency MultiGraph at {0}'.format(args.output_deps))

if __name__ == '__main__':
    main()
