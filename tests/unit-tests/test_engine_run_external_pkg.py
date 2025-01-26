# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import copy_template
from tests import prepare_testenv
from tests import prepare_workdir
import os


class TestEngineExternalPkg(RelengToolTestCase):
    def test_engine_run_external_pkg(self):
        with prepare_testenv(template='extern-pkg-base') as engine, \
                prepare_workdir() as pkg_repo1, \
                prepare_workdir() as pkg_repo2:

            copy_template('extern-pkg-need1', pkg_repo1)
            copy_template('extern-pkg-need2', pkg_repo2)

            os.environ['RELENG_TOOL_TEST_NEED1'] = pkg_repo1
            os.environ['RELENG_TOOL_TEST_NEED2'] = pkg_repo2

            rv = engine.run()
            self.assertTrue(rv)

            target_dir = engine.opts.target_dir
            flag = os.path.join(target_dir, 'invoked-bootstrap-need1')
            self.assertTrue(os.path.exists(flag))

            target_dir = engine.opts.target_dir
            flag = os.path.join(target_dir, 'invoked-bootstrap-need2')
            self.assertTrue(os.path.exists(flag))
