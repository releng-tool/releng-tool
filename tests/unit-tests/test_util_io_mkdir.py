# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.util.io_mkdir import mkdir
from tests import RelengToolTestCase
from tests import prepare_workdir
import os


class TestUtilIoMkdir(RelengToolTestCase):
    def run(self, result=None):
        with prepare_workdir() as work_dir:
            self.work_dir = Path(work_dir)
            super().run(result)

    def test_utilio_mkdir_already_exists(self):
        result = mkdir(self.work_dir)
        self.assertEqual(result, self.work_dir)

    def test_utilio_mkdir_fail_on_file(self):
        new_file = self.work_dir / 'test-file'
        self.assertFalse(new_file.exists())

        with open(new_file, 'ab'):
            pass

        self.assertTrue(new_file.is_file())

        result = mkdir(new_file)
        self.assertIsNone(result)
        self.assertTrue(new_file.is_file())

    def test_utilio_mkdir_multipart(self):
        new_dir = self.work_dir / 'test-dir'
        self.assertFalse(new_dir.exists())

        expected_dir = new_dir / 'part' / 'leaf'

        result = mkdir(new_dir, 'part', b'leaf')
        self.assertEqual(result, expected_dir)
        self.assertTrue(expected_dir.is_dir())

    def test_utilio_mkdir_new_dir_encoded(self):
        new_dir = self.work_dir / 'test-dir'
        self.assertFalse(new_dir.exists())

        new_dir_encoded = os.fsencode(new_dir)
        result = mkdir(new_dir_encoded)
        self.assertEqual(result, new_dir)
        self.assertTrue(new_dir.is_dir())

    def test_utilio_mkdir_new_dir_path(self):
        new_dir = self.work_dir / 'test-dir'
        self.assertFalse(new_dir.exists())

        result = mkdir(new_dir)
        self.assertEqual(result, new_dir)
        self.assertTrue(new_dir.is_dir())

    def test_utilio_mkdir_new_dir_str(self):
        new_dir = self.work_dir / 'test-dir'
        self.assertFalse(new_dir.exists())

        new_dir_str = str(new_dir)
        result = mkdir(new_dir_str)
        self.assertEqual(result, new_dir)
        self.assertTrue(new_dir.is_dir())
