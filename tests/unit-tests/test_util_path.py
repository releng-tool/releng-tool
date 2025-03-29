# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.util.path import P
from tests import RelengToolTestCase


class TestUtilPath(RelengToolTestCase):
    def test_util_path(self):
        self.assertEqual(P('a'), 'a')
        self.assertEqual(P('b'), Path('b'))
        self.assertEqual(P('c') / 'd', 'c/d')
        self.assertEqual(P('e') / 'f', Path('e') / 'f')
        self.assertEqual(P('g') + '-suffix', 'g-suffix')
        self.assertEqual('prefix-' + P('h'), 'prefix-h')
        self.assertEqual(P('..'), '..')
        self.assertEqual(P('..'), Path('..'))
