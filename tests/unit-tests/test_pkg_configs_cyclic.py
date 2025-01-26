# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages.exceptions import RelengToolCyclicPackageDependency
from tests import prepare_testenv
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsCyclic(TestPkgConfigsBase):
    def test_pkgconfig_cyclic_explicit_loading(self):
        pkg_names = [
            'test-a',
            'test-b',
            'test-c',
        ]

        with prepare_testenv(template='cyclic') as engine:
            with self.assertRaises(RelengToolCyclicPackageDependency):
                engine.pkgman.load(pkg_names)

    def test_pkgconfig_cyclic_implicit_loading(self):
        pkg_names = [
            'test-b',
        ]

        with prepare_testenv(template='cyclic') as engine:
            with self.assertRaises(RelengToolCyclicPackageDependency):
                engine.pkgman.load(pkg_names)

    def test_pkgconfig_cyclic_self(self):
        pkg_names = [
            'test-d',
        ]

        with prepare_testenv(template='cyclic') as engine:
            with self.assertRaises(RelengToolCyclicPackageDependency):
                engine.pkgman.load(pkg_names)
