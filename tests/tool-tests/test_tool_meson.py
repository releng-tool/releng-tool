# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests.support.site_tool_test import TestSiteToolBase
import os
import platform
import sys
import unittest

# template has two projects -- helpers to find the "lib" package
LIBPKG_DEFDIR = os.path.join('package', 'lib')
LIBPKG_DEFINITION = os.path.join(LIBPKG_DEFDIR, 'lib.rt')


class TestToolMeson(TestSiteToolBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # while in theory a Meson build could work in Windows, it appears that
        # issuing install requests to a Windows setup/built project can fail
        # since the generated targets are looking for library files which are
        # not created (e.g. trying to install `foo.lib` instead of `libfoo.a`)
        if platform.system() != 'Linux':
            raise unittest.SkipTest('meson tool test skipped for non-Linux')

        cls.filename = 'testapp'
        if sys.platform == 'win32':
            cls.filename += '.exe'

    def prepare_global_action(self):
        return None  # use releng-tool default

    def tool_template(self):
        return 'meson'

    def test_tool_meson_default(self):
        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.staging_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertFalse(os.path.exists(executable))

        bin_dir = os.path.join(self.engine.opts.target_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable))

    def test_tool_meson_host(self):
        self._update_install_type('host')

        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.host_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable))

    def test_tool_meson_staging(self):
        self._update_install_type('staging')

        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.staging_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable))

        bin_dir = os.path.join(self.engine.opts.target_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertFalse(os.path.exists(executable))

    def test_tool_meson_staging_and_target(self):
        self._update_install_type('staging_and_target')

        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.staging_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable))

        bin_dir = os.path.join(self.engine.opts.target_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertTrue(os.path.exists(executable))

    def test_tool_meson_noinstall(self):
        self.defconfig_add('MESON_NOINSTALL', value=True)

        rv = self.engine.run()
        self.assertTrue(rv)

        bin_dir = os.path.join(self.engine.opts.target_dir + self._prefix())
        executable = os.path.join(bin_dir, self.filename)
        self.assertFalse(os.path.exists(executable))

    def _update_install_type(self, install_type):
        self.defconfig_add('INSTALL_TYPE', install_type)

        defconfig = os.path.join(self.engine.opts.root_dir, LIBPKG_DEFINITION)
        self.defconfig_add('INSTALL_TYPE', install_type,
            defconfig=defconfig, pkg_name='lib')

    def _prefix(self):
        prefix = os.path.join(self.engine.opts.sysroot_prefix, 'bin')
        if not prefix.startswith(os.sep):
            prefix = os.sep + prefix
        return prefix
