# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.log import verbose
from releng_tool.util.spdx import ConjunctiveLicenses
from releng_tool.util.spdx import LicenseEntries
from releng_tool.util.spdx import spdx_parse
import os
import xml.dom.minidom as xml_minidom
import xml.etree.ElementTree as ET


# spdx license list version used
SPDX_LLVERSION = '3.28'

# specification followed for generated spdx-sboms
SPDX_SPEC = 'SPDX-2.3'


def generate_rdf_spdx(sbom, cache):
    """
    generate a SPDX compliant RDF (XML) format sbom file

    Compiles an RDF-formatted software build-of-materials document based
    on the cache information populated from a releng-tool project.

    Args:
        sbom: sbom manager instance
        cache: the sbom cache
    """

    rdf_license_burl = 'http://spdx.org/licenses/'
    rdf_term_na = 'http://spdx.org/rdf/terms#noassertion'
    rdf_term_none = 'http://spdx.org/rdf/terms#none'
    rdf_term_rdesc = 'http://spdx.org/rdf/terms#relationshipType_describes'

    data_license_ref = 'http://spdx.org/licenses/CC0-1.0'
    prj_name = cache['releng-tool-pid']
    tool_ref = 'Tool: releng-tool-' + cache['releng-tool-version']
    uid = cache['report-id']
    base_namespace = f'https://spdx.org/spdxdocs/{prj_name}-{uid}'
    doc_namespace = f'{base_namespace}#SPDXRef-DOCUMENT'

    # resource description root
    rdf_root = ET.Element('rdf:RDF')
    rdf_root.set('xmlns:rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    rdf_root.set('xmlns:spdx', 'http://spdx.org/rdf/terms#')
    rdf_root.set('xmlns:rdfs', 'http://www.w3.org/2000/01/rdf-schema#')

    # spdx document root
    root = ET.SubElement(rdf_root, 'spdx:SpdxDocument')
    root.set('rdf:about', doc_namespace)

    # common elements
    XML_ELEMENT(root, 'spdx:specVersion', SPDX_SPEC)
    XML_ELEMENT(root, 'spdx:name', prj_name)
    dle = ET.SubElement(root, 'spdx:dataLicense')
    dle.set('rdf:resource', data_license_ref)
    creation_info_container = ET.SubElement(root, 'spdx:creationInfo')

    cinfo_root = ET.SubElement(creation_info_container, 'spdx:CreationInfo')
    XML_ELEMENT(cinfo_root, 'spdx:created', cache['datetime'])
    XML_ELEMENT(cinfo_root, 'spdx:creator', tool_ref)
    XML_ELEMENT(cinfo_root, 'spdx:licenseListVersion', SPDX_LLVERSION)

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

            pkg_dl_loc = pkg.get('site', 'NONE')
            if pkg_dl_loc == 'local':
                pkg_dl_loc = 'NONE'

            rcontainer = ET.SubElement(root, 'spdx:relationship')
            rroot = ET.SubElement(rcontainer, 'spdx:Relationship')
            rtype = ET.SubElement(rroot, 'spdx:relationshipType')
            rtype.set('rdf:resource', rdf_term_rdesc)
            relement = ET.SubElement(rroot, 'spdx:relatedSpdxElement')
            proot = ET.SubElement(relement, 'spdx:Package')

            pkg_namespace = f'{base_namespace}#SPDXRef-{pkg_name}'
            proot.set('rdf:about', pkg_namespace)

            XML_ELEMENT(proot, 'spdx:specVersion', SPDX_SPEC)
            XML_ELEMENT(proot, 'spdx:name', pkg_name)
            XML_ELEMENT(proot, 'spdx:versionInfo', pkg.get('version', ''))
            XML_ELEMENT(proot, 'spdx:downloadLocation', pkg_dl_loc)
            if pkg_rev:
                XML_ELEMENT(proot, 'spdx:sourceInfo', f'commit {pkg_rev}')
            XML_ELEMENT(proot, 'spdx:filesAnalyzed', 'false')

            license_droot = ET.SubElement(proot, 'spdx:licenseDeclared')
            license_croot = ET.SubElement(proot, 'spdx:licenseConcluded')
            license_croot.set('rdf:resource', rdf_term_na)

            # if we have a parsed SPDX license string, either assign the
            # resource to the single license or prepare a list of license
            # entries; if not parsable, claim no assertion; and no license
            # information as none
            pkg_licenses = spdx_parse(pkg['licenses'])
            if pkg_licenses:
                def process_nested_licenses(base, licenses):
                    if isinstance(licenses, ConjunctiveLicenses):
                        root_entry_type = 'spdx:ConjunctiveLicenseSet'
                    else:
                        root_entry_type = 'spdx:DisjunctiveLicenseSet'

                    root_entry = ET.SubElement(base, root_entry_type)
                    for license_entry in licenses:
                        res = ET.SubElement(root_entry, 'spdx:member')

                        if isinstance(license_entry, LicenseEntries):
                            process_nested_licenses(res, license_entry)
                        else:
                            process_license_withex(res, license_entry)

                def process_license_withex(root, license_entry):
                    license_parts = license_entry.split(' WITH ')

                    if len(license_parts) > 1:
                        sroot = ET.SubElement(root,
                            'spdx:WithExceptionOperator')

                        res = ET.SubElement(sroot, 'spdx:member')
                        process_license_orlater(res, license_parts[0])

                        res = ET.SubElement(sroot, 'spdx:licenseException')
                        exception = license_parts[1]
                        evalue = rdf_license_burl + exception + '.html'
                        res.set('rdf:resource', evalue)
                    else:
                        process_license_orlater(root, license_parts[0])

                def process_license_orlater(root, license_entry):
                    resource = rdf_license_burl + license_entry.strip('+')

                    if license_entry.endswith('+'):
                        sroot = ET.SubElement(root, 'spdx:OrLaterOperator')
                        res = ET.SubElement(sroot, 'spdx:member')
                        res.set('rdf:resource', resource)
                    else:
                        root.set('rdf:resource', resource)

                if isinstance(pkg_licenses, LicenseEntries):
                    process_nested_licenses(license_droot, pkg_licenses)
                else:
                    process_license_withex(license_droot, pkg_licenses)

            elif pkg['licenses']:
                license_droot.set('rdf:resource', rdf_term_na)
            else:
                license_croot.set('rdf:resource', rdf_term_none)
                license_droot.set('rdf:resource', rdf_term_none)

    # writing the processed cache data to a file
    verbose('writing sbom (rdf-spdx)')
    sbom_file = os.path.join(sbom.opts.out_dir, 'sbom-spdx.xml')
    xml = ET.tostring(rdf_root, 'utf_8')
    tree = xml_minidom.parseString(xml)

    with open(sbom_file, 'w') as f:
        rdf_tree = tree.childNodes[0]
        data = rdf_tree.toprettyxml(indent=' ' * 4)
        f.write(data)

    sbom.generated.append(sbom_file)


def XML_ELEMENT(root, name, text=None):
    """
    helper to build an xml element

    Args:
        root: the root element to create on
        name: the name of the new element
        text (optional): the text to apply to the new element

    Returns:
        the newly created element
    """

    element = ET.SubElement(root, name)

    if text:
        element.text = text

    return element
