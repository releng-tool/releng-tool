# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.support import releng_include
from tests import RelengToolTestCase
from tests.support import fetch_unittest_assets_dir
import os


class TestSupport(RelengToolTestCase):
    @classmethod
    def setUpClass(cls):
        assets_dir = Path(fetch_unittest_assets_dir())
        cls.includes = assets_dir / 'includes'
        cls.assertTrue(cls.includes.exists(), 'missing includes directory')

    def test_support_include_default(self):
        test_include = self.includes / 'sample-include.rt'
        self.assertTrue(test_include.exists(), 'missing include file')
        releng_include(test_include)

        # verify variables are not sourced
        with self.assertRaises(NameError):
            print(SAMPLE_INCLUDE)  # noqa: F821  pylint: disable=E0602

    def test_support_include_expanded(self):
        test_include = self.includes / 'sample-include.rt'
        self.assertTrue(test_include.exists(), 'missing include file')

        os.environ['MYFILE'] = 'sample-include'
        test_include_str = f'{test_include.parent}/${{MYFILE}}.rt'
        releng_include(test_include_str)

    def test_support_include_fail(self):
        test_include = self.includes / 'fail-include.rt'
        self.assertTrue(test_include.exists(), 'missing include file')
        with self.assertRaises(SystemExit):
            releng_include(test_include)

    def test_support_include_sourced(self):
        test_include = self.includes / 'sample-include.rt'
        self.assertTrue(test_include.exists(), 'missing include file')
        releng_include(test_include, source=True)

        # verify variables are sourced
        print(SAMPLE_INCLUDE)  # noqa: F821  pylint: disable=E0602
