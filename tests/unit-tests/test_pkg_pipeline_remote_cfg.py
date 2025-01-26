# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import os


class TestPkgPipelineRemoteConfigs(RelengToolTestCase):
    def test_pkg_pipeline_remote_cfg_disabled_option(self):
        with prepare_testenv(template='remote-cfg-disabled') as engine:
            engine.run()
            self._assertFileFlagExists(engine, 'jobs-0')

    def test_pkg_pipeline_remote_cfg_disabled_quirk(self):
        config = {
            'quirk': [
                'releng.disable_remote_configs',
            ],
        }
        with prepare_testenv(config=config, template='remote-cfg') as engine:
            engine.run()
            self._assertFileFlagExists(engine, 'jobs-0')

    def test_pkg_pipeline_remote_cfg_enabled(self):
        with prepare_testenv(template='remote-cfg') as engine:
            engine.run()
            self._assertFileFlagExists(engine, 'jobs-1')

    def test_pkg_pipeline_remote_cfg_override(self):
        with prepare_testenv(template='remote-cfg-override') as engine:
            engine.run()
            self._assertFileFlagExists(engine, 'jobs-2')

    def _assertFileFlagExists(self, engine, name):
        file_flag = os.path.join(engine.opts.target_dir, name)
        self.assertTrue(os.path.exists(file_flag))
