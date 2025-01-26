# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.opts import RelengEngineOptions
from releng_tool.packages.manager import RelengPackageManager
from releng_tool.registry import RelengRegistry
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsExpand(TestPkgConfigsBase):
    def test_pkgconfig_expand_check01(self):
        pkg, _, _ = self.LOAD('expand')
        self.assertEqual(pkg.version, 'version')
        self.assertEqual(pkg.revision, 'revision')
        self.assertEqual(pkg.site, 'site-revision')

    def test_pkgconfig_expand_check02(self):
        opts = RelengEngineOptions()
        opts.devmode = 'version-lts'

        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        pkg, _, _ = self.LOAD('expand', manager=manager)
        self.assertEqual(pkg.version, 'version-lts')
        self.assertEqual(pkg.revision, 'version-lts')
        self.assertEqual(pkg.site, 'site-version-lts-archive')
