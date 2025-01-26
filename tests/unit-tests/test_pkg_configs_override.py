# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.opts import RelengEngineOptions
from releng_tool.packages.manager import RelengPackageManager
from releng_tool.registry import RelengRegistry
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsOverride(TestPkgConfigsBase):
    def test_pkgconfig_override_configured(self):
        # provide an override for the package's revision
        opts = RelengEngineOptions()
        opts.injected_kv = {
            'TEST_REVISION': 'overridden',
        }

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg, _, _ = self.LOAD('override-check', manager=manager)
        self.assertEqual(pkg.revision, 'overridden')

    def test_pkgconfig_override_notconfigured(self):
        pkg, _, _ = self.LOAD('override-check')
        self.assertEqual(pkg.revision, 'no-override')
