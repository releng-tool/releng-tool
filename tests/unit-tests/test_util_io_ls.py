# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.util.io_ls import ls
from tests import RelengToolTestCase
from tests import prepare_workdir
from tests import redirect_stdout
import os


class TestUtilIoLs(RelengToolTestCase):
    def test_utilio_ls_invalid_directory(self):
        with redirect_stdout() as stream:
            listed = ls(Path(__file__))

        self.assertFalse(listed)
        self.assertEqual(stream.getvalue(), '')

    def test_utilio_ls_missing_directory(self):
        with redirect_stdout() as stream:
            listed = ls('missing-directory')

        self.assertFalse(listed)
        self.assertEqual(stream.getvalue(), '')

    def test_utilio_ls_valid_directory_contents_encoded(self):
        base_dir = Path(__file__).parent
        base_dir_encoded = os.fsencode(base_dir)

        with redirect_stdout() as stream:
            listed = ls(base_dir_encoded)

        self.assertTrue(listed)

        entries = stream.getvalue().split('\n')
        self.assertIn(f'assets{os.sep}', entries)
        self.assertIn('__init__.py', entries)
        self.assertIn('test_util_io_ls.py', entries)

    def test_utilio_ls_valid_directory_contents_path(self):
        base_dir = Path(__file__).parent

        with redirect_stdout() as stream:
            listed = ls(base_dir)

        self.assertTrue(listed)

        entries = stream.getvalue().split('\n')
        self.assertIn(f'assets{os.sep}', entries)
        self.assertIn('__init__.py', entries)
        self.assertIn('test_util_io_ls.py', entries)

    def test_utilio_ls_valid_directory_contents_str(self):
        base_dir = Path(__file__).parent
        base_dir_str = str(base_dir)

        with redirect_stdout() as stream:
            listed = ls(base_dir_str)

        self.assertTrue(listed)

        entries = stream.getvalue().split('\n')
        self.assertIn(f'assets{os.sep}', entries)
        self.assertIn('__init__.py', entries)
        self.assertIn('test_util_io_ls.py', entries)

    def test_utilio_ls_valid_directory_empty(self):
        with redirect_stdout() as stream:
            with prepare_workdir() as empty_dir:
                listed = ls(empty_dir)

        self.assertTrue(listed)
        self.assertEqual(stream.getvalue(), '')
