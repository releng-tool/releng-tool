# -*- coding: utf-8 -*-
# Copyright 2023 releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from tests import RelengToolTestCase
from tests import prepare_testenv
import os


SBOM_FILENAME = 'sbom'

SBOM_FILE_TYPES = [
    'csv',
    'html',
    'json',
    'txt',
    'xml',
]


class TestEngineRunSbom(RelengToolTestCase):
    def test_engine_run_sbom_all(self):
        with prepare_testenv(template='sbom-all') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = SBOM_FILE_TYPES

            self._check_expected_files(engine.opts.out_dir, expected)

    def test_engine_run_sbom_csv(self):
        with prepare_testenv(template='sbom-csv') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = [
                'csv',
            ]

            self._check_expected_files(engine.opts.out_dir, expected)

    def test_engine_run_sbom_default(self):
        with prepare_testenv(template='sbom-default') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = [
                'txt',
            ]

            self._check_expected_files(engine.opts.out_dir, expected)

    def test_engine_run_sbom_html(self):
        with prepare_testenv(template='sbom-html') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = [
                'html',
            ]

            self._check_expected_files(engine.opts.out_dir, expected)

    def test_engine_run_sbom_json(self):
        with prepare_testenv(template='sbom-json') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = [
                'json',
            ]

            self._check_expected_files(engine.opts.out_dir, expected)

    def test_engine_run_sbom_mixed(self):
        with prepare_testenv(template='sbom-mixed') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = [
                'html',
                'json',
            ]

            self._check_expected_files(engine.opts.out_dir, expected)

    def test_engine_run_sbom_text(self):
        with prepare_testenv(template='sbom-text') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = [
                'txt',
            ]

            self._check_expected_files(engine.opts.out_dir, expected)

    def test_engine_run_sbom_xml(self):
        with prepare_testenv(template='sbom-xml') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected = [
                'xml',
            ]

            self._check_expected_files(engine.opts.out_dir, expected)

    def _check_expected_files(self, out_dir, expected):
        unexpected = [e for e in SBOM_FILE_TYPES if e not in expected]

        for ext in expected:
            fname = '{}.{}'.format(SBOM_FILENAME, ext)
            sbom_file = os.path.join(out_dir, fname)
            self.assertTrue(os.path.exists(sbom_file))

        for ext in unexpected:
            fname = '{}.{}'.format(SBOM_FILENAME, ext)
            sbom_file = os.path.join(out_dir, fname)
            self.assertFalse(os.path.exists(sbom_file))
