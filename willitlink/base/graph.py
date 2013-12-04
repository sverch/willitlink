"""
A simple (prototype) graph modeling toolkit/API for simple dependency analysis. Internally

Use:

- To create a new graph object, adds a few items, to the graph and then dumps
  the graph to a json file to persist state to disk and avoid over generation:

     tracked_relationships = [ 'files2cows', 'cows2people' ]

     g = MultiGraph(tracked_relationships)

     g.add('files2cows', 'a.out', ['bessie', 'hef'])
     g.add('files2cows', 'a.out', 'elsa')

     g.add('cows2people', 'bessie', ['shaun', 'tycho'])
     g.add('cows2people', 'elsa', 'jason')

     g.export('files2people.json')

- To create an equivalent ``g`` object from the ``file2people.json``
  dump to recover a previous state:

     g = MultiGraph().load('files2people.json')

- To return a standard directed graph for a single relationship, for integration
  with external graph analysis libraries:

     g.slice('cows2people')

- To return a list of dependencies, in a dict that maps ``{ relationship:
  dependencies}`` for item ``bessie``:

     g.resolve('bessie')

- To return a MultiGraph object that contains *only* the relationships for
  ``bessie``:

     g.narrow('bessie')

- To return a list of dependencies for an item and a particular relationship:

     g.get('cows2people', 'bessie')
"""

import os
import datetime
import logging
import json

from willitlink.base.jobs import runner, ThreadPool, resolve_dict_keys, resolve_results

from willitlink.base.dev_tools import Timer

logger = logging.getLogger(__name__)

class GraphError(Exception):
    pass

def graph_builder(relationship, graph):
    return relationship, Graph(graph)

class Graph(object):
    def __init__(self, base=None):
        if base is None:
            self.graph = dict()
        else:
            self.graph = base

    def add(self, item, deps):
        if isinstance(item, list):
            raise GraphError('cannot add lists to graph')

        if item not in self.graph:
            self.graph[item] = set()

        if isinstance(deps, list):
            self.graph[item].update(deps)
        else:
            self.graph[item].add(deps)

    def get(self, item):
        if item in self.graph:
            return list(self.graph[item])
        else:
            return list()

    def get_startswith(self, name):
        r = list()
        for i in self.graph.keys():
            if i.startswith(name):
                item = self.get(i)
                if item:
                    r.append(item)
        return r

    def get_endswith(self, name):
        r = list()
        for i in self.graph.keys():
            if i.endswith(name):
                item = self.get(i)
                if item:
                    r.append(item)
        return r

    def holds(self, name):
        r = dict()
        for k, v in self.graph.items():
            if name in v:
                r[k] = v
        return r

    def fetch(self):
        r = dict()
        for k in self.graph.keys():
            item = self.get(k)
            if item:
                r[k] = item
        return r

    def get_nodes(self):
        return list(self.graph.keys())

class MultiGraph(object):
    def __init__(self, relationships=None, timers=False):
        if relationships is None:
            self.relationships = []
        else:
            self.relationships = relationships

        self.graphs = self.new_graph()
        self.subset = False
        self.has_lists = False
        self.lists = []
        self.timer = timers

    def make_lists(self, lists):
        self.lists.extend(lists)

        for l in lists:
            if not hasattr(self, l):
                setattr(self, l, list())

        self.has_lists = True

    def extend_list(self, list_name, content):
        if list_name in self.lists:
            current = getattr(self, list_name)
            current.extend(content)

    def uniquify_lists(self):
        if self.has_lists is False:
            return False
        else:
            for l in self.lists:
                nl = set(getattr(self, l))
                setattr(self, l, list(nl))

            return True

    def new_graph(self):
        graph = dict()

        for i in self.relationships:
            graph[i] = Graph()

        return graph

    def add(self, relationship, item, deps):
        if relationship in self.relationships:
            self.graphs[relationship].add(item, deps)
        else:
            logger.debug('cannot add to non-extant relationship type ' + relationship)

    def get(self, relationship, item):
        if relationship in self.relationships:
            return self.graphs[relationship].get(item)
        else:
            logger.debug('cannot fetch from non-extant relationship type ' + relationship)

    def get_startswith(self, relationship, name):
        if relationship in self.relationships:
            return self.graphs[relationship].get_startswith(name)
        else:
            logger.debug('cannot fetch from non-extant relationship type ' + relationship)

    def get_endswith(self, relationship, name):
        if relationship in self.relationships:
            return self.graphs[relationship].get_endswith(name)
        else:
            logger.debug('cannot fetch from non-extant relationship type ' + relationship)

    def get_holds(self, relationship, name):
        if relationship in self.relationships:
            return self.graphs[relationship].get_holds(name)
        else:
            logger.debug('cannot fetch from non-extant relationship type ' + relationship)

    def get_nodes(self, relationship):
        return self.graphs[relationship].get_nodes()

    def resolve(self, item):
        o = dict()
        for i in self.relationships:
            o[i] = self.graphs[i].get(item)

        return o

    def narrow(self, item):
        graph = MultiGraph()
        graph.subset = True

        if isinstance(item, list):
            for node in item:
                for i in self.relationships:
                    graph.add(i, node, self.graphs[i].get(item))
        else:
            for i in self.relationships:
                graph.add(i, item, self.graphs[i].get(item))

        return graph

    def slice(self, relationship):
        return self.graphs[relationship].fetch()

    @classmethod
    def load(cls, fn):
        if not os.path.exists(fn):
            msg = 'cannot load from non existing file {0} please rebuild'.format(fn)
            logger.debug(msg)
            raise Exception(msg)

        with open(fn, 'r') as f:
            data = json.load(f)
            data_dir = os.path.dirname(fn)

            rels = data['relationships']

            c = MultiGraph(rels)

            tmp_graphs = {}
            tmp_lists = {}
            with ThreadPool() as p:
                for pair in data['graphs']:
                    for rel, graph in pair.items():
                        tmp_graphs[rel] = cls.load_part(graph, data_dir, p)

                for lst in data['list_names']:
                    tmp_lists[os.path.splitext(lst)[0]] = cls.load_part(lst, data_dir, p)


                data['graphs'] = resolve_dict_keys(tmp_graphs)
                data['lists'] = resolve_dict_keys(tmp_lists)

                graphs = []

                for relationship, graph in data['graphs'].items():
                    graphs.append(p.apply_async(graph_builder, args=[relationship, graph]))
                graphs = resolve_results(graphs)

            for relationship, graph in graphs:
                c.graphs[relationship] = graph

            c.make_lists(data['lists'].keys())

            for name, lst in data['lists'].items():
                c.extend_list(name, lst)

        return c

    @staticmethod
    def load_part(fn, data_dir, pool):
        graph = pool.apply_async(load_from_file,
                                 args=[os.path.join(data_dir, fn)])

        return graph

    def merge(self, g):
        for item in g.relationships:
            if item not in self.relationships:
                logger.warning('cannot merge dissimilar graphs: {0} is not in target graph'.format(item))
                raise GraphError

        self.make_lists(g.lists)

        for lst in g.lists:
            self.extend_list(lst, getattr(g, lst))

        self.uniquify_lists()

        for rel in g.relationship():
            for k,v in g.graphs[rel].items():
                self.graphs[rel].add(k, v)

    def fetch(self):
        o = {
             'main': {
                      'timestamp': datetime.datetime.utcnow().strftime("%s"),
                      'path': os.getcwd(),
                      'graphs': [],
                      'relationships': self.relationships,
                      'subset': self.subset,
                      'list_names': [],
                      'v': 2
                     }
        }

        for i in self.lists:
            o[i] = getattr(self, i)
            o['main']['list_names'].append('.'.join([i, 'json']))

        for i in self.relationships:
            o[i] = self.graphs[i].fetch()
            o['main']['graphs'].append({ i: '.'.join([i, 'json'])})

        return o

    def export(self, fn='.depgraph.json'):
        data_dir = os.path.dirname(fn)

        with Timer('constructing object for export', self.timer):
            o = self.fetch()

        with ThreadPool() as p:
            for k,v in o.items():
                if k == 'main':
                    part_fn = fn
                else:
                    part_fn = os.path.join(data_dir, '.'.join([k, 'json']))

                with Timer('writing file name ' + fn, self.timer):
                    p.apply_async(dump_to_file, args=[part_fn, v])

def dump_to_file(fn, data):
    with open(fn, 'w') as f:
        json.dump(data, f)

def load_from_file(fn):
    with open(fn, 'r') as f:
        return json.load(f)

class ResultsGraph(MultiGraph):
    def add(self, relationship, source, target, edge):
        if relationship in self.relationships:
            self.graphs[relationship].add(source, (target, edge))
        else:
            logger.debug('cannot add to non-extant relationship type ' + relationship)

    def narrow(self, item):
        graph = ResultsGraph(self.relationships)
        graph.subset = True

        if isinstance(item, list):
            for node in item:
                for i in self.relationships:
                    edges = self.graphs[i].get_endswith(node)[0]
                    for target, edge in edges:
                        graph.add(i, node, target, edge)
        else:
            for i in self.relationships:
                edges = self.graphs[i].get_endswith(item)[0]
                for target, edge in edges:
                    graph.add(item, node, target, edge)

        return graph

    def render(self):
        o = {}
        for i in self.relationships:
            o[i] = self.graphs[i].fetch()

        return o

class ResultsGraphD3(ResultsGraph):
    def render(self):
        output = { 'nodes': set(),
                   'edges': list() }

        for rel in self.relationships:
            output['nodes'].update(self.graphs[rel].keys())

            for source, target in self.graphs[rel].items():
                output['edges'].append( { 'to': target,
                                          'from': source,
                                          'relationship': rel } )

        output['nodes'] = list(output['nodes'])

        return output
