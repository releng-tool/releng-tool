# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests.support.site_tool_test import TestSiteToolBase
import os
import sys
import unittest

# xmake template has two projects -- helpers to find the "lib" package
LIBPKG_DEFDIR = os.path.join('package', 'lib')
LIBPKG_DEFINITION = os.path.join(LIBPKG_DEFDIR, 'lib.rt')


class TestToolXmake(TestSiteToolBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.filename = 'releng-tool-test'
        if sys.platform == 'win32':
            cls.filename += '.exe'

        # skip xmake tests when running windows in a mingw shell, since:
        #  - xmake will try to only detect mingw over visual studio installs
        #  - even when forcing for `-p windows`, xmake may report visual
        #     studios is not there, even if visual studio environment variables
        #     have already be loaded in the shell
        if sys.platform == 'win32' and 'MSYSTEM' in os.environ:
            raise unittest.SkipTest('xmake tool test skipped for non-Linux')

    def prepare_global_action(self):
        return None  # use releng-tool default

    def tool_template(self):
        return 'xmake'

    def test_tool_xmake_default(self):
        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.staging_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertFalse(os.path.exists(executable), executable)

        bin_dir = os.path.join(self.engine.opts.target_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable), executable)

    def test_tool_xmake_host(self):
        self._update_install_type('host')

        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.host_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable), executable)

    def test_tool_xmake_staging_only(self):
        self._update_install_type('staging')

        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.staging_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable), executable)

        bin_dir = os.path.join(self.engine.opts.target_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertFalse(os.path.exists(executable), executable)

    def test_tool_xmake_staging_and_target(self):
        self._update_install_type('staging_and_target')

        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.staging_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable), executable)

        bin_dir = os.path.join(self.engine.opts.target_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable), executable)

    def test_tool_xmake_noinstall(self):
        self.defconfig_add('XMAKE_NOINSTALL', value=True)

        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.target_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertFalse(os.path.exists(executable), executable)

    def _prefix(self):
        prefix = os.path.join(self.engine.opts.sysroot_prefix, 'bin')
        if not prefix.startswith(os.sep):
            prefix = os.sep + prefix
        return prefix

    def _update_install_type(self, install_type):
        self.defconfig_add('INSTALL_TYPE', install_type)

        defconfig = os.path.join(self.engine.opts.root_dir, LIBPKG_DEFINITION)
        self.assertTrue(os.path.exists(defconfig), defconfig)
        self.defconfig_add('INSTALL_TYPE', install_type,
            defconfig=defconfig, pkg_name='lib')
