# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import GlobalAction
from releng_tool.util.io import execute
from releng_tool.util.io import execute_rv
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.io_temp_dir import temp_dir
from releng_tool.util.io_touch import touch
from releng_tool.util.io_wd import wd
from tests.support.site_tool_test import TestSiteToolBase
import os
import sys
import unittest
import uuid


DEFAULT_BRANCH = 'test'


class TestToolGit(TestSiteToolBase):
    def prepare_defconfig(self, defconfig):
        self.defconfig_add('VCS_TYPE', 'git')

    def prepare_repo_dir(self, repo_dir):
        self._git_repo('init', repo_dir)
        self._git_repo('checkout', '-B', DEFAULT_BRANCH, repo=repo_dir)
        self._git_repo('config', 'user.email', 'test@releng.io', repo=repo_dir)
        self._git_repo('config', 'user.name', 'Unit Test', repo=repo_dir)
        self._create_commit('initial commit', repo=repo_dir)

    def test_tool_git_basic_branch(self):
        self.defconfig_add('VERSION', DEFAULT_BRANCH)
        rv = self.engine.run()
        self.assertTrue(rv)

    def test_tool_git_basic_commit(self):
        hash_ = self._create_commit()
        self.defconfig_add('VERSION', hash_)
        rv = self.engine.run()
        self.assertTrue(rv)

    def test_tool_git_basic_tag(self):
        tag = self._create_tag('my-tag')
        self.defconfig_add('VERSION', tag)
        rv = self.engine.run()
        self.assertTrue(rv)

    def test_tool_git_branch_forward_slash(self):
        # create a commit on a new branch with a forward slash
        TMP_BRANCH = 'container/test'
        self._git_repo('checkout', '-b', TMP_BRANCH)
        self._create_commit()
        self._git_repo('checkout', DEFAULT_BRANCH)

        self.defconfig_add('VERSION', TMP_BRANCH)
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

    def test_tool_git_custom_options_invalid(self):
        self.defconfig_add('GIT_CONFIG', {
            'bad-config-key': '',
        })
        self.defconfig_add('VERSION', DEFAULT_BRANCH)
        rv = self.engine.run()
        self.assertFalse(rv)

    def test_tool_git_custom_options_valid(self):
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
        hash_ = self._create_commit()
        self._git_repo('update-ref', 'refs/mycustomref/test', hash_)
        self._git_repo('checkout', DEFAULT_BRANCH)
        self._git_repo('branch', '-D', TMP_BRANCH)

        # first fetch attempt should fail since the custom reference will not be
        # fetched by default
        self.defconfig_add('VERSION', hash_)
        rv = self.engine.run()
        self.assertFalse(rv)

        # add the new custom reference to the configuration and re-fetch
        self.defconfig_add('GIT_REFSPECS', ['mycustomref/*'])
        rv = self.engine.run()
        self.assertTrue(rv)

    def test_tool_git_depth_shallow_default(self):
        self._create_commit()
        hash_ = self._create_commit()
        self.defconfig_add('VERSION', hash_)

        rv = self.engine.run()
        self.assertTrue(rv)

        rev_count = self._git_cache('rev-list', '--count', 'HEAD')
        self.assertEqual(int(rev_count), 1)

    def test_tool_git_depth_shallow_disabled_config(self):
        self._create_commit()
        hash_ = self._create_commit()
        self.defconfig_add('GIT_DEPTH', 0)
        self.defconfig_add('VERSION', hash_)

        rv = self.engine.run()
        self.assertTrue(rv)

        rev_count = self._git_cache('rev-list', '--count', 'HEAD')
        self.assertNotEqual(int(rev_count), 1)

    def test_tool_git_depth_shallow_disabled_quirk(self):
        self.engine.opts.quirks.append('releng.git.no_depth')

        self._create_commit()
        hash_ = self._create_commit()
        self.defconfig_add('VERSION', hash_)

        rv = self.engine.run()
        self.assertTrue(rv)

        rev_count = self._git_cache('rev-list', '--count', 'HEAD')
        self.assertNotEqual(int(rev_count), 1)

    def test_tool_git_depth_unshallow_initial(self):
        hash_ = self._create_commit()
        self._create_commit()
        self.defconfig_add('VERSION', hash_)

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

    def test_tool_git_devmode_auto_fetch_branch(self):
        # create a new branch with a commit
        TARGET_BRANCH = 'target'
        self._git_repo('checkout', '-b', TARGET_BRANCH)
        first_hash = self._create_commit('first')

        # enable development mode
        touch(self.engine.opts.ff_devmode)

        # note: default state should be automatic cache-ignoring
        #        (i.e enabled in development mode)

        # fetch the target
        self.defconfig_add('VERSION', TARGET_BRANCH)
        rv = self.engine.run()
        self.assertTrue(rv)

        current_hash = self._git_cache('rev-parse', 'HEAD')
        self.assertEqual(current_hash, first_hash)

        # cleanup
        self.cleanup_outdir()
        self.engine.opts.devmode = None

        # create a new commit
        second_hash = self._create_commit('second')

        # extract project; should be the second commit
        rv = self.engine.run()
        self.assertTrue(rv)

        current_hash = self._git_cache('rev-parse', 'HEAD')
        self.assertEqual(current_hash, second_hash)

        # cleanup
        self.cleanup_outdir()
        self.engine.opts.devmode = None

        # create a new commit
        third_hash = self._create_commit('third')

        # explicitly indicate that cache-ignoring should not happen
        self.defconfig_add('DEVMODE_IGNORE_CACHE', value=False)
        self.defconfig_dump()

        # extract; should be the second commit
        rv = self.engine.run()
        self.assertTrue(rv)

        current_hash = self._git_cache('rev-parse', 'HEAD')
        self.assertEqual(current_hash, second_hash)

        # cleanup
        self.cleanup_outdir()
        self.engine.opts.devmode = None

        # explicitly indicate that cache-ignoring can happen
        self.defconfig_add('DEVMODE_IGNORE_CACHE', value=True)

        # extract; should be the third commit
        rv = self.engine.run()
        self.assertTrue(rv)

        current_hash = self._git_cache('rev-parse', 'HEAD')
        self.assertEqual(current_hash, third_hash)

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

    def test_tool_git_submodules_default(self):
        self.defconfig_add('VERSION', DEFAULT_BRANCH)

        with temp_dir() as repo2:
            # prepare additional mock repository directories
            repo1 = self.repo_dir
            self.prepare_repo_dir(repo2)

            # dummy file on repo1
            touch(os.path.join(repo1, 'file1'))
            self._create_commit('add file', repo=repo1, add=True)

            # dummy file on repo2
            touch(os.path.join(repo2, 'file2'))
            self._create_commit('add file', repo=repo2, add=True)

            # add a submodule repo2 to repo1
            self._git_repo('-c', 'protocol.file.allow=always',
                'submodule', 'add', repo2, 'repo2', repo=repo1)
            self._create_commit('add module', repo=repo1, add=True)

            # extract package but not submodules (by default)
            self.engine.opts.gbl_action = GlobalAction.EXTRACT
            rv = self.engine.run()
            self.assertTrue(rv)

            # verify expected content from main package; not submodules
            out_dir = os.path.join(
                self.engine.opts.build_dir, 'test-' + DEFAULT_BRANCH)
            repo1_file = os.path.join(out_dir, 'file1')
            repo2_file = os.path.join(out_dir, 'repo2', 'file2')
            self.assertTrue(os.path.exists(repo1_file))
            self.assertFalse(os.path.exists(repo2_file))

    def test_tool_git_submodules_enabled(self):
        self.defconfig_add('GIT_SUBMODULES', value=True)
        self.defconfig_add('VERSION', DEFAULT_BRANCH)

        with temp_dir() as repo2, temp_dir() as repo3:
            # prepare additional mock repository directories
            repo1 = self.repo_dir
            self.prepare_repo_dir(repo2)
            self.prepare_repo_dir(repo3)

            # dummy file on repo1
            touch(os.path.join(repo1, 'file1'))
            self._create_commit('add file', repo=repo1, add=True)

            # dummy file on repo2
            touch(os.path.join(repo2, 'file2'))
            self._create_commit('add file', repo=repo2, add=True)

            # dummy file on repo3
            touch(os.path.join(repo3, 'file3'))
            self._create_commit('add file', repo=repo3, add=True)

            # add a submodule repo3 to repo2
            self._git_repo('-c', 'protocol.file.allow=always',
                'submodule', 'add', repo3, 'repo3', repo=repo2)
            self._create_commit('add repo3 module', repo=repo2, add=True)

            # add a submodule repo2 to repo1
            self._git_repo('-c', 'protocol.file.allow=always',
                'submodule', 'add', repo2, 'repo2', repo=repo1)
            self._create_commit('add repo2 module', repo=repo1, add=True)

            # extract package and submodules
            self.engine.opts.gbl_action = GlobalAction.EXTRACT
            rv = self.engine.run()
            self.assertTrue(rv)

            # verify expected content from main package and submodules
            out_dir = os.path.join(
                self.engine.opts.build_dir, 'test-' + DEFAULT_BRANCH)
            repo1_file = os.path.join(out_dir, 'file1')
            repo2_file = os.path.join(out_dir, 'repo2', 'file2')
            repo3_file = os.path.join(out_dir, 'repo2', 'repo3', 'file3')
            self.assertTrue(os.path.exists(repo1_file))
            self.assertTrue(os.path.exists(repo2_file))
            self.assertTrue(os.path.exists(repo3_file))

    def test_tool_git_submodules_branch_revision(self):
        self.defconfig_add('GIT_SUBMODULES', value=True)
        self.defconfig_add('VERSION', DEFAULT_BRANCH)

        with temp_dir() as repo2:
            # prepare additional mock repository directories
            repo1 = self.repo_dir
            self.prepare_repo_dir(repo2)

            # dummy file on repo1
            touch(os.path.join(repo1, 'file1'))
            self._create_commit('add file1', add=True)

            # dummy file on repo2
            touch(os.path.join(repo2, 'file2'))
            eref1 = self._create_commit('add file2', repo=repo2, add=True)

            # add a submodule repo2 to repo1
            self._git_repo('-c', 'protocol.file.allow=always',
                'submodule', 'add', repo2, 'repo2', repo=repo1)
            self._create_commit('add module', add=True)

            # second dummy file on repo2
            CUSTOM_BRANCH = 'custom'

            self._git_repo('checkout', '-b', CUSTOM_BRANCH, repo=repo2)

            touch(os.path.join(repo2, 'file3'))
            eref2 = self._create_commit('add file3', repo=repo2, add=True)

            # extract package with default submodule
            self.engine.opts.gbl_action = GlobalAction.EXTRACT
            rv = self.engine.run()
            self.assertTrue(rv)

            # verify expected content from main and default submodule branch
            out_dir = os.path.join(
                self.engine.opts.build_dir, 'test-' + DEFAULT_BRANCH)
            repo1_file1 = os.path.join(out_dir, 'file1')
            repo2_file2 = os.path.join(out_dir, 'repo2', 'file2')
            repo2_file3 = os.path.join(out_dir, 'repo2', 'file3')
            self.assertTrue(os.path.exists(repo1_file1))
            self.assertTrue(os.path.exists(repo2_file2))
            self.assertFalse(os.path.exists(repo2_file3))

            # cleanup
            self.cleanup_outdir()

            # adjust submodule to target the custom branch
            check_ref = self._git_repo('rev-parse', f'{DEFAULT_BRANCH}:repo2')
            self.assertEqual(check_ref, eref1)

            self._git_repo('config', '-f', '.gitmodules',
                'submodule.repo2.branch', CUSTOM_BRANCH)
            self._git_repo('-c', 'protocol.file.allow=always',
                'submodule', 'update', '--remote', 'repo2')
            self._create_commit('updated module reference', add=True)

            check_ref = self._git_repo('rev-parse', f'{DEFAULT_BRANCH}:repo2')
            self.assertEqual(check_ref, eref2)

            # force a fetch (which should update the cache)
            self.engine.opts.gbl_action = GlobalAction.FETCH
            rv = self.engine.run()
            self.assertTrue(rv)

            # re-extract package and submodules
            self.engine.opts.gbl_action = GlobalAction.EXTRACT
            rv = self.engine.run()
            self.assertTrue(rv)

            # verify expected content from main package and submodules
            self.assertTrue(os.path.exists(repo2_file3))

    def test_tool_git_unknown_branch_tag(self):
        self.defconfig_add('VERSION', 'unknown')
        rv = self.engine.run()
        self.assertFalse(rv)

    def test_tool_git_unknown_hash(self):
        self.defconfig_add('VERSION',
            'da39a3ee5e6b4b0d3255bfef95601890afd80709')
        rv = self.engine.run()
        self.assertFalse(rv)

    def test_tool_git_verify_revision_expected_fail(self):
        tag = self._create_tag('non-signed-tag')
        self.defconfig_add('GIT_VERIFY_REVISION', True)  # noqa: FBT003
        self.defconfig_add('VERSION', tag)
        rv = self.engine.run()
        self.assertFalse(rv)

    def test_tool_git_verify_revision_expected_pass(self):
        # Disabling macOS run for now; should be able to work but test is
        # not yet tailored to handle this environment yet.
        if sys.platform == 'darwin':
            raise unittest.SkipTest('skipping due to test runtime issues')

        # prepare a home directory for gpg; we initial setup with a
        # relative path, otherwise gpg-agent can fail to start in
        # Windows enviroments (see also: TestToolGpg.test_tool_gpg_valid)
        os.environ['GNUPGHOME'] = '.gnupghome'
        os.environ.pop('GPG_AGENT_INFO', None)
        os.environ.pop('SSH_AUTH_SOCK', None)
        os.environ.pop('SSH_AGENT_PID', None)
        mkdir('.gnupghome')

        rv, out = execute_rv('gpgconf', '--list-dirs', 'socketdir')
        if rv != 0:
            print(out)
            raise AssertionError('failed to issue gpg command')
        os.environ['GNUPGHOME'] = out

        # generate a new key
        rv, out = execute_rv('gpg', '--batch', '--quick-gen-key',
            '--passphrase', '', 'gpg-key-test@releng.io')
        if rv != 0:
            print(out)
            raise AssertionError('failed to create gpg key')

        # find the identifier for this new key
        rv, out = execute_rv('gpg', '--list-secret-keys',
            '--keyid-format=long', '--with-colons', '--quiet')
        if rv != 0:
            print(out)
            raise AssertionError('failed to query id of gpg key')

        find_gpg_key_id = None
        for line in out.splitlines():
            if line.startswith('sec'):
                parts = line.split(':')
                find_gpg_key_id = parts[4]
                break

        if not find_gpg_key_id:
            print(out)
            raise AssertionError('failed to find gpg key id')

        # configure git to sign with this key
        self._git_repo('config', 'tag.gpgsign', 'true')
        self._git_repo('config', 'user.signingkey', find_gpg_key_id + '!')

        # create a signed tag
        tag = self._create_tag('signed-tag', msg='expected-pass')

        # configure the package and verify
        self.defconfig_add('GIT_VERIFY_REVISION', True)  # noqa: FBT003
        self.defconfig_add('VERSION', tag)
        rv = self.engine.run()
        self.assertTrue(rv)

    def _git(self, workdir, *args):
        with wd(workdir):
            out = []
            if not execute(['git', *list(args)], capture=out, critical=False):
                print(['(TestToolGit) git', *list(args)])
                print('\n'.join(out))
                raise AssertionError('failed to issue git command')
            return '\n'.join(out)

    def _git_cache(self, *args):
        git_dir = '--git-dir=' + self.cache_dir
        return self._git_repo(git_dir, *args)

    def _git_repo(self, *args, **kwargs):
        repo = kwargs.get('repo')
        if not repo:
            repo = self.repo_dir
        return self._git(repo, *args)

    def _create_commit(self, msg='test', **kwargs):
        # always append a unique identifier; otherwise fresh/empty repositories
        # created at the same time for a test may result in the same hash value
        uid = str(uuid.uuid4())[:5]
        umsg = f'{msg} ({uid})'

        repo = kwargs.get('repo')
        if kwargs.get('add'):
            self._git_repo('add', '.', repo=repo)
        self._git_repo('commit', '--allow-empty', '-m', umsg, repo=repo)
        return self._git_repo('rev-parse', 'HEAD', repo=repo)

    def _create_tag(self, tag, msg='', repo=None):
        self._git_repo('tag', tag, '-m', msg, repo=repo)
        return tag

    def _delete_tag(self, tag, repo=None):
        self._git_repo('tag', '-d', tag, repo=repo)
