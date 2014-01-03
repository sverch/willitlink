from unittest import TestCase
from dict_compare import dict_compare

class TestWilFunctionality(TestCase):
    @classmethod
    def setUp(self):
        self.

    def test_easy(self):
        self.assertTrue(dict_compare({}, {}))

    def test_hard(self):
        # TODO: actually test the basic relationships
        self.assertTrue(dict_compare({ "a" : [ { "b" : 1 }, { "c" : 1 } ] }, { "a" : [ { "c" : 1 }, { "b" : 1 } ] }, reporter=self.fail))
