# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.util.io_wd import wd
from tests import RelengToolTestCase
import os
import sys
import tempfile


class TestUtilIoWd(RelengToolTestCase):
    def run(self, result=None):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.work_dir = Path(tmpdir)
            super().run(result)

    def setUp(self):
        self.test_file_name = Path('example-releng-test-file')
        test_file = self.work_dir / self.test_file_name
        with test_file.open('wb'):
            pass

    def test_utilio_wd_encoded(self):
        workdir_encoded = os.fsencode(self.work_dir)
        with wd(workdir_encoded) as workdir:
            self.assertEqual(Path(workdir), self._fetch_cwd())
            self.assertEqual(Path(workdir), self.work_dir)
            self.assertTrue(self.test_file_name.is_file())

    def test_utilio_wd_path(self):
        with wd(self.work_dir) as workdir:
            self.assertEqual(Path(workdir), self._fetch_cwd())
            self.assertEqual(Path(workdir), self.work_dir)
            self.assertTrue(self.test_file_name.is_file())

    def test_utilio_wd_str(self):
        workdir_str = str(self.work_dir)
        with wd(workdir_str) as workdir:
            self.assertEqual(Path(workdir), self._fetch_cwd())
            self.assertEqual(Path(workdir), self.work_dir)
            self.assertTrue(self.test_file_name.is_file())

    def _fetch_cwd(self):
        cwd = Path.cwd()
        if sys.platform == 'darwin' and Path('/private') in cwd.parents:
            cwd = Path('/') / cwd.relative_to(*cwd.parts[:2])
        return cwd
