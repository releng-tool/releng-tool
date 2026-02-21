# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv


class TestDefaultEngineBase(RelengToolTestCase):
    """
    a default engine setup unit test base

    Provides a base class for unit tests that want a releng-tool engine setup
    using a default/minimal configuration. This class avoids the need for
    projects to manually prepare a engine/template and use calls `setpkgcfg`
    and `setprjcfg` to make tweaks before starting an engine.

    Attributes:
        engine: the prepared engine
    """

    def run(self, result=None):
        """
        run the test

        Run the test, collecting the result into the TestResult object passed as
        result. See `unittest.TestCase.run()` for more details.

        Args:
            result (optional): the test result to populate
        """

        with self.env_wrap(), self.syspath_wrap():
            with prepare_testenv(template='minimal') as engine:
                self.engine = engine
                super().run(result)
