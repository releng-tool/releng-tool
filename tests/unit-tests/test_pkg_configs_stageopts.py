# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsStageOpts(TestPkgConfigsBase):
    def test_pkgconfig_build_defs_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('build-defs-invalid-base-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('build-defs-invalid-key-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('build-defs-invalid-strs')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('build-defs-invalid-value-type')

    def test_pkgconfig_build_defs_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.build_defs)

        pkg, _, _ = self.LOAD('conf-defs-valid')
        self.assertIsNone(pkg.build_defs)

        pkg, _, _ = self.LOAD('install-defs-valid')
        self.assertIsNone(pkg.build_defs)

    def test_pkgconfig_build_defs_valid(self):
        pkg, _, _ = self.LOAD('build-defs-valid')
        self.assertDictEqual(pkg.build_defs, {
            'key1': 'val1',
            'key2': None,
            'key3': 'val3',
        })

    def test_pkgconfig_build_env_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('build-env-invalid-base-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('build-env-invalid-key-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('build-env-invalid-strs')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('build-env-invalid-value-type')

    def test_pkgconfig_build_env_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.build_env)

        pkg, _, _ = self.LOAD('conf-env-valid')
        self.assertIsNone(pkg.build_env)

        pkg, _, _ = self.LOAD('install-env-valid')
        self.assertIsNone(pkg.build_env)

    def test_pkgconfig_build_env_valid(self):
        pkg, _, _ = self.LOAD('build-env-valid')
        self.assertDictEqual(pkg.build_env, {
            'key1': 'val1',
            'key2': None,
            'key3': 'val3',
        })

    def test_pkgconfig_build_opts_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('build-opts-invalid-base-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('build-opts-invalid-key-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('build-opts-invalid-value-type')

    def test_pkgconfig_build_opts_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.build_opts)

        pkg, _, _ = self.LOAD('conf-opts-valid-dict')
        self.assertIsNone(pkg.build_opts)

        pkg, _, _ = self.LOAD('conf-opts-valid-str')
        self.assertIsNone(pkg.build_opts)

        pkg, _, _ = self.LOAD('conf-opts-valid-strs')
        self.assertIsNone(pkg.build_opts)

        pkg, _, _ = self.LOAD('install-opts-valid-dict')
        self.assertIsNone(pkg.build_opts)

        pkg, _, _ = self.LOAD('install-opts-valid-str')
        self.assertIsNone(pkg.build_opts)

        pkg, _, _ = self.LOAD('install-opts-valid-strs')
        self.assertIsNone(pkg.build_opts)

    def test_pkgconfig_build_opts_valid(self):
        pkg, _, _ = self.LOAD('build-opts-valid-dict')
        self.assertDictEqual(pkg.build_opts, {
            'key1': 'val1',
            'key2': None,
            'key3': 'val3',
        })

        pkg, _, _ = self.LOAD('build-opts-valid-str')
        self.assertDictEqual(pkg.build_opts, {
            'option': '',
        })

        pkg, _, _ = self.LOAD('build-opts-valid-strs')
        self.assertDictEqual(pkg.build_opts, {
            'option1': '',
            'option2': '',
            'option3': '',
        })

    def test_pkgconfig_conf_defs_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('conf-defs-invalid-base-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('conf-defs-invalid-key-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('conf-defs-invalid-strs')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('conf-defs-invalid-value-type')

    def test_pkgconfig_conf_defs_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.conf_defs)

        pkg, _, _ = self.LOAD('build-defs-valid')
        self.assertIsNone(pkg.conf_defs)

        pkg, _, _ = self.LOAD('install-defs-valid')
        self.assertIsNone(pkg.conf_defs)

    def test_pkgconfig_conf_defs_valid(self):
        pkg, _, _ = self.LOAD('conf-defs-valid')
        self.assertDictEqual(pkg.conf_defs, {
            'key1': 'val1',
            'key2': None,
            'key3': 'val3',
        })

    def test_pkgconfig_conf_env_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('conf-env-invalid-base-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('conf-env-invalid-key-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('conf-env-invalid-strs')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('conf-env-invalid-value-type')

    def test_pkgconfig_conf_env_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.conf_env)

        pkg, _, _ = self.LOAD('build-env-valid')
        self.assertIsNone(pkg.conf_env)

        pkg, _, _ = self.LOAD('install-env-valid')
        self.assertIsNone(pkg.conf_env)

    def test_pkgconfig_conf_env_valid(self):
        pkg, _, _ = self.LOAD('conf-env-valid')
        self.assertDictEqual(pkg.conf_env, {
            'key1': 'val1',
            'key2': None,
            'key3': 'val3',
        })

    def test_pkgconfig_conf_opts_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('conf-opts-invalid-base-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('conf-opts-invalid-key-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('conf-opts-invalid-value-type')

    def test_pkgconfig_conf_opts_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.conf_opts)

        pkg, _, _ = self.LOAD('build-opts-valid-dict')
        self.assertIsNone(pkg.conf_opts)

        pkg, _, _ = self.LOAD('build-opts-valid-str')
        self.assertIsNone(pkg.conf_opts)

        pkg, _, _ = self.LOAD('build-opts-valid-strs')
        self.assertIsNone(pkg.conf_opts)

        pkg, _, _ = self.LOAD('install-opts-valid-dict')
        self.assertIsNone(pkg.conf_opts)

        pkg, _, _ = self.LOAD('install-opts-valid-str')
        self.assertIsNone(pkg.conf_opts)

        pkg, _, _ = self.LOAD('install-opts-valid-strs')
        self.assertIsNone(pkg.conf_opts)

    def test_pkgconfig_conf_opts_valid(self):
        pkg, _, _ = self.LOAD('conf-opts-valid-dict')
        self.assertDictEqual(pkg.conf_opts, {
            'key1': 'val1',
            'key2': None,
            'key3': 'val3',
        })

        pkg, _, _ = self.LOAD('conf-opts-valid-str')
        self.assertDictEqual(pkg.conf_opts, {
            'option': '',
        })

        pkg, _, _ = self.LOAD('conf-opts-valid-strs')
        self.assertDictEqual(pkg.conf_opts, {
            'option1': '',
            'option2': '',
            'option3': '',
        })

    def test_pkgconfig_env_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('env-invalid-base-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('env-invalid-key-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('env-invalid-strs')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('env-invalid-value-type')

    def test_pkgconfig_env_shared(self):
        pkg, _, _ = self.LOAD('env-mixed-valid')
        self.assertDictEqual(pkg.build_env, {
            'build': 'build',
            'shared': 'shared',
        })
        self.assertDictEqual(pkg.conf_env, {
            'configure': 'configure',
            'shared': 'shared',
        })
        self.assertDictEqual(pkg.install_env, {
            'install': 'install',
            'shared': 'shared',
        })

    def test_pkgconfig_env_valid(self):
        expected = {
            'key1': 'val1',
            'key2': None,
            'key3': 'val3',
        }

        pkg, _, _ = self.LOAD('env-valid')
        self.assertDictEqual(pkg.build_env, expected)
        self.assertDictEqual(pkg.conf_env, expected)
        self.assertDictEqual(pkg.install_env, expected)

    def test_pkgconfig_install_defs_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('install-defs-invalid-base-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('install-defs-invalid-key-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('install-defs-invalid-strs')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('install-defs-invalid-value-type')

    def test_pkgconfig_install_defs_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.install_defs)

        pkg, _, _ = self.LOAD('build-defs-valid')
        self.assertIsNone(pkg.install_defs)

        pkg, _, _ = self.LOAD('conf-defs-valid')
        self.assertIsNone(pkg.install_defs)

    def test_pkgconfig_install_defs_valid(self):
        pkg, _, _ = self.LOAD('install-defs-valid')
        self.assertDictEqual(pkg.install_defs, {
            'key1': 'val1',
            'key2': None,
            'key3': 'val3',
        })

    def test_pkgconfig_install_env_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('install-env-invalid-base-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('install-env-invalid-key-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('install-env-invalid-strs')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('install-env-invalid-value-type')

    def test_pkgconfig_install_env_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.install_env)

        pkg, _, _ = self.LOAD('build-env-valid')
        self.assertIsNone(pkg.install_env)

        pkg, _, _ = self.LOAD('conf-env-valid')
        self.assertIsNone(pkg.install_env)

    def test_pkgconfig_install_env_valid(self):
        pkg, _, _ = self.LOAD('install-env-valid')
        self.assertDictEqual(pkg.install_env, {
            'key1': 'val1',
            'key2': None,
            'key3': 'val3',
        })

    def test_pkgconfig_install_opts_invalid(self):
        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('install-opts-invalid-base-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('install-opts-invalid-key-type')

        with self.assertRaises(RelengToolInvalidPackageKeyValue):
            self.LOAD('install-opts-invalid-value-type')

    def test_pkgconfig_install_opts_missing(self):
        pkg, _, _ = self.LOAD('missing')
        self.assertIsNone(pkg.install_opts)

        pkg, _, _ = self.LOAD('build-opts-valid-dict')
        self.assertIsNone(pkg.install_opts)

        pkg, _, _ = self.LOAD('build-opts-valid-str')
        self.assertIsNone(pkg.install_opts)

        pkg, _, _ = self.LOAD('build-opts-valid-strs')
        self.assertIsNone(pkg.install_opts)

        pkg, _, _ = self.LOAD('conf-opts-valid-dict')
        self.assertIsNone(pkg.install_opts)

        pkg, _, _ = self.LOAD('conf-opts-valid-str')
        self.assertIsNone(pkg.install_opts)

        pkg, _, _ = self.LOAD('conf-opts-valid-strs')
        self.assertIsNone(pkg.install_opts)

    def test_pkgconfig_install_opts_valid(self):
        pkg, _, _ = self.LOAD('install-opts-valid-dict')
        self.assertDictEqual(pkg.install_opts, {
            'key1': 'val1',
            'key2': None,
            'key3': 'val3',
        })

        pkg, _, _ = self.LOAD('install-opts-valid-str')
        self.assertDictEqual(pkg.install_opts, {
            'option': '',
        })

        pkg, _, _ = self.LOAD('install-opts-valid-strs')
        self.assertDictEqual(pkg.install_opts, {
            'option1': '',
            'option2': '',
            'option3': '',
        })
