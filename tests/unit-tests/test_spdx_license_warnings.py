# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import unicode_literals
from io import open  # noqa: A004
from releng_tool.packages import pkg_key
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import redirect_stderr
import os


class TestSpdxLicenseWarnings(RelengToolTestCase):
    def test_spdx_licenses_broken_spdx_license_value01(self):
        stderr = self._process_license('MIT AND')
        self.assertIn('unexpected spdx license format detected', stderr)

    def test_spdx_licenses_broken_spdx_license_value02(self):
        stderr = self._process_license('BSD AND OR MIT')
        self.assertIn('unexpected spdx license format detected', stderr)

    def test_spdx_licenses_deprecated_spdx_exception(self):
        stderr = self._process_license(
            'LGPL-2.0-only WITH Nokia-Qt-exception-1.1')
        self.assertIn('deprecated spdx license exception detected', stderr)

    def test_spdx_licenses_deprecated_spdx_license(self):
        stderr = self._process_license('LGPL-3.0')
        self.assertIn('deprecated spdx license detected', stderr)

    def test_spdx_licenses_exception_check(self):
        stderr = self._process_license(None, template='spdx-extras')
        self.assertIn('unknown spdx license detected', stderr)
        self.assertIn('unknown spdx license exception detected', stderr)

    def test_spdx_licenses_exception_license_exception_extra(self):
        stderr = self._process_license('PERMIT_LICENSE', template='spdx-extras')
        self.assertNotIn('unknown spdx license detected', stderr)

    def test_spdx_licenses_exception_license_extra(self):
        stderr = self._process_license(
            'MIT WITH PERMIT_EXCEPTION', template='spdx-extras')
        self.assertNotIn('unknown spdx license detected', stderr)

    def test_spdx_licenses_suppress_quirk(self):
        config = {
            'quirk': ['releng.disable_spdx_check'],
        }

        stderr = self._process_license('DUMMY', config=config)
        self.assertNotIn('unknown spdx license detected', stderr)

    def test_spdx_licenses_unknown_spdx_exception(self):
        stderr = self._process_license('BSD WITH DUMMY')
        self.assertIn('unknown spdx license exception detected', stderr)

    def test_spdx_licenses_unknown_spdx_license(self):
        stderr = self._process_license('DUMMY')
        self.assertIn('unknown spdx license detected', stderr)

    def test_spdx_licenses_valid_spdx_license_common(self):
        stderr = self._process_license('BSD-2-Clause')
        self.assertEqual(stderr, '')  # no errors

    def test_spdx_licenses_valid_spdx_license_custom_ascii(self):
        stderr = self._process_license('LicenseRef-MyCompanyLicense')
        self.assertEqual(stderr, '')  # no errors

    def test_spdx_licenses_valid_spdx_license_custom_unicode(self):
        stderr = self._process_license('LicenseRef-Prüfen')
        self.assertEqual(stderr, '')  # no errors

    def _process_license(self, lid, config=None, template='minimal'):
        with redirect_stderr() as stream:
            with prepare_testenv(config=config, template=template) as engine:
                if lid:
                    root_dir = engine.opts.root_dir
                    pkg_script = os.path.join(root_dir,
                        'package', template, template + '.rt')
                    self.assertTrue(os.path.exists(pkg_script))

                    with open(pkg_script, 'a', encoding='utf_8') as f:
                        f.write('{key}={val}\n'.format(
                            key=pkg_key(template, 'INTERNAL'), val=True))
                        f.write('{}="{}"\n'.format(
                            pkg_key(template, 'LICENSE'), lid))

                rv = engine.run()
                self.assertTrue(rv)

        return stream.getvalue()
