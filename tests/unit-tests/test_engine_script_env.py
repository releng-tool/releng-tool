# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool import __version__ as releng_version
from releng_tool.defs import GlobalAction
from releng_tool.defs import PkgAction
from releng_tool.engine.script_env import prepare_script_environment
from releng_tool.opts import RelengEngineOptions
from tests import RelengToolTestCase
import ast


class TestEngineScriptEnv(RelengToolTestCase):
    def setUp(self):
        self.opts = RelengEngineOptions()

    def test_engine_scriptenv_env_jobs(self):
        self.opts.jobs = 24
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('NJOBS', env)
        self.assertEqual(env['NJOBS'], 24)

    def test_engine_scriptenv_env_jobsconf(self):
        self.opts.jobsconf = 2456
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('NJOBSCONF', env)
        self.assertEqual(env['NJOBSCONF'], 2456)

    def test_engine_scriptenv_env_prefix(self):
        self.opts.sysroot_prefix = 'example-prefix'
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('PREFIX', env)
        self.assertEqual(env['PREFIX'], 'example-prefix')

    def test_engine_scriptenv_env_releng_clean(self):
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('RELENG_CLEAN', env)
        self.assertFalse(env['RELENG_CLEAN'])

        self.opts.gbl_action = GlobalAction.CLEAN
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_CLEAN'])

        self.opts.gbl_action = GlobalAction.DISTCLEAN
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_CLEAN'])

        self.opts.gbl_action = GlobalAction.MRPROPER
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_CLEAN'])

        self.opts.gbl_action = None

        self.opts.pkg_action = PkgAction.CLEAN
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_CLEAN'])

        self.opts.pkg_action = PkgAction.DISTCLEAN
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_CLEAN'])

        self.opts.pkg_action = PkgAction.FRESH
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_CLEAN'])

    def test_engine_scriptenv_env_releng_debug(self):
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('RELENG_DEBUG', env)
        self.assertFalse(env['RELENG_DEBUG'])

        self.opts.debug = True
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_DEBUG'])

    def test_engine_scriptenv_env_releng_devmode(self):
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('RELENG_DEVMODE', env)
        self.assertFalse(env['RELENG_DEVMODE'])

        self.opts.devmode = True
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_DEVMODE'])

        self.opts.devmode = 'custom'
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertEqual(env['RELENG_DEVMODE'], 'custom')

    def test_engine_scriptenv_env_releng_distclean(self):
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('RELENG_DISTCLEAN', env)
        self.assertFalse(env['RELENG_DISTCLEAN'])

        self.opts.gbl_action = GlobalAction.CLEAN
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertFalse(env['RELENG_DISTCLEAN'])

        self.opts.gbl_action = GlobalAction.DISTCLEAN
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_DISTCLEAN'])

        self.opts.gbl_action = GlobalAction.MRPROPER
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertFalse(env['RELENG_DISTCLEAN'])

        self.opts.gbl_action = None

        self.opts.pkg_action = PkgAction.CLEAN
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertFalse(env['RELENG_DISTCLEAN'])

        self.opts.pkg_action = PkgAction.DISTCLEAN
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_DISTCLEAN'])

        self.opts.pkg_action = PkgAction.FRESH
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertFalse(env['RELENG_DISTCLEAN'])

    def test_engine_scriptenv_env_releng_exec(self):
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('RELENG_EXEC', env)
        self.assertFalse(env['RELENG_EXEC'])

        self.opts.pkg_action = PkgAction.EXEC
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_EXEC'])

    def test_engine_scriptenv_env_releng_force(self):
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('RELENG_FORCE', env)
        self.assertFalse(env['RELENG_FORCE'])

        self.opts.force = True
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_FORCE'])

        self.opts.force = None

        self.opts.gbl_action = GlobalAction.PUNCH
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_FORCE'])

    def test_engine_scriptenv_env_releng_localsrcs(self):
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('RELENG_LOCALSRCS', env)
        self.assertFalse(env['RELENG_LOCALSRCS'])

        self.opts.local_srcs = True
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_LOCALSRCS'])

    def test_engine_scriptenv_env_releng_mrproper(self):
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('RELENG_MRPROPER', env)
        self.assertFalse(env['RELENG_MRPROPER'])

        self.opts.gbl_action = GlobalAction.CLEAN
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertFalse(env['RELENG_MRPROPER'])

        self.opts.gbl_action = GlobalAction.DISTCLEAN
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_MRPROPER'])

        self.opts.gbl_action = GlobalAction.MRPROPER
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_MRPROPER'])

        self.opts.gbl_action = None

        self.opts.pkg_action = PkgAction.CLEAN
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertFalse(env['RELENG_MRPROPER'])

        self.opts.pkg_action = PkgAction.DISTCLEAN
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_MRPROPER'])

        self.opts.pkg_action = PkgAction.FRESH
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertFalse(env['RELENG_MRPROPER'])

    def test_engine_scriptenv_env_releng_profiles(self):
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('RELENG_PROFILES', env)
        self.assertFalse(env['RELENG_PROFILES'])

        self.opts.profiles = [
            'example',
        ]
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertEqual(env['RELENG_PROFILES'], [
            'example',
        ])

        self.opts.profiles = [
            'one',
            'two',
            'three',
        ]
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertEqual(env['RELENG_PROFILES'], [
            'one',
            'two',
            'three',
        ])

    def test_engine_scriptenv_env_releng_rebuild(self):
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('RELENG_REBUILD', env)
        self.assertFalse(env['RELENG_REBUILD'])

        self.opts.pkg_action = PkgAction.RECONFIGURE
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_REBUILD'])

        self.opts.pkg_action = PkgAction.RECONFIGURE_ONLY
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertFalse(env['RELENG_REBUILD'])

        self.opts.pkg_action = PkgAction.REBUILD
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_REBUILD'])

        self.opts.pkg_action = PkgAction.REBUILD_ONLY
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_REBUILD'])

        self.opts.pkg_action = PkgAction.REINSTALL
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertFalse(env['RELENG_REBUILD'])

    def test_engine_scriptenv_env_releng_reconfigure(self):
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('RELENG_RECONFIGURE', env)
        self.assertFalse(env['RELENG_RECONFIGURE'])

        self.opts.pkg_action = PkgAction.RECONFIGURE
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_RECONFIGURE'])

        self.opts.pkg_action = PkgAction.RECONFIGURE_ONLY
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_RECONFIGURE'])

        self.opts.pkg_action = PkgAction.REBUILD
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertFalse(env['RELENG_RECONFIGURE'])

        self.opts.pkg_action = PkgAction.REBUILD_ONLY
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertFalse(env['RELENG_RECONFIGURE'])

        self.opts.pkg_action = PkgAction.REINSTALL
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertFalse(env['RELENG_RECONFIGURE'])

    def test_engine_scriptenv_env_releng_reinstall(self):
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('RELENG_REINSTALL', env)
        self.assertFalse(env['RELENG_REINSTALL'])

        self.opts.pkg_action = PkgAction.RECONFIGURE
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_REINSTALL'])

        self.opts.pkg_action = PkgAction.RECONFIGURE_ONLY
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertFalse(env['RELENG_REINSTALL'])

        self.opts.pkg_action = PkgAction.REBUILD
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_REINSTALL'])

        self.opts.pkg_action = PkgAction.REBUILD_ONLY
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertFalse(env['RELENG_REINSTALL'])

        self.opts.pkg_action = PkgAction.REINSTALL
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_REINSTALL'])

    def test_engine_scriptenv_env_releng_target_pkg(self):
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('RELENG_TARGET_PKG', env)
        self.assertIsNone(env['RELENG_TARGET_PKG'])

        self.opts.target_action = 'custom-target'
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertEqual(env['RELENG_TARGET_PKG'], 'custom-target')

    def test_engine_scriptenv_env_releng_verbose(self):
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('RELENG_VERBOSE', env)
        self.assertFalse(env['RELENG_VERBOSE'])

        self.opts.verbose = True
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertTrue(env['RELENG_VERBOSE'])

    def test_engine_scriptenv_env_releng_version(self):
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('RELENG_VERSION', env)
        self.assertEqual(env['RELENG_VERSION'], releng_version)

    def test_engine_scriptenv_env_root_dir(self):
        self.opts.root_dir = 'example-root-path'
        env = {}
        prepare_script_environment(env, self.opts)
        self.assertIn('ROOT_DIR', env)
        self.assertEqual(env['ROOT_DIR'], 'example-root-path')

    def test_engine_scriptenv_verify_utility_methods(self):
        # prepare a script environment
        env = {}
        prepare_script_environment(env, self.opts)

        # find the releng-tool module script helpers can be imported from
        root_dir = Path(__file__).parent.parent.parent
        rtm = root_dir / 'releng_tool' / '__init__.py'
        self.assertTrue(rtm.is_file())

        # read this file and extract all import aliases
        rtm_contents = rtm.read_text()
        tree = ast.parse(rtm_contents)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ImportFrom):
                continue

            # each alias should be found in the script environment
            for alias in node.names:
                self.assertIn(alias.asname, env)
