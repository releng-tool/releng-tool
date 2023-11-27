#!/usr/bin/env python
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

import json
import os
import urllib.request


license_tag = 'v3.22'
license_host_url = 'https://raw.githubusercontent.com'
license_base_url = '{}/spdx/license-list-data/{}/json/'.format(
    license_host_url, license_tag)


def main():
    # download and parse the license and exception data
    with urllib.request.urlopen(license_base_url + 'licenses.json') as f:
        license_data = json.loads(f.read().decode('utf-8'))

    with urllib.request.urlopen(license_base_url + 'exceptions.json') as f:
        exception_data = json.loads(f.read().decode('utf-8'))

    # sanity checks
    assert 'licenses' in license_data
    assert 'exceptions' in exception_data
    lv_key = 'licenseListVersion'
    assert license_data[lv_key] == exception_data[lv_key]

    data = {
        'licenseListVersion': license_data[lv_key],
        'licenses': {},
        'exceptions': {},
    }

    for entry in license_data['licenses']:
        data['licenses'][entry['licenseId']] = {
            'name': entry['name'],
            'deprecated': entry['isDeprecatedLicenseId'],
        }

    for entry in exception_data['exceptions']:
        data['exceptions'][entry['licenseExceptionId']] = {
            'name': entry['name'],
            'deprecated': entry['isDeprecatedLicenseId'],
        }

    # inject a non-license "Proprietary" string for convenience, since we aim
    # to promote either SPDX licenses or users proprietary packages
    data['licenses']['Proprietary'] = {
        'name': 'Proprietary',
        'deprecated': False,
    }

    scripts_dir = os.path.dirname(os.path.realpath(__file__))
    root_dir = os.path.dirname(scripts_dir)
    licenses_dir = os.path.join(root_dir, 'releng_tool', 'data', 'licenses')
    licenses_file = os.path.join(licenses_dir, 'data.json')

    with open(licenses_file, 'w') as f:
        json.dump(data, f, indent=2)


if __name__ == '__main__':
    main()
