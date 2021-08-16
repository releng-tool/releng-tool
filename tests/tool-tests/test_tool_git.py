# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

from releng_tool.defs import GlobalAction
from releng_tool.util.io import execute
from releng_tool.util.io import interim_working_dir
from tests.support.site_tool_test import TestSiteToolBase

DEFAULT_BRANCH = 'test'

class TestToolGit(TestSiteToolBase):
    def prepare_defconfig(self, defconfig):
        self.defconfig_add('VCS_TYPE', 'git')

    def prepare_repo_dir(self, repo_dir):
        self._git_repo('init', repo_dir, '--initial-branch=' + DEFAULT_BRANCH)
        self._git_repo('config', 'user.email', 'unit-test@releng.io')
        self._git_repo('config', 'user.name', 'Unit Test')
        self._create_commit('initial commit')

    def test_tool_git_basic_branch(self):
        self.defconfig_add('VERSION', DEFAULT_BRANCH)
        rv = self.engine.run()
        self.assertTrue(rv)

    def test_tool_git_basic_commit(self):
        hash = self._create_commit()
        self.defconfig_add('VERSION', hash)
        rv = self.engine.run()
        self.assertTrue(rv)

    def test_tool_git_basic_tag(self):
        tag = self._create_tag('my-tag')
        self.defconfig_add('VERSION', tag)
        rv = self.engine.run()
        self.assertTrue(rv)

    def test_tool_git_changing_revision(self):
        # verify pulling from an original tag
        first_hash = self._create_commit('first commit')
        first_tag = self._create_tag('first')

        self.defconfig_add('VERSION', first_tag)
        rv = self.engine.run()
        self.assertTrue(rv)

        current_hash = self._git_cache('rev-parse', 'HEAD')
        self.assertEqual(current_hash, first_hash)

        # cleanup
        self.cleanup_outdir()

        # create a new remote revision, update the target and see if it uses the
        # newer tag
        second_hash = self._create_commit('second commit')
        second_tag = self._create_tag('second')

        self.defconfig_add('VERSION', second_tag)
        rv = self.engine.run()
        self.assertTrue(rv)

        # cleanup
        self.cleanup_outdir()

        # update the package definition to use the older tag and see if we can
        # still load the older tag properly
        current_hash = self._git_cache('rev-parse', 'HEAD')
        self.assertEqual(current_hash, second_hash)

        self.defconfig_add('VERSION', first_tag)
        rv = self.engine.run()
        self.assertTrue(rv)

        current_hash = self._git_cache('rev-parse', 'HEAD')
        self.assertEqual(current_hash, first_hash)

    def test_tool_git_custom_options(self):
        MY_CUSTOM_CFG = 'tmp.example'
        MY_CUSTOM_CFG_VALUE = 'my-value'

        self.defconfig_add('GIT_CONFIG', {
            MY_CUSTOM_CFG: MY_CUSTOM_CFG_VALUE,
        })
        self.defconfig_add('VERSION', DEFAULT_BRANCH)
        rv = self.engine.run()
        self.assertTrue(rv)

        fetched_cfg = self._git_cache('config', '--get', MY_CUSTOM_CFG)
        self.assertEqual(fetched_cfg, MY_CUSTOM_CFG_VALUE)

    def test_tool_git_custom_reference(self):
        # create a commit on a new custom reference
        TMP_BRANCH = 'tmp'
        self._git_repo('checkout', '-b', TMP_BRANCH)
        hash = self._create_commit()
        self._git_repo('update-ref', 'refs/mycustomref/test', hash)
        self._git_repo('checkout', DEFAULT_BRANCH)
        self._git_repo('branch', '-D', TMP_BRANCH)

        # first fetch attempt should fail since the custom reference will not be
        # fetched by default
        self.defconfig_add('VERSION', hash)
        rv = self.engine.run()
        self.assertFalse(rv)

        # add the new custom reference to the configuration and re-fetch
        self.defconfig_add('GIT_REFSPECS', ['mycustomref/*'])
        rv = self.engine.run()
        self.assertTrue(rv)

    def test_tool_git_depth_shallow_default(self):
        self._create_commit()
        hash = self._create_commit()
        self.defconfig_add('VERSION', hash)

        rv = self.engine.run()
        self.assertTrue(rv)

        rev_count = self._git_cache('rev-list', '--count', 'HEAD')
        self.assertEqual(int(rev_count), 1)

    def test_tool_git_depth_shallow_disabled_config(self):
        self._create_commit()
        hash = self._create_commit()
        self.defconfig_add('GIT_DEPTH', 0)
        self.defconfig_add('VERSION', hash)

        rv = self.engine.run()
        self.assertTrue(rv)

        rev_count = self._git_cache('rev-list', '--count', 'HEAD')
        self.assertNotEqual(int(rev_count), 1)

    def test_tool_git_depth_shallow_disabled_quirk(self):
        self.engine.opts.quirks.append('releng.git.no_depth')

        self._create_commit()
        hash = self._create_commit()
        self.defconfig_add('VERSION', hash)

        rv = self.engine.run()
        self.assertTrue(rv)

        rev_count = self._git_cache('rev-list', '--count', 'HEAD')
        self.assertNotEqual(int(rev_count), 1)

    def test_tool_git_depth_unshallow_initial(self):
        hash = self._create_commit()
        self._create_commit()
        self.defconfig_add('VERSION', hash)

        rv = self.engine.run()
        self.assertTrue(rv)

        rev_count = self._git_cache('rev-list', '--count', 'HEAD')
        self.assertNotEqual(int(rev_count), 1)

    def test_tool_git_depth_unshallow_updated(self):
        self._create_commit()
        commit_a = self._create_commit()
        commit_b = self._create_commit()
        self.defconfig_add('VERSION', commit_b)

        # the engine run should fetch a single commit
        rv = self.engine.run()
        self.assertTrue(rv)

        current_hash = self._git_cache('rev-parse', 'HEAD')
        self.assertEqual(current_hash, commit_b)
        rev_count = self._git_cache('rev-list', '--count', 'HEAD')
        self.assertEqual(int(rev_count), 1)

        # cleanup
        self.cleanup_outdir()

        # update to a older commit, check if the engine fetch will unshallow the
        # currently shallow state cache
        self.defconfig_add('VERSION', commit_a)

        rv = self.engine.run()
        self.assertTrue(rv)

        current_hash = self._git_cache('rev-parse', 'HEAD')
        self.assertEqual(current_hash, commit_a)
        rev_count = self._git_cache('rev-list', '--count', 'HEAD')
        self.assertNotEqual(int(rev_count), 1)

    def test_tool_git_diverged_branch(self):
        # create a new branch with a commit
        TARGET_BRANCH = 'target'
        self._git_repo('checkout', '-b', TARGET_BRANCH)
        first_hash = self._create_commit('first')

        # fetch the target
        self.defconfig_add('VERSION', TARGET_BRANCH)
        rv = self.engine.run()
        self.assertTrue(rv)

        current_hash = self._git_cache('rev-parse', 'HEAD')
        self.assertEqual(current_hash, first_hash)

        # cleanup
        self.cleanup_outdir()

        # destroy the old branch and build a new one with the same name
        self._git_repo('checkout', DEFAULT_BRANCH)
        self._git_repo('branch', '-D', TARGET_BRANCH)
        self._git_repo('checkout', '-b', TARGET_BRANCH)
        second_hash = self._create_commit('second')

        # force a fetch (which should update the cache)
        self.engine.opts.gbl_action = GlobalAction.FETCH
        rv = self.engine.run()
        self.assertTrue(rv)

        # fetch/extract the new target
        self.engine.opts.gbl_action = GlobalAction.EXTRACT
        rv = self.engine.run()
        self.assertTrue(rv)

        current_hash = self._git_cache('rev-parse', 'HEAD')
        self.assertEqual(current_hash, second_hash)

    def test_tool_git_remote_tag_change(self):
        tag_name = 'my-tag'

        first_hash = self._create_commit('first')
        self._create_tag(tag_name)
        self.defconfig_add('VERSION', tag_name)

        rv = self.engine.run()
        self.assertTrue(rv)

        current_hash = self._git_cache('rev-parse', 'HEAD')
        self.assertEqual(current_hash, first_hash)

        # cleanup
        self.cleanup_outdir()

        # re-invoke with a new tag on a remote should not change cache state,
        # as we should not have fetched
        self._delete_tag(tag_name)
        second_hash = self._create_commit('second')
        self._create_tag(tag_name)

        rv = self.engine.run()
        self.assertTrue(rv)

        current_hash = self._git_cache('rev-parse', 'HEAD')
        self.assertEqual(current_hash, first_hash)

        # cleanup
        self.cleanup_outdir()

        # force a fetch (which should update the cache)
        self.engine.opts.gbl_action = GlobalAction.FETCH
        rv = self.engine.run()
        self.assertTrue(rv)

        # re-invoke extraction stage to see if it uses the newer tagged commit
        self.engine.opts.gbl_action = GlobalAction.EXTRACT
        rv = self.engine.run()
        self.assertTrue(rv)

        current_hash = self._git_cache('rev-parse', 'HEAD')
        self.assertEqual(current_hash, second_hash)

    def test_tool_git_unknown_branch_tag(self):
        self.defconfig_add('VERSION', 'unknown')
        rv = self.engine.run()
        self.assertFalse(rv)

    def test_tool_git_unknown_hash(self):
        self.defconfig_add('VERSION',
            'da39a3ee5e6b4b0d3255bfef95601890afd80709')
        rv = self.engine.run()
        self.assertFalse(rv)

    def _git(self, workdir, *args):
        with interim_working_dir(workdir):
            out = []
            if not execute(['git'] + list(args), capture=out, critical=False):
                print('\n'.join(out))
                assert False, 'failed to issue git command'
            return '\n'.join(out)

    def _git_cache(self, *args):
        return self._git(self.cache_dir, *args)

    def _git_repo(self, *args):
        return self._git(self.repo_dir, *args)

    def _create_commit(self, msg='test'):
        self._git_repo('commit', '--allow-empty', '-m', msg)
        return self._git_repo('rev-parse', 'HEAD')

    def _create_tag(self, tag):
        self._git_repo('tag', tag)
        return tag

    def _delete_tag(self, tag):
        self._git_repo('tag', '-d', tag)
