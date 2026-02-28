# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.packages import pkg_key
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import redirect_stdout
import os


class TestSpdxLicenseWarnings(RelengToolTestCase):
    def test_spdx_licenses_broken_spdx_license_value01(self):
        output = self._process_license('MIT AND')
        self.assertIn('unexpected spdx license format detected', output)

    def test_spdx_licenses_broken_spdx_license_value02(self):
        output = self._process_license('BSD AND OR MIT')
        self.assertIn('unexpected spdx license format detected', output)

    def test_spdx_licenses_deprecated_spdx_exception(self):
        output = self._process_license(
            'LGPL-2.0-only WITH Nokia-Qt-exception-1.1')
        self.assertIn('deprecated spdx license exception detected', output)

    def test_spdx_licenses_deprecated_spdx_license(self):
        output = self._process_license('LGPL-3.0')
        self.assertIn('deprecated spdx license detected', output)

    def test_spdx_licenses_exception_check(self):
        output = self._process_license(None, template='spdx-extras')
        self.assertIn('unknown spdx license detected', output)
        self.assertIn('unknown spdx license exception detected', output)

    def test_spdx_licenses_exception_license_exception_extra(self):
        output = self._process_license('PERMIT_LICENSE', template='spdx-extras')
        self.assertNotIn('unknown spdx license detected', output)

    def test_spdx_licenses_exception_license_extra(self):
        output = self._process_license(
            'MIT WITH PERMIT_EXCEPTION', template='spdx-extras')
        self.assertNotIn('unknown spdx license detected', output)

    def test_spdx_licenses_unknown_spdx_exception(self):
        output = self._process_license('BSD WITH DUMMY')
        self.assertIn('unknown spdx license exception detected', output)

    def test_spdx_licenses_unknown_spdx_license(self):
        output = self._process_license('DUMMY')
        self.assertIn('unknown spdx license detected', output)

    def test_spdx_licenses_valid_spdx_license_common(self):
        output = self._process_license('BSD-2-Clause')
        self.assertNotIn('MINIMAL_LICENSE', output)  # no warnings

    def test_spdx_licenses_valid_spdx_license_custom_ascii(self):
        output = self._process_license('LicenseRef-MyCompanyLicense')
        self.assertNotIn('MINIMAL_LICENSE', output)  # no warnings

    def test_spdx_licenses_valid_spdx_license_custom_unicode(self):
        output = self._process_license('LicenseRef-Prüfen')
        self.assertNotIn('MINIMAL_LICENSE', output)  # no warnings

    def _process_license(self, lid, template='minimal'):
        config = {
            'action': 'lint',
        }

        with redirect_stdout() as stream:
            try:
                with prepare_testenv(config=config, template=template) as engine:
                    if lid:
                        root_dir = engine.opts.root_dir
                        pkg_script = os.path.join(root_dir,
                            'package', template, template + '.rt')
                        self.assertTrue(os.path.exists(pkg_script))

                        with open(pkg_script, 'a', encoding='utf_8') as f:
                            key = pkg_key(template, 'INTERNAL')
                            f.write(f'{key}=True\n')
                            key = pkg_key(template, 'LICENSE')
                            f.write(f'{key}="{lid}"\n')

                    engine.run()
            finally:
                print(stream.getvalue())

        return stream.getvalue()
