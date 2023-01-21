# -*- coding: utf-8 -*-
# Copyright 2023-2023 releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.util.spdx import spdx_extract
import unittest


class TestUtilSpdx(unittest.TestCase):
    def test_utilspdx_extract(self):
        self.assertEqual(
            spdx_extract('BSD-3-Clause'),
            (True, set(['BSD-3-Clause']), set()))

        self.assertEqual(
            spdx_extract('LGPL-3.0-only'),
            (True, set(['LGPL-3.0-only']), set()))

        self.assertEqual(
            spdx_extract('NPL-1.0+'),
            (True, set(['NPL-1.0']), set()))

        self.assertEqual(
            spdx_extract('LGPL-2.1-only OR MIT'),
            (True, set(['LGPL-2.1-only', 'MIT']), set()))

        self.assertEqual(
            spdx_extract('LGPL-2.1-only AND MIT AND BSD-3-Clause'),
            (True, set(['LGPL-2.1-only', 'MIT', 'BSD-3-Clause']), set()))

        self.assertEqual(
            spdx_extract('GPL-2.0-or-later WITH Bison-exception-2.2'),
            (True, set(['GPL-2.0-or-later']), set(['Bison-exception-2.2'])))

        self.assertEqual(
            spdx_extract('LGPL-2.0-only WITH Nokia-Qt-exception-1.1'),
            (True, set(['LGPL-2.0-only']), set(['Nokia-Qt-exception-1.1'])))

        self.assertEqual(
            spdx_extract('GPL-3.0-only WITH GPL-3.0-linking-exception OR MIT'),
            (True, set(['GPL-3.0-only', 'MIT']),
                set(['GPL-3.0-linking-exception'])))

        self.assertEqual(
            spdx_extract('MIT AND (LGPL-2.1-or-later OR BSD-3-Clause)'),
            (True, set(['MIT', 'LGPL-2.1-or-later', 'BSD-3-Clause']), set()))

        self.assertEqual(
            spdx_extract('MIT AND'),
            (False, set(['MIT']), set()))

        self.assertEqual(
            spdx_extract('GPL-2.0-only WITH'),
            (False, set(['GPL-2.0-only']), set()))
