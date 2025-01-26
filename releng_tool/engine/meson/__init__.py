# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import PackageInstallType
import os

#: default lib container directory
DEFAULT_LIB_DIR = 'lib'


# prepare a meson stage's environment
#
# The following is used to prepare a Meson environment for running a stage
# (either configuration or build stages). There looks to be no specific way
# for an outside instance to override the path of where dependencies may be
# found. Meson does provide `find_library` calls, where if a Meson project
# uses these calls, releng-tool can try to assist by providing expected
# library paths by setting the `LIBRARY_PATH` environment variable.
def meson_prepare_environment(opts):
    env = {}

    base_locs = []
    if opts.install_type == PackageInstallType.HOST:
        base_locs.append(opts.host_dir)
    else:
        base_locs.append(opts.staging_dir)

        # only reference the target directory if this package is
        # aimed to use the target directory
        target_area_types = [
            PackageInstallType.STAGING_AND_TARGET,
            PackageInstallType.TARGET,
        ]
        if opts.install_type in target_area_types:
            base_locs.append(opts.target_dir)

    include_locs = []
    library_locs = []
    for base_loc in base_locs:
        prefixed_base = base_loc + opts.prefix
        include_locs.append(os.path.join(prefixed_base, 'include'))
        library_locs.append(os.path.join(prefixed_base, DEFAULT_LIB_DIR))

    env['CPATH'] = os.pathsep.join(include_locs)
    env['LIBRARY_PATH'] = os.pathsep.join(library_locs)

    return env
