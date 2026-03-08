# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.engine.sbom.cyclonedx import COMPAT_CYCLONEDX_HASH_ID
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
from releng_tool.util.spdx import spdx_parse
import os
import xml.dom.minidom as xml_minidom
import xml.etree.ElementTree as ET


def generate_xml_cyclonedx(sbom, cache):
    """
    generate an CycloneDX compliant XML format sbom file

    Compiles an XML-formatted software build-of-materials document based
    on the cache information populated from a releng-tool project.

    Args:
        sbom: sbom manager instance
        cache: the sbom cache
    """

    report_id = cache['report-id']

    root = ET.Element('bom')
    root.set('xmlns', 'http://cyclonedx.org/schema/bom/1.7')
    root.set('serialNumber', f'urn:uuid:{report_id}')
    root.set('version', '1')

    # package entries
    package_entries = [
        'packages',
        'host-packages',
    ]

    for entry in package_entries:
        data = cache.get(entry, None)
        if not data:
            continue

        metadata = ET.SubElement(root, 'metadata')
        ET.SubElement(metadata, 'timestamp').text = cache['datetime']

        md_tools = ET.SubElement(metadata, 'tools')
        md_tool = ET.SubElement(md_tools, 'tool')
        ET.SubElement(md_tool, 'name').text = cache['type']
        ET.SubElement(md_tool, 'version').text = cache['releng-tool-version']

        components = ET.SubElement(root, 'components')

        for pkg_name, pkg in data.items():
            pkg_root = ET.SubElement(components, 'component')
            pkg_root.set('type', 'library')
            ET.SubElement(pkg_root, 'name').text = pkg_name
            ET.SubElement(pkg_root, 'version').text = pkg.get('version', '')

            hashes_root = ET.SubElement(pkg_root, 'hashes')
            for ph in pkg['hashes']:
                raw_hash = ph['algorithm']
                hid = COMPAT_CYCLONEDX_HASH_ID.get(raw_hash)
                if not hid:
                    warn(f'unsupported hash for cyclonedx: {raw_hash}')
                    continue

                hr = ET.SubElement(hashes_root, 'hash')
                hr.set('alg', hid)
                hr.text = ph['hash']

            license_data = spdx_parse(pkg['licenses'])
            if license_data:
                licenses_root = ET.SubElement(pkg_root, 'licenses')
                ET.SubElement(licenses_root, 'expression').text = \
                    str(license_data)

            site_value = pkg.get('site', '')
            if site_value:
                eref_root = ET.SubElement(pkg_root, 'externalReferences')
                ref_root = ET.SubElement(eref_root, 'reference')
                ref_root.set('type', 'vcs')
                ET.SubElement(ref_root, 'url').text = site_value

    # writing the processed cache data to a file
    verbose('writing sbom (xml-cyclonedx)')
    sbom_file = os.path.join(sbom.opts.out_dir, 'sbom-cyclonedx.xml')
    xml = ET.tostring(root, 'utf_8')
    tree = xml_minidom.parseString(xml)

    with open(sbom_file, 'w') as f:
        data = tree.toprettyxml(indent=' ' * 4)
        f.write(data)

    sbom.generated.append(sbom_file)
