#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018-2019 releng-tool

from collections import OrderedDict
from releng.util.io import execute
from releng.util.io import interpretStemExtension as ise
from releng.util.io import pathCopy
from releng.util.io import pathExists
from releng.util.io import pathMove
from releng.util.io import prepare_arguments
from releng.util.io import prepare_definitions
from releng.util.io import prependShebangInterpreter as psi
from releng.util.io import touch
from test import RelengTestUtil
import os
import unittest

ASSETS_DIR = 'assets'

class TestUtilIo(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        base_dir = os.path.dirname(os.path.realpath(__file__))
        self.assets_dir = os.path.join(base_dir, ASSETS_DIR)

        def assertExists(self, path, *args):
            self.assertTrue(pathExists(path, *args),
                'missing file: ' + os.path.join(path, *args))
        self.assertExists = assertExists

    def test_utilio_copy(self):
        check_dir_01 = os.path.join(self.assets_dir, 'copy-check-01')
        check_dir_02 = os.path.join(self.assets_dir, 'copy-check-02')

        with RelengTestUtil.prepareWorkdir() as work_dir:
            # (directories)

            # copy the first batch of assets into the working directory
            result = pathCopy(check_dir_01, work_dir, critical=False)
            self.assertTrue(result)
            self.assertExists(work_dir, 'test-file-a')
            self.assertExists(work_dir, 'test-file-b')
            self.assertExists(work_dir, 'test-file-x')
            cc1 = RelengTestUtil.compare(
                os.path.join(check_dir_01, 'test-file-b'),
                os.path.join(work_dir, 'test-file-b'))
            self.assertIsNone(cc1, cc1)

            # override the working directory with the second batch
            result = pathCopy(check_dir_02, work_dir, critical=False)
            self.assertTrue(result)
            self.assertExists(work_dir, 'test-file-a')
            self.assertExists(work_dir, 'test-file-b')
            self.assertExists(work_dir, 'test-file-c')
            self.assertExists(work_dir, 'test-file-x')
            cc2 = RelengTestUtil.compare(
                os.path.join(check_dir_02, 'test-file-b'),
                os.path.join(work_dir, 'test-file-b'))
            self.assertIsNone(cc2, cc2)

            # (files)
            sub_dir = os.path.join(work_dir, 'sub', 'dir', 'xyz', '')
            copied_file_a = os.path.join(work_dir, 'test-file-a')
            copied_file_b = os.path.join(work_dir, 'test-file-b')
            target_ow = os.path.join(sub_dir, 'test-file-a')

            # copy individual files (file to new directory)
            result = pathCopy(copied_file_a, sub_dir, critical=False)
            self.assertTrue(result)
            self.assertExists(target_ow)
            cc3 = RelengTestUtil.compare(copied_file_a, target_ow)
            self.assertIsNone(cc3, cc3)

            # copy individual files (overwrite)
            result = pathCopy(copied_file_b, target_ow, critical=False)
            self.assertTrue(result)
            cc4 = RelengTestUtil.compare(copied_file_b, target_ow)
            self.assertIsNone(cc4, cc4)

    def test_utilio_execution(self):
        result = execute(None, quiet=True, critical=False)
        self.assertFalse(result)

        result = execute([], quiet=True, critical=False)
        self.assertFalse(result)

        test_cmd = ['python', '-c', 'print("Hello")']
        result = execute(test_cmd, quiet=True, critical=False)
        self.assertTrue(result)

        result = execute(['an_unknown_command'], quiet=True, critical=False)
        self.assertFalse(result)

    def test_utilio_ise(self):
        provided = 'my-file.txt'
        expected = ('my-file', 'txt')
        self.assertEquals(ise(provided), expected)

        provided = 'my-file.tar.Z'
        expected = ('my-file', 'tar.Z')
        self.assertEquals(ise(provided), expected)

        provided = 'my-file.tar.gz'
        expected = ('my-file', 'tar.gz')
        self.assertEquals(ise(provided), expected)

        provided = 'my-file.tar.xz'
        expected = ('my-file', 'tar.xz')
        self.assertEquals(ise(provided), expected)

        provided = 'my.file.name.dat'
        expected = ('my.file.name', 'dat')
        self.assertEquals(ise(provided), expected)

        provided = 'my-file'
        expected = ('my-file', None)
        self.assertEquals(ise(provided), expected)

        provided = None
        expected = (None, None)
        self.assertEquals(ise(provided), expected)

    def test_utilio_move(self):
        with RelengTestUtil.prepareWorkdir() as work_dir:
            def _(*args):
                return os.path.join(work_dir, *args)

            # setup
            directories = [
                _('dir1'),
                _('dir2', 'dir3'),
                _('dir4', 'dir5', 'dir6'),
            ]
            for dir in directories:
                os.makedirs(dir)

            files = [
                _('file1'),
                _('dir2', 'file2'),
                _('dir2', 'dir3', 'file3'),
                _('dir4', 'file4'),
                _('dir4', 'dir5', 'file5'),
                _('dir4', 'dir5', 'dir6', 'file6'),
            ]
            for file in files:
                with open(file, 'a') as f:
                    f.write(file)

            # (simple file move)
            src = _('file1')
            dst = _('file7')
            moved = pathMove(src, dst, critical=False)
            self.assertTrue(moved)
            self.assertFalse(os.path.isfile(src))
            self.assertTrue(os.path.isfile(dst))

            # (another file move)
            src = _('dir4', 'dir5', 'dir6', 'file6')
            dst = _('dir9', 'dir10', 'file8')
            moved = pathMove(src, dst, critical=False)
            self.assertTrue(moved)
            self.assertFalse(os.path.isfile(src))
            self.assertTrue(os.path.isfile(dst))

            # (another file move)
            src = _('dir9', 'dir10', 'file8')
            dst = _('dir9', 'dir11', '')
            moved = pathMove(src, dst, critical=False)
            self.assertTrue(moved)
            self.assertFalse(os.path.isfile(src))
            self.assertTrue(os.path.isfile(_('dir9', 'dir11', 'file8')))

            # (overwriting file move)
            src = _('dir2', 'file2')
            dst = _('file7')
            moved = pathMove(src, dst, critical=False)
            self.assertTrue(moved)
            self.assertFalse(os.path.isfile(src))
            self.assertTrue(os.path.isfile(dst))

            # (bad file move attempt)
            src = _('file7')
            dst_part = _('dir4', 'file4')
            dst = _(dst_part, 'bad')
            moved = pathMove(src, dst, quiet=True, critical=False)
            self.assertFalse(moved)
            self.assertTrue(os.path.isfile(src))
            self.assertTrue(os.path.isfile(dst_part))

            # (bad directory move self container)
            src = _('dir2')
            dst = _('dir2', 'dir3')
            moved = pathMove(src, dst, quiet=True, critical=False)
            self.assertFalse(moved)
            self.assertTrue(os.path.isdir(src))
            self.assertTrue(os.path.isdir(dst))

            # (simple directory move)
            src = _('dir2', 'dir3')
            dst = _('dir4')
            moved = pathMove(src, dst, critical=False)
            self.assertTrue(moved)
            self.assertFalse(os.path.isdir(src))
            self.assertFalse(os.path.isdir(_(dst, 'dir3')))
            self.assertTrue(os.path.isfile(_(dst, 'file3')))

            # (another directory move)
            src = _('dir4')
            dst = _('dir9', 'dir10')
            moved = pathMove(src, dst, critical=False)
            self.assertTrue(moved)
            self.assertFalse(os.path.isdir(src))
            self.assertTrue(os.path.isdir(dst))
            self.assertTrue(os.path.isfile(_(dst, 'file3')))
            self.assertTrue(os.path.isfile(_(dst, 'file4')))
            self.assertTrue(os.path.isdir(_(dst, 'dir5')))

            # (bad directory move into file)
            src = _('dir9')
            dst = _('file7')
            moved = pathMove(src, dst, quiet=True, critical=False)
            self.assertFalse(moved)
            self.assertTrue(os.path.isdir(src))
            self.assertTrue(os.path.isfile(dst))

    def test_utilio_prepare_helpers(self):
        prepared = prepare_arguments(None)
        expected = []
        self.assertEquals(prepared, expected)

        prepared = prepare_arguments({})
        expected = []
        self.assertEquals(prepared, expected)

        args = OrderedDict()
        args['foo'] = 'bar'
        args['xyz'] = ''
        prepared = prepare_arguments(args)
        expected = ['foo', 'bar', 'xyz']
        self.assertEquals(prepared, expected)

        args = OrderedDict()
        args['foo'] = 'bar'
        args['test'] = None
        prepared = prepare_arguments(args)
        expected = ['foo', 'bar']
        self.assertEquals(prepared, expected)

        prepared = prepare_definitions(None)
        expected = []
        self.assertEquals(prepared, expected)

        prepared = prepare_definitions({})
        expected = []
        self.assertEquals(prepared, expected)

        args = OrderedDict()
        args['foo'] = 'bar'
        args['xyz'] = ''
        prepared = prepare_definitions(args)
        expected = ['foo=bar', 'xyz']
        self.assertEquals(prepared, expected)

        args = OrderedDict()
        args['foo'] = 'bar'
        args['test'] = None
        prepared = prepare_definitions(args)
        expected = ['foo=bar']
        self.assertEquals(prepared, expected)

    def test_utilio_shebang_interpreter(self):
        si_dir = os.path.join(self.assets_dir, 'shebang-interpreter')
        si01 = [os.path.join(si_dir, 'interpreter')]
        si02 = [os.path.join(si_dir, 'interpreter-arg')]
        si03 = [os.path.join(si_dir, 'interpreter-args-multiple')]
        si04 = [os.path.join(si_dir, 'interpreter-extremely-long')]
        si05 = [os.path.join(si_dir, 'interpreter-whitespaces')]
        si06 = [os.path.join(si_dir, 'example.py')]

        # encode helper as helper utility will execute with encoded strings
        def E(val):
            rv = []
            for v in val:
                rv.append(v.encode())
            return rv

        # simple interpreter
        self.assertEquals(psi(si01), [b'interpreter'] + E(si01))
        # interpreter with a single argument
        self.assertEquals(psi(si02), [b'interpreter', b'arg'] + E(si02))
        # interpreter with a single argument (with whitespaces)
        self.assertEquals(psi(si03), [b'interpreter', b'arg1 arg2'] + E(si03))
        # too long of an interpreter
        self.assertEquals(psi(si04), si04)
        # interpreter with whitespaces
        self.assertEquals(psi(si05), [b'interpreter'] + E(si05))
        # real example of an interpreter
        self.assertEquals(psi(si06), [b'/usr/bin/env', b'python'] + E(si06))

    def test_utilio_touch(self):
        with RelengTestUtil.prepareWorkdir() as work_dir:
            test_file = os.path.join(work_dir, 'test-file')

            created = touch(test_file)
            self.assertTrue(created)

            exists = os.path.isfile(test_file)
            self.assertTrue(exists)

            updated = touch(test_file)
            self.assertTrue(updated)
