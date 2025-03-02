# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.io import execute
from releng_tool.util.io_temp_dir import temp_dir
from tests.support.site_tool_test import TestSiteToolBase
import os
import time


DEFAULT_MODULE = 'test'


class TestToolCvs(TestSiteToolBase):
    def prepare_defconfig(self, defconfig):
        self.defconfig_add('VCS_TYPE', 'cvs')
        self.defconfig_add('REVISION', 'HEAD')
        self.defconfig_add('SITE', self.repo_dir + ' ' + DEFAULT_MODULE)

    def prepare_repo_dir(self, repo_dir):
        self._cvs_repo('init')

    def test_tool_cvs_basic_default(self):
        # register some new files
        self._cvs_add(DEFAULT_MODULE, 'file1', 2)
        self._cvs_add(DEFAULT_MODULE, 'file2', 3)

        # run the engine (to checkout sources)
        rv = self.engine.run()
        self.assertTrue(rv)

        # verify expected content
        out_dir = os.path.join(self.engine.opts.build_dir, DEFAULT_MODULE)
        repo1_file = os.path.join(out_dir, 'file1')
        repo2_file = os.path.join(out_dir, 'file2')
        self.assertTrue(os.path.exists(repo1_file))
        self.assertTrue(os.path.exists(repo2_file))

        self._assertFileContains(repo1_file, 'commit 2')
        self._assertFileContains(repo2_file, 'commit 3')

    def test_tool_cvs_basic_revision(self):
        # register some new files, and tag along the way
        self._cvs_add(DEFAULT_MODULE, 'file1')
        self._cvs_tag(DEFAULT_MODULE, 'tag-1')

        self._cvs_add(DEFAULT_MODULE, 'file2')
        self._cvs_tag(DEFAULT_MODULE, 'tag-2')

        self._cvs_add(DEFAULT_MODULE, 'file3')
        self._cvs_tag(DEFAULT_MODULE, 'tag-3')

        # configure for the target revision we want
        self.defconfig_add('REVISION', 'tag-2')

        # run the engine (to checkout sources)
        rv = self.engine.run()
        self.assertTrue(rv)

        # verify expected content
        out_dir = os.path.join(self.engine.opts.build_dir, DEFAULT_MODULE)
        repo1_file = os.path.join(out_dir, 'file1')
        repo2_file = os.path.join(out_dir, 'file2')
        repo3_file = os.path.join(out_dir, 'file3')
        self.assertTrue(os.path.exists(repo1_file))
        self.assertTrue(os.path.exists(repo2_file))
        self.assertFalse(os.path.exists(repo3_file))

    def test_tool_cvs_malformed_site(self):
        self.defconfig_add('SITE', self.repo_dir)  # missing module
        rv = self.engine.run()
        self.assertFalse(rv)

    def test_tool_cvs_missing_module(self):
        self.defconfig_add('SITE', self.repo_dir + ' unknown')
        rv = self.engine.run()
        self.assertFalse(rv)

    def test_tool_cvs_unknown_revision(self):
        self.defconfig_add('VERSION', 'unknown')
        rv = self.engine.run()
        self.assertFalse(rv)

    def _cvs(self, *args):
        out = []
        if not execute(['cvs', *list(args)], capture=out, critical=False):
            print(['(TestToolCvs) cvs', *list(args)])
            print('\n'.join(out))
            raise AssertionError('failed to issue cvs command')
        return '\n'.join(out)

    def _cvs_repo(self, *args, **kwargs):
        repo = kwargs.get('repo')
        if not repo:
            repo = self.repo_dir

        # configure CVSROOT to the repository
        new_args = ('-d', repo, *args)

        return self._cvs(*new_args)

    def _cvs_add(self, module, filename, total=1):
        with temp_dir(wd=True):
            self._cvs_repo('checkout', '.')

            # build a module (if not yet created)
            if not os.path.exists(module):
                os.mkdir(module)
                self._cvs_repo('add', module)

            # add a new change/commit to the file
            target_file = os.path.join(module, filename)
            for n in range(1, total + 1):
                # wait a moment per commit, since committing in less than
                # second intervals can lead to unexpected results where a cvs
                # client may not think the file has been updated since last
                # commit (so it wont make a new commit entry)
                if n > 1:
                    time.sleep(1)

                with open(target_file, 'w') as f:
                    f.write(f'commit {n}\n')

                # first time writing to this file, register it
                if n == 1:
                    self._cvs_repo('add', target_file)
                self._cvs_repo('commit', '-m', f'adding commit {n}')

    def _cvs_remove(self, module, filename):
        with temp_dir(wd=True):
            self._cvs_repo('checkout', '.')

            target_file = os.path.join(module, filename)
            os.remove(target_file)
            self._cvs_repo('remove', target_file)
            self._cvs_repo('commit', '-m', 'removing file')

    def _cvs_tag(self, module, tag):
        self._cvs_repo('rtag', tag, module)

    def _assertFileContains(self, path, contents):
        with open(path) as f:
            data = f.read().strip()

        msg = f'found `{data}` instead of `{contents}`'
        self.assertIn(contents, data, msg)
