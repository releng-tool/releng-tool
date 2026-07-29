# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os


TEMPLATE = 'sbom-exclude'
SBOM_FILE = 'sbom-spdx.json'


class TestSbomExclude(RelengToolTestCase):
    def test_sbom_exclude(self):
        config = {
            'action': 'sbom',
            'sbom_format': ['json-spdx'],
        }

        with prepare_testenv(config=config, template=TEMPLATE) as engine:
            rv = engine.run()
            self.assertTrue(rv)

            sbom_file = os.path.join(engine.opts.out_dir, SBOM_FILE)
            self.assertTrue(os.path.exists(sbom_file))

            with open(sbom_file) as f:
                data = json.load(f)

            self.assertIn('packages', data)
            packages = data['packages']

            for pkg in packages:
                self.assertIn('name', pkg)
                pkg_name = pkg['name']

                if pkg_name == 'test-a':
                    raise RuntimeError('test-a should not be captured')

                if pkg_name != 'test-b':
                    raise RuntimeError('unknown package')
