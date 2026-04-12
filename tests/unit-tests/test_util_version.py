# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.version import str_to_version
from tests import RelengToolTestCase


class TestUtilVersion(RelengToolTestCase):
    def test_util_version(self):
        ver1 = str_to_version('1.0')
        ver2 = str_to_version('1.0')

        self.assertEqual(ver1, [1])
        self.assertEqual(ver2, [1])
        self.assertTrue(ver1 == ver2)

        ver1 = str_to_version('1.0.0')
        ver2 = str_to_version('1.0.0.0.0.0')

        self.assertEqual(ver1, [1])
        self.assertEqual(ver2, [1])
        self.assertTrue(ver1 == ver2)

        ver1 = str_to_version('1.1')
        ver2 = str_to_version('1.2')

        self.assertEqual(ver1, [1, 1])
        self.assertEqual(ver2, [1, 2])
        self.assertTrue(ver1 < ver2)

        ver1 = str_to_version('1.2.1')
        ver2 = str_to_version('1.2.0')
        self.assertEqual(ver1, [1, 2, 1])
        self.assertEqual(ver2, [1, 2])
        self.assertTrue(ver1 > ver2)

        ver1 = str_to_version('2')
        ver2 = str_to_version('3')
        self.assertEqual(ver1, [2])
        self.assertEqual(ver2, [3])
        self.assertTrue(ver1 < ver2)

        ver1 = str_to_version('2.4.5')
        ver2 = str_to_version('3')
        self.assertEqual(ver1, [2, 4, 5])
        self.assertEqual(ver2, [3])
        self.assertTrue(ver1 < ver2)

        ver1 = str_to_version('8')
        ver2 = str_to_version('9.0.2')
        self.assertEqual(ver1, [8])
        self.assertEqual(ver2, [9, 0, 2])
        self.assertTrue(ver1 < ver2)

        with self.assertRaises(ValueError):
            str_to_version('5.dev0')

        ver1 = str_to_version('5.dev0', relaxed=True)
        ver2 = str_to_version('5.dev1', relaxed=True)
        self.assertEqual(ver1, [5])
        self.assertEqual(ver2, [5])
        self.assertTrue(ver1 == ver2)

        ver1 = str_to_version('5')
        ver2 = str_to_version('5.dev0', relaxed=True)
        self.assertEqual(ver1, [5])
        self.assertEqual(ver2, [5])
        self.assertTrue(ver1 == ver2)
