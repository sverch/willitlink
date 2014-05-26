# Module to read and write YAML files but still preserve the order Usage should be exactly the same
# as using yaml directly, except the "load" function overrides the "Loader" keyword argument.  This
# is kind of a hack, but exists because the current yaml library does not support OrderedDict
# objects.

import yaml

try:
    # included in standard lib from Python 2.7
    from collections import OrderedDict
except ImportError:
    # try importing the backported drop-in replacement
    # it's available on PyPI
    from ordereddict import OrderedDict

# This allows us to dump an OrderedDict with yaml.dump
def dump_anydict_as_map(anydict):
    yaml.add_representer(anydict, _represent_dictorder)
def _represent_dictorder( self, data):
    return self.represent_mapping('tag:yaml.org,2002:map', data.items() )
dump_anydict_as_map(OrderedDict)

# This allows us to load an OrderedDict with yaml.load
import yaml.constructor

class OrderedDictYAMLLoader(yaml.Loader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError, exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping',
                    node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

def load(*args, **kwargs):
    kwargs['Loader'] = OrderedDictYAMLLoader
    res = yaml.load(*args, **kwargs)
    return res

def dump(*args, **kwargs):
    return yaml.dump(*args, **kwargs)
