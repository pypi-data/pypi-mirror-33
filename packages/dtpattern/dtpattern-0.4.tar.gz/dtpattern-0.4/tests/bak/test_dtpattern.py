# -*- coding: utf-8 -*-

import unittest
import sys

from dtpattern.dtpattern import pattern, aggregate_group_of_same_symbols
from tests.bak.value_lists import same_length_numbers, same_length_lowercase, same_length_uppercase, var_length_numbers, \
    var_length_lowercase
from tests.bak.value_pattern_types_list import random_number, random_date, random_time, random_iso8601, \
    random_lowercase_string, random_word, random_words




##basic straight forward aggregation
test_cols_aggregated=[
    (random_number(10,digits=1, fix_len=True), '1'),
    (random_number(10,digits=2, fix_len=True), '11'),
    (random_number(10,digits=3, fix_len=True), '111'),
    (random_number(10,digits=5, fix_len=True), '11111'),
    ( random_number(2,digits=1, fix_len=True)+random_number(2,digits=2, fix_len=True), '01'),
    (random_date(5), '1111-11-11'),
    (random_time(5), '11:11:11'),
    (random_iso8601(5), '1111-11-11C11:11:11'),
    (random_lowercase_string(10, length=5),'ccccc'),
    (random_lowercase_string(5, length=5)+random_lowercase_string(5, length=3),'aaccc'),
    (random_word(10,length=5),'Ccccc'),
    (random_word(5,length=5)+random_word(5,length=3),'Caacc'),
    (random_words(10,length=[5,3]),'Ccccc Ccc'),
    (random_words(5,length=[5,3])+random_words(5,length=[3,5]),'Caacc Caacc'),

]

#This cases are not that straight forward
test_cols_aggregated_complex=[
    ( [u'-1']+random_number(5,digits=1, fix_len=True), '[-]1'), # sometimes numbers contain a minus
    ( [u'-1',u'+1']+random_number(5,digits=1, fix_len=True), '[-/+]1')
]


class TestFormatEncoder(unittest.TestCase):
    def setUp(self):
        self.f = pattern
        print(same_length_numbers)

    @for_examples(same_length_numbers)
    def test_basic(self, x, y):
        res=self.f(values=x)
        self.assertEqual(res[0][0], y)
        self.assertEqual(res[0][1], len(x))

    @for_examples(test_cols_aggregated_complex)
    def test_complex(self, x, y):
        res = self.f(values=x)
        self.assertEqual(res[0][0], y)
        self.assertEqual(res[0][1], len(x))

class FixLengthSameSymbolTest(unittest.TestCase):

    def _tester(self,input_tests,prefix):
        for i,t in enumerate(input_tests):
            with self.subTest(i=i):
                print("{}{} {} -> {}".format(prefix,i,t[0],t[1]))
                input=t[0]
                res = pattern(values=input)
                self.assertEqual(res[0][0], t[1])
                self.assertEqual(res[0][1], len(input))

    def test_numbers(self):
        self._tester(same_length_numbers, 'N')

    def test_lower(self):
        self._tester(same_length_lowercase, 'L')

    def test_upper(self):
        self._tester(same_length_uppercase,'U')

class VarLengthSameSymbolTest(unittest.TestCase):

    def _tester(self,input_tests,prefix):
        for i,t in enumerate(input_tests):
            with self.subTest(i=i):
                print("{}{} {} -> {}".format(prefix,i,t[0],t[1]))
                input=t[0]
                res = pattern(values=input)
                self.assertEqual(res[0][0], t[1])
                self.assertEqual(res[0][1], len(input))

    def test_numbers(self):
        self._tester(var_length_numbers, 'N')

    def test_lower(self):
        self._tester(var_length_lowercase, 'L')

    #def test_upper(self):
    #    self._tester(var_length_uppercase,'U')



if __name__ == '__main__':
    unittest.main()
