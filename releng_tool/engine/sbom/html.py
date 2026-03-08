# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from collections import OrderedDict
from releng_tool.util.log import verbose
import os
import xml.etree.ElementTree as ET


def generate_html(sbom, cache):
    """
    generate an html format sbom file

    Compiles an HTML-formatted software build-of-materials document based
    on the cache information populated from a releng-tool project.

    Args:
        sbom: sbom manager instance
        cache: the sbom cache
    """

    root = ET.Element('html')

    # head section
    head = ET.SubElement(root, 'head')
    ET.SubElement(head, 'title').text = 'Software build of materials'

    meta_fields = [
        'report-id',
        'releng-tool-sbom-version',
        'releng-tool-version',
    ]

    for meta_field in meta_fields:
        meta = ET.SubElement(head, 'meta')
        meta.set('name', meta_field)
        meta.set('content', cache[meta_field])

    ET.SubElement(head, 'style').text = ''.join(
        [v.strip() for v in HTML_TEMPLATE_STYLE.split('\n')])

    # body section
    body = ET.SubElement(root, 'body')
    ET.SubElement(body, 'h1').text = 'Software build of materials'

    # properties
    properties = OrderedDict()
    properties['report-id'] = 'Report ID'
    properties['datetime'] = 'Generated'

    props = ET.SubElement(body, 'div')
    props.set('class', 'entries')

    for key, val in properties.items():
        entry = ET.SubElement(props, 'div')
        ET.SubElement(entry, 'div').text = val
        ET.SubElement(entry, 'div').text = cache[key]

    # process packages
    package_entries = OrderedDict()
    package_entries['packages'] = 'Packages'
    package_entries['host-packages'] = 'Host packages'

    has_pkg_data = False
    for entry, desc in package_entries.items():
        data = cache.get(entry, None)
        if not data:
            continue

        has_pkg_data = True
        ET.SubElement(body, 'h2').text = desc

        for pkg_name, pkg in data.items():
            ET.SubElement(body, 'h3').text = pkg_name

            pkg_data = ET.SubElement(body, 'div')

            # package properties
            properties = OrderedDict()
            properties['version'] = 'Version'
            properties['site'] = 'Site'
            properties['revision'] = 'Revision'

            pkg_props = ET.SubElement(pkg_data, 'div')
            pkg_props.set('class', 'entries')

            has_pkg_info = False

            for key, val in properties.items():
                prop_data = pkg.get(key)
                if prop_data:
                    has_pkg_info = True
                    entry = ET.SubElement(pkg_props, 'div')
                    ET.SubElement(entry, 'div').text = val
                    ET.SubElement(entry, 'div').text = prop_data

            if pkg['licenses']:
                has_pkg_info = True
                entry = ET.SubElement(pkg_props, 'div')
                ET.SubElement(entry, 'div').text = 'Licenses'
                licenses_root = ET.SubElement(entry, 'div')
                licenses_list = ET.SubElement(licenses_root, 'ul')

                for pkg_license in pkg['licenses']:
                    ET.SubElement(licenses_list, 'li').text = pkg_license

            if pkg['hashes']:
                has_pkg_info = True
                pkg_hashes = ET.SubElement(pkg_data, 'div')
                pkg_hashes.set('class', 'hashes')

                for ph in pkg['hashes']:
                    ph_hdr = ET.SubElement(pkg_hashes, 'div')
                    ET.SubElement(ph_hdr, 'div').text = ph['algorithm']
                    ET.SubElement(ph_hdr, 'div').text = ph['file']

                    ph_data = ET.SubElement(pkg_hashes, 'div')
                    ET.SubElement(ph_data, 'div').text = ph['hash']

            if not has_pkg_info:
                entry = ET.SubElement(pkg_data, 'div')
                no_details = ET.SubElement(entry, 'div')
                no_details.set('class', 'clean')
                no_details.text = '(no details)'

    if not has_pkg_data:
        no_pkg_data = ET.SubElement(body, 'div')
        no_pkg_data.set('class', 'no-pkg-data')
        no_pkg_data.text = 'No package information provided.'

    # writing the processed cache data to a file
    verbose('writing sbom (html)')
    sbom_file = os.path.join(sbom.opts.out_dir, 'sbom.html')
    xml = ET.tostring(root, 'utf_8')
    crude_html = xml.replace(b'&gt;', b'>')

    with open(sbom_file, 'wb') as f:
        f.write(crude_html)

    sbom.generated.append(sbom_file)


HTML_TEMPLATE_STYLE = '''
body {
    font-family: Helvetica, "Trebuchet MS", Verdana, sans-serif;
    max-width: 800px;
    margin: 20px auto;
}

h3 {
    margin-left: 20px;
}

.entries > div {
    display: grid;
    grid-template-columns: 150px 100%;
    padding: 2px;
}

.entries > div > :first-child {
    text-align: right;
    padding-right: 5px;
}

.entries > div > :first-child::after {
    content: ':';
}

.entries .clean::after {
    content: unset !important;
}

.entries ul {
    list-style-type: none;
    margin: 0;
    padding: 0;
}

.hashes {
    margin-top: 10px;
}

.hashes > div {
    display: flex;
    text-align: center;
}

.hashes > div > div {
    flex: 1;
}

.hashes > div:nth-child(odd) {
    border-bottom: 1px solid #aaa;
}

.hashes > div:nth-child(even) {
    border-bottom: 1px solid #e9e9e9;
}

.no-pkg-data {
    color: #8b0000;
    font-size: 20px;
    font-weight: heavy;
    margin: 50px;
    text-align: center;
}
'''
