# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from tests import RelengToolTestCase
from tests import prepare_testenv
import os


class TestEngineRunNoPkgDef(RelengToolTestCase):
    def test_engine_run_nopkgdef(self):
        with prepare_testenv(template='package-without-pkgdef') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            file_flag = os.path.join(engine.opts.target_dir, 'build-triggered')
            self.assertTrue(os.path.exists(file_flag))