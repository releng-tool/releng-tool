# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os


class TestEngineRunLicenses(RelengToolTestCase):
    def test_engine_run_licenses(self):
        with prepare_testenv(template='licenses') as engine:
            out_dir = engine.opts.out_dir

            rv = engine.run()
            self.assertTrue(rv)

            results = os.path.join(out_dir, 'generated-licenses.json')
            self.assertTrue(os.path.isfile(results))

            with open(results) as f:
                generated_licenses = json.load(f)

            for entry in generated_licenses:
                self.assertTrue(os.path.isfile(entry))
