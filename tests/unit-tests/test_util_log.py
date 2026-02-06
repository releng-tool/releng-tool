# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.log import note
from tests import redirect_stdout
from tests import RelengToolTestCase
import os


class TestUtilLog(RelengToolTestCase):
    def test_utilio_log_expanded(self):
        os.environ['KEYWORD'] = 'example'

        with redirect_stdout() as stream:
            note('this is an $KEYWORD message')

        self.assertIn('this is an example message', stream.getvalue())
