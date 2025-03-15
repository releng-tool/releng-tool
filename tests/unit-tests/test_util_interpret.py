# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.defs import VOID
from releng_tool.util.interpret import interpret_dict
from releng_tool.util.interpret import interpret_opts
from releng_tool.util.interpret import interpret_seq
from tests import RelengToolTestCase


class TestUtilInterpret(RelengToolTestCase):
    def test_utilinterpret_dict(self):
        val = interpret_dict(None, str)
        self.assertIsNone(val)

        # empty dict returns same dict
        test_dict = {}
        val = interpret_dict(test_dict, str)
        self.assertEqual(val, {})
        self.assertIs(val, test_dict)

        # valid dict returns same dict
        test_dict = {'a': 'b', 'c': 'd'}
        val = interpret_dict(test_dict, str)
        self.assertEqual(val, {'a': 'b', 'c': 'd'})
        self.assertIs(val, test_dict)

        # dict with a none entry is desired ("unconfigure case")
        test_dict = {'a': None}
        val = interpret_dict(test_dict, str)
        self.assertEqual(val, {'a': None})
        self.assertIs(val, test_dict)

        # check with another type
        test_dict = {'a': Path('b')}
        val = interpret_dict(test_dict, Path)
        self.assertEqual(val, {'a': Path('b')})
        self.assertIs(val, test_dict)

        # check with mixing types
        test_dict = {'a': 'b', 'c': Path('d')}
        val = interpret_dict(test_dict, (Path, str))
        self.assertEqual(val, {'a': 'b', 'c': Path('d')})
        self.assertIs(val, test_dict)

        # string should return none
        val = interpret_dict('this is a string', str)
        self.assertIsNone(val)

        # list should return none
        val = interpret_dict(['a', 'b'], str)
        self.assertIsNone(val)

        # tuple should return none
        val = interpret_dict(('a', 'b'), str)
        self.assertIsNone(val)

        # bad entry returns none
        val = interpret_dict({'a': 123}, str)
        self.assertIsNone(val)

    def test_utilinterpret_opts(self):
        val = interpret_opts(None, str)
        self.assertIsNone(val)

        # empty dict returns same dict
        test_dict = {}
        val = interpret_opts(test_dict, str)
        self.assertEqual(val, {})
        self.assertIs(val, test_dict)

        # valid dict returns same dict
        test_dict = {'a': 'b', 'c': 'd'}
        val = interpret_opts(test_dict, str)
        self.assertEqual(val, {'a': 'b', 'c': 'd'})
        self.assertIs(val, test_dict)

        # dict with a none entry is desired ("unconfigure case")
        test_dict = {'a': None}
        val = interpret_opts(test_dict, str)
        self.assertEqual(val, {'a': None})
        self.assertIs(val, test_dict)
        self.assertIsNone(val['a'])

        # list should return dict with expected keys and empty values
        val = interpret_opts(['a', 'b'], str)
        self.assertEqual(val, {'a': VOID, 'b': VOID})
        self.assertIsNotNone(val['a'])
        self.assertFalse(val['a'])

        # tuple should return dict with expected keys and empty values
        val = interpret_opts(('a', 'b'), str)
        self.assertEqual(val, {'a': VOID, 'b': VOID})

        # string should return dict with expected key and empty value
        val = interpret_opts('c', str)
        self.assertEqual(val, {'c': VOID})

        # check with another type
        test_dict = {'a': Path('b')}
        val = interpret_opts(test_dict, Path)
        self.assertEqual(val, {'a': Path('b')})
        self.assertIs(val, test_dict)

        # check with mixing types
        test_dict = {'a': 'b', 'c': Path('d')}
        val = interpret_opts(test_dict, (Path, str))
        self.assertEqual(val, {'a': 'b', 'c': Path('d')})
        self.assertIs(val, test_dict)

        # bad dict entry returns none
        val = interpret_opts({'a': 123}, str)
        self.assertIsNone(val)

        # bad sequence entry returns none
        val = interpret_opts([123], str)
        self.assertIsNone(val)

    def test_utilinterpret_seq(self):
        val = interpret_seq(None, str)
        self.assertIsNone(val)

        # string returns a list with the single string
        val = interpret_seq('this is a string', str)
        self.assertEqual(val, ['this is a string'])

        # list returns same list
        test_list = ['a', 'b']
        val = interpret_seq(test_list, str)
        self.assertEqual(val, ['a', 'b'])
        self.assertIs(val, test_list)

        # tuple returns same tuple
        test_tuple = ('a', 'b')
        val = interpret_seq(test_tuple, str)
        self.assertEqual(val, ('a', 'b'))
        self.assertIs(val, test_tuple)

        # empty list returns same list
        test_list = []
        val = interpret_seq(test_list, str)
        self.assertEqual(val, [])
        self.assertIs(val, test_list)

        # empty tuple returns same tuple
        test_tuple = ()
        val = interpret_seq(test_tuple, str)
        self.assertEqual(val, ())
        self.assertIs(val, test_tuple)

        # check with another type
        test_list = [Path('a'), Path('b')]
        val = interpret_seq(test_list, Path)
        self.assertEqual(val, [Path('a'), Path('b')])
        self.assertIs(val, test_list)

        # check with mixing types
        test_list = ['a', Path('b')]
        val = interpret_seq(test_list, (Path, str))
        self.assertEqual(val, ['a', Path('b')])
        self.assertIs(val, test_list)

        # bad entry returns none
        val = interpret_seq(['a', None], str)
        self.assertIsNone(val)
