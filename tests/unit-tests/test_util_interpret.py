# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.interpret import interpret_dict_strs
from releng_tool.util.interpret import interpret_strs
from releng_tool.util.interpret import interpret_zero_to_one_strs
from tests import RelengToolTestCase


class TestUtilInterpret(RelengToolTestCase):
    def test_utilinterpret_dict_strs(self):
        val = interpret_dict_strs(None)
        self.assertIsNone(val)

        # empty dict returns same dict
        val = interpret_dict_strs({})
        self.assertEqual(val, {})

        # valid dict returns same dict
        val = interpret_dict_strs({'a': 'b', 'c': 'd'})
        self.assertEqual(val, {'a': 'b', 'c': 'd'})

        # dict with a none entry is desired ("unconfigure case")
        val = interpret_dict_strs({'a': None})
        self.assertEqual(val, {'a': None})

        # string should return none
        val = interpret_dict_strs('this is a string')
        self.assertIsNone(val)

        # list should return none
        val = interpret_dict_strs(['a', 'b'])
        self.assertIsNone(val)

        # tuple should return none
        val = interpret_dict_strs(('a', 'b'))
        self.assertIsNone(val)

        # bad entry returns none
        val = interpret_dict_strs({'a': 123})
        self.assertIsNone(val)

    def test_utilinterpret_strs(self):
        val = interpret_strs(None)
        self.assertIsNone(val)

        # string returns a list with the single string
        val = interpret_strs('this is a string')
        self.assertEqual(val, ['this is a string'])

        # list returns same list
        val = interpret_strs(['a', 'b'])
        self.assertEqual(val, ['a', 'b'])

        # tuple returns same tuple
        val = interpret_strs(('a', 'b'))
        self.assertEqual(val, ('a', 'b'))

        # empty list returns same list
        val = interpret_strs([])
        self.assertEqual(val, [])

        # empty tuple returns same tuple
        val = interpret_strs(())
        self.assertEqual(val, ())

        # bad entry returns none
        val = interpret_strs(['a', None])
        self.assertIsNone(val)

    def test_utilinterpret_z2o_strs(self):
        val = interpret_zero_to_one_strs(None)
        self.assertIsNone(val)

        # empty dict returns same dict
        val = interpret_zero_to_one_strs({})
        self.assertEqual(val, {})

        # valid dict returns same dict
        val = interpret_zero_to_one_strs({'a': 'b', 'c': 'd'})
        self.assertEqual(val, {'a': 'b', 'c': 'd'})

        # dict with a none entry is desired ("unconfigure case")
        val = interpret_zero_to_one_strs({'a': None})
        self.assertEqual(val, {'a': None})

        # list should return dict with expected keys and empty values
        val = interpret_zero_to_one_strs(['a', 'b'])
        self.assertEqual(val, {'a': '', 'b': ''})

        # tuple should return dict with expected keys and empty values
        val = interpret_zero_to_one_strs(('a', 'b'))
        self.assertEqual(val, {'a': '', 'b': ''})

        # string should return dict with expected key and empty value
        val = interpret_zero_to_one_strs('c')
        self.assertEqual(val, {'c': ''})

        # bad dict entry returns none
        val = interpret_zero_to_one_strs({'a': 123})
        self.assertIsNone(val)

        # bad sequence entry returns none
        val = interpret_zero_to_one_strs([123])
        self.assertIsNone(val)
