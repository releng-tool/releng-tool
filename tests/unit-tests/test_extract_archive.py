# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.api import RelengExtractOptions
from releng_tool.extract.archive import extract
from releng_tool.tool.python import PYTHON
from tests import RelengToolTestCase
from tests import prepare_workdir
from tests.support import fetch_unittest_assets_dir
import json
import os
import posixpath


class TestExtractArchive(RelengToolTestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets_dir = fetch_unittest_assets_dir()
        cls.sample_files = os.path.join(cls.assets_dir, 'sample-files')

    def run(self, result=None):
        self.opts = RelengExtractOptions()
        self.opts.strip_count = 0

        with prepare_workdir() as work_dir:
            self.opts.work_dir = work_dir

            super().run(result)

    def test_extract_archive_override_invalid(self):
        cache_file = os.path.join(self.opts.work_dir, 'mock.dat')
        self.opts.cache_file = cache_file

        self.opts._extract_override = {
            'dat': os.path.join(self.opts.work_dir, 'missing-cmd'),
        }

        extracted = extract(self.opts)
        self.assertFalse(extracted)

    def test_extract_archive_override_valid(self):
        cache_file = os.path.join(self.opts.work_dir, 'mock.dat')
        self.opts.cache_file = cache_file

        override_cmd = os.path.join(self.assets_dir, 'test-invoke.py')
        self.opts._extract_override = {
            'dat': f'{PYTHON.tool} {override_cmd} {{file}} {{dir}}',
        }

        extracted = extract(self.opts)
        self.assertTrue(extracted)

        results = os.path.join(self.opts.work_dir, 'invoke-results.json')
        self.assertTrue(os.path.exists(results))

        with open(results) as f:
            data = json.load(f)

        self.assertTrue('args' in data)
        invoke_args = data['args']
        self.assertEqual(len(invoke_args), 3)
        self.assertEqual(invoke_args[0], override_cmd)
        self.assertEqual(invoke_args[1], cache_file)
        self.assertEqual(invoke_args[2], self.opts.work_dir)

    def test_extract_archive_tar_default(self):
        cache_file = os.path.join(self.sample_files, 'sample-files.tar')
        self.opts.cache_file = cache_file

        extracted = extract(self.opts)
        self.assertTrue(extracted)

        self._assertExtracted([
            'container/tar-file-container.txt',
            'container/',
            'tar-file-root',
        ])

    def test_extract_archive_tar_strip(self):
        cache_file = os.path.join(self.sample_files, 'sample-files.tgz')
        self.opts.cache_file = cache_file

        self.opts.strip_count = 1

        extracted = extract(self.opts)
        self.assertTrue(extracted)

        self._assertExtracted([
            'tgz-file-container.txt',
        ])

    def test_extract_archive_zip_default(self):
        cache_file = os.path.join(self.sample_files, 'sample-files.zip')
        self.opts.cache_file = cache_file

        extracted = extract(self.opts)
        self.assertTrue(extracted)

        self._assertExtracted([
            'container/zip-file-container.txt',
            'container/',
            'zip-file-root',
        ])

    def test_extract_archive_zip_strip(self):
        cache_file = os.path.join(self.sample_files, 'sample-files.zip')
        self.opts.cache_file = cache_file

        self.opts.strip_count = 1

        extracted = extract(self.opts)
        self.assertTrue(extracted)

        self._assertExtracted([
            'zip-file-container.txt',
        ])

    def _assertExtracted(self, required):
        entries = []
        for root, dirs, files in os.walk(self.opts.work_dir):
            for name in files:
                entries.append(os.path.join(root, name))

            for name in dirs:
                entries.append(os.path.join(root, name))

        found_entries = set()
        for entry in entries:
            relpath = os.path.relpath(entry, self.opts.work_dir)

            if os.path.isdir(entry):
                relpath += os.sep

            found_entries.add(relpath.replace(os.sep, posixpath.sep))

        required_set = set(required)
        missing = sorted(required_set.difference(found_entries))
        unknowns = sorted(found_entries.difference(required))

        if missing or unknowns:
            print(f'failed to verify extracted data: {self.opts.cache_file}')
            print()

        if missing:
            print('missing entries]')
            for entry in missing:
                print(entry)
            print()

        if unknowns:
            print('unknown entries]')
            for entry in unknowns:
                print(entry)
            print()

        self.assertTrue(not missing and not unknowns)
