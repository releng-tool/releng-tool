# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.util.io_step import FailedToPrepareStepError
from releng_tool.util.io_step import step
from tests import RelengToolTestCase
import os
import tempfile


class TestUtilIoStep(RelengToolTestCase):
    def run(self, result=None):
        with tempfile.TemporaryDirectory() as tmpdir:
            self.work_dir = Path(tmpdir)
            super().run(result)

    def test_utilio_step_default_outdir(self):
        expected_file_flag = self.work_dir / '.releng-tool-step-default-dir'
        self.assertFalse(expected_file_flag.is_file())

        global PKG_BUILD_OUTPUT_DIR
        PKG_BUILD_OUTPUT_DIR = self.work_dir

        for _ in step('default-dir'):
            pass

        del PKG_BUILD_OUTPUT_DIR

        expected_file_flag = self.work_dir / '.releng-tool-step-default-dir'
        self.assertTrue(expected_file_flag.is_file())

    def test_utilio_step_dir_encoded(self):
        workdir_encoded = os.fsencode(self.work_dir)

        step_invoked = False
        for _ in step('encoded', dir_=workdir_encoded):
            step_invoked = True

        self.assertTrue(step_invoked)

        expected_file_flag = self.work_dir / '.releng-tool-step-encoded'
        self.assertTrue(expected_file_flag.is_file())

        step_invoked = False
        for _ in step('encoded', dir_=workdir_encoded):
            step_invoked = True

        self.assertFalse(step_invoked)

    def test_utilio_step_dir_path(self):
        step_invoked = False
        for _ in step('path', dir_=self.work_dir):
            step_invoked = True

        self.assertTrue(step_invoked)

        expected_file_flag = self.work_dir / '.releng-tool-step-path'
        self.assertTrue(expected_file_flag.is_file())

        step_invoked = False
        for _ in step('path', dir_=self.work_dir):
            step_invoked = True

        self.assertFalse(step_invoked)

    def test_utilio_step_dir_str(self):
        workdir_str = str(self.work_dir)

        step_invoked = False
        for _ in step('str', dir_=workdir_str):
            step_invoked = True

        self.assertTrue(step_invoked)

        expected_file_flag = self.work_dir / '.releng-tool-step-str'
        self.assertTrue(expected_file_flag.is_file())

        step_invoked = False
        for _ in step('str', dir_=workdir_str):
            step_invoked = True

        self.assertFalse(step_invoked)

    def test_utilio_step_force(self):
        step_invoked = False

        for _ in step('rebuild', dir_=self.work_dir):
            step_invoked = True

        self.assertTrue(step_invoked)

        step_invoked = False

        for _ in step('rebuild', dir_=self.work_dir, force=True):
            step_invoked = True

        self.assertTrue(step_invoked)

    def test_utilio_step_multiple(self):
        step_invoked_one = False
        step_invoked_two = False

        for _ in step('one', dir_=self.work_dir):
            step_invoked_one = True

        for _ in step('two', dir_=self.work_dir):
            step_invoked_two = True

        self.assertTrue(step_invoked_one)
        self.assertTrue(step_invoked_two)

        step_invoked_one = False
        step_invoked_two = False

        for _ in step('two', dir_=self.work_dir):
            step_invoked_two = True

        for _ in step('one', dir_=self.work_dir):
            step_invoked_one = True

        self.assertFalse(step_invoked_one)
        self.assertFalse(step_invoked_two)

    def test_utilio_step_issue(self):
        with self.assertRaises(FailedToPrepareStepError):
            for _ in step('issue'):
                pass

        expected_file_flag = self.work_dir / '.releng-tool-step-issue'
        self.assertFalse(expected_file_flag.is_file())
