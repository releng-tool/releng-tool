# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.log import verbose
import csv
import os


def generate_csv(sbom, cache):
    """
    generate a csv format sbom file

    Compiles a CSV-formatted software build-of-materials document based
    on the cache information populated from a releng-tool project.

    Args:
        sbom: sbom manager instance
        cache: the sbom cache
    """

    verbose('writing sbom (csv)')
    sbom_file = os.path.join(sbom.opts.out_dir, 'sbom.csv')

    with open(sbom_file, mode='w', newline='') as f:
        f.write('# Software build of materials (SBOM; releng-tool)\n')
        f.write('# Report ID: ' + cache['report-id'] + '\n')
        f.write('# Generated: ' + cache['datetime'] + '\n')
        f.write('# SBOM Version: {}\n'.format(
            cache['releng-tool-sbom-version']))
        f.write('Name,Version,Site,Licenses,Flags\n')

        csv_writer = csv.writer(f)

        package_entries = {}
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

                pkg_revision = pkg.get('revision', '')
                if pkg_revision:
                    flags.append(f'revision={pkg_revision}')

                csv_writer.writerow([
                    pkg_name,
                    pkg.get('version', ''),
                    pkg.get('site', ''),
                    ';'.join(pkg.get('licenses', [])),
                    ';'.join(flags),
                ])

    sbom.generated.append(sbom_file)
