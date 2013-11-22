from willitlink.cli.tools import get_graph, render

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer

from willitlink.queries.symbols import locate_symbol


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

        render({ rel: { name: g.get_endswith(get_relationship_types()[rel][0], name)}})
    except KeyError:
        print('[wil]: there is no {0} named {1}'.format(args.thing, args.name))


def get_relationship_types():
    return { 'symbol_dep':('symbol_to_file_sources', 'symbol', 'the file sources for a symbol'),
             'symbol_src':('symbol_to_file_dependencies', 'symbol', 'the file(s) that a symbol depends on'),
             'file_def':('file_to_symbol_definitions', 'file', 'the files that define a symbol'),
             'file_dep':('file_to_symbol_dependencies', 'file', 'the files that a symbol depends on'),
             'target_dep':('target_to_dependencies', 'target', 'the dependencies for a build target'),
             'dep_target':('dependency_to_targets', 'dependency', 'the build targets for a dependency'),
             'archive':('archives_to_components', 'archive', 'the components of an archive'),
    }

def get_list(args):
    g = get_graph(args)

    render([ i for i in getattr(g, args.type) if i.endswith(args.filter)])

def get_symbol_location(args):
    g = get_graph(args)

    with Timer('find symbol location', args.timers):
        render(locate_symbol(g, args.name))
