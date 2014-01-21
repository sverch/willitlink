from unittest import TestCase
from dict_compare import dict_compare
from helpers import get_test_graph

from willitlink.queries.libstats import resolve_leak_info

class TestLeaksQueries(TestCase):
    @classmethod
    def setUp(self):
        self.graph = get_test_graph()

    def test_leaks(self):
        # wil.py --data test/data tree --leak provides_strcpy_needs_memcmp_malloc_free.o --source_names provides_free_needs_memcmp.o
        expected = [
                {
                    "sources": {
                        "libutil.a": {
                            "provides_memcmp.o": {}
                            }
                        },
                    "symbol": "memcmp",
                    "object": "provides_strcpy_needs_memcmp_malloc_free.o"
                    },
                {
                    "sources": {
                        "libmemory.a": {
                            "provides_malloc_needs_memcmp.o": {}
                            }
                        },
                    "symbol": "malloc",
                    "object": "provides_strcpy_needs_memcmp_malloc_free.o"
                    }
                ]
        result = resolve_leak_info(self.graph, "provides_strcpy_needs_memcmp_malloc_free.o", 2, True, "provides_free_needs_memcmp.o")
        self.assertTrue(dict_compare(expected, result, reporter=self.fail))
