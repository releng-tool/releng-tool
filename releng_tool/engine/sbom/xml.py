# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.log import verbose
import os
import xml.dom.minidom as xml_minidom
import xml.etree.ElementTree as ET


def generate_xml(sbom, cache):
    """
    generate an XML format sbom file

    Compiles an XML-formatted software build-of-materials document based
    on the cache information populated from a releng-tool project.

    Args:
        sbom: sbom manager instance
        cache: the sbom cache
    """

    root = ET.Element(cache['type'])
    root.set('version', cache['releng-tool-sbom-version'])

    # common root entries
    ET.SubElement(root, 'report-id').text = cache['report-id']
    ET.SubElement(root, 'generated').text = cache['datetime']

    # package entries
    package_entries = [
        'packages',
        'host-packages',
    ]

    for entry in package_entries:
        data = cache.get(entry, None)
        if not data:
            continue

        packages_root = ET.SubElement(root, entry)

        for pkg_name, pkg in data.items():
            pkg_root = ET.SubElement(packages_root, 'package')
            pkg_root.set('id', pkg['id'])
            ET.SubElement(pkg_root, 'name').text = pkg_name
            ET.SubElement(pkg_root, 'version').text = pkg.get('version', '')
            ET.SubElement(pkg_root, 'site').text = pkg.get('site', '')

            revision = pkg.get('revision', '')
            if revision:
                ET.SubElement(pkg_root, 'revision').text = revision

            licenses_root = ET.SubElement(pkg_root, 'licenses')
            for pkg_license in pkg['licenses']:
                ET.SubElement(licenses_root, 'license').text = pkg_license

            hashes_root = ET.SubElement(pkg_root, 'hashes')
            for ph in pkg['hashes']:
                hr = ET.SubElement(hashes_root, 'hash')
                ET.SubElement(hr, 'algorithm').text = ph['algorithm']
                ET.SubElement(hr, 'file').text = ph['file']
                ET.SubElement(hr, 'hash').text = ph['hash']

    # extra information
    rtv = ET.SubElement(root, 'releng-tool-version')
    rtv.text = cache['releng-tool-version']

    # writing the processed cache data to a file
    verbose('writing sbom (xml)')
    sbom_file = os.path.join(sbom.opts.out_dir, 'sbom.xml')
    xml = ET.tostring(root, 'utf_8')
    tree = xml_minidom.parseString(xml)

    with open(sbom_file, 'w') as f:
        data = tree.toprettyxml(indent=' ' * 4)
        f.write(data)

    sbom.generated.append(sbom_file)
