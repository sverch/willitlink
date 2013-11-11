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

logger = logging.getLogger(__name__)

class Graph(object):
    def __init__(self, base=None):
        if base is None:
            self.graph = dict()
        else:
            self.graph = base

    def add(self, item, deps):
        if isinstance(item, list):
            print item
            return

        if item not in self.graph:
            self.graph[item] = set()

        if isinstance(deps, list):
            for dep in deps:
                self.graph[item].add(dep)
        else:
            self.graph[item].add(deps)

    def get(self, item):
        return list(self.graph[item])

    def get_startswith(self, name):
        r = list()
        for i in self.graph.keys():
            if i.startswith(name):
                r = self.get(i)
        return r

    def get_endswith(self, name):
        r = list()
        for i in self.graph.keys():
            if i.endswith(name):
                r = self.get(i)
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
            r[k] = self.get(k)
        return r

class MultiGraph(object):
    def __init__(self, relationships=None):
        if relationships is None:
            self.relationships = []
        else:
            self.relationships = relationships

        self.graphs = self.new_graph()
        self.subset = False
        self.has_lists = False
        self.lists = []

    def make_lists(self, lists):
        self.lists.extend(lists)

        for l in lists:
            if not hasattr(self, l):
                setattr(self, l, list())

        self.has_lists = True

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

    def resolve(self, item):
        o = dict()
        for i in self.relationships:
            o[i] = self.graphs[i].get(item)

        return o

    def narrow(self, item):
        graph = MultiGraph()
        graph.subset = True

        for i in self.relationships:
            graph.add(i, item, self.graphs[i].get(item))

        return graph

    def slice(self, relationship):
        return self.graphs[relationship].fetch()

    @classmethod
    def load(cls, fn):
        if not os.path.exists(fn):
            logger.debug('cannot load from non existing file {0} please rebuild'.format(fn))
            return False

        with open(fn, 'r') as f:
            data = json.load(f)

            rels = data['relationships']

            c = MultiGraph(rels)

            for relationship, graph in data['graphs'].items():
                c.graphs[relationship] = Graph(graph)

            return c

    def fetch(self):
        o = {
            'timestamp': datetime.datetime.utcnow().strftime("%s"),
            'path': os.getcwd(),
            'relationships': self.relationships,
            'graphs': {},
            'subset': self.subset
            }

        for i in self.relationships:
            o['graphs'][i] = self.graphs[i].fetch()

        return o

    def export(self, fn='.depgraph.json'):
        o = self.fetch()

        with open(fn, 'w') as f:
            json.dump(o, f)
