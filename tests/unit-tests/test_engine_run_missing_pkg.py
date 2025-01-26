# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolMissingPackageScript
from tests import RelengToolTestCase
from tests import prepare_testenv


class TestEngineRunMissingPkg(RelengToolTestCase):
    def test_engine_run_missing_pkg(self):
        with prepare_testenv(template='missing-pkg') as engine:
            with self.assertRaises(RelengToolMissingPackageScript):
                engine.run()
