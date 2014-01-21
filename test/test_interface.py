from unittest import TestCase
from dict_compare import dict_compare
from helpers import get_test_graph

from willitlink.queries.find_interface import find_interface

class TestInterfaceQuery(TestCase):
    @classmethod
    def setUp(self):
        self.graph = get_test_graph()

    def test_interface(self):
        # wil.py --data test/data interface libmemory.a
        expected = [
                {
                    "used_by": [
                        "provides_strcpy_needs_memcmp_malloc_free.o"
                        ],
                    "object": "provides_malloc_needs_memcmp.o",
                    "archive": "libmemory.a",
                    "symbol": "malloc"
                    },
                {
                    "used_by": [
                        "provides_strcpy_needs_memcmp_malloc_free.o"
                        ],
                    "object": "provides_free_needs_memcmp.o",
                    "archive": "libmemory.a",
                    "symbol": "free"
                    }
                ]
        self.assertTrue(dict_compare(expected, find_interface(self.graph, "libmemory.a"), reporter=self.fail))
