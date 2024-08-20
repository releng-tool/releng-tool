# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from collections import OrderedDict
from copy import deepcopy
from datetime import datetime
from releng_tool import __version__ as releng_version
from releng_tool.defs import PackageInstallType
from releng_tool.defs import SbomFormatType
from releng_tool.defs import VcsType
from releng_tool.util.compat import utc_timezone
from releng_tool.util.hash import BadFileHashLoadError
from releng_tool.util.hash import BadFormatHashLoadError
from releng_tool.util.hash import load as load_hashes
from releng_tool.util.io import ensure_dir_exists
from releng_tool.util.log import err
from releng_tool.util.log import verbose
from releng_tool.util.spdx import ConjunctiveLicenses
from releng_tool.util.spdx import LicenseEntries
from releng_tool.util.spdx import spdx_parse
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

# spdx license list version used
SPDX_LLVERSION = '3.25'

# specification followed for generated spdx-sboms
SPDX_SPEC = 'SPDX-2.3'


class SbomManager:
    """
    sbom manager

    An SBOM manager is used to help generate a software build-of-materials for
    a releng-tool project. This can be used to help track package versions
    used, dependency history and more.

    Args:
        opts: options used to configure the engine

    Attributes:
        generated: list of generated sbom files
        opts: options used to configure the engine
    """
    def __init__(self, opts):
        self.generated = []
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
                cache_pkg['licenses'] = deepcopy(pkg.license)

        # remove host packages entry if we have no host packages
        if not cache['host-packages']:
            del cache['host-packages']

        # if no project identifier is set, generate one
        if 'releng-tool-pid' not in cache:
            pid_tmp = 'releng-tool'
            for pkg in pkgs:
                pid_tmp += ';' + pkg.name
            uid_data = pid_tmp.encode('utf_8')
            pid = hashlib.sha1(uid_data).hexdigest()  # noqa: S324
            cache['releng-tool-pid'] = 'releng-tool-' + pid[:8]

        # after processing all packages, now is a good time to timestamp the
        # cache of when this content was populated
        utc_now = datetime.now(tz=utc_timezone)
        utc_now_str = utc_now.strftime("%Y-%m-%dT%H:%M:%S") + 'Z'
        cache['datetime'] = utc_now_str

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

        # ensure output directory exists before any attempts to generate
        # (e.g. if an engine was just asked to create SBOMs)
        if not ensure_dir_exists(self.opts.out_dir):
            return False

        fmt = self.opts.sbom_format
        all_fmt = SbomFormatType.ALL in fmt

        sbom_cvs = all_fmt or SbomFormatType.CSV in fmt
        sbom_html = all_fmt or SbomFormatType.HTML in fmt
        sbom_json = all_fmt or SbomFormatType.JSON in fmt
        sbom_json_spdx = all_fmt or SbomFormatType.JSON_SPDX in fmt
        sbom_rdp_spdx = all_fmt or SbomFormatType.RDP_SPDX in fmt
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

            if sbom_json_spdx:
                self._generate_json_spdx(cache)

            if sbom_rdp_spdx:
                self._generate_rdp_spdx(cache)

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

        self.generated.append(sbom_file)

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

        self.generated.append(sbom_file)

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

        self.generated.append(sbom_file)

    def _generate_json_spdx(self, cache):
        """
        generate a SPDX compliant JSON format sbom file

        Compiles a JSON-formatted software build-of-materials document based
        on the cache information populated from a releng-tool project.

        Args:
            cache: the sbom cache
        """

        prj_name = cache['releng-tool-pid']
        uid = cache['report-id']
        doc_namespace = 'https://spdx.org/spdxdocs/{}-{}'.format(prj_name, uid)

        spdx_cache = OrderedDict()
        spdx_cache['SPDXID'] = 'SPDXRef-DOCUMENT'
        spdx_cache['spdxVersion'] = SPDX_SPEC
        spdx_cache['name'] = prj_name
        spdx_cache['dataLicense'] = 'CC0-1.0'
        spdx_cache['documentDescribes'] = []
        spdx_cache['documentNamespace'] = doc_namespace
        spdx_cache['creationInfo'] = OrderedDict()
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

                package_entry = OrderedDict()
                package_entry['SPDXID'] = 'SPDXRef-' + pkg_name
                package_entry['name'] = pkg_name
                package_entry['versionInfo'] = pkg.get('version', '')
                package_entry['downloadLocation'] = pkg.get('site', 'NONE')
                package_entry['filesAnalyzed'] = False
                package_entry['licenseDeclared'] = pkg_license
                package_entry['licenseConcluded'] = pkg_license_final

                spdx_cache['packages'].append(package_entry)
                spdx_cache['documentDescribes'].append(package_entry['SPDXID'])

        verbose('writing sbom (json-spdx)')
        sbom_file = os.path.join(self.opts.out_dir, 'sbom-spdx.json')
        with open(sbom_file, 'w') as f:
            json.dump(spdx_cache, f, indent=4)

        self.generated.append(sbom_file)

    def _generate_rdp_spdx(self, cache):
        """
        generate a SPDX compliant RDP (XML) format sbom file

        Compiles an RDP-formatted software build-of-materials document based
        on the cache information populated from a releng-tool project.

        Args:
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
        base_namespace = 'https://spdx.org/spdxdocs/{}-{}'.format(prj_name, uid)
        doc_namespace = '{}#{}'.format(base_namespace, 'SPDXRef-DOCUMENT')

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
                pkg_dl_loc = pkg.get('site', 'NONE')

                rcontainer = ET.SubElement(root, 'spdx:relationship')
                rroot = ET.SubElement(rcontainer, 'spdx:Relationship')
                rtype = ET.SubElement(rroot, 'spdx:relationshipType')
                rtype.set('rdf:resource', rdf_term_rdesc)
                relement = ET.SubElement(rroot, 'spdx:relatedSpdxElement')
                proot = ET.SubElement(relement, 'spdx:Package')

                pkg_namespace = '{}#SPDXRef-{}'.format(base_namespace, pkg_name)
                proot.set('rdf:about', pkg_namespace)

                XML_ELEMENT(proot, 'spdx:specVersion', SPDX_SPEC)
                XML_ELEMENT(proot, 'spdx:name', pkg_name)
                XML_ELEMENT(proot, 'spdx:versionInfo', pkg.get('version', ''))
                XML_ELEMENT(proot, 'spdx:downloadLocation', pkg_dl_loc)
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
        verbose('writing sbom (rdp-spdx)')
        sbom_file = os.path.join(self.opts.out_dir, 'sbom-spdx.xml')
        xml = ET.tostring(rdf_root, 'utf_8')
        tree = xml_minidom.parseString(xml)

        with open(sbom_file, 'w') as f:
            rdf_tree = tree.childNodes[0]
            data = rdf_tree.toprettyxml(indent=' ' * 4)
            f.write(data)

        self.generated.append(sbom_file)

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

        self.generated.append(sbom_file)

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

        self.generated.append(sbom_file)


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
