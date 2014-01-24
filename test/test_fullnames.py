from unittest import TestCase
from dict_compare import dict_compare
from helpers import get_test_graph

from willitlink.queries.find_interface import find_interface
from willitlink.queries.fullnames import expand_file_names, expand_symbol_names

class TestInterfaceQuery(TestCase):
    @classmethod
    def setUp(self):
        self.graph = get_test_graph()

    def test_get_full_filenames(self):
        expected = [
                "provides_strlen_needs_memcmp.o",
                "provides_malloc_needs_memcmp.o",
                "provides_free_needs_memcmp.o",
                "provides_memcmp.o",
                ]
        self.assertTrue(dict_compare(expected, expand_file_names(self.graph, "memcmp.o"), reporter=self.fail))

    def test_get_full_symbol_names(self):
        expected = [
                "strlen",
                "strcpy",
                ]
        self.assertTrue(dict_compare(expected, expand_symbol_names(self.graph, "str"), reporter=self.fail))
