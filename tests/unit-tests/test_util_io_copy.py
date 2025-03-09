# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.util.io_copy import path_copy
from releng_tool.util.io_copy import path_copy_into
from releng_tool.util.io_temp_dir import temp_dir
from tests import RelengToolTestCase
from tests import compare_contents
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
        cls.assets_dir = Path(fetch_unittest_assets_dir())

        def assertExists(cls, path: Path, *args: Path):
            target = path.joinpath(*args)
            cls.assertTrue(target.exists(), f'missing file: {target}')
        cls.assertExists = assertExists

    def test_utilio_copy(self):
        check_dir_01 = self.assets_dir / 'copy-check-01'
        check_dir_02 = self.assets_dir / 'copy-check-02'

        with prepare_workdir() as work_dir:
            work_dir = Path(work_dir)

            # (directories)
            # copy the first batch of assets into the working directory
            result = path_copy(check_dir_01, work_dir, critical=False)
            self.assertTrue(result)
            self.assertExists(work_dir, 'test-file-a')
            self.assertExists(work_dir, 'test-file-b')
            self.assertExists(work_dir, 'test-file-x')
            cc1 = compare_contents(
                check_dir_01 / 'test-file-b',
                work_dir / 'test-file-b')
            self.assertIsNone(cc1, cc1)

            # override the working directory with the second batch
            result = path_copy(check_dir_02, work_dir, critical=False)
            self.assertTrue(result)
            self.assertExists(work_dir, 'test-file-a')
            self.assertExists(work_dir, 'test-file-b')
            self.assertExists(work_dir, 'test-file-c')
            self.assertExists(work_dir, 'test-file-x')
            cc2 = compare_contents(
                check_dir_02 / 'test-file-b',
                work_dir / 'test-file-b')
            self.assertIsNone(cc2, cc2)

            # (files)
            sub_dir = work_dir / 'sub' / 'dir' / 'xyz'
            copied_file_a = work_dir / 'test-file-a'
            copied_file_b = work_dir / 'test-file-b'
            target_ow = sub_dir / 'test-file-a'

            # copy individual files (file to new directory)
            result = path_copy(copied_file_a, f'{sub_dir}/', critical=False)
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
            force_src = work_dir / 'test-file-a'
            self.assertExists(force_src)

            force1 = work_dir / 'force1'
            result = path_copy(force_src, force1, critical=False)
            self.assertTrue(result)
            self.assertTrue(os.path.isfile(force1))

            force2 = work_dir / 'force2'
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
            work_dir = Path(work_dir)

            # attempt to copy a missing path
            missing_path = work_dir / 'test-path-missing'
            target = work_dir / 'container'
            result = path_copy(missing_path, target, critical=False)
            self.assertFalse(result)

            # attempt to copy a missing path (critical)
            with self.assertRaises(SystemExit):
                path_copy(missing_path, target)

    def test_utilio_copy_self(self):
        src_dir = self.assets_dir / 'copy-check-01'
        src_file = src_dir / 'test-file-a'

        with prepare_workdir() as work_dir:
            work_dir = Path(work_dir)

            dst_file = work_dir / 'test-file'
            shutil.copyfile(src_file, dst_file)

            # attempt to copy a directory to itself
            with self.assertRaises(SystemExit):
                path_copy(work_dir, work_dir)

            # attempt to copy a file to itself
            with self.assertRaises(SystemExit):
                path_copy(dst_file, dst_file)

    def test_utilio_copy_symlink_dir_nested(self):
        if platform.system() != 'Linux':
            raise unittest.SkipTest('symlink test skipped for non-Linux')

        with prepare_workdir() as work_dir:
            work_dir = Path(work_dir)

            example_dir = Path(work_dir) / 'example'
            example_dir.mkdir()

            subdir_dir = example_dir / 'subdir'
            subdir_dir.mkdir()

            example_file = subdir_dir / 'test-file'
            example_file.touch()
            self.assertExists(example_file)

            symlink_dir = Path(example_dir) / 'symlinked'
            symlink_dir.symlink_to(subdir_dir)
            self.assertTrue(symlink_dir.is_symlink())

            new_dir = Path(work_dir) / 'newdir'
            path_copy_into(example_dir, new_dir)

            new_subdir = new_dir / 'subdir'
            self.assertTrue(new_subdir.is_dir())

            new_symlinked = new_dir / 'symlinked'
            self.assertTrue(new_symlinked.is_symlink())

            new_example_file = new_symlinked / 'test-file'
            self.assertExists(new_example_file)

    def test_utilio_copy_symlink_dir_root(self):
        if platform.system() != 'Linux':
            raise unittest.SkipTest('symlink test skipped for non-Linux')

        with prepare_workdir() as work_dir:
            work_dir = Path(work_dir)

            example_dir = work_dir / 'example'
            example_dir.mkdir()

            example_file = example_dir / 'test-file'
            example_file.touch()
            self.assertExists(example_file)

            symlink_dir = work_dir / 'symlinked'
            symlink_dir.symlink_to(example_dir, target_is_directory=True)
            self.assertTrue(symlink_dir.is_symlink())

            example_file2 = symlink_dir / 'test-file'
            self.assertExists(example_file2)

            new_dir = work_dir / 'newdir'
            path_copy(symlink_dir, new_dir)
            self.assertTrue(new_dir.is_symlink())

            example_file3 = new_dir / 'test-file'
            self.assertExists(example_file3)

    def test_utilio_copy_symlink_file_nested(self):
        if platform.system() != 'Linux':
            raise unittest.SkipTest('symlink test skipped for non-Linux')

        src_dir = self.assets_dir / 'copy-check-01'
        src_file = src_dir / 'test-file-a'

        with prepare_workdir() as work_dir:
            work_dir = Path(work_dir)

            subdir = work_dir / 'subdir'
            os.mkdir(subdir)

            dst_file = subdir / 'test-file'
            shutil.copyfile(src_file, dst_file)

            lnka_file = subdir / 'test-file-link-a'
            os.symlink(dst_file, lnka_file)

            subdir2 = work_dir / 'subdir2'
            path_copy(subdir, subdir2)

            lnkb_file = subdir2 / 'test-file-link-a'
            read_lnk = lnkb_file.readlink()
            self.assertEqual(read_lnk, dst_file)

    def test_utilio_copy_symlink_file_root(self):
        if sys.platform == 'win32':
            raise unittest.SkipTest('symlink test skipped for win32')

        src_dir = self.assets_dir / 'copy-check-01'
        src_file = src_dir / 'test-file-a'

        with prepare_workdir() as work_dir:
            work_dir = Path(work_dir)

            dst_file = work_dir / 'test-file'
            shutil.copyfile(src_file, dst_file)

            lnka_file = work_dir / 'test-file-link-a'
            os.symlink(dst_file, lnka_file)

            lnkb_file = work_dir / 'test-file-link-b'
            path_copy(lnka_file, lnkb_file)

            read_lnk = lnkb_file.readlink()
            self.assertEqual(read_lnk, dst_file)

    def test_utilio_copy_symlink_missing(self):
        if sys.platform == 'win32':
            raise unittest.SkipTest('symlink test skipped for win32')

        with temp_dir(wd=True):
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

        with temp_dir(wd=True):
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
        check_dir_01 = self.assets_dir / 'copy-check-01'
        check_dir_02 = self.assets_dir / 'copy-check-02'

        with prepare_workdir() as work_dir:
            work_dir = Path(work_dir)

            # (directories)
            # copy the first batch of assets into the working directory
            single_file = check_dir_01 / 'test-file-a'

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
                check_dir_01 / 'test-file-b', work_dir /'test-file-b')
            self.assertIsNone(cc1, cc1)

            # override the working directory with the second batch
            result = path_copy_into(check_dir_02, work_dir, critical=False)
            self.assertTrue(result)
            self.assertExists(work_dir, 'test-file-a')
            self.assertExists(work_dir, 'test-file-b')
            self.assertExists(work_dir, 'test-file-c')
            self.assertExists(work_dir, 'test-file-x')
            cc2 = compare_contents(
                check_dir_02 / 'test-file-b', work_dir / 'test-file-b')
            self.assertIsNone(cc2, cc2)

            # attempt to copy to a file
            bad_target = work_dir / 'test-file-a'
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

    def test_utilio_copy_types(self):
        with prepare_workdir() as work_dir:
            work_dir = Path(work_dir)
            path1 = work_dir / 'dir1'
            path2 = work_dir / 'dir2'
            path3 = work_dir / 'dir3'
            path4 = work_dir / 'dir4'
            path1.mkdir()
            self.assertTrue(path1.is_dir())

            result = path_copy(Path(path1), Path(path2))
            self.assertTrue(result)
            self.assertTrue(path1.is_dir())
            self.assertTrue(path2.is_dir())

            result = path_copy(str(path2), str(path3))
            self.assertTrue(result)
            self.assertTrue(path2.is_dir())
            self.assertTrue(path3.is_dir())

            result = path_copy(os.fsencode(path3), os.fsencode(path4))
            self.assertTrue(result)
            self.assertTrue(path3.is_dir())
            self.assertTrue(path4.is_dir())
