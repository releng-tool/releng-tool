# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from contextlib import redirect_stderr
from contextlib import redirect_stdout
from io import StringIO
from releng_tool.__main__ import main
from tests import RelengToolTestCase
from unittest.mock import patch
import json


class TestApiMode(RelengToolTestCase):
    @patch('releng_tool.__main__.RelengEngine')
    @patch('releng_tool.__main__.releng_log_configuration')
    @patch('releng_tool.util.log.RELENG_LOG_APIMODE_FLAG', new=True)
    def test_api_mode_streams(self, lcfg, engine):
        stdout = StringIO()
        stderr = StringIO()

        with redirect_stdout(stdout), redirect_stderr(stderr):
            main([
                '--api',
            ])

        # verify api mode results are json parsable
        json.loads(stdout.getvalue())

        # verify banner (and other content) is on the standard error string
        self.assertIn('releng-tool ', stderr.getvalue())
