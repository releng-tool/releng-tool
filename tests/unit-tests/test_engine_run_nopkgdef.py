# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import os


class TestEngineRunNoPkgDef(RelengToolTestCase):
    def test_engine_run_nopkgdef_default(self):
        with prepare_testenv(template='package-without-pkgdef') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flag = os.path.join(engine.opts.target_dir, 'build-triggered')
            self.assertTrue(os.path.exists(file_flag))

    def test_engine_run_nopkgdef_depend(self):
        with prepare_testenv(template='package-without-pkgdef-deps') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flag = os.path.join(engine.opts.target_dir, 'build-triggered')
            self.assertTrue(os.path.exists(file_flag))
