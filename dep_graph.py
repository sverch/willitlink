"""
A simple (prototype) graph modeling toolkit/API for simple dependency analysis. Internally

Use:

- To create a new graph object, adds a few items, to the graph and then dumps
  the graph to a json file to persist state to disk and avoid over generation:

     tracked_relationships = [ 'files2cows', 'cows2people' ]

     g = DependencyGraph(tracked_relationships)

     g.add('files2cows', 'a.out', ['bessie', 'hef'])
     g.add('files2cows', 'a.out', 'elsa')

     g.add('cows2people', 'bessie', ['shaun', 'tycho'])
     g.add('cows2people', 'elsa', 'jason')

     g.export('files2people.json')

- To create an equivalent ``g`` object from the ``file2people.json``
  dump to recover a previous state:

     g = DependencyGraph().load('files2people.json')

- To return a standard directed graph for a single relationship, for integration
  with external graph analysis libraries:

     g.slice('cows2people')

- To return a list of dependencies, in a dict that maps ``{ relationship:
  dependencies}`` for item ``bessie``:

     g.resolve('bessie')

- To return a DependencyGraph object that contains *only* the relationships for
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
    def __init__(self):
        self.graph = dict()

    def add(item, deps):
        if item not in self.graph:
            self.graph[item] = set()

        if isinstance(deps, list):
            for dep in deps:
                self.graph[item].add(dep)
        else:
            self.graph[item].add(dep)

    def get(item):
        return list(self.graph[item])

    def fetch():
        return self.graph

class DependencyGraph(object):
    def __init__(self, relationships):
        self.relationships = relationships
        self.graphs = self.new_graph()
        self.subset = False

    def new_graph(self):
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
            self.graphs[relationship].get(item)
        else:
            logger.debug('cannot fetch non-extant relationship type ' + relationship)

    def resolve(self, item):
        o = dict()
        for i in self.relationships:
            o[i] = self.graphs[i].get(item)

        return o

    def narrow(self, item)
        graph = DependencyGraph()
        grap.subset = True

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

            c = cls(rels)
            c.subset = data['subset']

            for relationship, graph in data['graphs'].items():
                c[relationship] = graph

            return c

    def export(self, fn='.depgraph.json'):
        o = {
            'timestamp': datetime.datetime.utcnow().strftime("%s"),
            'path' os.getcwd(),
            'relationships': self.relationships
            'graphs': {},
            'subset': self.subset
            }

        for i in self.relationships:
            o['graphs'][i] = self.graphs[i]

        with open(fn, 'w') as f:
            json.dump(o, f)
