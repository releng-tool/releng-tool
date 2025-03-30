# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.gpg import GPG
from releng_tool.util.io_temp_dir import temp_dir
from tests.support import fetch_unittest_assets_dir
from tests.support.site_tool_test import TestSiteToolBase
import os
import sys


class TestToolGpg(TestSiteToolBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        sample_files = fetch_unittest_assets_dir('sample-files')
        cls.archive = os.path.join(sample_files, 'sample-files.tar')

    def prepare_defconfig(self, defconfig):
        self.defconfig_add('SITE', f'file://{self.archive}')
        self.asc_file = os.path.join(self.def_dir, self.pkg_name + '.asc')

    def test_tool_gpg_invalid(self):
        with open(self.asc_file, 'w') as f:
            f.write('dummy data\n')

        rv = self.engine.run()
        self.assertFalse(rv)

    def test_tool_gpg_missing_ignore(self):
        self.assertFalse(os.path.exists(self.asc_file))
        rv = self.engine.run()
        self.assertTrue(rv)

    def test_tool_gpg_valid(self):
        # export GNUPGHOME=$(pwd)/home
        # gpg --batch --passphrase '' --quick-gen-key \
        #  gpg-key-test@releng.io default default
        # gpg --armor --detach-sign test.txt
        # gpg --verify test.txt.asc test.txt

        # NOTE: there is some trickery here to have this unit test be flexible
        # for Windows -- while we want to set `GNUPGHOME` to a random
        # temporary directory to hold dummy test keys (to verify
        # against), gpg-agent (which is required) does not support colon
        # characters, causing a failure when launching on Windows:
        #
        #    ':' are not allowed in the socket name
        #
        # This is not observed in MinGW/cygwin because of its alternative root
        # paths (e.g. `/c/` over `C:\`). However, we can configure `GNUPGHOME`
        # to a relative path which allows the agent to start (to allow key
        # generation and verification). The trick here lies with a combination
        # of using the engine's `out_dir` as the base of a temporary GPG
        # playground -- specifically, since all fetch operations are performed
        # in temporary folders based off the configured output directory. By
        # specifying `GNUPGHOME` as a parent directory, both the GPG key
        # generation and signature generation from the unit test, and the GPG
        # verification request (inside the releng-tool engine) will share the
        # same home directory.
        if sys.platform == 'win32':
            with temp_dir(self.engine.opts.out_dir, wd=True) as gpg_tmp:
                os.environ['GNUPGHOME'] = '..'
                self._test_tool_gpg_valid()
        else:
            # NOTE: osx will fail to implicitly start gpg-agent if the
            # temporary directory is too long
            with temp_dir(wd=True) as gpg_tmp:
                os.environ['GNUPGHOME'] = gpg_tmp
                self._test_tool_gpg_valid()

    def _test_tool_gpg_valid(self):
        rv, out = GPG.execute_rv('--verbose', '--batch', '--passphrase', '',
            '--quick-gen-key', 'gpg-key-test@releng.io',
            'default', 'default')
        self.assertEqual(rv, 0, out)

        rv, out = GPG.execute_rv('--armor', '--detach-sign', '--batch',
            '--output', self.asc_file, self.archive)
        self.assertEqual(rv, 0, out)

        rv = self.engine.run()
        self.assertTrue(rv)
