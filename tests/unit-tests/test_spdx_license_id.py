# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.spdx import spdx_license_identifier
from tests import RelengToolTestCase


class TestSpdxLicenseIds(RelengToolTestCase):
    def test_spdx_license_ids(self):
        # empty/invalid id
        lid = spdx_license_identifier('')
        self.assertFalse(lid)

        # non-license reference marking
        lid = spdx_license_identifier('MyCustomLicense')
        self.assertFalse(lid)

        # empty custom license id
        lid = spdx_license_identifier('LicenseRef-')
        self.assertFalse(lid)

        # bad license name format
        lid = spdx_license_identifier('LicenseRef-My Custom License')
        self.assertFalse(lid)

        # a sane custom license identifier
        lid = spdx_license_identifier('LicenseRef-MyCustomLicense')
        self.assertTrue(lid)
