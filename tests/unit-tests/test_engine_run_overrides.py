# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import os
import json


class TestEngineRunOverrides(RelengToolTestCase):
    def test_engine_run_overrides_revision(self):
        with prepare_testenv(template='override-revision') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            # verify package-specific variables were set
            self.assertTrue('TEST_BUILD_OUTPUT_DIR' in os.environ)
            test_outdir = os.environ['TEST_BUILD_OUTPUT_DIR']
            results = os.path.join(test_outdir, 'invoke-vars.json')
            self.assertTrue(os.path.exists(results))

            with open(results) as f:
                data = json.load(f)

            # check that the revision has been overridden
            self.assertTrue('PKG_REVISION' in data)
            self.assertEqual(data['PKG_REVISION'], '2')

    def test_engine_run_overrides_site(self):
        with prepare_testenv(template='override-site') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            # verify package-specific variables were set
            self.assertTrue('TEST_BUILD_OUTPUT_DIR' in os.environ)
            test_outdir = os.environ['TEST_BUILD_OUTPUT_DIR']
            results = os.path.join(test_outdir, 'invoke-vars.json')
            self.assertTrue(os.path.exists(results))

            with open(results) as f:
                data = json.load(f)

            # check that the revision has been overridden
            self.assertTrue('PKG_SITE' in data)
            self.assertEqual(data['PKG_SITE'], 'overridden-site')
