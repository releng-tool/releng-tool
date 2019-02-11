#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from releng.util.file_flags import FileFlag
from releng.util.file_flags import processFileFlag
from test import RelengTestUtil
import os
import unittest

class TestFileFlags(unittest.TestCase):
    def test_ff_create(self):
        with RelengTestUtil.prepareWorkdir() as work_dir:
            file = os.path.join(work_dir, 'flag-create')
            self.assertTrue(not os.path.exists(file))

            state = processFileFlag(True, file)
            self.assertEqual(state, FileFlag.CONFIGURED)
            self.assertTrue(os.path.exists(file))

    def test_ff_forced(self):
        with RelengTestUtil.prepareWorkdir() as work_dir:
            file = os.path.join(work_dir, 'flag-forced')
            self.assertTrue(not os.path.exists(file))

            state = processFileFlag(False, file)
            self.assertEqual(state, FileFlag.NO_EXIST)
            self.assertTrue(not os.path.exists(file))

            open(file, 'a').close()
            self.assertTrue(os.path.exists(file))
            state = processFileFlag(False, file)
            self.assertEqual(state, FileFlag.NO_EXIST)
            self.assertTrue(os.path.exists(file))

    def test_ff_read_existence(self):
        with RelengTestUtil.prepareWorkdir() as work_dir:
            file = os.path.join(work_dir, 'flag-exists')
            open(file, 'a').close()

            state = processFileFlag(None, file)
            self.assertEqual(state, FileFlag.EXISTS)
            self.assertTrue(os.path.exists(file))

    def test_ff_read_not_exists(self):
        with RelengTestUtil.prepareWorkdir() as work_dir:
            file = os.path.join(work_dir, 'flag-no-exist')
            self.assertTrue(not os.path.exists(file))

            state = processFileFlag(None, file)
            self.assertEqual(state, FileFlag.NO_EXIST)
            self.assertTrue(not os.path.exists(file))
