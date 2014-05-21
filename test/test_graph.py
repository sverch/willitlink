from unittest import TestCase
from dict_compare import dict_compare
import helpers

from willitlink.queries.find_interface import find_interface

class TestInterfaceQuery(TestCase):
    @classmethod
    def setUp(self):
        self.graph = helpers.get_test_graph()

    def test_extra_info(self):
        extra_info = {"data":["arbitrary data, possibly version information"]}
        self.graph.set_extra_info(extra_info)
        helpers.export_temporary_test_graph(self.graph)
        temporary_graph = helpers.load_temporary_test_graph()
        helpers.cleanup_temporary_test_graph()
        round_trip_extra_info = temporary_graph.get_extra_info()
        self.assertTrue(dict_compare(round_trip_extra_info, extra_info, reporter=self.fail))
