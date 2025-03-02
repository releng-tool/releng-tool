# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.io import execute
from releng_tool.util.io_touch import touch
from releng_tool.util.io_wd import wd
from tests.support.site_tool_test import TestSiteToolBase
import os


DEFAULT_BRANCH = 'default'


class TestToolMercurial(TestSiteToolBase):
    def prepare_defconfig(self, defconfig):
        self.defconfig_add('VCS_TYPE', 'hg')

    def prepare_repo_dir(self, repo_dir):
        self._hg_repo('init', repo_dir)
        self._create_commit('initial commit', repo=repo_dir, fresh=True)

    def test_tool_mercurial_basic_branch(self):
        self.defconfig_add('VERSION', DEFAULT_BRANCH)
        rv = self.engine.run()
        self.assertTrue(rv)

    def test_tool_mercurial_basic_commit(self):
        hash_ = self._create_commit()
        self.defconfig_add('VERSION', hash_)
        rv = self.engine.run()
        self.assertTrue(rv)

    def test_tool_mercurial_basic_tag(self):
        tag, _ = self._create_tag('my-tag')
        self.defconfig_add('VERSION', tag)
        rv = self.engine.run()
        self.assertTrue(rv)

    def test_tool_mercurial_branch_forward_slash(self):
        # create a commit on a new branch with a forward slash
        TMP_BRANCH = 'container/test'
        self._hg_repo('branch', TMP_BRANCH)
        self._create_commit()
        self._hg_repo('update', DEFAULT_BRANCH)

        self.defconfig_add('VERSION', TMP_BRANCH)
        rv = self.engine.run()
        self.assertTrue(rv)

    def test_tool_mercurial_changing_revision(self):
        # verify pulling from an original tag
        touch(os.path.join(self.repo_dir, 'first'))
        self._create_commit('first commit', add=True)
        first_tag, first_tag_hash = self._create_tag('first')

        self.defconfig_add('VERSION', first_tag)
        rv = self.engine.run()
        self.assertTrue(rv)

        current_hash = self._hg_tip_id()
        self.assertEqual(current_hash, first_tag_hash)

        build_out = self.build_dir_prefix + '-first'
        file_check = os.path.join(build_out, 'first')
        self.assertTrue(os.path.exists(file_check))

        # cleanup
        self.cleanup_outdir()

        # create a new remote revision, update the target and see if it uses the
        # newer tag
        touch(os.path.join(self.repo_dir, 'second'))
        self._create_commit('second commit', add=True)
        second_tag, second_tag_hash = self._create_tag('second')

        self.defconfig_add('VERSION', second_tag)
        rv = self.engine.run()
        self.assertTrue(rv)

        current_hash = self._hg_tip_id()
        self.assertEqual(current_hash, second_tag_hash)

        build_out = self.build_dir_prefix + '-second'
        file_check = os.path.join(build_out, 'first')
        self.assertTrue(os.path.exists(file_check))
        file_check = os.path.join(build_out, 'second')
        self.assertTrue(os.path.exists(file_check))

        # cleanup
        self.cleanup_outdir()

        # update the package definition to use the older tag and see if we can
        # still load the older tag properly
        self.defconfig_add('VERSION', first_tag)
        rv = self.engine.run()
        self.assertTrue(rv)

        build_out = self.build_dir_prefix + '-first'
        file_check = os.path.join(build_out, 'first')
        self.assertTrue(os.path.exists(file_check))
        file_check = os.path.join(build_out, 'second')
        self.assertFalse(os.path.exists(file_check))

    def test_tool_mercurial_unknown_branch_tag(self):
        self.defconfig_add('VERSION', 'unknown')
        rv = self.engine.run()
        self.assertFalse(rv)

    def test_tool_mercurial_unknown_revision(self):
        self.defconfig_add('VERSION', '12345')
        rv = self.engine.run()
        self.assertFalse(rv)

    def _hg(self, workdir, *args):
        with wd(workdir):
            out = []
            if not execute(['hg', '--noninteractive', *list(args)],
                    capture=out, critical=False):
                print(['(TestToolMercurial) hg', *list(args)])
                print('\n'.join(out))
                raise AssertionError('failed to issue hg command')
            return '\n'.join(out)

    def _hg_repo(self, *args, **kwargs):
        repo = kwargs.get('repo')
        if not repo:
            repo = self.repo_dir
        return self._hg(repo, *args)

    def _hg_tip_id(self):
        return self._hg_repo('identify', '--id', '--rev', 'tip', self.cache_dir)

    def _create_commit(self, msg='test', **kwargs):
        repo = kwargs.get('repo')

        if kwargs.get('fresh'):
            # Mercurial requires some content on new repos; add a dummy file
            # for new repositories.
            touch(os.path.join(repo if repo else self.repo_dir, 'dummy'))
            self._hg_repo('add', '.', repo=repo)
            self._hg_repo('commit', '-m', msg, repo=repo)
        elif kwargs.get('add'):
            self._hg_repo('add', '.', repo=repo)
            self._hg_repo('commit', '-m', msg, repo=repo)
        else:
            # Mercurial does not have empty commits; instead, force build a
            # tag to make a new commit.
            dummy_id = getattr(self, '_hg_tmpid', 1)
            dummy_id += 1
            self._id = dummy_id
            dummy_tag = f'dummy-{dummy_id}'
            self._hg_repo('tag', dummy_tag, '-f', '-m', msg, repo=repo)

        return self._hg_repo('identify', '--id', repo=repo)

    def _create_tag(self, tag, repo=None):
        self._hg_repo('tag', tag, repo=repo)
        return tag, self._hg_repo('identify', '--id', repo=repo)

    def _delete_tag(self, tag, repo=None):
        self._hg_repo('tag', '--remove', tag, repo=repo)
