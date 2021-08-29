# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

from tests import prepare_testenv
import os
import unittest

class TestPkgPipelineRemoteScripts(unittest.TestCase):
    def test_pkg_pipeline_remote_scripts_disabled_option(self):
        with prepare_testenv(template='remote-scripts-disabled') as engine:
            engine.run()
            self._assertFileFlag(engine, 'build-remote', False)
            self._assertFileFlag(engine, 'configure-remote', False)
            self._assertFileFlag(engine, 'install-remote', False)

    def test_pkg_pipeline_remote_scripts_disabled_quirk(self):
        config = {
            'quirk': [
                'releng.disable_remote_scripts',
            ],
        }
        with prepare_testenv(config=config, template='remote-scripts') as engine:
            engine.run()
            self._assertFileFlag(engine, 'build-remote', False)
            self._assertFileFlag(engine, 'configure-remote', False)
            self._assertFileFlag(engine, 'install-remote', False)

    def test_pkg_pipeline_remote_scripts_enabled(self):
        with prepare_testenv(template='remote-scripts') as engine:
            engine.run()
            self._assertFileFlag(engine, 'build-remote', True)
            self._assertFileFlag(engine, 'configure-remote', True)
            self._assertFileFlag(engine, 'install-remote', True)

    def test_pkg_pipeline_remote_scripts_override_all(self):
        with prepare_testenv(template='remote-scripts-override-all') as engine:
            engine.run()
            self._assertFileFlag(engine, 'build-override', True)
            self._assertFileFlag(engine, 'build-remote', False)
            self._assertFileFlag(engine, 'configure-override', True)
            self._assertFileFlag(engine, 'configure-remote', False)
            self._assertFileFlag(engine, 'install-override', True)
            self._assertFileFlag(engine, 'install-remote', False)

    def test_pkg_pipeline_remote_scripts_override_subset(self):
        with prepare_testenv(template='remote-scripts-override-subset') as engine:
            engine.run()
            self._assertFileFlag(engine, 'build-remote', True)
            self._assertFileFlag(engine, 'configure-remote', True)
            self._assertFileFlag(engine, 'install-override', True)
            self._assertFileFlag(engine, 'install-remote', False)

    def _assertFileFlag(self, engine, name, exists):
        file_flag = os.path.join(engine.opts.target_dir, name)
        self.assertEqual(os.path.exists(file_flag), exists)