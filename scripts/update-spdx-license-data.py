#!/usr/bin/env python
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

import configparser
import json
import os
import urllib.request


CONFIG_FILE = 'spdx-license-data.ini'


def main():
    script_dir = os.path.dirname(__file__)
    cfg_file = os.path.join(script_dir, CONFIG_FILE)

    cfg = configparser.ConfigParser()
    try:
        # extract license version
        cfg.read(cfg_file)
        license_tag = cfg.get('spdx-license-data', 'version')

        # determine url base for license file
        license_host_url = 'https://raw.githubusercontent.com'
        license_base_url = '{}/spdx/license-list-data/{}/json/'.format(
            license_host_url, license_tag)

        # update license data
        update(license_base_url)

        # update internally tracked license list version
        llv = '.'.join(license_tag[1:].split('.', 2)[:2])
        root_dir = os.path.dirname(script_dir)
        engine_dir = os.path.join(root_dir, 'releng_tool', 'engine')
        sbom_implementation = os.path.join(engine_dir, 'sbom.py')

        with open(sbom_implementation) as f:
            sbom_py_data = f.readlines()

        with open(sbom_implementation, 'w') as f:
            for line in sbom_py_data:
                if 'SPDX_LLVERSION = ' in line:
                    f.write(f"SPDX_LLVERSION = '{llv}'\n")
                else:
                    f.write(line)

    except configparser.Error as ex:
        raise SystemExit(f'failed to load configuration: {ex}') from ex


def update(license_base_url):
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

    scripts_dir = os.path.dirname(os.path.realpath(__file__))
    root_dir = os.path.dirname(scripts_dir)
    licenses_dir = os.path.join(root_dir, 'releng_tool', 'data', 'licenses')
    licenses_file = os.path.join(licenses_dir, 'data.json')

    with open(licenses_file, 'w') as f:
        json.dump(data, f, indent=2)


if __name__ == '__main__':
    main()
