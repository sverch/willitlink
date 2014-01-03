from willitlink.cli.tools import get_graph, render

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer

from willitlink.queries.symbols import locate_symbol

def get_relationship_node(args):
    g = get_graph(args)

    try:
        name = args.name

        rel = args.relationship

        if rel is None:
            raise Exception('invalid relationship type.')

        # XXX: get_contains is more user friendly for long symbol names, but the problem is that we
        # don't know WHICH symbol we actually matched.  All we know is what we are looking for.
        # This means if we look for "inShutdown", we get a list of lists, but have no idea what the
        # original symbol was.
        #
        # The solution to this would be to look in the list of all symbols first, then expand the
        # names and return that as part of the result to the user.  That requires some refactoring.
        render({ rel: { name: g.get_contains(get_relationship_types()[rel][0], name)}})
    except KeyError:
        print('[wil]: there is no {0} named {1}'.format(args.thing, args.name))


def get_relationship_types():
    return { 'sources':('symbol_to_file_sources', 'symbol', 'the files where a symbol is defined'),
             'uses':('symbol_to_file_dependencies', 'symbol', 'the files where a symbol is used'),
             'definitions':('file_to_symbol_definitions', 'file', 'the symbols defined by a file'),
             'dependencies':('file_to_symbol_dependencies', 'file', 'the symbols needed by a file'),
             'children':('target_to_dependencies', 'target', 'the build targets that this build target depends on'),
             'parents':('dependency_to_targets', 'dependency', 'the build targets that require this build target'),
             'components':('archives_to_components', 'archive', 'the components of an archive'),
    }

def get_list(args):
    g = get_graph(args)

    render([ i for i in getattr(g, args.type) if i.endswith(args.filter)])

def get_symbol_location(args):
    g = get_graph(args)

    with Timer('find symbol location', args.timers):
        render(locate_symbol(g, args.name))
