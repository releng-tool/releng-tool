# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.spdx import spdx_extract
from tests import RelengToolTestCase


class TestUtilSpdx(RelengToolTestCase):
    def test_utilspdx_extract(self):
        self.assertEqual(
            spdx_extract('BSD-3-Clause'),
            (True, {'BSD-3-Clause'}, set()))

        self.assertEqual(
            spdx_extract('LGPL-3.0-only'),
            (True, {'LGPL-3.0-only'}, set()))

        self.assertEqual(
            spdx_extract('NPL-1.0+'),
            (True, {'NPL-1.0'}, set()))

        self.assertEqual(
            spdx_extract('LGPL-2.1-only OR MIT'),
            (True, {'LGPL-2.1-only', 'MIT'}, set()))

        self.assertEqual(
            spdx_extract('LGPL-2.1-only AND MIT AND BSD-3-Clause'),
            (True, {'LGPL-2.1-only', 'MIT', 'BSD-3-Clause'}, set()))

        self.assertEqual(
            spdx_extract('GPL-2.0-or-later WITH Bison-exception-2.2'),
            (True, {'GPL-2.0-or-later'}, {'Bison-exception-2.2'}))

        self.assertEqual(
            spdx_extract('LGPL-2.0-only WITH Nokia-Qt-exception-1.1'),
            (True, {'LGPL-2.0-only'}, {'Nokia-Qt-exception-1.1'}))

        self.assertEqual(
            spdx_extract('GPL-3.0-only WITH GPL-3.0-linking-exception OR MIT'),
            (True, {'GPL-3.0-only', 'MIT'},
                {'GPL-3.0-linking-exception'}))

        self.assertEqual(
            spdx_extract('MIT AND (LGPL-2.1-or-later OR BSD-3-Clause)'),
            (True, {'MIT', 'LGPL-2.1-or-later', 'BSD-3-Clause'}, set()))

        self.assertEqual(
            spdx_extract('MIT AND'),
            (False, {'MIT'}, set()))

        self.assertEqual(
            spdx_extract('GPL-2.0-only WITH'),
            (False, {'GPL-2.0-only'}, set()))

        self.assertEqual(
            spdx_extract('My Custom License'),
            (True, {'My Custom License'}, set()))
