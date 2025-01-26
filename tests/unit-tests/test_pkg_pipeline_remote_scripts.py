# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import os


class TestPkgPipelineRemoteScripts(RelengToolTestCase):
    def test_pkg_pipeline_remote_scripts_deprecated(self):
        with prepare_testenv(template='remote-scripts-deprecated') as engine:
            engine.run()
            self._assertFileFlag(engine, 'build-remote', exists=True)
            self._assertFileFlag(engine, 'configure-remote', exists=True)
            self._assertFileFlag(engine, 'install-remote', exists=True)

    def test_pkg_pipeline_remote_scripts_disabled_option(self):
        with prepare_testenv(template='remote-scripts-disabled') as engine:
            engine.run()
            self._assertFileFlag(engine, 'build-remote', exists=False)
            self._assertFileFlag(engine, 'configure-remote', exists=False)
            self._assertFileFlag(engine, 'install-remote', exists=False)

    def test_pkg_pipeline_remote_scripts_disabled_quirk(self):
        conf = {
            'quirk': [
                'releng.disable_remote_scripts',
            ],
        }
        with prepare_testenv(config=conf, template='remote-scripts') as engine:
            engine.run()
            self._assertFileFlag(engine, 'build-remote', exists=False)
            self._assertFileFlag(engine, 'configure-remote', exists=False)
            self._assertFileFlag(engine, 'install-remote', exists=False)

    def test_pkg_pipeline_remote_scripts_enabled(self):
        with prepare_testenv(template='remote-scripts') as engine:
            engine.run()
            self._assertFileFlag(engine, 'build-remote', exists=True)
            self._assertFileFlag(engine, 'configure-remote', exists=True)
            self._assertFileFlag(engine, 'install-remote', exists=True)

    def test_pkg_pipeline_remote_scripts_none(self):
        with prepare_testenv(template='remote-scripts-none') as engine:
            rv = engine.run()
            self.assertTrue(rv)

    def test_pkg_pipeline_remote_scripts_override_all(self):
        with prepare_testenv(template='remote-scripts-override-all') as engine:
            engine.run()
            self._assertFileFlag(engine, 'build-override', exists=True)
            self._assertFileFlag(engine, 'build-remote', exists=False)
            self._assertFileFlag(engine, 'configure-override', exists=True)
            self._assertFileFlag(engine, 'configure-remote', exists=False)
            self._assertFileFlag(engine, 'install-override', exists=True)
            self._assertFileFlag(engine, 'install-remote', exists=False)

    def test_pkg_pipeline_remote_scripts_override_subset(self):
        template = 'remote-scripts-override-subset'
        with prepare_testenv(template=template) as engine:
            engine.run()
            self._assertFileFlag(engine, 'build-remote', exists=True)
            self._assertFileFlag(engine, 'configure-remote', exists=True)
            self._assertFileFlag(engine, 'install-override', exists=True)
            self._assertFileFlag(engine, 'install-remote', exists=False)

    def _assertFileFlag(self, engine, name, exists):
        file_flag = os.path.join(engine.opts.target_dir, name)
        self.assertEqual(os.path.exists(file_flag), exists)
