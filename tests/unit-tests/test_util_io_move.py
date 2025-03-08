# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.util.io_move import path_move
from releng_tool.util.io_move import path_move_into
from tests import RelengToolTestCase
from tests import prepare_workdir
import os


class TestUtilIoMove(RelengToolTestCase):
    def run(self, result=None):
        with prepare_workdir() as work_dir:
            self.work_dir = work_dir

            super().run(result)

    def _(self, *args):
        return os.path.join(self.work_dir, *args)

    def test_utilio_move(self):
        # setup
        directories = [
            self._('dir1'),
            self._('dir2', 'dir3'),
            self._('dir4', 'dir5', 'dir6'),
            self._('dir20'),
            self._('dir22'),
        ]
        for dir_ in directories:
            os.makedirs(dir_)

        files = [
            self._('file1'),
            self._('dir2', 'file2'),
            self._('dir2', 'dir3', 'file3'),
            self._('dir4', 'file4'),
            self._('dir4', 'dir5', 'file5'),
            self._('dir4', 'dir5', 'dir6', 'file6'),
            self._('dir20', 'file30'),
            self._('dir20', 'file31'),
        ]
        for file in files:
            with open(file, 'a') as f:
                f.write(os.path.basename(file))

        # (simple file move)
        src = self._('file1')
        dst = self._('file7')
        moved = path_move(src, dst, critical=False)
        self.assertTrue(moved)
        self.assertFalse(os.path.isfile(src))
        self.assertTrue(os.path.isfile(dst))
        self._assertContents(dst, 'file1')

        # (another file move)
        src = self._('dir4', 'dir5', 'dir6', 'file6')
        dst = self._('dir9', 'dir10', 'file8')
        moved = path_move(src, dst, critical=False)
        self.assertTrue(moved)
        self.assertFalse(os.path.isfile(src))
        self.assertTrue(os.path.isfile(dst))
        self._assertContents(dst, 'file6')

        # (another file move)
        src = self._('dir9', 'dir10', 'file8')
        dst = self._('dir9', 'dir11', '')
        exp = self._('dir9', 'dir11', 'file8')
        moved = path_move(src, dst, critical=False)
        self.assertTrue(moved)
        self.assertFalse(os.path.isfile(src))
        self.assertTrue(os.path.isfile(exp))
        self._assertContents(exp, 'file6')

        # (overwriting file move)
        src = self._('dir2', 'file2')
        dst = self._('file7')
        moved = path_move(src, dst, critical=False)
        self.assertTrue(moved)
        self.assertFalse(os.path.isfile(src))
        self.assertTrue(os.path.isfile(dst))
        self._assertContents(dst, 'file2')

        # (bad file move attempt)
        src = self._('file7')
        dst_part = self._('dir4', 'file4')
        dst = self._(dst_part, 'bad')
        moved = path_move(src, dst, quiet=True, critical=False)
        self.assertFalse(moved)
        self.assertTrue(os.path.isfile(src))
        self.assertTrue(os.path.isfile(dst_part))

        # (bad directory move self container)
        src = self._('dir2')
        dst = self._('dir2', 'dir3')
        moved = path_move(src, dst, quiet=True, critical=False)
        self.assertFalse(moved)
        self.assertTrue(os.path.isdir(src))
        self.assertTrue(os.path.isdir(dst))

        # (simple directory move)
        src = self._('dir2', 'dir3')
        dst = self._('dir4')
        moved = path_move(src, dst, critical=False)
        self.assertTrue(moved)
        self.assertFalse(os.path.isdir(src))
        self.assertFalse(os.path.isdir(self._(dst, 'dir3')))
        self.assertTrue(os.path.isfile(self._(dst, 'file3')))
        self._assertContents(self._(dst, 'file3'), 'file3')

        # (another directory move)
        src = self._('dir4')
        dst = self._('dir9', 'dir10')
        moved = path_move(src, dst, critical=False)
        self.assertTrue(moved)
        self.assertFalse(os.path.isdir(src))
        self.assertTrue(os.path.isdir(dst))
        self.assertTrue(os.path.isfile(self._(dst, 'file3')))
        self.assertTrue(os.path.isfile(self._(dst, 'file4')))
        self.assertTrue(os.path.isdir(self._(dst, 'dir5')))
        self._assertContents(self._(dst, 'file3'), 'file3')
        self._assertContents(self._(dst, 'file4'), 'file4')

        # (nested directory move into non-existing directory)
        src = self._('dir20')
        dst = self._('dir21')
        moved = path_move(src, dst, nested=True)
        self.assertTrue(moved)
        self.assertFalse(os.path.exists(src))
        self.assertTrue(os.path.isfile(self._(dst, 'dir20', 'file30')))
        self.assertTrue(os.path.isfile(self._(dst, 'dir20', 'file31')))
        self._assertContents(self._(dst, 'dir20', 'file30'), 'file30')
        self._assertContents(self._(dst, 'dir20', 'file31'), 'file31')

        # (nested directory move into existing directory)
        src = self._('dir21')
        dst = self._('dir22')
        moved = path_move(src, dst, nested=True)
        self.assertTrue(moved)
        self.assertFalse(os.path.exists(src))
        self.assertTrue(os.path.isfile(self._(dst, 'dir21', 'dir20', 'file30')))
        self.assertTrue(os.path.isfile(self._(dst, 'dir21', 'dir20', 'file31')))
        self._assertContents(self._(dst, 'dir21', 'dir20', 'file30'), 'file30')
        self._assertContents(self._(dst, 'dir21', 'dir20', 'file31'), 'file31')

        # (check directory replacing a file)
        src = self._('dir9')
        dst = self._('file7')
        self.assertTrue(os.path.isdir(src))
        self.assertTrue(os.path.isfile(dst))
        moved = path_move(src, dst, quiet=True, critical=False)
        self.assertTrue(moved)
        self.assertFalse(os.path.isdir(src))
        self.assertTrue(os.path.isdir(dst))

    def test_utilio_move_into(self):
        # setup
        directories = [
            self._('dir1', 'dir2'),
            self._('dir3'),
            self._('dir4', 'dir5', 'dir6'),
            self._('dir20'),
            self._('dir22'),
        ]
        for dir_ in directories:
            os.makedirs(dir_)

        files = [
            self._('file1'),
            self._('dir1', 'dir2', 'file2'),
            self._('dir3', 'file3'),
            self._('dir4', 'file4'),
            self._('dir4', 'dir5', 'file5'),
            self._('dir4', 'dir5', 'dir6', 'file6'),
            self._('dir20', 'file30'),
            self._('dir20', 'file31'),
        ]
        for file in files:
            with open(file, 'a') as f:
                f.write(os.path.basename(file))

        # (file move)
        src = self._('file1')
        dst = self._('dir4', 'dir5')
        expected = self._('dir4', 'dir5', 'file1')
        moved = path_move_into(src, dst, critical=False)
        self.assertTrue(moved)
        self.assertFalse(os.path.exists(src))
        self.assertTrue(os.path.isfile(expected))
        self._assertContents(expected, 'file1')

        # (directory move)
        src = self._('dir4', 'dir5')
        dst = self._('dir7', 'dir10')
        moved = path_move_into(src, dst, critical=False)
        self.assertTrue(moved)
        self.assertFalse(os.path.exists(src))
        self.assertTrue(os.path.isfile(self._(dst, 'file5')))
        self.assertTrue(os.path.isfile(self._(dst, 'dir6', 'file6')))
        self._assertContents(self._(dst, 'file5'), 'file5')
        self._assertContents(self._(dst, 'dir6', 'file6'), 'file6')

        # (another file move)
        src = self._('dir3')
        dst = self._('dir9', 'dir11', '')
        moved = path_move_into(src, dst, critical=False)
        self.assertTrue(moved)
        self.assertFalse(os.path.exists(src))
        self.assertTrue(os.path.isfile(self._('dir9', 'dir11', 'file3')))
        self._assertContents(self._('dir9', 'dir11', 'file3'), 'file3')

        # (nested directory move into non-existing directory)
        src = self._('dir20')
        dst = self._('dir21')
        moved = path_move_into(src, dst, nested=True)
        self.assertTrue(moved)
        self.assertFalse(os.path.exists(src))
        self.assertTrue(os.path.isfile(self._(dst, 'dir20', 'file30')))
        self.assertTrue(os.path.isfile(self._(dst, 'dir20', 'file31')))
        self._assertContents(self._(dst, 'dir20', 'file30'), 'file30')
        self._assertContents(self._(dst, 'dir20', 'file31'), 'file31')

        # (nested directory move into existing directory)
        src = self._('dir21')
        dst = self._('dir22')
        moved = path_move_into(src, dst, nested=True)
        self.assertTrue(moved)
        self.assertFalse(os.path.exists(src))
        self.assertTrue(os.path.isfile(self._(dst, 'dir21', 'dir20', 'file30')))
        self.assertTrue(os.path.isfile(self._(dst, 'dir21', 'dir20', 'file31')))
        self._assertContents(self._(dst, 'dir21', 'dir20', 'file30'), 'file30')
        self._assertContents(self._(dst, 'dir21', 'dir20', 'file31'), 'file31')

    def test_utilio_move_invalid_nest(self):
        # setup
        directories = [
            self._('dir1', 'dir2'),
        ]
        for dir_ in directories:
            os.makedirs(dir_)

        files = [
            self._('file1'),
            self._('dir1', 'file2'),
            self._('dir1', 'dir2', 'file3'),
        ]
        for file in files:
            with open(file, 'a') as f:
                f.write(os.path.basename(file))

        # attempt to into a parent folder into a child folder
        src_dir = os.path.join(self.work_dir, 'dir1')
        dst_dir = os.path.join(self.work_dir, 'dir1', 'dir2')
        result = path_move_into(src_dir, dst_dir, critical=False)
        self.assertFalse(result)

        # attempt to into a parent folder into a child folder (critical)
        with self.assertRaises(SystemExit):
            path_move_into(src_dir, dst_dir)

    def test_utilio_move_missing(self):
        # attempt to move a missing path
        missing_path = os.path.join(self.work_dir, 'test-path-missing')
        target = os.path.join(self.work_dir, 'container')
        result = path_move(missing_path, target, critical=False)
        self.assertFalse(result)

        # attempt to move a missing path (critical)
        with self.assertRaises(SystemExit):
            path_move(missing_path, target)

    def test_utilio_move_overwrite(self):
        # setup
        directories = [
            self._('d1', 'dz', 'entry'),
            self._('d3', 'dz'),
        ]
        for dir_ in directories:
            os.makedirs(dir_)

        files = [
            self._('d1', 'file1'),
            self._('d1', 'dz', 'file2'),
            self._('d1', 'dz', 'entry', 'file3'),
        ]

        for file in files:
            with open(file, 'a') as f:
                f.write('{}-A'.format(os.path.basename(file)))

        files = [
            self._('d3', 'file1'),
            self._('d3', 'dz', 'file2'),
            self._('d3', 'dz', 'entry'),
        ]

        for file in files:
            with open(file, 'a') as f:
                f.write('{}-B'.format(os.path.basename(file)))

        # move entire folder tree into a new base
        src_dir = self._('d1')
        dst_dir = self._('d2')
        result = path_move(src_dir, dst_dir, critical=False)
        self.assertTrue(result)
        self.assertFalse(os.path.isdir(src_dir))
        self.assertTrue(os.path.isdir(dst_dir))
        self._assertContents(self._('d2', 'file1'), 'file1-A')
        self._assertContents(self._('d2', 'dz', 'file2'), 'file2-A')
        self._assertContents(self._('d2', 'dz', 'entry', 'file3'), 'file3-A')

        # move entire folder tree into an existing base to override files
        self._assertContents(self._('d3', 'file1'), 'file1-B')
        self._assertContents(self._('d3', 'dz', 'file2'), 'file2-B')
        self._assertContents(self._('d3', 'dz', 'entry'), 'entry-B')

        src_dir = self._('d2')
        dst_dir = self._('d3')
        result = path_move(src_dir, dst_dir, critical=False)
        self.assertTrue(result)
        self.assertFalse(os.path.exists(src_dir))
        self.assertTrue(os.path.isdir(dst_dir))
        self._assertContents(self._('d3', 'file1'), 'file1-A')
        self._assertContents(self._('d3', 'dz', 'file2'), 'file2-A')
        self._assertContents(self._('d3', 'dz', 'entry', 'file3'), 'file3-A')

    def test_utilio_move_to_self(self):
        path = self._('dir1')
        os.makedirs(path)

        # attempt to move to itself; ignore it
        result = path_move(path, path)
        self.assertTrue(result)

    def test_utilio_move_types(self):
        path1 = self._('dir1')
        path2 = self._('dir2')
        path3 = self._('dir3')
        path4 = self._('dir4')
        os.makedirs(path1)
        self.assertTrue(os.path.isdir(path1))

        result = path_move(Path(path1), Path(path2))
        self.assertTrue(result)
        self.assertFalse(os.path.isdir(path1))
        self.assertTrue(os.path.isdir(path2))

        result = path_move(str(path2), str(path3))
        self.assertTrue(result)
        self.assertFalse(os.path.isdir(path2))
        self.assertTrue(os.path.isdir(path3))

        result = path_move(os.fsencode(path3), os.fsencode(path4))
        self.assertTrue(result)
        self.assertFalse(os.path.isdir(path3))
        self.assertTrue(os.path.isdir(path4))

    def _assertContents(self, f, data):
        contents = ''

        with open(f, encoding='utf_8') as file:
            for line in file:
                contents += line.strip() + '\n'

        contents = contents.strip()
        self.assertEqual(contents, data)
