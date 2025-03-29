# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import VOID
from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from tests.support.pkg_config_test import TestPkgConfigsBase


class TestPkgConfigsStageOpts(TestPkgConfigsBase):
    def test_pkgconfig_build_defs_append(self):
        pkg, _, _ = self.LOAD('build-defs-append')
        self.assertDictEqual(pkg.build_defs, {
            'some-key': 'appended',
        })

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

    def test_pkgconfig_build_env_append(self):
        pkg, _, _ = self.LOAD('build-env-append')
        self.assertDictEqual(pkg.build_env, {
            'some-key': 'appended',
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

    def test_pkgconfig_build_opts_append(self):
        pkg, _, _ = self.LOAD('build-opts-append')
        self.assertDictEqual(pkg.build_opts, {
            'some-key': 'appended',
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

        pkg, _, _ = self.LOAD('conf-opts-valid-mixed')
        self.assertIsNone(pkg.build_opts)

        pkg, _, _ = self.LOAD('conf-opts-valid-path')
        self.assertIsNone(pkg.build_opts)

        pkg, _, _ = self.LOAD('conf-opts-valid-paths')
        self.assertIsNone(pkg.build_opts)

        pkg, _, _ = self.LOAD('conf-opts-valid-str')
        self.assertIsNone(pkg.build_opts)

        pkg, _, _ = self.LOAD('conf-opts-valid-strs')
        self.assertIsNone(pkg.build_opts)

        pkg, _, _ = self.LOAD('install-opts-valid-dict')
        self.assertIsNone(pkg.build_opts)

        pkg, _, _ = self.LOAD('install-opts-valid-mixed')
        self.assertIsNone(pkg.build_opts)

        pkg, _, _ = self.LOAD('install-opts-valid-path')
        self.assertIsNone(pkg.build_opts)

        pkg, _, _ = self.LOAD('install-opts-valid-paths')
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

        pkg, _, _ = self.LOAD('build-opts-valid-mixed')
        self.assertDictEqual(pkg.build_opts, {
            'option1': VOID,
            'option2': VOID,
        })

        pkg, _, _ = self.LOAD('build-opts-valid-path')
        self.assertDictEqual(pkg.build_opts, {
            'option': VOID,
        })

        pkg, _, _ = self.LOAD('build-opts-valid-paths')
        self.assertDictEqual(pkg.build_opts, {
            'option1': VOID,
            'option2': VOID,
            'option3': VOID,
        })

        pkg, _, _ = self.LOAD('build-opts-valid-str')
        self.assertDictEqual(pkg.build_opts, {
            'option': VOID,
        })

        pkg, _, _ = self.LOAD('build-opts-valid-strs')
        self.assertDictEqual(pkg.build_opts, {
            'option1': VOID,
            'option2': VOID,
            'option3': VOID,
        })

    def test_pkgconfig_conf_defs_append(self):
        pkg, _, _ = self.LOAD('conf-defs-append')
        self.assertDictEqual(pkg.conf_defs, {
            'some-key': 'appended',
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

    def test_pkgconfig_conf_env_append(self):
        pkg, _, _ = self.LOAD('conf-env-append')
        self.assertDictEqual(pkg.conf_env, {
            'some-key': 'appended',
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

    def test_pkgconfig_conf_opts_append(self):
        pkg, _, _ = self.LOAD('conf-opts-append')
        self.assertDictEqual(pkg.conf_opts, {
            'some-key': 'appended',
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

        pkg, _, _ = self.LOAD('build-opts-valid-mixed')
        self.assertIsNone(pkg.conf_opts)

        pkg, _, _ = self.LOAD('build-opts-valid-path')
        self.assertIsNone(pkg.conf_opts)

        pkg, _, _ = self.LOAD('build-opts-valid-paths')
        self.assertIsNone(pkg.conf_opts)

        pkg, _, _ = self.LOAD('build-opts-valid-str')
        self.assertIsNone(pkg.conf_opts)

        pkg, _, _ = self.LOAD('build-opts-valid-strs')
        self.assertIsNone(pkg.conf_opts)

        pkg, _, _ = self.LOAD('install-opts-valid-dict')
        self.assertIsNone(pkg.conf_opts)

        pkg, _, _ = self.LOAD('install-opts-valid-mixed')
        self.assertIsNone(pkg.conf_opts)

        pkg, _, _ = self.LOAD('install-opts-valid-path')
        self.assertIsNone(pkg.conf_opts)

        pkg, _, _ = self.LOAD('install-opts-valid-paths')
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

        pkg, _, _ = self.LOAD('conf-opts-valid-mixed')
        self.assertDictEqual(pkg.conf_opts, {
            'option1': VOID,
            'option2': VOID,
        })

        pkg, _, _ = self.LOAD('conf-opts-valid-path')
        self.assertDictEqual(pkg.conf_opts, {
            'option': VOID,
        })

        pkg, _, _ = self.LOAD('conf-opts-valid-paths')
        self.assertDictEqual(pkg.conf_opts, {
            'option1': VOID,
            'option2': VOID,
            'option3': VOID,
        })

        pkg, _, _ = self.LOAD('conf-opts-valid-str')
        self.assertDictEqual(pkg.conf_opts, {
            'option': VOID,
        })

        pkg, _, _ = self.LOAD('conf-opts-valid-strs')
        self.assertDictEqual(pkg.conf_opts, {
            'option1': VOID,
            'option2': VOID,
            'option3': VOID,
        })

    def test_pkgconfig_env_append(self):
        expected = {
            'some-key': 'appended',
        }

        pkg, _, _ = self.LOAD('env-append')
        self.assertDictEqual(pkg.build_env, expected)
        self.assertDictEqual(pkg.conf_env, expected)
        self.assertDictEqual(pkg.install_env, expected)

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

    def test_pkgconfig_install_defs_append(self):
        pkg, _, _ = self.LOAD('install-defs-append')
        self.assertDictEqual(pkg.install_defs, {
            'some-key': 'appended',
        })

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

    def test_pkgconfig_install_env_append(self):
        pkg, _, _ = self.LOAD('install-env-append')
        self.assertDictEqual(pkg.install_env, {
            'some-key': 'appended',
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

    def test_pkgconfig_install_opts_append(self):
        pkg, _, _ = self.LOAD('install-opts-append')
        self.assertDictEqual(pkg.install_opts, {
            'some-key': 'appended',
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

        pkg, _, _ = self.LOAD('build-opts-valid-mixed')
        self.assertIsNone(pkg.install_opts)

        pkg, _, _ = self.LOAD('build-opts-valid-path')
        self.assertIsNone(pkg.install_opts)

        pkg, _, _ = self.LOAD('build-opts-valid-paths')
        self.assertIsNone(pkg.install_opts)

        pkg, _, _ = self.LOAD('build-opts-valid-str')
        self.assertIsNone(pkg.install_opts)

        pkg, _, _ = self.LOAD('build-opts-valid-strs')
        self.assertIsNone(pkg.install_opts)

        pkg, _, _ = self.LOAD('conf-opts-valid-dict')
        self.assertIsNone(pkg.install_opts)

        pkg, _, _ = self.LOAD('conf-opts-valid-mixed')
        self.assertIsNone(pkg.install_opts)

        pkg, _, _ = self.LOAD('conf-opts-valid-path')
        self.assertIsNone(pkg.install_opts)

        pkg, _, _ = self.LOAD('conf-opts-valid-paths')
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

        pkg, _, _ = self.LOAD('install-opts-valid-mixed')
        self.assertDictEqual(pkg.install_opts, {
            'option1': VOID,
            'option2': VOID,
        })

        pkg, _, _ = self.LOAD('install-opts-valid-path')
        self.assertDictEqual(pkg.install_opts, {
            'option': VOID,
        })

        pkg, _, _ = self.LOAD('install-opts-valid-paths')
        self.assertDictEqual(pkg.install_opts, {
            'option1': VOID,
            'option2': VOID,
            'option3': VOID,
        })

        pkg, _, _ = self.LOAD('install-opts-valid-str')
        self.assertDictEqual(pkg.install_opts, {
            'option': VOID,
        })

        pkg, _, _ = self.LOAD('install-opts-valid-strs')
        self.assertDictEqual(pkg.install_opts, {
            'option1': VOID,
            'option2': VOID,
            'option3': VOID,
        })
