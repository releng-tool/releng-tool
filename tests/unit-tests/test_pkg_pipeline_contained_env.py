# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.pipeline import RelengPackagePipeline
from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os


class TestPkgPipelineContainedEnvironment(RelengToolTestCase):
    def test_pkg_pipeline_containedenv(self):
        pkg_names = [
            'test1',
            'test2',
        ]

        expected_prefix = '/my-custom-prefix'

        with prepare_testenv(template='contained-env') as engine:
            pkgs = engine.pkgman.load(pkg_names)

            pipeline = RelengPackagePipeline(engine, engine.opts, {})
            for pkg in pkgs:
                if not pipeline.process(pkg):
                    break

            # verify package-specific environment variables were set
            self.assertTrue('TEST1_BUILD_OUTPUT_DIR' in os.environ)
            test1_outdir = os.environ['TEST1_BUILD_OUTPUT_DIR']
            results1 = os.path.join(test1_outdir, 'invoke-env.json')
            self.assertTrue(os.path.exists(results1))

            with open(results1) as f:
                data = json.load(f)

            pkg_keys = [
                'HOST_BIN_DIR',
                'HOST_INCLUDE_DIR',
                'HOST_LIB_DIR',
                'HOST_SHARE_DIR',
                'NJOBS',
                'NJOBSCONF',
                'PREFIX',
                'PREFIXED_HOST_DIR',
                'PREFIXED_STAGING_DIR',
                'PREFIXED_TARGET_DIR',
                'STAGING_BIN_DIR',
                'STAGING_INCLUDE_DIR',
                'STAGING_LIB_DIR',
                'STAGING_SHARE_DIR',
                'TARGET_BIN_DIR',
                'TARGET_INCLUDE_DIR',
                'TARGET_LIB_DIR',
                'TARGET_SHARE_DIR',
            ]
            self.assertTrue(all(x in data for x in pkg_keys))
            self.assertEqual(data['NJOBS'], '42')
            self.assertEqual(data['NJOBSCONF'], '42')
            self.assertEqual(data['PREFIX'], expected_prefix)

            opts = engine.opts
            nprefix = os.path.normpath(expected_prefix)
            expected_host_pdir = opts.host_dir + nprefix
            expected_staging_pdir = opts.staging_dir + nprefix
            expected_target_pdir = opts.target_dir + nprefix

            J = os.path.join
            expected_host_bin_dir = J(expected_host_pdir, 'bin')
            expected_host_include_dir = J(expected_host_pdir, 'include')
            expected_host_lib_dir = J(expected_host_pdir, 'lib')
            expected_host_share_dir = J(expected_host_pdir, 'share')
            expected_staging_bin_dir = J(expected_staging_pdir, 'bin')
            expected_staging_include_dir = J(expected_staging_pdir, 'include')
            expected_staging_lib_dir = J(expected_staging_pdir, 'lib')
            expected_staging_share_dir = J(expected_staging_pdir, 'share')
            expected_target_bin_dir = J(expected_target_pdir, 'bin')
            expected_target_include_dir = J(expected_target_pdir, 'include')
            expected_target_lib_dir = J(expected_target_pdir, 'lib')
            expected_target_share_dir = J(expected_target_pdir, 'share')

            self.assertEqual(
                data['HOST_BIN_DIR'], expected_host_bin_dir)
            self.assertEqual(
                data['HOST_INCLUDE_DIR'], expected_host_include_dir)
            self.assertEqual(
                data['HOST_LIB_DIR'], expected_host_lib_dir)
            self.assertEqual(
                data['HOST_SHARE_DIR'], expected_host_share_dir)
            self.assertEqual(
                data['PREFIXED_HOST_DIR'], expected_host_pdir)
            self.assertEqual(
                data['PREFIXED_STAGING_DIR'], expected_staging_pdir)
            self.assertEqual(
                data['PREFIXED_TARGET_DIR'], expected_target_pdir)
            self.assertEqual(
                data['STAGING_BIN_DIR'], expected_staging_bin_dir)
            self.assertEqual(
                data['STAGING_INCLUDE_DIR'], expected_staging_include_dir)
            self.assertEqual(
                data['STAGING_LIB_DIR'], expected_staging_lib_dir)
            self.assertEqual(
                data['STAGING_SHARE_DIR'], expected_staging_share_dir)
            self.assertEqual(
                data['TARGET_BIN_DIR'], expected_target_bin_dir)
            self.assertEqual(
                data['TARGET_INCLUDE_DIR'], expected_target_include_dir)
            self.assertEqual(
                data['TARGET_LIB_DIR'], expected_target_lib_dir)
            self.assertEqual(
                data['TARGET_SHARE_DIR'], expected_target_share_dir)

            # verify package-specific environment variables were properly
            # restored to original counts (leak check)
            self.assertTrue('TEST2_BUILD_OUTPUT_DIR' in os.environ)
            test2_outdir = os.environ['TEST2_BUILD_OUTPUT_DIR']
            results2 = os.path.join(test2_outdir, 'invoke-env.json')
            self.assertTrue(os.path.exists(results2))

            with open(results2) as f:
                data = json.load(f)

            if 'NJOBS' in data:
                self.assertNotEqual(data['NJOBS'], '42')
            if 'NJOBSCONF' in data:
                self.assertNotEqual(data['NJOBSCONF'], '42')
            if 'PREFIX' in data:
                self.assertNotEqual(data['PREFIX'], '/my-custom-prefix')
                self.assertNotEqual(
                    data['HOST_BIN_DIR'], expected_host_bin_dir)
                self.assertNotEqual(
                    data['HOST_INCLUDE_DIR'], expected_host_include_dir)
                self.assertNotEqual(
                    data['HOST_INCLUDE_DIR'], expected_host_include_dir)
                self.assertNotEqual(
                    data['HOST_LIB_DIR'], expected_host_lib_dir)
                self.assertNotEqual(
                    data['HOST_SHARE_DIR'], expected_host_share_dir)
                self.assertNotEqual(
                    data['PREFIXED_HOST_DIR'], expected_host_pdir)
                self.assertNotEqual(
                    data['PREFIXED_STAGING_DIR'], expected_staging_pdir)
                self.assertNotEqual(
                    data['PREFIXED_TARGET_DIR'], expected_target_pdir)
                self.assertNotEqual(
                    data['STAGING_BIN_DIR'], expected_staging_bin_dir)
                self.assertNotEqual(
                    data['STAGING_INCLUDE_DIR'], expected_staging_include_dir)
                self.assertNotEqual(
                    data['STAGING_LIB_DIR'], expected_staging_lib_dir)
                self.assertNotEqual(
                    data['STAGING_SHARE_DIR'], expected_staging_share_dir)
                self.assertNotEqual(
                    data['TARGET_BIN_DIR'], expected_target_bin_dir)
                self.assertNotEqual(
                    data['TARGET_INCLUDE_DIR'], expected_target_include_dir)
                self.assertNotEqual(
                    data['TARGET_LIB_DIR'], expected_target_lib_dir)
                self.assertNotEqual(
                    data['TARGET_SHARE_DIR'], expected_target_share_dir)
