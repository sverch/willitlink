import json
from flask import Flask, Response, request

from willitlink.base.graph import MultiGraph
from willitlink.base.dev_tools import Timer

from willitlink.queries.extra_archives import find_all_extra_archives
app = Flask('wil')

def render(obj):
    return Response(json.dumps(obj), status=200, mimetype='application/json')

@app.route('/symbols')
def return_symbols(prefix=None):
    try:
        ret = filter_lists(app.g, request, 'symbols')
    except Exception as e:
        print(e)

    return render(ret)

@app.route('/files')
def return_files():
    try:
        ret = filter_lists(app.g, request, 'files')
    except Exception as e:
        print(e)

    return render(ret)

def filter_lists(graph, request, kind):
    queries = { 'prefix': request.args.get('prefix'),
                'suffix': request.args.get('suffix'),
                'name': request.args.get('name'),
                'all': request.args.get('all')
              }

    query = None
    for q,v in queries.items():
        if v is not None:
            query = ( q, v )

    if query is None:
        ret = { kind: None }
    else:
        if query[0] == 'prefix':
            ret = { kind: [ f for f in getattr(graph, kind) if f.startswith(query[1])] }
        elif query[0] == 'suffix':
            ret = { kind: [ f for f in getattr(graph, kind) if f.endswith(query[1])] }
        elif query[0] == 'name':
            ret = { kind : [ f for f in getattr(graph, kind) if f == query[1] ] }
        elif query[0] == 'all':
            ret = { kind: getattr(graph, kind)}

    return ret

@app.route('/unneeded-dependencies')
def return_unneeded_archive_dependencies():
    archive = request.args.get('archive')
    if archive is not None:
        archive = archive.split(',')

    with Timer('render all extra archives', True):
        unneeded_deps = find_all_extra_archives(app.g)

    return render(unneeded_deps.narrow(archive).render())


@app.route('/')
def root():
    return render({})

def start_app(args):
    with Timer('importing data into global app state'):
        app.g = MultiGraph(timers=False).load(args.data)

    app.debug = True
    app.run()
