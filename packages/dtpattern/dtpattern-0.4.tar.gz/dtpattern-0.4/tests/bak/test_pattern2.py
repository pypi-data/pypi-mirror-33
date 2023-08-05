import unittest
from dtpattern.dtpattern2 import pattern
import sys

from tests import for_examples

same_length_numbers  =[
    (['123','123'], "123"),
    (['123','124'], "'12'd"),
    (['123','456'], "ddd"),
    ]

class TestOneGroup(unittest.TestCase):
    def setUp(self):
        self.f = pattern
        print(same_length_numbers)

    @for_examples(same_length_numbers)
    def test_basic(self, x, y):
        res = self.f(x, max_groups=1)
        self.assertEqual(res[0][0], y)
        self.assertEqual(res[0][1], len(x))
