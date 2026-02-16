# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
from unittest.mock import patch
import json
import os


class TestPkgJobs(RelengToolTestCase):
    def test_pkg_jobs_env_default(self):
        with prepare_testenv(template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            target_dir = engine.opts.target_dir

            # default njobsconf
            test3_env = os.path.join(target_dir, 'test-3-invoke-env.json')
            self.assertTrue(os.path.exists(test3_env))

            with open(test3_env) as f:
                test3_data = json.load(f)

            # verify that all expected variables are set
            self.assertIn('NJOBSCONF', test3_data, 'missing NJOBSCONF')
            self.assertEqual(test3_data['NJOBSCONF'], '0')

    def test_pkg_jobs_env_scenario1(self):
        config = {
            'jobs': 10,
        }

        with prepare_testenv(config=config, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            target_dir = engine.opts.target_dir

            # job count should be capped at five
            test1_env = os.path.join(target_dir, 'test-1-invoke-env.json')
            self._verify_env_njobs(test1_env, 5)

            # subtracted two from job count
            test2_env = os.path.join(target_dir, 'test-2-invoke-env.json')
            self._verify_env_njobs(test2_env, 8)

            # default njobsconf
            test3_env = os.path.join(target_dir, 'test-3-invoke-env.json')
            self._verify_env_njobs(test3_env, 10)

    def test_pkg_jobs_env_scenario2(self):
        config = {
            'jobs': 4,
        }

        with prepare_testenv(config=config, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            target_dir = engine.opts.target_dir

            # job count should not have change since global limit is under
            test1_env = os.path.join(target_dir, 'test-1-invoke-env.json')
            self._verify_env_njobs(test1_env, 4)

            # subtracted two from job count
            test2_env = os.path.join(target_dir, 'test-2-invoke-env.json')
            self._verify_env_njobs(test2_env, 2)

    def test_pkg_jobs_env_scenario3(self):
        config = {
            'jobs': 2,
        }

        with prepare_testenv(config=config, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            target_dir = engine.opts.target_dir

            # job count should not have change since global limit is under
            test1_env = os.path.join(target_dir, 'test-1-invoke-env.json')
            self._verify_env_njobs(test1_env, 2)

            # subtracted two from job count, but always at least one
            test2_env = os.path.join(target_dir, 'test-2-invoke-env.json')
            self._verify_env_njobs(test2_env, 1)

    def _verify_env_njobs(self, path, value):
        self.assertTrue(os.path.exists(path))

        with open(path) as f:
            data = json.load(f)

        # verify that all expected variables are set
        self.assertIn('NJOBS', data, 'missing NJOBS')
        self.assertIn('NJOBSCONF', data, 'missing NJOBSCONF')
        self.assertEqual(data['NJOBS'], str(value))
        self.assertEqual(data['NJOBSCONF'], str(value))

    @patch('releng_tool.engine.build.build_script')
    def test_pkg_jobs_stage_build_default(self, build):
        cfg = {
            'action': 'test-3',
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            build.assert_called_once()
            args = build.call_args.args[0]
            # default mode should have a zero value for configured job count
            self.assertEqual(args.jobsconf, 0)

    @patch('releng_tool.engine.build.build_script')
    def test_pkg_jobs_stage_build_scenario1_test1(self, build):
        cfg = {
            'action': 'test-1',
            'jobs': 10,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            build.assert_called_once()
            args = build.call_args.args[0]
            self.assertEqual(args.jobs, 5)
            self.assertEqual(args.jobsconf, 5)

    @patch('releng_tool.engine.build.build_script')
    def test_pkg_jobs_stage_build_scenario1_test2(self, build):
        cfg = {
            'action': 'test-2',
            'jobs': 10,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            build.assert_called_once()
            args = build.call_args.args[0]
            self.assertEqual(args.jobs, 8)
            self.assertEqual(args.jobsconf, 8)

    @patch('releng_tool.engine.build.build_script')
    def test_pkg_jobs_stage_build_scenario1_test3(self, build):
        cfg = {
            'action': 'test-3',
            'jobs': 10,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            build.assert_called_once()
            args = build.call_args.args[0]
            self.assertEqual(args.jobs, 10)
            self.assertEqual(args.jobsconf, 10)

    @patch('releng_tool.engine.build.build_script')
    def test_pkg_jobs_stage_build_scenario2_test1(self, build):
        cfg = {
            'action': 'test-1',
            'jobs': 4,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            build.assert_called_once()
            args = build.call_args.args[0]
            self.assertEqual(args.jobs, 4)
            self.assertEqual(args.jobsconf, 4)

    @patch('releng_tool.engine.build.build_script')
    def test_pkg_jobs_stage_build_scenario2_test2(self, build):
        cfg = {
            'action': 'test-2',
            'jobs': 4,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            build.assert_called_once()
            args = build.call_args.args[0]
            self.assertEqual(args.jobs, 2)
            self.assertEqual(args.jobsconf, 2)

    @patch('releng_tool.engine.build.build_script')
    def test_pkg_jobs_stage_build_scenario2_test3(self, build):
        cfg = {
            'action': 'test-3',
            'jobs': 4,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            build.assert_called_once()
            args = build.call_args.args[0]
            self.assertEqual(args.jobs, 4)
            self.assertEqual(args.jobsconf, 4)

    @patch('releng_tool.engine.build.build_script')
    def test_pkg_jobs_stage_build_scenario3_test1(self, build):
        cfg = {
            'action': 'test-1',
            'jobs': 2,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            build.assert_called_once()
            args = build.call_args.args[0]
            self.assertEqual(args.jobs, 2)
            self.assertEqual(args.jobsconf, 2)

    @patch('releng_tool.engine.build.build_script')
    def test_pkg_jobs_stage_build_scenario3_test2(self, build):
        cfg = {
            'action': 'test-2',
            'jobs': 2,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            build.assert_called_once()
            args = build.call_args.args[0]
            self.assertEqual(args.jobs, 1)
            self.assertEqual(args.jobsconf, 1)

    @patch('releng_tool.engine.build.build_script')
    def test_pkg_jobs_stage_build_scenario3_test3(self, build):
        cfg = {
            'action': 'test-3',
            'jobs': 2,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            build.assert_called_once()
            args = build.call_args.args[0]
            self.assertEqual(args.jobs, 2)
            self.assertEqual(args.jobsconf, 2)

    @patch('releng_tool.engine.configure.conf_script')
    def test_pkg_jobs_stage_configure_default(self, configure):
        cfg = {
            'action': 'test-3',
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            configure.assert_called_once()
            args = configure.call_args.args[0]
            # default mode should have a zero value for configured job count
            self.assertEqual(args.jobsconf, 0)

    @patch('releng_tool.engine.configure.conf_script')
    def test_pkg_jobs_stage_configure_scenario1_test1(self, configure):
        cfg = {
            'action': 'test-1',
            'jobs': 10,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            configure.assert_called_once()
            args = configure.call_args.args[0]
            self.assertEqual(args.jobs, 5)
            self.assertEqual(args.jobsconf, 5)

    @patch('releng_tool.engine.configure.conf_script')
    def test_pkg_jobs_stage_configure_scenario1_test2(self, configure):
        cfg = {
            'action': 'test-2',
            'jobs': 10,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            configure.assert_called_once()
            args = configure.call_args.args[0]
            self.assertEqual(args.jobs, 8)
            self.assertEqual(args.jobsconf, 8)

    @patch('releng_tool.engine.configure.conf_script')
    def test_pkg_jobs_stage_configure_scenario1_test3(self, configure):
        cfg = {
            'action': 'test-3',
            'jobs': 10,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            configure.assert_called_once()
            args = configure.call_args.args[0]
            self.assertEqual(args.jobs, 10)
            self.assertEqual(args.jobsconf, 10)

    @patch('releng_tool.engine.configure.conf_script')
    def test_pkg_jobs_stage_configure_scenario2_test1(self, configure):
        cfg = {
            'action': 'test-1',
            'jobs': 4,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            configure.assert_called_once()
            args = configure.call_args.args[0]
            self.assertEqual(args.jobs, 4)
            self.assertEqual(args.jobsconf, 4)

    @patch('releng_tool.engine.configure.conf_script')
    def test_pkg_jobs_stage_configure_scenario2_test2(self, configure):
        cfg = {
            'action': 'test-2',
            'jobs': 4,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            configure.assert_called_once()
            args = configure.call_args.args[0]
            self.assertEqual(args.jobs, 2)
            self.assertEqual(args.jobsconf, 2)

    @patch('releng_tool.engine.configure.conf_script')
    def test_pkg_jobs_stage_configure_scenario2_test3(self, configure):
        cfg = {
            'action': 'test-3',
            'jobs': 4,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            configure.assert_called_once()
            args = configure.call_args.args[0]
            self.assertEqual(args.jobs, 4)
            self.assertEqual(args.jobsconf, 4)

    @patch('releng_tool.engine.configure.conf_script')
    def test_pkg_jobs_stage_configure_scenario3_test1(self, configure):
        cfg = {
            'action': 'test-1',
            'jobs': 2,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            configure.assert_called_once()
            args = configure.call_args.args[0]
            self.assertEqual(args.jobs, 2)
            self.assertEqual(args.jobsconf, 2)

    @patch('releng_tool.engine.configure.conf_script')
    def test_pkg_jobs_stage_configure_scenario3_test2(self, configure):
        cfg = {
            'action': 'test-2',
            'jobs': 2,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            configure.assert_called_once()
            args = configure.call_args.args[0]
            self.assertEqual(args.jobs, 1)
            self.assertEqual(args.jobsconf, 1)

    @patch('releng_tool.engine.configure.conf_script')
    def test_pkg_jobs_stage_configure_scenario3_test3(self, configure):
        cfg = {
            'action': 'test-3',
            'jobs': 2,
        }

        with prepare_testenv(config=cfg, template='max-jobs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            configure.assert_called_once()
            args = configure.call_args.args[0]
            self.assertEqual(args.jobs, 2)
            self.assertEqual(args.jobsconf, 2)
