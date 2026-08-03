# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.io_path import releng_register_env_path
from releng_tool.util.io_temp_dir import temp_dir
from tests import RelengToolTestCase
import os


class TestUtilIoPathRegisterEnvPath(RelengToolTestCase):
    def test_utilio_path_register_env_path_invalid_crtiical(self):
        with self.assertRaises(SystemExit):
            releng_register_env_path('RELENG_TOOL_TEST_BADPATH')

    def test_utilio_path_register_env_path_invalid_noncritical(self):
        rv = releng_register_env_path(
            'RELENG_TOOL_TEST_BADPATH', critical=False)
        self.assertFalse(rv)

    def test_utilio_path_register_env_path_prepend(self):
        with temp_dir() as tmp_dir:
            rv = releng_register_env_path(tmp_dir, prepend=True)
            self.assertTrue(rv)

            # path is first
            paths = os.environ['PATH'].split(os.pathsep)
            self.assertEqual(tmp_dir, paths[0])

    def test_utilio_path_register_env_path_single(self):
        with temp_dir() as tmp_dir:
            rv = releng_register_env_path(tmp_dir)
            self.assertTrue(rv)

            # register a second time
            rv = releng_register_env_path(tmp_dir)
            self.assertTrue(rv)

            # should still only have one
            paths = os.environ['PATH'].split(os.pathsep)
            self.assertEqual(paths.count(tmp_dir), 1)

    def test_utilio_path_register_env_path_valid(self):
        with temp_dir() as tmp_dir:
            rv = releng_register_env_path(tmp_dir)
            self.assertTrue(rv)
            self.assertIn(tmp_dir, os.environ['PATH'])
