# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.defs import PackageInstallType
from releng_tool.engine.xmake import detect_default_xmake_arch
from releng_tool.tool.xmake import XMAKE
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand
import os

#: default lib container directory
DEFAULT_LIB_DIR = 'lib'


def configure(opts):
    """
    support configuration for xmake projects

    With provided configuration options (``RelengConfigureOptions``), the
    configuration stage will be processed.

    Args:
        opts: configuration options

    Returns:
        ``True`` if the configuration stage is completed; ``False`` otherwise
    """

    if not XMAKE.exists():
        err('unable to configure package; xmake is not installed')
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

    include_locs = []
    library_locs = []
    for base_loc in base_locs:
        prefixed_base = Path(base_loc + prefix)
        include_locs.append((prefixed_base / 'include').as_posix())
        library_locs.append((prefixed_base / DEFAULT_LIB_DIR).as_posix())

    # definitions
    xmake_defs = {
        '--includedirs': os.pathsep.join(include_locs),
        '--linkdirs': os.pathsep.join(library_locs),
    }

    if 'releng.xmake.disable_arch_detection' not in opts._quirks:
        detected_arch = detect_default_xmake_arch()
        if detected_arch:
            xmake_defs['--arch'] = detected_arch

    if opts._xmake_build_type:
        xmake_defs['--mode'] = opts._xmake_build_type

    if opts.conf_defs:
        xmake_defs.update(expand(opts.conf_defs))

    # options
    xmake_opts = {
    }
    if opts.conf_opts:
        xmake_opts.update(expand(opts.conf_opts))

    # environment
    xmake_env = {
        'XMAKE_CONFIGDIR': opts.build_output_dir,
        'XMAKE_GLOBALDIR': f'{opts.build_base_dir}/.releng-tool-xmake-global',
        'XMAKE_TMPDIR': f'{opts.build_base_dir}/.releng-tool-xmake-tmp',
    }
    if opts.conf_env:
        xmake_env.update(opts.conf_env)

    # argument building
    xmake_args = [
        'config',
        # use -o over `--builddir` to support legacy installs with `--buildir`
        '-o', opts.build_output_dir,
    ]
    xmake_args.extend(prepare_definitions(xmake_defs))
    xmake_args.extend(prepare_arguments(xmake_opts))

    if not XMAKE.execute(xmake_args, env=expand(xmake_env)):
        err('failed to prepare xmake project: {}', opts.name)
        return False

    return True
