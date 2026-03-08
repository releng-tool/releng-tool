# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from collections import OrderedDict
from releng_tool.engine.sbom.cyclonedx import COMPAT_CYCLONEDX_HASH_ID
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
from releng_tool.util.spdx import spdx_parse
import json
import os


def generate_json_cyclonedx(sbom, cache):
    """
    generate a CycloneDX compliant JSON format sbom file

    Compiles a JSON-formatted software build-of-materials document based
    on the cache information populated from a releng-tool project.

    Args:
        sbom: sbom manager instance
        cache: the sbom cache
    """

    schema = 'http://cyclonedx.org/schema/bom-1.7.schema.json'
    report_id = cache['report-id']

    cyclonedx_cache = OrderedDict()
    cyclonedx_cache['$schema'] = schema
    cyclonedx_cache['bomFormat'] = 'CycloneDX'
    cyclonedx_cache['specVersion'] = '1.7'
    cyclonedx_cache['version'] = 1
    cyclonedx_cache['serialNumber'] = f'urn:uuid:{report_id}'
    cyclonedx_cache['metadata'] = {
        'timestamp': cache['datetime'],
        'tools': {
            'components': [
                {
                    'type': 'application',
                    'name': cache['type'],
                    'version': cache['releng-tool-version'],
                },
            ],
        },
    }

    components = []

    # package entries
    package_entries = [
        'packages',
        'host-packages',
    ]

    for entry in package_entries:
        data = cache.get(entry, None)
        if not data:
            continue

        for pkg_name, pkg in data.items():
            package_entry = OrderedDict()
            package_entry['type'] = 'library'
            package_entry['name'] = pkg_name
            package_entry['version'] = pkg.get('version', '')

            license_data = spdx_parse(pkg['licenses'])
            if license_data:
                license_entry = OrderedDict()
                license_entry['expression'] = str(license_data)
                package_entry['licenses'] = [license_entry]

            pkg_hashes = []
            for pkg_hash in pkg['hashes']:
                raw_hash = pkg_hash['algorithm']
                hid = COMPAT_CYCLONEDX_HASH_ID.get(raw_hash)
                if not hid:
                    warn(f'unsupported hash for cyclonedx: {raw_hash}')
                    continue

                pkg_hashes.append({
                    'alg': hid,
                    'content': pkg_hash['hash'],
                })

            if pkg_hashes:
                package_entry['hashes'] = pkg_hashes

            site_value = pkg.get('site', '')
            if site_value:
                site_entry = OrderedDict()
                site_entry['type'] = 'vcs'
                site_entry['url'] = site_value
                package_entry['externalReferences'] = [site_entry]

            components.append(package_entry)

    if components:
        cyclonedx_cache['components'] = components

    verbose('writing sbom (json-cyclonedx)')
    sbom_file = os.path.join(sbom.opts.out_dir, 'sbom-cyclonedx.json')
    with open(sbom_file, 'w') as f:
        json.dump(cyclonedx_cache, f, indent=4)

    sbom.generated.append(sbom_file)
