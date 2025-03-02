# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.util.io_remove import path_remove
from tests import RelengToolTestCase
from tests import mock_os_remove_permission_denied
from tests import prepare_workdir
import os
import sys


class TestUtilIoRemove(RelengToolTestCase):
    def run(self, result=None):
        with prepare_workdir() as work_dir:
            self.work_dir = Path(work_dir)
            super().run(result)

    def test_utilio_remove_arg_encoded(self):
        new_file = self.work_dir / 'test-file'
        self.assertFalse(new_file.exists())

        with open(new_file, 'ab'):
            pass

        self.assertTrue(new_file.is_file())

        new_file_encoded = os.fsencode(new_file)
        removed = path_remove(new_file_encoded)
        self.assertTrue(removed)
        self.assertFalse(new_file.is_file())

    def test_utilio_remove_arg_path(self):
        new_file = self.work_dir / 'test-file'
        self.assertFalse(new_file.exists())

        with open(new_file, 'ab'):
            pass

        self.assertTrue(new_file.is_file())

        removed = path_remove(new_file)
        self.assertTrue(removed)
        self.assertFalse(new_file.is_file())

    def test_utilio_remove_arg_str(self):
        new_file = self.work_dir / 'test-file'
        self.assertFalse(new_file.exists())

        with open(new_file, 'ab'):
            pass

        self.assertTrue(new_file.is_file())

        new_file_str = str(new_file)
        removed = path_remove(new_file_str)
        self.assertTrue(removed)
        self.assertFalse(new_file.is_file())

    def test_utilio_remove_default(self):
        def _(*args):
            return os.path.join(self.work_dir, *args)

        # setup
        directories = [
            _('dir1'),
            _('dir2', 'dir3'),
            _('dir4', 'dir5', 'dir6'),
        ]
        for dir_ in directories:
            os.makedirs(dir_)

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

        path = _('file7')
        removed = path_remove(path)
        self.assertTrue(removed)
        self.assertFalse(os.path.isfile(path))

        container = _('dir2')
        path = _(container, 'file2')
        removed = path_remove(path)
        self.assertTrue(removed)
        self.assertFalse(os.path.isfile(path))
        self.assertTrue(os.path.isdir(container))
        self.assertFalse(os.path.isfile(path))

        container = _('dir2')
        path = _(container, 'dir3')
        file = _(path, 'file3')
        removed = path_remove(path)
        self.assertTrue(removed)
        self.assertFalse(os.path.isdir(path))
        self.assertFalse(os.path.isfile(file))
        self.assertTrue(os.path.isdir(container))

        path = _('dir4')
        files = [
            _(path, 'file4'),
            _(path, 'dir5', 'file5'),
            _(path, 'dir5', 'dir6', 'file6'),
        ]
        removed = path_remove(path)
        self.assertTrue(removed)
        self.assertFalse(os.path.isdir(path))
        for file in files:
            self.assertFalse(os.path.isfile(file))

        # allow noop calls to be true
        path = _('missing')
        removed = path_remove(path)
        self.assertTrue(removed)

    def test_utilio_remove_failure(self):
        with mock_os_remove_permission_denied():
            def _(*args):
                return os.path.join(self.work_dir, *args)

            # setup
            directories = [
                _('dir1'),
                _('dir2'),
            ]
            for dir_ in directories:
                os.makedirs(dir_)

            files = [
                _('file1'),
                _('dir2', 'file2'),
            ]
            for file in files:
                with open(file, 'a') as f:
                    f.write(file)

            dir1 = _('dir1')
            file1 = _('file1')
            file2 = _('dir2', 'file2')

            self.assertTrue(os.path.exists(file1))
            removed = path_remove(file1)
            self.assertFalse(removed)
            self.assertTrue(os.path.exists(file1))

            self.assertTrue(os.path.exists(file2))
            removed = path_remove(file2)
            self.assertFalse(removed)
            self.assertTrue(os.path.exists(file2))

            self.assertTrue(os.path.exists(dir1))
            removed = path_remove(dir1)
            self.assertFalse(removed)
            self.assertTrue(os.path.exists(dir1))

    def test_utilio_remove_symlink(self):
        if sys.platform == 'win32':
            raise self.skipTest('symlink test skipped for win32')

        new_symlink = os.path.join(self.work_dir, 'test-symlink')
        os.symlink('dummy', new_symlink)
        self.assertTrue(os.path.islink(new_symlink))

        removed = path_remove(new_symlink)
        self.assertTrue(removed)

        self.assertFalse(os.path.islink(new_symlink))
        self.assertFalse(os.path.exists(new_symlink))
