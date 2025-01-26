# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.spdx import ConjunctiveLicenses
from releng_tool.util.spdx import DisjunctiveLicenses
from releng_tool.util.spdx import spdx_parse
from tests import RelengToolTestCase


class TestSpdxLicenseParse(RelengToolTestCase):
    def test_spdx_license_parse_conjunctive(self):
        parts = spdx_parse('id1 AND id2')
        self.assertIsInstance(parts, ConjunctiveLicenses)
        self.assertListEqual(parts, ['id1', 'id2'])

        parts = spdx_parse('id5 AND id4 WITH e1 AND id3')
        self.assertIsInstance(parts, ConjunctiveLicenses)
        self.assertListEqual(parts, ['id5', 'id4 WITH e1', 'id3'])

        parts = spdx_parse('((id6) AND (id7))')
        self.assertIsInstance(parts, ConjunctiveLicenses)
        self.assertListEqual(parts, ['id6', 'id7'])

    def test_spdx_license_parse_disjunctive(self):
        parts = spdx_parse('id1 OR id2')
        self.assertIsInstance(parts, DisjunctiveLicenses)
        self.assertListEqual(parts, ['id1', 'id2'])

        parts = spdx_parse('id5 OR id4 WITH e1 OR id3')
        self.assertIsInstance(parts, DisjunctiveLicenses)
        self.assertListEqual(parts, ['id5', 'id4 WITH e1', 'id3'])

        parts = spdx_parse('((id6) OR (id7))')
        self.assertIsInstance(parts, DisjunctiveLicenses)
        self.assertListEqual(parts, ['id6', 'id7'])

    def test_spdx_license_parse_example(self):
        parts = spdx_parse('LGPL-2.1-only OR MIT OR BSD-3-Clause')
        self.assertIsInstance(parts, DisjunctiveLicenses)
        self.assertListEqual(parts, ['LGPL-2.1-only', 'MIT', 'BSD-3-Clause'])

        parts = spdx_parse('LGPL-2.1-only OR BSD-3-Clause AND MIT')
        self.assertIsInstance(parts, DisjunctiveLicenses)
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0], 'LGPL-2.1-only')
        self.assertIsInstance(parts[1], ConjunctiveLicenses)
        self.assertListEqual(parts[1], ['BSD-3-Clause', 'MIT'])

        parts = spdx_parse('MIT AND (LGPL-2.1-or-later OR BSD-3-Clause)')
        self.assertIsInstance(parts, ConjunctiveLicenses)
        self.assertEqual(len(parts), 2)
        self.assertEqual(parts[0], 'MIT')
        self.assertIsInstance(parts[1], DisjunctiveLicenses)
        self.assertListEqual(parts[1], ['LGPL-2.1-or-later', 'BSD-3-Clause'])

        parts = spdx_parse('GPL-2.0-or-later WITH Bison-exception-2.2')
        self.assertEqual(parts, 'GPL-2.0-or-later WITH Bison-exception-2.2')

    def test_spdx_license_parse_invalid(self):
        parts = spdx_parse('(INVALID')
        self.assertIsNone(parts)

        parts = spdx_parse('INVALID)')
        self.assertIsNone(parts)

        parts = spdx_parse('id1 AND')
        self.assertIsNone(parts)

        parts = spdx_parse('OR id2')
        self.assertIsNone(parts)

        parts = spdx_parse('(id3))')
        self.assertIsNone(parts)

    def test_spdx_license_parse_mixed(self):
        values = [
            'id1 AND id2 OR id3',
            ['id1 AND id2', 'id3'],
        ]
        for v in values:
            parts = spdx_parse(v)
            self.assertIsInstance(parts, DisjunctiveLicenses)
            self.assertEqual(len(parts), 2)
            self.assertIsInstance(parts[0], ConjunctiveLicenses)
            self.assertListEqual(parts[0], ['id1', 'id2'])
            self.assertEqual(parts[1], 'id3')

        values = [
            'id4 OR id5 AND id6',
            ['id4', 'id5 AND id6'],
        ]
        for v in values:
            parts = spdx_parse(v)
            self.assertIsInstance(parts, DisjunctiveLicenses)
            self.assertEqual(len(parts), 2)
            self.assertEqual(parts[0], 'id4')
            self.assertIsInstance(parts[1], ConjunctiveLicenses)
            self.assertListEqual(parts[1], ['id5', 'id6'])

        values = [
            '(id7 AND id8) OR id9',
            ['(id7 AND id8)', 'id9'],
        ]
        for v in values:
            parts = spdx_parse(v)
            self.assertIsInstance(parts, DisjunctiveLicenses)
            self.assertEqual(len(parts), 2)
            self.assertIsInstance(parts[0], ConjunctiveLicenses)
            self.assertListEqual(parts[0], ['id7', 'id8'])
            self.assertEqual(parts[1], 'id9')

        values = [
            'ida OR (idb AND idc)',
            ['ida', '(idb AND idc)'],
        ]
        for v in values:
            parts = spdx_parse(v)
            self.assertIsInstance(parts, DisjunctiveLicenses)
            self.assertEqual(len(parts), 2)
            self.assertEqual(parts[0], 'ida')
            self.assertIsInstance(parts[1], ConjunctiveLicenses)
            self.assertListEqual(parts[1], ['idb', 'idc'])

        values = [
            'ide AND (idf OR idg)',
            ('ide', 'idf OR idg'),
        ]
        for v in values:
            parts = spdx_parse(v)
            self.assertIsInstance(parts, ConjunctiveLicenses)
            self.assertEqual(len(parts), 2)
            self.assertEqual(parts[0], 'ide')
            self.assertIsInstance(parts[1], DisjunctiveLicenses)
            self.assertListEqual(parts[1], ['idf', 'idg'])

        values = [
            '(idh OR idi) AND idj',
            ('idh OR idi', 'idj'),
        ]
        for v in values:
            parts = spdx_parse(v)
            self.assertIsInstance(parts, ConjunctiveLicenses)
            self.assertEqual(len(parts), 2)
            self.assertIsInstance(parts[0], DisjunctiveLicenses)
            self.assertListEqual(parts[0], ['idh', 'idi'])
            self.assertEqual(parts[1], 'idj')

    def test_spdx_license_parse_single(self):
        parts = spdx_parse('id1')
        self.assertEqual(parts, 'id1')

        parts = spdx_parse('id1 WITH e1')
        self.assertEqual(parts, 'id1 WITH e1')
