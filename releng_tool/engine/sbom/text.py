# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from collections import OrderedDict
from releng_tool.util.log import verbose
import os


def generate_text(sbom, cache):
    """
    generate a text format sbom file

    Compiles a text-formatted software build-of-materials document based
    on the cache information populated from a releng-tool project.

    Args:
        sbom: sbom manager instance
        cache: the sbom cache
    """

    verbose('writing sbom (text)')
    sbom_file = os.path.join(sbom.opts.out_dir, 'sbom.txt')
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
            f.write(f'''\
--------------------------------------------------------------------------------
{desc}
--------------------------------------------------------------------------------
''')

            for pkg_name, pkg in data.items():
                has_pkg_info = False
                f.write('\n')

                f.write(pkg_name)
                if pkg['version']:
                    has_pkg_info = True
                    f.write(' ({})'.format(pkg['version']))
                f.write('\n')

                has_site = pkg.get('site', '')
                if has_site:
                    has_pkg_info = True
                    f.write(' Site: ' + pkg['site'] + '\n')

                has_revision = pkg.get('revision', '')
                if has_revision:
                    has_pkg_info = True
                    f.write(' Revision: ' + pkg['revision'] + '\n')

                if pkg['licenses']:
                    has_pkg_info = True
                    f.write(' Licenses:\n')
                    for pkg_license in pkg['licenses']:
                        f.write(f'  {pkg_license}\n')
                elif has_site:
                    f.write('  No licenses.\n')

                if pkg['hashes']:
                    has_pkg_info = True
                    f.write(' Hashes:\n')
                    for pkg_hash in pkg['hashes']:
                        f.write('  [{}] {}: {}\n'.format(
                            pkg_hash['algorithm'],
                            pkg_hash['file'],
                            pkg_hash['hash'],
                        ))
                elif has_site:
                    f.write('  No hashes.\n')

                if not has_pkg_info:
                    f.write('  (no details)\n')

        if not has_pkg_data:
            f.write('No package information provided.\n')

    sbom.generated.append(sbom_file)
