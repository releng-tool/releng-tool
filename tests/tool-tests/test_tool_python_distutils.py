# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests.support.python_tool_test import PythonSiteToolBase
import os
import sys
import unittest


class TestToolPythonDistutils(PythonSiteToolBase):
    @classmethod
    def setUpClass(cls):
        # support skipping the test for a distribution build
        if os.getenv('RELENG_SKIP_TEST_TOOL_PYTHON_DISTUTILS'):
            raise unittest.SkipTest('skipped due to environment flag')

        # distutils is no longer available in Python 3.12+
        if sys.version_info >= (3, 12):
            raise unittest.SkipTest('unsupported interpreter')

    def tool_template(self):
        return 'python-distutils'

    def test_tool_python_distutils_default(self):
        rv = self.engine.run()
        self.assertTrue(rv)

        site_packages = self.find_site_packages(self.engine.opts.host_dir)
        self.assertIsNone(site_packages)

        site_packages = self.find_site_packages(self.engine.opts.staging_dir)
        self.assertIsNone(site_packages)

        site_packages = self.find_site_packages(self.engine.opts.target_dir)
        self.assertIsNotNone(site_packages)
        self.assertPythonModuleExists(site_packages, 'hello_module')

    def test_tool_python_distutils_host(self):
        self.defconfig_add('INSTALL_TYPE', 'host')

        rv = self.engine.run()
        self.assertTrue(rv)

        site_packages = self.find_site_packages(self.engine.opts.host_dir)
        self.assertIsNotNone(site_packages)
        self.assertPythonModuleExists(site_packages, 'hello_module')

        site_packages = self.find_site_packages(self.engine.opts.staging_dir)
        self.assertIsNone(site_packages)

        site_packages = self.find_site_packages(self.engine.opts.target_dir)
        self.assertIsNone(site_packages)

    def test_tool_python_distutils_staging(self):
        self.defconfig_add('INSTALL_TYPE', 'staging')

        rv = self.engine.run()
        self.assertTrue(rv)

        site_packages = self.find_site_packages(self.engine.opts.host_dir)
        self.assertIsNone(site_packages)

        site_packages = self.find_site_packages(self.engine.opts.staging_dir)
        self.assertIsNotNone(site_packages)
        self.assertPythonModuleExists(site_packages, 'hello_module')

        site_packages = self.find_site_packages(self.engine.opts.target_dir)
        self.assertIsNone(site_packages)

    def test_tool_python_distutils_staging_and_target(self):
        self.defconfig_add('INSTALL_TYPE', 'staging_and_target')

        rv = self.engine.run()
        self.assertTrue(rv)

        site_packages = self.find_site_packages(self.engine.opts.host_dir)
        self.assertIsNone(site_packages)

        site_packages = self.find_site_packages(self.engine.opts.staging_dir)
        self.assertIsNotNone(site_packages)
        self.assertPythonModuleExists(site_packages, 'hello_module')

        site_packages = self.find_site_packages(self.engine.opts.target_dir)
        self.assertIsNotNone(site_packages)
        self.assertPythonModuleExists(site_packages, 'hello_module')
