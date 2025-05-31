# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os


SBOM_FILENAME = 'sbom'

SBOM_FILES = [
    SBOM_FILENAME + '.csv',
    SBOM_FILENAME + '.html',
    SBOM_FILENAME + '.json',
    SBOM_FILENAME + '-spdx.json',
    SBOM_FILENAME + '.txt',
    SBOM_FILENAME + '.xml',
    SBOM_FILENAME + '-spdx.xml',
]


class TestEngineRunSbom(RelengToolTestCase):
    def test_engine_run_sbom_all(self):
        with prepare_testenv(template='sbom-all') as engine:
            out_dir = engine.opts.out_dir

            rv = engine.run()
            self.assertTrue(rv)

            expected = SBOM_FILES

            self._check_expected_files(out_dir, expected)

            results = os.path.join(out_dir, 'generated-sbom.json')
            self.assertTrue(os.path.isfile(results))

            with open(results) as f:
                generated_sboms = json.load(f)

            self.assertEqual(len(generated_sboms), len(expected))

            for entry in generated_sboms:
                self.assertTrue(os.path.isfile(entry))

    def test_engine_run_sbom_csv(self):
        with prepare_testenv(template='sbom-csv') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = [
                SBOM_FILENAME + '.csv',
            ]

            self._check_expected_files(engine.opts.out_dir, expected)

    def test_engine_run_sbom_default(self):
        with prepare_testenv(template='sbom-default') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = [
                SBOM_FILENAME + '.txt',
            ]

            self._check_expected_files(engine.opts.out_dir, expected)

    def test_engine_run_sbom_html(self):
        with prepare_testenv(template='sbom-html') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = [
                SBOM_FILENAME + '.html',
            ]

            self._check_expected_files(engine.opts.out_dir, expected)

    def test_engine_run_sbom_json(self):
        with prepare_testenv(template='sbom-json') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = [
                SBOM_FILENAME + '.json',
            ]

            self._check_expected_files(engine.opts.out_dir, expected)

    def test_engine_run_sbom_json_spdx(self):
        with prepare_testenv(template='sbom-json-spdx') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = [
                SBOM_FILENAME + '-spdx.json',
            ]

            self._check_expected_files(engine.opts.out_dir, expected)

    def test_engine_run_sbom_mixed(self):
        with prepare_testenv(template='sbom-mixed') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = [
                SBOM_FILENAME + '.html',
                SBOM_FILENAME + '.json',
            ]

            self._check_expected_files(engine.opts.out_dir, expected)

    def test_engine_run_sbom_rdf_spdx(self):
        with prepare_testenv(template='sbom-rdf-spdx') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = [
                SBOM_FILENAME + '-spdx.xml',
            ]

            self._check_expected_files(engine.opts.out_dir, expected)

    def test_engine_run_sbom_text(self):
        with prepare_testenv(template='sbom-text') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = [
                SBOM_FILENAME + '.txt',
            ]

            self._check_expected_files(engine.opts.out_dir, expected)

    def test_engine_run_sbom_xml(self):
        with prepare_testenv(template='sbom-xml') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = [
                SBOM_FILENAME + '.xml',
            ]

            self._check_expected_files(engine.opts.out_dir, expected)

    def _check_expected_files(self, out_dir, expected):
        unexpected = [e for e in SBOM_FILES if e not in expected]

        for fname in expected:
            sbom_file = os.path.join(out_dir, fname)
            self.assertTrue(os.path.exists(sbom_file))

        for fname in unexpected:
            sbom_file = os.path.join(out_dir, fname)
            self.assertFalse(os.path.exists(sbom_file))
