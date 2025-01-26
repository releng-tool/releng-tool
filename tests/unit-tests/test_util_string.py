# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.string import expand
from releng_tool.util.string import interpret_strings
import os
import unittest


class TestUtilStrings(unittest.TestCase):
    def test_utilstr_expand(self):
        def assertExpand(self, obj, result, kv=None):
            self.assertEqual(expand(obj, kv), result)

        val = expand(None)
        self.assertIsNone(val)

        assertExpand(self, '', '')
        assertExpand(self,
            'this is a simple message', 'this is a simple message')

        os.environ['__RELENGTEST'] = 'test'
        assertExpand(self, '$__RELENGTEST', 'test')
        assertExpand(self, 'A $__RELENGTEST Z', 'A test Z')
        assertExpand(self, 'A $__RELENGTEST$__RELENGTEST Z', 'A testtest Z')
        assertExpand(self, 'longer $__RELENGTEST string', 'longer test string')
        assertExpand(self, 'a/$__RELENGTEST/b', 'a/test/b')
        assertExpand(self, 'a-$__RELENGTEST-b', 'a-test-b')
        assertExpand(self, ' $__RELENGTEST ', ' test ')
        assertExpand(self, '${__RELENGTEST}', 'test')
        assertExpand(self, 'A${__RELENGTEST}Z', 'AtestZ')
        assertExpand(self, 'A${__RELENGTEST}${__RELENGTEST}Z', 'AtesttestZ')
        assertExpand(self,
            'longer ${__RELENGTEST} string', 'longer test string')
        assertExpand(self, ' ${__RELENGTEST} ', ' test ')
        assertExpand(self, '${invalid', '${invalid')
        assertExpand(self, '${}ignored', 'ignored')
        assertExpand(self, '$$escaped', '$escaped')
        assertExpand(self, '${__RELENGTEST}', 'override',
            kv={'__RELENGTEST': 'override'})
        assertExpand(self, ['a', 'b', 'c'], ['a', 'b', 'c'])
        assertExpand(self,
            ['${__RELENGTEST}', 'b', '${__RELENGTEST}'], ['test', 'b', 'test'])
        assertExpand(self, {'a', 'b', 'c'}, {'a', 'b', 'c'})
        assertExpand(self, {'a', '${__RELENGTEST}', 'c'}, {'a', 'test', 'c'})
        assertExpand(self, {'key': 'value'}, {'key': 'value'})
        assertExpand(self,
            {'${__RELENGTEST}': '${__RELENGTEST}'}, {'test': 'test'})

        os.environ.pop('__RELENGTEST', None)
        assertExpand(self, '$__RELENGTEST', '')

    def test_utilstr_interpretstrings(self):
        val = interpret_strings(None)
        self.assertIsNone(val)

        # string returns a list with the single string
        val = interpret_strings('this is a string')
        self.assertEqual(val, ['this is a string'])

        # list returns same list
        val = interpret_strings(['a', 'b'])
        self.assertEqual(val, ['a', 'b'])

        # set returns same set
        val = interpret_strings(('a', 'b'))
        self.assertEqual(val, ('a', 'b'))

        # empty list returns same list
        val = interpret_strings([])
        self.assertEqual(val, [])

        # empty set returns same set
        val = interpret_strings(())
        self.assertEqual(val, ())

        # bad entry returns none
        val = interpret_strings(['a', None])
        self.assertIsNone(val)
