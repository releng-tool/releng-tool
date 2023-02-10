# -*- coding: utf-8 -*-
# Copyright 2023 releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from collections import OrderedDict
from datetime import datetime
from releng_tool import __version__ as releng_version
from releng_tool.defs import PackageInstallType
from releng_tool.defs import SbomFormatType
from releng_tool.defs import VcsType
from releng_tool.util.compat import utc_timezone
from releng_tool.util.hash import BadFileHashLoadError
from releng_tool.util.hash import BadFormatHashLoadError
from releng_tool.util.hash import load as load_hashes
from releng_tool.util.log import err
from releng_tool.util.log import verbose
import csv
import hashlib
import json
import os
import sys
import uuid
import xml.dom.minidom as xml_minidom
import xml.etree.cElementTree as ET  # noqa: N817


# version string of the SBOM definition generated by releng-tool
SBOM_VERSION = '0'


class SbomManager:
    """
    sbom manager

    An SBOM manager is used to help generate a software build-of-materials for
    a releng-tool project. This can be used to help track package versions
    used, dependency history and more.

    Args:
        opts: options used to configure the engine

    Attributes:
        opts: options used to configure the engine
    """
    def __init__(self, opts):
        self.opts = opts

    def build_cache(self, pkgs):
        """
        compile a cache of sbom information

        This request will compile SBOM information for the running releng-tool
        project. Provides packages will be cycled through to track package
        versions and licenses. The result should be a dictionary of
        information which can then be used for generating an SBOM output file.

        Args:
            pkgs: packages which may be assigned licenses

        Returns:
            the sbom cache
        """

        cache = OrderedDict()
        cache['type'] = 'releng-tool-sbom'
        cache['report-id'] = str(uuid.uuid4())
        cache['packages'] = OrderedDict()
        cache['host-packages'] = OrderedDict()
        cache['releng-tool-sbom-version'] = SBOM_VERSION
        cache['releng-tool-version'] = releng_version

        for pkg in pkgs:
            # ignore placeholder packages
            if pkg.vcs_type == VcsType.NONE:
                continue

            # determine location where to store package cache
            if pkg.install_type == PackageInstallType.HOST:
                cache_base = cache['host-packages']
            else:
                cache_base = cache['packages']

            cache_pkg = cache_base.setdefault(pkg.name, OrderedDict())

            # generate a unique id to identify this package across different
            # builds and other releng-tool projects -- just a simple id string
            # to help reference a package component when interpreters do not
            # want to explicitly rely on a package name
            uid_str = 'releng-tool-' + pkg.name
            uid_data = uid_str.encode('utf_8')
            uid = hashlib.sha1(uid_data).hexdigest()  # noqa: S324

            version_desc = pkg.version
            if not version_desc and pkg.revision:
                version_desc = pkg.revision

            cache_pkg['id'] = uid
            cache_pkg['version'] = version_desc
            cache_pkg['site'] = pkg.site
            cache_pkg['licenses'] = []
            cache_pkg['hashes'] = []

            # extract hash entries (if any)
            try:
                hash_info = load_hashes(pkg.hash_file)
                if hash_info:
                    for type_, hash_, asset in hash_info:
                        cache_pkg['hashes'].append({
                            'algorithm': type_,
                            'file': asset,
                            'hash': hash_,
                        })
            except (BadFileHashLoadError, BadFormatHashLoadError):
                pass

            # copy license entries (if any)
            if pkg.license:
                cache_pkg['licenses'].extend(pkg.license)

        # remove host packages entry if we have no host packages
        if not cache['host-packages']:
            del cache['host-packages']

        # after processing all packages, now is a good time to timestamp the
        # cache of when this content was populated
        utc_now = datetime.now(tz=utc_timezone)
        cache['datetime'] = str(utc_now.isoformat())

        return cache

    def generate(self, cache):
        """
        generate an sbom file for the project

        Compiles a software build-of-materials document based on the cache
        information populated from a releng-tool project.

        Args:
            cache: the sbom cache

        Returns:
            ``True`` if the file was generated; ``False`` if the file could
            not be generated
        """

        fmt = self.opts.sbom_format
        all_fmt = SbomFormatType.ALL in fmt

        sbom_cvs = all_fmt or SbomFormatType.CSV in fmt
        sbom_html = all_fmt or SbomFormatType.HTML in fmt
        sbom_json = all_fmt or SbomFormatType.JSON in fmt
        sbom_text = all_fmt or SbomFormatType.TEXT in fmt
        sbom_xml = all_fmt or SbomFormatType.XML in fmt

        # if not formats are configured, enable text-SBOM by default
        if not fmt:
            sbom_text = True

        try:
            if sbom_cvs:
                self._generate_csv(cache)

            if sbom_html:
                self._generate_html(cache)

            if sbom_json:
                self._generate_json(cache)

            if sbom_text:
                self._generate_text(cache)

            if sbom_xml:
                self._generate_xml(cache)
        except IOError as e:
            err('unable to generate sbom output\n'
                '    {}\n', e)
            return False

        return True

    def _generate_csv(self, cache):
        """
        generate a csv format sbom file

        Compiles a CSV-formatted software build-of-materials document based
        on the cache information populated from a releng-tool project.

        Args:
            cache: the sbom cache
        """

        verbose('writing sbom (csv)')
        sbom_file = os.path.join(self.opts.out_dir, 'sbom.csv')

        attribs = {}
        if sys.version_info >= (3, 0):
            attribs['mode'] = 'w'
            attribs['newline'] = ''
        else:
            attribs['mode'] = 'wb'

        with open(sbom_file, **attribs) as f:
            f.write('# Software build of materials (SBOM; releng-tool)\n')
            f.write('# Report ID: ' + cache['report-id'] + '\n')
            f.write('# Generated: ' + cache['datetime'] + '\n')
            f.write('# SBOM Version: {}\n'.format(
                cache['releng-tool-sbom-version']))
            f.write('Name,Version,Site,Licenses,Flags\n')

            csv_writer = csv.writer(f)

            package_entries = OrderedDict()
            package_entries['packages'] = False
            package_entries['host-packages'] = True

            for entry, host_pkg in package_entries.items():
                data = cache.get(entry, None)
                if not data:
                    continue

                for pkg_name, pkg in data.items():
                    flags = []
                    if host_pkg:
                        flags.append('host')

                    csv_writer.writerow([
                        pkg_name,
                        pkg.get('version', ''),
                        pkg.get('site', ''),
                        ';'.join(pkg.get('licenses', [])),
                        ';'.join(flags),
                    ])

    def _generate_html(self, cache):
        """
        generate an html format sbom file

        Compiles an HTML-formatted software build-of-materials document based
        on the cache information populated from a releng-tool project.

        Args:
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

                pkg_props = ET.SubElement(pkg_data, 'div')
                pkg_props.set('class', 'entries')

                for key, val in properties.items():
                    entry = ET.SubElement(pkg_props, 'div')
                    ET.SubElement(entry, 'div').text = val
                    ET.SubElement(entry, 'div').text = pkg.get(key, '(none)')

                if pkg['licenses']:
                    entry = ET.SubElement(pkg_props, 'div')
                    ET.SubElement(entry, 'div').text = 'Licenses'
                    licenses_root = ET.SubElement(entry, 'div')
                    licenses_list = ET.SubElement(licenses_root, 'ul')

                    for pkg_license in pkg['licenses']:
                        ET.SubElement(licenses_list, 'li').text = pkg_license

                if pkg['hashes']:
                    pkg_hashes = ET.SubElement(pkg_data, 'div')
                    pkg_hashes.set('class', 'hashes')

                    for ph in pkg['hashes']:
                        ph_hdr = ET.SubElement(pkg_hashes, 'div')
                        ET.SubElement(ph_hdr, 'div').text = ph['algorithm']
                        ET.SubElement(ph_hdr, 'div').text = ph['file']

                        ph_data = ET.SubElement(pkg_hashes, 'div')
                        ET.SubElement(ph_data, 'div').text = ph['hash']

        if not has_pkg_data:
            no_pkg_data = ET.SubElement(body, 'div')
            no_pkg_data.set('class', 'no-pkg-data')
            no_pkg_data.text = 'No package information provided.'

        # writing the processed cache data to a file
        verbose('writing sbom (html)')
        sbom_file = os.path.join(self.opts.out_dir, 'sbom.html')
        xml = ET.tostring(root, 'utf_8')
        crude_html = xml.replace(b'&gt;', b'>')

        with open(sbom_file, 'wb') as f:
            f.write(crude_html)

    def _generate_json(self, cache):
        """
        generate a JSON format sbom file

        Compiles a JSON-formatted software build-of-materials document based
        on the cache information populated from a releng-tool project.

        Args:
            cache: the sbom cache
        """

        verbose('writing sbom (json)')
        sbom_file = os.path.join(self.opts.out_dir, 'sbom.json')
        with open(sbom_file, 'w') as f:
            json.dump(cache, f, indent=4)

    def _generate_text(self, cache):
        """
        generate a text format sbom file

        Compiles a text-formatted software build-of-materials document based
        on the cache information populated from a releng-tool project.

        Args:
            cache: the sbom cache
        """

        verbose('writing sbom (text)')
        sbom_file = os.path.join(self.opts.out_dir, 'sbom.txt')
        with open(sbom_file, 'w') as f:
            f.write('Software build of materials (SBOM; releng-tool)\n')
            f.write('Report ID: ' + cache['report-id'] + '\n')
            f.write('Generated: ' + cache['datetime'] + '\n')
            f.write('\n')

            package_entries = OrderedDict()
            package_entries['packages'] = 'Packages'
            package_entries['host-packages'] = 'Host packages'

            has_pkg_data = False
            for entry, desc in package_entries.items():
                data = cache.get(entry, None)
                if not data:
                    continue

                has_pkg_data = True
                f.write('''\
--------------------------------------------------------------------------------
{}
--------------------------------------------------------------------------------
'''.format(desc))

                for pkg_name, pkg in data.items():
                    f.write('\n')

                    f.write(pkg_name)
                    if pkg['version']:
                        f.write(' ({})'.format(pkg['version']))
                    f.write('\n')

                    if pkg['site']:
                        f.write(' Site: ' + pkg['site'] + '\n')

                    if pkg['licenses']:
                        f.write(' Licenses:\n')
                        for pkg_license in pkg['licenses']:
                            f.write('  {}\n'.format(pkg_license))

                    if pkg['hashes']:
                        f.write(' Hashes:\n')
                        for pkg_hash in pkg['hashes']:
                            f.write('  [{}] {}: {}\n'.format(
                                pkg_hash['algorithm'],
                                pkg_hash['file'],
                                pkg_hash['hash'],
                            ))

            if not has_pkg_data:
                f.write('No package information provided.\n')

    def _generate_xml(self, cache):
        """
        generate an XML format sbom file

        Compiles an XML-formatted software build-of-materials document based
        on the cache information populated from a releng-tool project.

        Args:
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
        sbom_file = os.path.join(self.opts.out_dir, 'sbom.xml')
        xml = ET.tostring(root, 'utf_8')
        tree = xml_minidom.parseString(xml)

        with open(sbom_file, 'w') as f:
            data = tree.toprettyxml(indent=' ' * 4)
            f.write(data)

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

.entries ul {
    margin: 0;
    padding: 0 0 0 15px;
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