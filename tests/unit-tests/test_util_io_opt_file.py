# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.io_opt_file import opt_file
from tests import RelengToolTestCase
from tests import prepare_workdir
from tests import redirect_stdout
import os


class TestUtilIo(RelengToolTestCase):
    def run(self, result=None):
        with prepare_workdir() as work_dir:
            self.work_dir = work_dir

            super().run(result)

    def test_utilio_optfile_find_legacy_no_ext(self):
        self._create_file('no-ext')

        with redirect_stdout() as stream:
            self._verify_expected('no-ext', 'no-ext')

        self.assertIn('deprecated file:', stream.getvalue())

    def test_utilio_optfile_find_legacy_releng_ext(self):
        self._create_file('releng-ext.releng')

        with redirect_stdout() as stream:
            self._verify_expected('releng-ext', 'releng-ext.releng')

        self.assertIn('deprecated file:', stream.getvalue())

    def test_utilio_optfile_find_py_ext(self):
        self._create_file('py-ext.py')
        self._verify_expected('py-ext', 'py-ext.py')

    def test_utilio_optfile_find_rt_ext(self):
        self._create_file('rt-ext.rt')
        self._verify_expected('rt-ext', 'rt-ext.rt')

    def test_utilio_optfile_missing(self):
        self._verify_expected('missing', None)

    def test_utilio_optfile_priority_01_rt_over_py(self):
        self._create_file('priority-test.py')
        self._create_file('priority-test.rt')
        self._verify_expected('priority-test', 'priority-test.rt')

    def test_utilio_optfile_priority_02_py_over_none(self):
        self._create_file('priority-test')
        self._create_file('priority-test.py')
        self._verify_expected('priority-test', 'priority-test.py')

    def test_utilio_optfile_priority_03_none_over_releng(self):
        self._create_file('priority-test')
        self._create_file('priority-test.releng')
        self._verify_expected('priority-test', 'priority-test')

    def _create_file(self, name):
        with open(self._wd_file(name), 'a'):
            pass

    def _verify_expected(self, req, expected):
        src = self._wd_file(req)
        target, existence = opt_file(src)

        if expected:
            self.assertTrue(existence)
            self.assertEqual(target, self._wd_file(expected))
        else:
            self.assertFalse(existence)
            self.assertEqual(target, self._wd_file(f'{src}.rt'))

    def _wd_file(self, *args):
        return os.path.join(self.work_dir, *args)
