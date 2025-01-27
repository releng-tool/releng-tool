# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import PkgAction
from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os


class TestPkgPipelinePackageRestageFlags(RelengToolTestCase):
    def test_pkg_pipeline_pkg_restage_rebuild(self):
        action = PkgAction.REBUILD

        expected_keys = [
            'RELENG_REBUILD',
            'RELENG_REINSTALL',
        ]

        unexpected_keys = [
            'RELENG_RECONFIGURE',
        ]

        self._check_flags(action, expected_keys, unexpected_keys)

    def test_pkg_pipeline_pkg_restage_rebuild_only(self):
        action = PkgAction.REBUILD_ONLY

        expected_keys = [
            'RELENG_REBUILD',
        ]

        unexpected_keys = [
            'RELENG_RECONFIGURE',
            'RELENG_REINSTALL',
        ]

        self._check_flags(action, expected_keys, unexpected_keys)

    def test_pkg_pipeline_pkg_restage_reconfigure(self):
        action = PkgAction.RECONFIGURE

        expected_keys = [
            'RELENG_REBUILD',
            'RELENG_RECONFIGURE',
            'RELENG_REINSTALL',
        ]

        unexpected_keys = [
        ]

        self._check_flags(action, expected_keys, unexpected_keys)

    def test_pkg_pipeline_pkg_restage_reconfigure_only(self):
        action = PkgAction.RECONFIGURE_ONLY

        expected_keys = [
            'RELENG_RECONFIGURE',
        ]

        unexpected_keys = [
            'RELENG_REBUILD',
            'RELENG_REINSTALL',
        ]

        self._check_flags(action, expected_keys, unexpected_keys)

    def test_pkg_pipeline_pkg_restage_reinstall(self):
        action = PkgAction.REINSTALL

        expected_keys = [
            'RELENG_REINSTALL',
        ]

        unexpected_keys = [
            'RELENG_REBUILD',
            'RELENG_RECONFIGURE',
        ]

        self._check_flags(action, expected_keys, unexpected_keys)

    def _check_flags(self, action, expected_keys, unexpected_keys):
        config = {
            'action': 'test-' + action,
        }

        with prepare_testenv(config=config, template='env-capture') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            # extract environment variables
            capture = os.path.join(engine.opts.target_dir, 'invoke-env.json')
            self.assertTrue(os.path.exists(capture))

            with open(capture) as f:
                data = json.load(f)

            # verify that all expected variables are set
            for key in expected_keys:
                self.assertIn(key, data, 'missing ' + key)

            # verify that all unexpected variables are not set
            for key in unexpected_keys:
                self.assertNotIn(key, data, 'detected ' + key)
