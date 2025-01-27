# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.pipeline import RelengPackagePipeline
from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os


class TestPkgPipelinePackageEnvironment(RelengToolTestCase):
    def test_pkg_pipeline_pkgenv_empty(self):
        pkg_name = 'test-empty'
        with prepare_testenv(template='pkg-env') as engine:
            pkgs = engine.pkgman.load([pkg_name])

            pipeline = RelengPackagePipeline(engine, engine.opts, {})
            for pkg in pkgs:
                processed = pipeline.process(pkg)
                self.assertTrue(processed)

            # verify package-specific environment variables were set
            self.assertTrue('TEST_EMPTY_BUILD_OUTPUT_DIR' in os.environ)
            test_outdir = os.environ['TEST_EMPTY_BUILD_OUTPUT_DIR']
            results = os.path.join(test_outdir, 'invoke-env.json')
            self.assertTrue(os.path.exists(results))

            with open(results) as f:
                data = json.load(f)

            # verify that provided environment keys which may be empty if not
            # set are indeed empty
            self.assertEqual(data['PKG_SITE'], '')
            self.assertEqual(data['PKG_VERSION'], '')

    def test_pkg_pipeline_pkgenv_generic(self):
        pkg_name = 'test-generic'
        with prepare_testenv(template='pkg-env') as engine:
            pkgs = engine.pkgman.load([pkg_name])

            pipeline = RelengPackagePipeline(engine, engine.opts, {})
            for pkg in pkgs:
                processed = pipeline.process(pkg)
                self.assertTrue(processed)

            # verify package-specific environment variables were set
            self.assertTrue('TEST_GENERIC_BUILD_OUTPUT_DIR' in os.environ)
            test_outdir = os.environ['TEST_GENERIC_BUILD_OUTPUT_DIR']
            results = os.path.join(test_outdir, 'invoke-env.json')
            self.assertTrue(os.path.exists(results))

            with open(results) as f:
                data = json.load(f)

            # verify that all expected environment variables are set
            expected_pkg_env_keys = [
                'PKG_BUILD_BASE_DIR',
                'PKG_BUILD_DIR',
                'PKG_BUILD_OUTPUT_DIR',
                'PKG_CACHE_DIR',
                'PKG_CACHE_FILE',
                'PKG_DEFDIR',
                'PKG_NAME',
                'PKG_REVISION',
                'PKG_SITE',
                'PKG_VERSION',
            ]
            self.assertTrue(all(x in data for x in expected_pkg_env_keys))

            # verify that all unexpected environment variables are not set
            unexpected_pkg_env_keys = [
                'PKG_INTERNAL',
            ]
            self.assertTrue(all(x not in data for x in unexpected_pkg_env_keys))

            # sanity check the contents of various environment variables
            self.assertEqual(data['PKG_BUILD_DIR'], data['PKG_BUILD_BASE_DIR'])
            self.assertEqual(data['PKG_NAME'], pkg_name)
            self.assertEqual(data['PKG_REVISION'], 'test-revision')
            self.assertEqual(data['PKG_SITE'], 'mocked-site')
            self.assertEqual(data['PKG_VERSION'], 'test-version')

    def test_pkg_pipeline_pkgenv_internal(self):
        pkg_name = 'test-internal'
        with prepare_testenv(template='pkg-env') as engine:
            pkgs = engine.pkgman.load([pkg_name])

            pipeline = RelengPackagePipeline(engine, engine.opts, {})
            for pkg in pkgs:
                processed = pipeline.process(pkg)
                self.assertTrue(processed)

            # verify package-specific environment variables were set
            self.assertTrue('TEST_INTERNAL_BUILD_OUTPUT_DIR' in os.environ)
            test_outdir = os.environ['TEST_INTERNAL_BUILD_OUTPUT_DIR']
            results = os.path.join(test_outdir, 'invoke-env.json')
            self.assertTrue(os.path.exists(results))

            with open(results) as f:
                data = json.load(f)

            # ensure that the internal environment flag is set when processing
            # an internal-flagged package
            self.assertTrue('PKG_INTERNAL' in data)

    def test_pkg_pipeline_pkgenv_subdir(self):
        pkg_name = 'test-subdir'
        with prepare_testenv(template='pkg-env') as engine:
            pkgs = engine.pkgman.load([pkg_name])

            pipeline = RelengPackagePipeline(engine, engine.opts, {})
            for pkg in pkgs:
                processed = pipeline.process(pkg)
                self.assertTrue(processed)

            # verify package-specific environment variables were set
            self.assertTrue('TEST_SUBDIR_BUILD_OUTPUT_DIR' in os.environ)
            test_outdir = os.environ['TEST_SUBDIR_BUILD_OUTPUT_DIR']
            results = os.path.join(test_outdir, 'invoke-env.json')
            self.assertTrue(os.path.exists(results))

            with open(results) as f:
                data = json.load(f)

            # sanity check that the base and build directories are different
            # since a sub-directory has been configured
            build_base_dir = data['PKG_BUILD_BASE_DIR']
            build_dir = data['PKG_BUILD_DIR']
            self.assertNotEqual(build_base_dir, build_dir)
            self.assertNotEqual(build_base_dir, build_dir)
            self.assertTrue(os.path.commonprefix((build_base_dir, build_dir)))
