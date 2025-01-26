# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.io_symlink import symlink
from tests import new_test_wd
import posixpath
import os
import sys
import unittest


class TestUtilIoSymlink(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def assertLinkExists(cls, path, *args):
            target = os.path.join(path, *args)
            cls.assertTrue(os.path.islink(target), 'missing link: ' + target)
        cls.assertLinkExists = assertLinkExists

        def assertLinkMatches(cls, target, expected):
            link_value = os.readlink(target)
            if sys.platform == 'darwin':
                # macOS may include a `/private` prefix; ignore it
                link_value = link_value.replace('/private', '')
            elif sys.platform == 'win32':
                # Windows may include a `\\\\?` prefix (UNC path); ignore it
                link_value = link_value.replace('\\\\?\\', '')
            posix_link_value = link_value.replace(os.sep, posixpath.sep)
            posix_expected = expected.replace(os.sep, posixpath.sep)
            cls.assertEqual(posix_link_value, posix_expected)
        cls.assertLinkMatches = assertLinkMatches

        if not callable(getattr(os, 'symlink', None)):
            raise unittest.SkipTest('symlink not available')

        if sys.platform == 'win32':
            # [WinError 1314] A required privilege is not held by the client
            WINERROR_1314 = 1314

            try:
                with new_test_wd():
                    os.symlink('arg1', 'arg2')
            except OSError as ex:
                if ex.winerror == WINERROR_1314 or \
                        'symbolic link privilege not held' in str(ex):
                    raise unittest.SkipTest(
                        'symlink test skipped for Windows') from ex

    def test_utilio_symlink_absolute(self):
        with new_test_wd() as work_dir:
            rv1 = symlink(       'target1',        'my-link1', relative=False)
            rv2 = symlink('nested/target2',        'my-link2', relative=False)
            rv3 = symlink(       'target3', 'nested/my-link3', relative=False)

            self.assertTrue(rv1)
            self.assertTrue(rv2)
            self.assertTrue(rv3)

            self.assertLinkExists(       'my-link1')
            self.assertLinkExists(       'my-link2')
            self.assertLinkExists('nested/my-link3')

            target1_abspath = os.path.join(work_dir, 'target1')
            target2_abspath = os.path.join(work_dir, 'nested', 'target2')
            target3_abspath = os.path.join(work_dir, 'target3')

            self.assertLinkMatches(       'my-link1', target1_abspath)
            self.assertLinkMatches(       'my-link2', target2_abspath)
            self.assertLinkMatches('nested/my-link3', target3_abspath)

    def test_utilio_symlink_blocked(self):
        with new_test_wd():
            with open('already-exists', 'w'):
                pass

            with self.assertRaises(SystemExit):
                symlink('target', 'already-exists')

            created = symlink('target', 'already-exists', critical=False)
            self.assertFalse(created)

    def test_utilio_symlink_container(self):
        with new_test_wd():
            created = symlink('target', 'container', lpd=True)
            self.assertTrue(created)
            self.assertLinkExists('container/target')
            self.assertLinkMatches('container/target', '../target')

    def test_utilio_symlink_overwrite(self):
        with new_test_wd():
            created = symlink('target1', 'my-symlink')
            self.assertTrue(created)
            self.assertLinkExists('my-symlink')
            self.assertLinkMatches('my-symlink', 'target1')

            updated = symlink('target2', 'my-symlink')
            self.assertTrue(updated)
            self.assertLinkExists('my-symlink')
            self.assertLinkMatches('my-symlink', 'target2')

    def test_utilio_symlink_relative(self):
        with new_test_wd():
            rv1 = symlink(       'target1',        'my-link1')
            rv2 = symlink('nested/target2',        'my-link2')
            rv3 = symlink(       'target3', 'nested/my-link3')

            self.assertTrue(rv1)
            self.assertTrue(rv2)
            self.assertTrue(rv3)

            self.assertLinkExists(       'my-link1')
            self.assertLinkExists(       'my-link2')
            self.assertLinkExists('nested/my-link3')

            self.assertLinkMatches(       'my-link1',        'target1')
            self.assertLinkMatches(       'my-link2', 'nested/target2')
            self.assertLinkMatches('nested/my-link3',     '../target3')
