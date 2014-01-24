from willitlink.cli.tools import get_graph, render

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer

from willitlink.queries.symbols import locate_symbol
from willitlink.queries.fullnames import expand_file_names, expand_symbol_names

def get_relationship_node(args):
    g = get_graph(args)

    try:
        name = args.name

        rel = args.relationship

        if rel is None:
            raise Exception('invalid relationship type.')

        result = {}
        if get_relationship_types()[rel][1] == 'symbol':
            full_symbol_names = expand_symbol_names(g, args.name)
            for full_symbol_name in full_symbol_names:
                result[full_symbol_name] = g.get(get_relationship_types()[rel][0], full_symbol_name)
        else:
            full_file_names = expand_file_names(g, args.name)
            for full_file_name in full_file_names:
                result[full_file_name] = g.get(get_relationship_types()[rel][0], full_file_name)
        render(result)
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
             'headers':('file_to_header_includes', 'file', 'the headers that are built into an object file'),
             'objects-including':('header_to_files_including', 'file', 'the objects that include a header'),
             'source':('file_to_source', 'file', 'the source that an object file is built from'),
             'object-built':('source_to_file', 'file', 'the source that is used to build an object file'),
    }

def get_list(args):
    g = get_graph(args)

    render([ i for i in getattr(g, args.type) if i.endswith(args.filter)])

def get_symbol_location(args):
    g = get_graph(args)

    with Timer('find symbol location', args.timers):
        render(locate_symbol(g, args.name))
