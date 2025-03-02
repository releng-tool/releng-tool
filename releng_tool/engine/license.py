# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.log import err
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
from releng_tool.util.string import expand
from shutil import copyfileobj
import os


class LicenseManager:
    """
    license manager

    A license manager is used to help scanning known package definitions
    to find associated licenses for a project and help build a complete
    license description.

    Args:
        opts: options used to configure the engine

    Attributes:
        generated: list of generated license files
        opts: options used to configure the engine
    """
    def __init__(self, opts):
        self.generated = []
        self.opts = opts

    def build_cache(self, pkgs):
        """
        compile a cache of project license information

        For each provided package, check for license information and
        compile a list of known licenses files for a given package's version.

        Args:
            pkgs: packages which may be assigned licenses

        Returns:
            ``True`` if the license file was generated; ``False`` if the
            license file could not be generated
        """

        license_cache = {}

        # for each package, cache a list of license files for the applicable
        # package version
        for pkg in pkgs:
            if not pkg.license_files:
                continue

            version_desc = pkg.version
            if not version_desc and pkg.revision:
                version_desc = pkg.revision

            license_cache[pkg.name] = {
                'files': [],
                'version': version_desc,
            }

            for file in pkg.license_files:
                file = os.path.join(pkg.build_dir, file)
                license_cache[pkg.name]['files'].append(file)

        return license_cache

    def generate(self, cache):
        """
        generate a license file for the project

        Compiles a document containing all the license information for a
        configured project. License information defined the provided cache
        will be populated into a single file.

        Args:
            cache: the license cache

        Returns:
            ``True`` if the license file was generated; ``False`` if the
            license file could not be generated
        """

        # ensure we can output any license content into the license folder
        if not mkdir(self.opts.license_dir):
            return False

        # build a single license file -- holding a list of all license
        # definitions for all applicable packages for this run
        license_file = os.path.join(self.opts.license_dir, 'licenses')
        try:
            with open(license_file, 'w') as dst:
                license_header = expand(self.opts.license_header)
                if not license_header:
                    license_header = 'license(s)'

                # output license header
                dst.write(f'''{license_header}
################################################################################
''')

                # output license header
                has_pkg_info = False
                for license_name, license_data in sorted(cache.items()):
                    license_files = license_data['files']
                    license_version = license_data['version']
                    has_pkg_info = True
                    dst.write(f'''
{license_name}-{license_version}
--------------------------------------------------------------------------------
''')
                    for pkg_license_file in sorted(license_files):
                        verbose('writing license file ({}): {}',
                            license_name, pkg_license_file)

                        if os.path.isfile(pkg_license_file):
                            with open(pkg_license_file) as f:
                                copyfileobj(f, dst)
                        else:
                            dst.write('(missing)\n')
                            warn('license file missing: {}', pkg_license_file)

                        dst.write('')

                if not has_pkg_info:
                    dst.write('\nNo package license information available.')

            self.generated.append(license_file)
            verbose('license file has been written')
        except OSError as e:
            err('unable to populate license information\n'
                '    {}', e)
            return False

        return True
