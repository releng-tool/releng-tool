# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from tests.support.python_tool_test import PythonSiteToolBase
import sys
import unittest


class TestToolPythonPoetry(PythonSiteToolBase):
    @classmethod
    def setUpClass(cls):
        # installer is only available in Python 3.7+
        if sys.version_info < (3, 7):
            raise unittest.SkipTest('unsupported interpreter')

    def tool_template(self):
        return 'python-poetry'

    def test_tool_python_poetry_default(self):
        rv = self.engine.run()
        self.assertTrue(rv)

        site_packages = self.find_site_packages(self.engine.opts.host_dir)
        self.assertIsNone(site_packages)

        site_packages = self.find_site_packages(self.engine.opts.staging_dir)
        self.assertIsNone(site_packages)

        site_packages = self.find_site_packages(self.engine.opts.target_dir)
        self.assertIsNotNone(site_packages)
        self.assertPythonModuleExists(site_packages, 'hello_module')

    def test_tool_python_poetry_host(self):
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

    def test_tool_python_poetry_staging(self):
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

    def test_tool_python_poetry_staging_and_target(self):
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
