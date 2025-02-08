# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests.support.site_tool_test import TestSiteToolBase
import platform
import os
import unittest


class TestToolMake(TestSiteToolBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        if platform.system() != 'Linux':
            raise unittest.SkipTest('make tool test skipped for non-Linux')

    def prepare_global_action(self):
        return None  # use releng-tool default

    def tool_template(self):
        return 'make'

    def test_tool_make_configure(self):
        self.defconfig_add('CONF_OPTS', ['configure'])

        rv = self.engine.run()
        self.assertTrue(rv)

        host_dir = os.path.join(self.engine.opts.host_dir)
        root_dir = os.path.join(self.engine.opts.root_dir)
        staging_dir = os.path.join(self.engine.opts.staging_dir)
        target_dir = os.path.join(self.engine.opts.target_dir)

        expected_exists = [
            os.path.join(root_dir, 'test-make-build'),
            os.path.join(root_dir, 'test-make-configure'),
            os.path.join(target_dir, 'test-make-install'),
        ]

        expected_missing = [
            os.path.join(host_dir, 'test-make-install'),
            os.path.join(staging_dir, 'test-make-install'),
        ]

        for expected in expected_exists:
            self.assertTrue(os.path.exists(expected), expected)

        for expected in expected_missing:
            self.assertFalse(os.path.exists(expected), expected)

    def test_tool_make_default(self):
        rv = self.engine.run()
        self.assertTrue(rv)

        host_dir = os.path.join(self.engine.opts.host_dir)
        root_dir = os.path.join(self.engine.opts.root_dir)
        staging_dir = os.path.join(self.engine.opts.staging_dir)
        target_dir = os.path.join(self.engine.opts.target_dir)

        expected_exists = [
            os.path.join(root_dir, 'test-make-build'),
            os.path.join(target_dir, 'test-make-install'),
        ]

        expected_missing = [
            os.path.join(host_dir, 'test-make-install'),
            os.path.join(root_dir, 'test-make-configure'),
            os.path.join(staging_dir, 'test-make-install'),
        ]

        for expected in expected_exists:
            self.assertTrue(os.path.exists(expected), expected)

        for expected in expected_missing:
            self.assertFalse(os.path.exists(expected), expected)

    def test_tool_make_host_configure(self):
        self.defconfig_add('CONF_OPTS', ['configure'])
        self.defconfig_add('INSTALL_TYPE', 'host')

        rv = self.engine.run()
        self.assertTrue(rv)

        host_dir = os.path.join(self.engine.opts.host_dir)
        root_dir = os.path.join(self.engine.opts.root_dir)
        staging_dir = os.path.join(self.engine.opts.staging_dir)
        target_dir = os.path.join(self.engine.opts.target_dir)

        expected_exists = [
            os.path.join(host_dir, 'test-make-install'),
            os.path.join(root_dir, 'test-make-build'),
            os.path.join(root_dir, 'test-make-configure'),
        ]

        expected_missing = [
            os.path.join(staging_dir, 'test-make-install'),
            os.path.join(target_dir, 'test-make-install'),
        ]

        for expected in expected_exists:
            self.assertTrue(os.path.exists(expected), expected)

        for expected in expected_missing:
            self.assertFalse(os.path.exists(expected), expected)

    def test_tool_make_host_default(self):
        self.defconfig_add('INSTALL_TYPE', 'host')

        rv = self.engine.run()
        self.assertTrue(rv)

        host_dir = os.path.join(self.engine.opts.host_dir)
        root_dir = os.path.join(self.engine.opts.root_dir)
        staging_dir = os.path.join(self.engine.opts.staging_dir)
        target_dir = os.path.join(self.engine.opts.target_dir)

        expected_exists = [
            os.path.join(host_dir, 'test-make-install'),
            os.path.join(root_dir, 'test-make-build'),
        ]

        expected_missing = [
            os.path.join(root_dir, 'test-make-configure'),
            os.path.join(staging_dir, 'test-make-install'),
            os.path.join(target_dir, 'test-make-install'),
        ]

        for expected in expected_exists:
            self.assertTrue(os.path.exists(expected), expected)

        for expected in expected_missing:
            self.assertFalse(os.path.exists(expected), expected)

    def test_tool_make_staging_configure(self):
        self.defconfig_add('CONF_OPTS', ['configure'])
        self.defconfig_add('INSTALL_TYPE', 'staging')

        rv = self.engine.run()
        self.assertTrue(rv)

        host_dir = os.path.join(self.engine.opts.host_dir)
        root_dir = os.path.join(self.engine.opts.root_dir)
        staging_dir = os.path.join(self.engine.opts.staging_dir)
        target_dir = os.path.join(self.engine.opts.target_dir)

        expected_exists = [
            os.path.join(root_dir, 'test-make-build'),
            os.path.join(root_dir, 'test-make-configure'),
            os.path.join(staging_dir, 'test-make-install'),
        ]

        expected_missing = [
            os.path.join(host_dir, 'test-make-install'),
            os.path.join(target_dir, 'test-make-install'),
        ]

        for expected in expected_exists:
            self.assertTrue(os.path.exists(expected), expected)

        for expected in expected_missing:
            self.assertFalse(os.path.exists(expected), expected)

    def test_tool_make_staging_default(self):
        self.defconfig_add('INSTALL_TYPE', 'staging')

        rv = self.engine.run()
        self.assertTrue(rv)

        host_dir = os.path.join(self.engine.opts.host_dir)
        root_dir = os.path.join(self.engine.opts.root_dir)
        staging_dir = os.path.join(self.engine.opts.staging_dir)
        target_dir = os.path.join(self.engine.opts.target_dir)

        expected_exists = [
            os.path.join(root_dir, 'test-make-build'),
            os.path.join(staging_dir, 'test-make-install'),
        ]

        expected_missing = [
            os.path.join(host_dir, 'test-make-install'),
            os.path.join(root_dir, 'test-make-configure'),
            os.path.join(target_dir, 'test-make-install'),
        ]

        for expected in expected_exists:
            self.assertTrue(os.path.exists(expected), expected)

        for expected in expected_missing:
            self.assertFalse(os.path.exists(expected), expected)

    def test_tool_make_staging_and_target_configure(self):
        self.defconfig_add('CONF_OPTS', ['configure'])
        self.defconfig_add('INSTALL_TYPE', 'staging_and_target')

        rv = self.engine.run()
        self.assertTrue(rv)

        host_dir = os.path.join(self.engine.opts.host_dir)
        root_dir = os.path.join(self.engine.opts.root_dir)
        staging_dir = os.path.join(self.engine.opts.staging_dir)
        target_dir = os.path.join(self.engine.opts.target_dir)

        expected_exists = [
            os.path.join(root_dir, 'test-make-build'),
            os.path.join(root_dir, 'test-make-configure'),
            os.path.join(staging_dir, 'test-make-install'),
            os.path.join(target_dir, 'test-make-install'),
        ]

        expected_missing = [
            os.path.join(host_dir, 'test-make-install'),
        ]

        for expected in expected_exists:
            self.assertTrue(os.path.exists(expected), expected)

        for expected in expected_missing:
            self.assertFalse(os.path.exists(expected), expected)

    def test_tool_make_staging_and_target_default(self):
        self.defconfig_add('INSTALL_TYPE', 'staging_and_target')

        rv = self.engine.run()
        self.assertTrue(rv)

        host_dir = os.path.join(self.engine.opts.host_dir)
        root_dir = os.path.join(self.engine.opts.root_dir)
        staging_dir = os.path.join(self.engine.opts.staging_dir)
        target_dir = os.path.join(self.engine.opts.target_dir)

        expected_exists = [
            os.path.join(root_dir, 'test-make-build'),
            os.path.join(staging_dir, 'test-make-install'),
            os.path.join(target_dir, 'test-make-install'),
        ]

        expected_missing = [
            os.path.join(host_dir, 'test-make-build'),
            os.path.join(host_dir, 'test-make-install'),
            os.path.join(root_dir, 'test-make-configure'),
        ]

        for expected in expected_exists:
            self.assertTrue(os.path.exists(expected), expected)

        for expected in expected_missing:
            self.assertFalse(os.path.exists(expected), expected)

    def test_tool_make_noinstall_configure(self):
        self.defconfig_add('CONF_OPTS', ['configure'])
        self.defconfig_add('MAKE_NOINSTALL', value=True)

        rv = self.engine.run()
        self.assertTrue(rv)

        host_dir = os.path.join(self.engine.opts.host_dir)
        root_dir = os.path.join(self.engine.opts.root_dir)
        staging_dir = os.path.join(self.engine.opts.staging_dir)
        target_dir = os.path.join(self.engine.opts.target_dir)

        expected_exists = [
            os.path.join(root_dir, 'test-make-build'),
            os.path.join(root_dir, 'test-make-configure'),
        ]

        expected_missing = [
            os.path.join(host_dir, 'test-make-install'),
            os.path.join(staging_dir, 'test-make-install'),
            os.path.join(target_dir, 'test-make-install'),
        ]

        for expected in expected_exists:
            self.assertTrue(os.path.exists(expected), expected)

        for expected in expected_missing:
            self.assertFalse(os.path.exists(expected), expected)

    def test_tool_make_noinstall_default(self):
        self.defconfig_add('MAKE_NOINSTALL', value=True)

        rv = self.engine.run()
        self.assertTrue(rv)

        host_dir = os.path.join(self.engine.opts.host_dir)
        root_dir = os.path.join(self.engine.opts.root_dir)
        staging_dir = os.path.join(self.engine.opts.staging_dir)
        target_dir = os.path.join(self.engine.opts.target_dir)

        expected_exists = [
            os.path.join(root_dir, 'test-make-build'),
        ]

        expected_missing = [
            os.path.join(host_dir, 'test-make-install'),
            os.path.join(root_dir, 'test-make-configure'),
            os.path.join(staging_dir, 'test-make-install'),
            os.path.join(target_dir, 'test-make-install'),
        ]

        for expected in expected_exists:
            self.assertTrue(os.path.exists(expected), expected)

        for expected in expected_missing:
            self.assertFalse(os.path.exists(expected), expected)
