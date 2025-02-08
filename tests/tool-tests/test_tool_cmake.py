# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests.support.site_tool_test import TestSiteToolBase
import os
import sys

# cmake template has two projects -- helpers to find the "lib" package
LIBPKG_DEFDIR = os.path.join('package', 'lib')
LIBPKG_DEFINITION = os.path.join(LIBPKG_DEFDIR, 'lib.rt')


class TestToolCmake(TestSiteToolBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.filename = 'testapp'
        if sys.platform == 'win32':
            cls.filename += '.exe'

    def prepare_global_action(self):
        return None  # use releng-tool default

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
        self._update_install_type('host')

        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.host_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable))

    def test_tool_cmake_staging_only(self):
        self._update_install_type('staging')

        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.staging_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable))

        bin_dir = os.path.join(self.engine.opts.target_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertFalse(os.path.exists(executable))

    def test_tool_cmake_staging_and_target(self):
        self._update_install_type('staging_and_target')

        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.staging_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable))

        bin_dir = os.path.join(self.engine.opts.target_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable))

    def test_tool_cmake_noinstall(self):
        self.defconfig_add('CMAKE_NOINSTALL', value=True)

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

    def _update_install_type(self, install_type):
        self.defconfig_add('INSTALL_TYPE', install_type)

        defconfig = os.path.join(self.engine.opts.root_dir, LIBPKG_DEFINITION)
        self.assertTrue(os.path.exists(defconfig))
        self.defconfig_add('INSTALL_TYPE', install_type,
            defconfig=defconfig, pkg_name='lib')
