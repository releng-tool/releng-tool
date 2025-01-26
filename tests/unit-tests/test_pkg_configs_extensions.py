# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.api import RelengExtractExtensionInterface
from releng_tool.opts import RelengEngineOptions
from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from releng_tool.packages.exceptions import RelengToolUnknownExtractType
from releng_tool.packages.manager import RelengPackageManager
from releng_tool.registry import RelengRegistry
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsExtensions(TestPkgConfigsBase):
    def test_pkgconfig_ext_mods_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('ext-mods-invalid-type')

    def test_pkgconfig_ext_mods_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.ext_modifiers)

    def test_pkgconfig_ext_mods_valid(self):
        pkg, _, _ = self.LOAD('ext-mods-valid-empty')
        self.assertDictEqual(pkg.ext_modifiers, {})

        pkg, _, _ = self.LOAD('ext-mods-valid-data')
        self.assertDictEqual(pkg.ext_modifiers, {
            'mod1': 'value',
            'mod2': True,
            123: {
                'more': 'data',
            },
        })

    def test_pkgconfig_extract_type_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('extract-type-invalid-type')

    def test_pkgconfig_extract_type_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.extract_type)

    def test_pkgconfig_extract_type_registered(self):
        opts = RelengEngineOptions()
        registry = RelengRegistry()
        manager = RelengPackageManager(opts, registry)

        # register the custom extraction type
        class MockExtract(RelengExtractExtensionInterface):
            def extract(self, name, opts):
                return False

        CUSTOM_EXTRACT_NAME = 'ext-my-custom-extract-type'
        registry.add_extract_type(CUSTOM_EXTRACT_NAME, MockExtract)

        pkg, _, _ = self.LOAD('extract-type-valid', manager=manager)
        self.assertEqual(pkg.extract_type, CUSTOM_EXTRACT_NAME)

    def test_pkgconfig_extract_type_unregistered(self):
        with self.assertRaises(RelengToolUnknownExtractType):
            self.LOAD('extract-type-valid')
