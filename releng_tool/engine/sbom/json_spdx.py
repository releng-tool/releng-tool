# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.log import verbose
from releng_tool.util.spdx import spdx_parse
import json
import os


# spdx license list version used
SPDX_LLVERSION = '3.28'

# specification followed for generated spdx-sboms
SPDX_SPEC = 'SPDX-2.3'


def generate_json_spdx(sbom, cache):
    """
    generate a SPDX compliant JSON format sbom file

    Compiles a JSON-formatted software build-of-materials document based
    on the cache information populated from a releng-tool project.

    Args:
        sbom: sbom manager instance
        cache: the sbom cache
    """

    prj_name = cache['releng-tool-pid']
    uid = cache['report-id']
    doc_namespace = f'https://spdx.org/spdxdocs/{prj_name}-{uid}'

    spdx_cache = {}
    spdx_cache['SPDXID'] = 'SPDXRef-DOCUMENT'
    spdx_cache['spdxVersion'] = SPDX_SPEC
    spdx_cache['name'] = prj_name
    spdx_cache['dataLicense'] = 'CC0-1.0'
    spdx_cache['documentDescribes'] = []
    spdx_cache['documentNamespace'] = doc_namespace
    spdx_cache['creationInfo'] = {}
    spdx_cache['creationInfo']['created'] = cache['datetime']
    spdx_cache['creationInfo']['licenseListVersion'] = SPDX_LLVERSION
    spdx_cache['creationInfo']['creators'] = [
        'Tool: releng-tool-' + cache['releng-tool-version'],
    ]
    spdx_cache['packages'] = []

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
            pkg_rev = pkg.get('revision', '')

            # if we have no package licenses, claim as none
            if not pkg['licenses']:
                pkg_license = 'NONE'
                pkg_license_final = 'NONE'
            else:
                pkg_license_final = 'NOASSERTION'

            license_data = spdx_parse(pkg['licenses'])
            if license_data:
                pkg_license = str(license_data)
            else:
                pkg_license = 'NOASSERTION'

            pkg_dl_loc = pkg.get('site', 'NONE')
            if pkg_dl_loc == 'local':
                pkg_dl_loc = 'NONE'

            package_entry = {}
            package_entry['SPDXID'] = 'SPDXRef-' + pkg_name
            package_entry['name'] = pkg_name
            package_entry['versionInfo'] = pkg.get('version', '')
            package_entry['downloadLocation'] = pkg_dl_loc
            if pkg_rev:
                package_entry['sourceInfo'] = f'commit {pkg_rev}'
            package_entry['filesAnalyzed'] = False
            package_entry['licenseDeclared'] = pkg_license
            package_entry['licenseConcluded'] = pkg_license_final

            spdx_cache['packages'].append(package_entry)
            spdx_cache['documentDescribes'].append(package_entry['SPDXID'])

    verbose('writing sbom (json-spdx)')
    sbom_file = os.path.join(sbom.opts.out_dir, 'sbom-spdx.json')
    with open(sbom_file, 'w') as f:
        json.dump(spdx_cache, f, indent=4)

    sbom.generated.append(sbom_file)
