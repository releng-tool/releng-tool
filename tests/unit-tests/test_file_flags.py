# -*- coding: utf-8 -*-
# Copyright 2018-2023 releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.util.file_flags import FileFlag
from releng_tool.util.file_flags import process_file_flag
from tests import prepare_workdir
import os
import unittest


class TestFileFlags(unittest.TestCase):
    def test_ff_create(self):
        with prepare_workdir() as work_dir:
            file = os.path.join(work_dir, 'flag-create')
            self.assertTrue(not os.path.exists(file))

            state = process_file_flag(file, flag=True)
            self.assertEqual(state, FileFlag.CONFIGURED)
            self.assertTrue(os.path.exists(file))

    def test_ff_forced(self):
        with prepare_workdir() as work_dir:
            file = os.path.join(work_dir, 'flag-forced')
            self.assertTrue(not os.path.exists(file))

            state = process_file_flag(file, flag=False)
            self.assertEqual(state, FileFlag.NO_EXIST)
            self.assertTrue(not os.path.exists(file))

            open(file, 'ab').close()
            self.assertTrue(os.path.exists(file))
            state = process_file_flag(file, flag=False)
            self.assertEqual(state, FileFlag.NO_EXIST)
            self.assertTrue(os.path.exists(file))

    def test_ff_read_existence(self):
        with prepare_workdir() as work_dir:
            file = os.path.join(work_dir, 'flag-exists')
            open(file, 'ab').close()

            state = process_file_flag(file, flag=None)
            self.assertEqual(state, FileFlag.EXISTS)
            self.assertTrue(os.path.exists(file))

    def test_ff_read_not_exists(self):
        with prepare_workdir() as work_dir:
            file = os.path.join(work_dir, 'flag-no-exist')
            self.assertTrue(not os.path.exists(file))

            state = process_file_flag(file, flag=None)
            self.assertEqual(state, FileFlag.NO_EXIST)
            self.assertTrue(not os.path.exists(file))
