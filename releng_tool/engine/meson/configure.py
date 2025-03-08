# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import PackageInstallType
from releng_tool.engine.meson import DEFAULT_LIB_DIR
from releng_tool.engine.meson import meson_prepare_environment
from releng_tool.tool.meson import MESON
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.io_exists import path_exists
from releng_tool.util.log import err
from releng_tool.util.string import expand
import os


def configure(opts):
    """
    support configuration for meson projects

    With provided configuration options (``RelengConfigureOptions``), the
    configuration stage will be processed.

    Args:
        opts: configuration options

    Returns:
        ``True`` if the configuration stage is completed; ``False`` otherwise
    """

    if not MESON.exists():
        err('unable to configure package; meson is not installed')
        return False

    prefix = opts.prefix

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

    pkgconfig_locs = []
    prefix_locs = []
    for base_loc in base_locs:
        prefixed_base = base_loc + prefix
        pkgconfig_locs.append(
            os.path.join(prefixed_base, DEFAULT_LIB_DIR, 'pkgconfig'))
        prefix_locs.append(prefixed_base)

    # definitions
    meson_defs = {
        'libdir': DEFAULT_LIB_DIR,
        # common paths for releng-tool sysroots
        'cmake_prefix_path': os.pathsep.join(prefix_locs),
        'pkg_config_path': os.pathsep.join(pkgconfig_locs),
        # do not permit downloads of dependencies by default; in theory,
        # projects could have a package definition for each dependency needed
        # for a package
        'wrap_mode': 'nodownload',
    }

    if prefix:
        meson_defs['prefix'] = prefix

    if opts.conf_defs:
        meson_defs.update(expand(opts.conf_defs))

    # options
    meson_opts = {
        '--buildtype': 'debugoptimized',
    }
    if opts.conf_opts:
        meson_opts.update(expand(opts.conf_opts))

    # environment
    meson_env = meson_prepare_environment(opts)
    if opts.conf_env:
        meson_env.update(opts.conf_env)

    # argument building
    meson_args = [
        'setup',
    ]
    meson_args.extend(prepare_definitions(meson_defs, '-D'))
    meson_args.extend(prepare_arguments(meson_opts))

    # provide build directory
    meson_args.append(opts.build_output_dir)

    # if this is a forced reconfiguration and we have built before,
    # inform meson
    if path_exists(opts.build_output_dir) and \
            opts.env.get('RELENG_RECONFIGURE'):
        meson_args.append('--reconfigure')

    if not MESON.execute(meson_args, env=expand(meson_env)):
        err('failed to prepare meson project: {}', opts.name)
        return False

    return True
