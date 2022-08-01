# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

from tests.support.site_tool_test import TestSiteToolBase
import os
import sys

class TestToolCmake(TestSiteToolBase):
    @classmethod
    def setUpClass(cls):
        cls.filename = 'testapp'
        if sys.platform == 'win32':
            cls.filename += '.exe'

    def prepare_global_action(self):
        return None # use releng-tool default

    def tool_template(self):
        return 'cmake'

    def test_tool_cmake_default(self):
        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.staging_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertFalse(os.path.exists(executable))

        bin_dir = os.path.join(self.engine.opts.target_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable))

    def test_tool_cmake_host(self):
        self.defconfig_add('INSTALL_TYPE', 'host')

        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.host_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable))

    def test_tool_cmake_staging(self):
        self.defconfig_add('INSTALL_TYPE', 'staging')

        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.staging_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable))

        bin_dir = os.path.join(self.engine.opts.target_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertFalse(os.path.exists(executable))

    def test_tool_cmake_staging_and_target(self):
        self.defconfig_add('INSTALL_TYPE', 'staging_and_target')

        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.staging_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable))

        bin_dir = os.path.join(self.engine.opts.target_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable))

    def test_tool_cmake_noinstall(self):
        self.defconfig_add('CMAKE_NOINSTALL', True)

        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.target_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertFalse(os.path.exists(executable))

    def _prefix(self):
        prefix = os.path.join(self.engine.opts.sysroot_prefix, 'bin')
        if not prefix.startswith(os.sep):
            prefix = os.sep + prefix
        return prefix
