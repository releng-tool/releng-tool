# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.util.io_cat import cat
from tests import prepare_workdir
from tests import redirect_stdout
from tests import RelengToolTestCase
import os


class TestUtilIoCat(RelengToolTestCase):
    def test_utilio_cat_invalid_file(self):
        with redirect_stdout() as stream:
            with prepare_workdir() as test_dir:
                output = cat(test_dir)

        self.assertFalse(output)
        self.assertEqual(stream.getvalue(), '')

    def test_utilio_cat_missing_file(self):
        with redirect_stdout() as stream:
            with prepare_workdir() as test_dir:
                missing_file = Path(test_dir) / 'missing-file'

                output = cat(missing_file)

        self.assertFalse(output)
        self.assertEqual(stream.getvalue(), '')

    def test_utilio_cat_valid_contents_multiple(self):
        with redirect_stdout() as stream:
            with prepare_workdir() as test_dir:
                test_file1 = Path(test_dir) / 'test1'
                with test_file1.open('w') as f:
                    f.write('1')

                test_file2 = Path(test_dir) / 'test2'
                with test_file2.open('w') as f:
                    f.write('2')

                test_file3 = Path(test_dir) / 'test3'
                with test_file3.open('w') as f:
                    f.write('3')

                output = cat(test_file1, test_file2, test_file3)

        self.assertTrue(output)
        self.assertEqual(stream.getvalue(), '123')

    def test_utilio_cat_valid_contents_single_encoded(self):
        with redirect_stdout() as stream:
            with prepare_workdir() as test_dir:
                test_file = Path(test_dir) / 'test'

                with test_file.open('w') as f:
                    f.write('this is a test')

                test_file_encoded = os.fsencode(test_file)
                output = cat(test_file_encoded)

        self.assertTrue(output)
        self.assertEqual(stream.getvalue(), 'this is a test')

    def test_utilio_cat_valid_contents_single_path(self):
        with redirect_stdout() as stream:
            with prepare_workdir() as test_dir:
                test_file = Path(test_dir) / 'test'

                with test_file.open('w') as f:
                    f.write('this is a test')

                output = cat(test_file)

        self.assertTrue(output)
        self.assertEqual(stream.getvalue(), 'this is a test')

    def test_utilio_cat_valid_contents_single_str(self):
        with redirect_stdout() as stream:
            with prepare_workdir() as test_dir:
                test_file = Path(test_dir) / 'test'

                with test_file.open('w') as f:
                    f.write('this is a test')

                test_file_str = str(test_file)
                output = cat(test_file_str)

        self.assertTrue(output)
        self.assertEqual(stream.getvalue(), 'this is a test')

    def test_utilio_cat_valid_empty(self):
        with redirect_stdout() as stream:
            with prepare_workdir() as test_dir:
                test_file = Path(test_dir) / 'test'

                with test_file.open('w'):
                    pass  # empty

                output = cat(test_file)

        self.assertTrue(output)
        self.assertEqual(stream.getvalue(), '')
