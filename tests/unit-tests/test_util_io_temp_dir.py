# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.util.io_temp_dir import temp_dir
from tests import RelengToolTestCase
import os
import sys
import tempfile


class TestUtilIoTempDir(RelengToolTestCase):
    def run(self, result=None):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.work_dir = Path(tmpdir)
            super().run(result)

    def test_utilio_tempdir_encoded(self):
        base_dir = self.work_dir / 'base-dir'
        self.assertFalse(base_dir.exists())

        base_dir_encoded = os.fsencode(base_dir)
        with temp_dir(base_dir_encoded) as tmp_dir:
            new_dir = Path(tmp_dir)
            self.assertTrue(new_dir.is_dir())
            self.assertIn(base_dir, new_dir.parents)

        self.assertFalse(new_dir.is_dir())

    def test_utilio_tempdir_multipart(self):
        base_dir = self.work_dir / 'base-dir'
        self.assertFalse(base_dir.exists())

        expected_base = base_dir / 'part' / 'leaf'

        with temp_dir(base_dir, 'part', b'leaf') as tmp_dir:
            new_dir = Path(tmp_dir)
            self.assertTrue(new_dir.is_dir())
            self.assertIn(expected_base, new_dir.parents)

    def test_utilio_tempdir_path(self):
        base_dir = self.work_dir / 'base-dir'
        self.assertFalse(base_dir.exists())

        with temp_dir(base_dir) as tmp_dir:
            new_dir = Path(tmp_dir)
            self.assertTrue(new_dir.is_dir())
            self.assertIn(base_dir, new_dir.parents)

    def test_utilio_tempdir_str(self):
        base_dir = self.work_dir / 'base-dir'
        self.assertFalse(base_dir.exists())

        base_dir_str = str(base_dir)
        with temp_dir(base_dir_str) as tmp_dir:
            new_dir = Path(tmp_dir)
            self.assertTrue(new_dir.is_dir())
            self.assertIn(base_dir, new_dir.parents)

    def test_utilio_tempdir_working_directory(self):
        base_dir = self.work_dir / 'base-dir'

        with temp_dir(base_dir, wd=True) as tmp_dir:
            new_dir = Path(tmp_dir)
            self.assertTrue(new_dir.is_dir())

            cwd = Path.cwd()
            if sys.platform == 'darwin' and Path('/private') in cwd.parents:
                cwd = Path('/') / cwd.relative_to(*cwd.parts[:2])

            self.assertEqual(new_dir, cwd)
