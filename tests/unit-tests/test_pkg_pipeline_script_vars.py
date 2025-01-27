# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.pipeline import RelengPackagePipeline
from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os


class TestPkgPipelinePackageScriptVars(RelengToolTestCase):
    def test_pkg_pipeline_script_vars(self):
        with prepare_testenv(template='script-vars') as engine:
            pkgs = engine.pkgman.load(['test'])

            pipeline = RelengPackagePipeline(engine, engine.opts, {})
            for pkg in pkgs:
                processed = pipeline.process(pkg)
                self.assertTrue(processed)

            # verify package-specific variables were set
            self.assertTrue('TEST_BUILD_OUTPUT_DIR' in os.environ)
            test_outdir = os.environ['TEST_BUILD_OUTPUT_DIR']
            results = os.path.join(test_outdir, 'invoke-vars.json')
            self.assertTrue(os.path.exists(results))

            with open(results) as f:
                data = json.load(f)

            # verify that all expected variables exist
            expected_pkg_keys = [
                'PKG_BUILD_BASE_DIR',
                'PKG_BUILD_DIR',
                'PKG_BUILD_OUTPUT_DIR',
                'PKG_CACHE_DIR',
                'PKG_CACHE_FILE',
                'PKG_DEFDIR',
                'PKG_DEVMODE',
                'PKG_INTERNAL',
                'PKG_LOCALSRCS',
                'PKG_NAME',
                'PKG_REVISION',
                'PKG_SITE',
                'PKG_VERSION',
            ]
            self.assertTrue(all(x in data for x in expected_pkg_keys))

            # verify that all flags are not set to True
            unset_pkg_keys = [
                'PKG_DEVMODE',
                'PKG_INTERNAL',
                'PKG_LOCALSRCS',
            ]
            self.assertTrue(all(not data[x] for x in unset_pkg_keys))
