# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.engine.license import LicenseManager
from tests import RelengToolTestCase
from tests import prepare_testenv
import os


class TestLicenses(RelengToolTestCase):
    def test_licenses_generated(self):
        with prepare_testenv(template='licenses') as engine:
            opts = engine.opts

            # create a license header file
            HEADER_STR = 'verify-header-add'
            opts.license_header = HEADER_STR

            # generate a license file
            license_manager = LicenseManager(opts)
            generated = license_manager.generate({})
            self.assertTrue(generated)

            # check that we tracked any generates files
            self.assertTrue(license_manager.generated)
            for entry in license_manager.generated:
                self.assertTrue(os.path.isfile(entry))

    def test_licenses_header_injection(self):
        with prepare_testenv(template='licenses') as engine:
            opts = engine.opts

            # create a license header file
            HEADER_STR = 'verify-header-add'
            opts.license_header = HEADER_STR

            # generate a license file
            license_manager = LicenseManager(opts)
            generated = license_manager.generate({})
            self.assertTrue(generated)

            # read the license file to ensure the header data is there
            license_file = os.path.join(opts.license_dir, 'licenses')
            with open(license_file) as f:
                raw_data = f.read().strip()

            self.assertIn(HEADER_STR, raw_data)
            self.assertTrue(raw_data.startswith(HEADER_STR))

    def test_licenses_multiple(self):
        pkg_names = [
            'test-a',
            'test-b',
            'test-c',
        ]

        expected_licenses = [
            2,  # mocked BSD + MIT
            None,
            1,  # mocked GPL
        ]

        with prepare_testenv(template='licenses') as engine:
            pkgs = engine.pkgman.load(pkg_names)

            license_manager = LicenseManager(engine.opts)
            license_cache = license_manager.build_cache(pkgs)

            for pkg, expected in zip(pkg_names, expected_licenses):
                if expected is not None:
                    # a package with license information should be tracked
                    self.assertTrue(pkg in license_cache)

                    # verify we have expected license counts
                    licenses = license_cache[pkg]['files']
                    self.assertEqual(len(licenses), expected)

                    # verify that the license reference maps to a real file
                    for license_ in licenses:
                        self.assertTrue(os.path.exists(license_))
                else:
                    # packages without license data should not provide any
                    # information
                    self.assertFalse(pkg in license_cache)

    def test_licenses_none(self):
        with prepare_testenv(template='licenses') as engine:
            pkgs = engine.pkgman.load(['test-b'])

            license_manager = LicenseManager(engine.opts)
            license_cache = license_manager.build_cache(pkgs)

            # verify we have no license information if packages have no license
            # information to provide
            self.assertFalse(license_cache)

    def test_licenses_version(self):
        pkg_names = [
            'test-c',
            'test-d',
        ]

        expected_version_desc = [
            '2.0',
            '3.0',
        ]

        with prepare_testenv(template='licenses') as engine:
            pkgs = engine.pkgman.load(pkg_names)

            license_manager = LicenseManager(engine.opts)
            license_cache = license_manager.build_cache(pkgs)

            for pkg, expected in zip(pkg_names, expected_version_desc):
                # a package with license information should be tracked
                self.assertTrue(pkg in license_cache)

                # verify we have expected version description
                version_desc = license_cache[pkg]['version']
                self.assertEqual(version_desc, expected)
