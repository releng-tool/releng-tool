# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.util.io_touch import touch
from tests import RelengToolTestCase
from tests import prepare_workdir
import os


class TestUtilIoTouch(RelengToolTestCase):
    def run(self, result=None):
        with prepare_workdir() as work_dir:
            self.work_dir = Path(work_dir)
            super().run(result)

    def test_utilio_touch_already_exists(self):
        test_file = self.work_dir / 'test-file'
        with test_file.open('wb'):
            pass

        self.assertTrue(test_file.is_file())

        exists = touch(test_file)
        self.assertTrue(exists)
        self.assertTrue(test_file.is_file())

    def test_utilio_touch_multipart(self):
        container_dir = self.work_dir / 'test-dir'
        self.assertFalse(container_dir.exists())

        expected_file = container_dir / 'part' / 'leaf'

        exists = touch(container_dir, 'part', b'leaf')
        self.assertTrue(exists)
        self.assertTrue(expected_file.is_file())

    def test_utilio_touch_new_file_encoded(self):
        test_file = self.work_dir / 'test-file'
        self.assertFalse(test_file.is_file())

        test_file_encoded = os.fsencode(test_file)
        exists = touch(test_file_encoded)
        self.assertTrue(exists)
        self.assertTrue(test_file.is_file())

    def test_utilio_touch_new_file_path(self):
        test_file = self.work_dir / 'test-file'
        self.assertFalse(test_file.is_file())

        exists = touch(test_file)
        self.assertTrue(exists)
        self.assertTrue(test_file.is_file())

    def test_utilio_touch_new_file_str(self):
        test_file = self.work_dir / 'test-file'
        self.assertFalse(test_file.is_file())

        test_file_str = str(test_file)
        exists = touch(test_file_str)
        self.assertTrue(exists)
        self.assertTrue(test_file.is_file())
