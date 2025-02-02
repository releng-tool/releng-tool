# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests.support.python_tool_test import PythonSiteToolBase
import os
import unittest


class TestToolPythonHost(PythonSiteToolBase):
    @classmethod
    def setUpClass(cls):
        # support skipping the test for a distribution build
        if os.getenv('RELENG_SKIP_TEST_TOOL_PYTHON_HOST'):
            raise unittest.SkipTest('skipped due to environment flag')

    def tool_template(self):
        return 'python-host'

    def test_tool_python_host_custom_prefix(self):
        self.defconfig_add('PREFIX', '/my-custom/prefix')
        self.defconfig_add('PREFIX', '/my-custom/prefix', pkg_name='test2')

        rv = self.engine.run()
        self.assertTrue(rv)

    def test_tool_python_host_default_prefix(self):
        rv = self.engine.run()
        self.assertTrue(rv)

    def test_tool_python_host_empty_prefix(self):
        self.defconfig_add('PREFIX', '')
        self.defconfig_add('PREFIX', '', pkg_name='test2')

        rv = self.engine.run()
        self.assertTrue(rv)

    def test_tool_python_host_mixed_prefix(self):
        self.defconfig_add('PREFIX', '/custom-prefix')
        self.defconfig_add('PREFIX', '/some-other-prefix', pkg_name='test2')

        rv = self.engine.run()
        self.assertTrue(rv)
