# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.io_copy import path_copy
from releng_tool.util.io_copy import path_copy_into
from tests import RelengToolTestCase
from tests import compare_contents
from tests import new_test_wd
from tests import prepare_workdir
from tests.support import fetch_unittest_assets_dir
import os
import platform
import shutil
import sys
import unittest


class TestUtilIoCopy(RelengToolTestCase):
    @classmethod
    def setUpClass(cls):
        cls.assets_dir = fetch_unittest_assets_dir()

        def assertExists(cls, path, *args):
            target = os.path.join(path, *args)
            cls.assertTrue(os.path.exists(target), 'missing file: ' + target)
        cls.assertExists = assertExists

    def test_utilio_copy(self):
        check_dir_01 = os.path.join(self.assets_dir, 'copy-check-01')
        check_dir_02 = os.path.join(self.assets_dir, 'copy-check-02')

        with prepare_workdir() as work_dir:
            # (directories)

            # copy the first batch of assets into the working directory
            result = path_copy(check_dir_01, work_dir, critical=False)
            self.assertTrue(result)
            self.assertExists(work_dir, 'test-file-a')
            self.assertExists(work_dir, 'test-file-b')
            self.assertExists(work_dir, 'test-file-x')
            cc1 = compare_contents(
                os.path.join(check_dir_01, 'test-file-b'),
                os.path.join(work_dir, 'test-file-b'))
            self.assertIsNone(cc1, cc1)

            # override the working directory with the second batch
            result = path_copy(check_dir_02, work_dir, critical=False)
            self.assertTrue(result)
            self.assertExists(work_dir, 'test-file-a')
            self.assertExists(work_dir, 'test-file-b')
            self.assertExists(work_dir, 'test-file-c')
            self.assertExists(work_dir, 'test-file-x')
            cc2 = compare_contents(
                os.path.join(check_dir_02, 'test-file-b'),
                os.path.join(work_dir, 'test-file-b'))
            self.assertIsNone(cc2, cc2)

            # (files)
            sub_dir = os.path.join(work_dir, 'sub', 'dir', 'xyz', '')
            copied_file_a = os.path.join(work_dir, 'test-file-a')
            copied_file_b = os.path.join(work_dir, 'test-file-b')
            target_ow = os.path.join(sub_dir, 'test-file-a')

            # copy individual files (file to new directory)
            result = path_copy(copied_file_a, sub_dir, critical=False)
            self.assertTrue(result)
            self.assertExists(target_ow)
            cc3 = compare_contents(copied_file_a, target_ow)
            self.assertIsNone(cc3, cc3)

            # copy individual files (overwrite)
            result = path_copy(copied_file_b, target_ow, critical=False)
            self.assertTrue(result)
            cc4 = compare_contents(copied_file_b, target_ow)
            self.assertIsNone(cc4, cc4)

            # force a directory target with a non-trailing path separator
            force_src = os.path.join(work_dir, 'test-file-a')
            self.assertExists(force_src)

            force1 = os.path.join(work_dir, 'force1')
            result = path_copy(force_src, force1, critical=False)
            self.assertTrue(result)
            self.assertTrue(os.path.isfile(force1))

            force2 = os.path.join(work_dir, 'force2')
            result = path_copy(force_src, force2, critical=False, dst_dir=True)
            self.assertTrue(result)
            self.assertTrue(os.path.isdir(force2))

            # copy entire contents of copy-check-02 into work folder
            result = path_copy(check_dir_02, work_dir, nested=True)
            self.assertTrue(result)
            self.assertExists(work_dir, 'copy-check-02')
            self.assertExists(work_dir, 'copy-check-02', 'test-file-b')
            self.assertExists(work_dir, 'copy-check-02', 'test-file-c')

    def test_utilio_copy_missing(self):
        with prepare_workdir() as work_dir:
            # attempt to copy a missing path
            missing_path = os.path.join(work_dir, 'test-path-missing')
            target = os.path.join(work_dir, 'container')
            result = path_copy(missing_path, target, critical=False)
            self.assertFalse(result)

            # attempt to copy a missing path (critical)
            with self.assertRaises(SystemExit):
                path_copy(missing_path, target)

    def test_utilio_copy_self(self):
        src_dir = os.path.join(self.assets_dir, 'copy-check-01')
        src_file = os.path.join(src_dir, 'test-file-a')

        with prepare_workdir() as work_dir:
            dst_file = os.path.join(work_dir, 'test-file')
            shutil.copyfile(src_file, dst_file)

            # attempt to copy a directory to itself
            with self.assertRaises(SystemExit):
                path_copy(work_dir, work_dir)

            # attempt to copy a file to itself
            with self.assertRaises(SystemExit):
                path_copy(dst_file, dst_file)

    def test_utilio_copy_symlink_directory(self):
        if platform.system() != 'Linux':
            raise unittest.SkipTest('symlink test skipped for non-Linux')

        src_dir = os.path.join(self.assets_dir, 'copy-check-01')
        src_file = os.path.join(src_dir, 'test-file-a')

        with prepare_workdir() as work_dir:
            subdir = os.path.join(work_dir, 'subdir')
            os.mkdir(subdir)

            dst_file = os.path.join(subdir, 'test-file')
            shutil.copyfile(src_file, dst_file)

            lnka_file = os.path.join(subdir, 'test-file-link-a')
            os.symlink(dst_file, lnka_file)

            subdir2 = os.path.join(work_dir, 'subdir2')
            path_copy(subdir, subdir2)

            lnkb_file = os.path.join(subdir2, 'test-file-link-a')
            read_lnk = os.readlink(lnkb_file)
            self.assertEqual(read_lnk, dst_file)

    def test_utilio_copy_symlink_file(self):
        if sys.platform == 'win32':
            raise unittest.SkipTest('symlink test skipped for win32')

        src_dir = os.path.join(self.assets_dir, 'copy-check-01')
        src_file = os.path.join(src_dir, 'test-file-a')

        with prepare_workdir() as work_dir:
            dst_file = os.path.join(work_dir, 'test-file')
            shutil.copyfile(src_file, dst_file)

            lnka_file = os.path.join(work_dir, 'test-file-link-a')
            os.symlink(dst_file, lnka_file)

            lnkb_file = os.path.join(work_dir, 'test-file-link-b')
            path_copy(lnka_file, lnkb_file)

            read_lnk = os.readlink(lnkb_file)
            self.assertEqual(read_lnk, dst_file)

    def test_utilio_copy_symlink_missing(self):
        if sys.platform == 'win32':
            raise unittest.SkipTest('symlink test skipped for win32')

        with new_test_wd():
            # copy a broken symlink
            os.symlink('nonexistent-a', 'new-symlink')
            self.assertTrue(os.path.islink('new-symlink'))

            read_lnk = os.readlink('new-symlink')
            self.assertEqual(read_lnk, 'nonexistent-a')

            path_copy('new-symlink', 'second-symlink')
            self.assertTrue(os.path.islink('second-symlink'))

            read_lnk = os.readlink('second-symlink')
            self.assertEqual(read_lnk, 'nonexistent-a')

            # copy directory that contains a broken symlink
            os.mkdir('container')
            os.symlink('nonexistent-b', 'container/sub-symlink')
            self.assertTrue(os.path.islink('container/sub-symlink'))

            read_lnk = os.readlink('container/sub-symlink')
            self.assertEqual(read_lnk, 'nonexistent-b')

            path_copy('container', 'second-container')
            self.assertTrue(os.path.islink('second-container/sub-symlink'))

            read_lnk = os.readlink('second-container/sub-symlink')
            self.assertEqual(read_lnk, 'nonexistent-b')

    def test_utilio_copy_symlink_replace(self):
        if sys.platform == 'win32':
            raise unittest.SkipTest('symlink test skipped for win32')

        with new_test_wd():
            os.symlink('entry-a', 'test-symlink')
            self.assertTrue(os.path.islink('test-symlink'))
            read_lnk = os.readlink('test-symlink')
            self.assertEqual(read_lnk, 'entry-a')

            os.symlink('entry-b', 'new-symlink')
            self.assertTrue(os.path.islink('new-symlink'))
            read_lnk = os.readlink('new-symlink')
            self.assertEqual(read_lnk, 'entry-b')

            path_copy('new-symlink', 'test-symlink')
            self.assertTrue(os.path.islink('test-symlink'))
            read_lnk = os.readlink('test-symlink')
            self.assertEqual(read_lnk, 'entry-b')

            os.mkdir('container')
            os.symlink('entry-c', 'container/sub-symlink')
            self.assertTrue(os.path.islink('container/sub-symlink'))
            read_lnk = os.readlink('container/sub-symlink')
            self.assertEqual(read_lnk, 'entry-c')

            os.mkdir('second-container')
            os.symlink('entry-d', 'second-container/sub-symlink')
            self.assertTrue(os.path.islink('second-container/sub-symlink'))
            read_lnk = os.readlink('second-container/sub-symlink')
            self.assertEqual(read_lnk, 'entry-d')

            path_copy('container', 'second-container')
            self.assertTrue(os.path.islink('second-container/sub-symlink'))
            read_lnk = os.readlink('container/sub-symlink')
            self.assertEqual(read_lnk, 'entry-c')

    def test_utilio_copyinto(self):
        check_dir_01 = os.path.join(self.assets_dir, 'copy-check-01')
        check_dir_02 = os.path.join(self.assets_dir, 'copy-check-02')

        with prepare_workdir() as work_dir:
            # (directories)

            # copy the first batch of assets into the working directory
            single_file = os.path.join(check_dir_01, 'test-file-a')

            result = path_copy_into(single_file, work_dir, critical=False)
            self.assertTrue(result)
            self.assertExists(work_dir, 'test-file-a')

            # copy the first batch of assets into the working directory
            result = path_copy_into(check_dir_01, work_dir, critical=False)
            self.assertTrue(result)
            self.assertExists(work_dir, 'test-file-a')
            self.assertExists(work_dir, 'test-file-b')
            self.assertExists(work_dir, 'test-file-x')
            cc1 = compare_contents(
                os.path.join(check_dir_01, 'test-file-b'),
                os.path.join(work_dir, 'test-file-b'))
            self.assertIsNone(cc1, cc1)

            # override the working directory with the second batch
            result = path_copy_into(check_dir_02, work_dir, critical=False)
            self.assertTrue(result)
            self.assertExists(work_dir, 'test-file-a')
            self.assertExists(work_dir, 'test-file-b')
            self.assertExists(work_dir, 'test-file-c')
            self.assertExists(work_dir, 'test-file-x')
            cc2 = compare_contents(
                os.path.join(check_dir_02, 'test-file-b'),
                os.path.join(work_dir, 'test-file-b'))
            self.assertIsNone(cc2, cc2)

            # attempt to copy to a file
            bad_target = os.path.join(work_dir, 'test-file-a')
            result = path_copy_into(check_dir_01, bad_target, critical=False)
            self.assertFalse(result)

            # copy entire contents of copy-check-01 into work folder
            result = path_copy_into(check_dir_01, work_dir, nested=True)
            self.assertTrue(result)
            self.assertExists(work_dir, 'copy-check-01')
            self.assertExists(work_dir, 'copy-check-01', 'test-file-a')
            self.assertExists(work_dir, 'copy-check-01', 'test-file-b')
            self.assertExists(work_dir, 'copy-check-01', 'test-file-x')

            with self.assertRaises(SystemExit):
                path_copy_into(check_dir_02, bad_target)
