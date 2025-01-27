# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.spdx import ConjunctiveLicenses
from releng_tool.util.spdx import DisjunctiveLicenses
from releng_tool.util.spdx import spdx_parse
from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os


TEMPLATE = 'spdx-expects'
SBOM_FILE = 'sbom-spdx.json'


class TestSpdxLicenseExpects(RelengToolTestCase):
    def test_spdx_license_expects(self):
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

                self.assertIn('licenseDeclared', pkg)
                parts = spdx_parse(pkg['licenseDeclared'])

                if pkg_name == 'test-a':
                    self._check_test_a(parts)
                elif pkg_name == 'test-b':
                    self._check_test_a(parts)
                else:
                    raise RuntimeError('unknown package')

    def _check_test_a(self, parts):
        self.assertIsInstance(parts, DisjunctiveLicenses)
        self.assertEqual(len(parts), 4)

        self.assertEqual(parts[0], 'Apache-2.0')
        self.assertEqual(parts[1], 'GPL-2.0-or-later')
        self.assertEqual(parts[2], 'BSD-2-Clause')

        self.assertIsInstance(parts[3], ConjunctiveLicenses)
        self.assertListEqual(parts[3], ['MPL-2.0', 'snprintf'])

    def _check_test_b(self, parts):
        self.assertIsInstance(parts, ConjunctiveLicenses)
        self.assertEqual(len(parts), 3)

        self.assertIsInstance(parts[0], DisjunctiveLicenses)
        self.assertListEqual(parts[0], ['Apache-2.0', 'GPL-2.0-or-later'])

        self.assertEqual(parts[1], 'BSD-2-Clause')

        self.assertIsInstance(parts[2], ConjunctiveLicenses)
        self.assertListEqual(parts[2], ['MPL-2.0', 'snprintf'])
