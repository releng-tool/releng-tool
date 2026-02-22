# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.defs import PackageInstallType
from releng_tool.tool.waf import WAF
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand
import os

#: default bin container directory
DEFAULT_BIN_DIR = 'bin'

#: default lib container directory
DEFAULT_LIB_DIR = 'lib'


def configure(opts):
    """
    support configuration for waf projects

    With provided configuration options (``RelengConfigureOptions``), the
    configuration stage will be processed.

    Args:
        opts: configuration options

    Returns:
        ``True`` if the configuration stage is completed; ``False`` otherwise
    """

    if not WAF.exists():
        err('unable to configure package; waf is not installed')
        return False

    prefix = opts.prefix

    base_locs = []
    if opts.install_type == PackageInstallType.HOST:
        base_locs.append(opts.host_dir)
    else:
        base_locs.append(opts.staging_dir)

        # only reference/pre-create the target directory if this package is
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
    waf_defs = {
        '--bindir': DEFAULT_BIN_DIR,
        '--libdir': DEFAULT_LIB_DIR,
        '--out': opts.build_output_dir,
        '--prefix': opts.prefix,
    }
    if opts.conf_defs:
        waf_defs.update(expand(opts.conf_defs))

    # default options
    waf_opts = {
    }
    if opts.conf_opts:
        waf_opts.update(expand(opts.conf_opts))

    # default environment
    env = {
        'INCLUDES': os.pathsep.join(include_locs),
        'LIBPATH': os.pathsep.join(library_locs),
    }

    if opts.conf_env:
        env.update(expand(opts.conf_env))

    # argument building
    waf_args = [
        'configure',
    ]
    waf_args.extend(prepare_definitions(waf_defs))
    waf_args.extend(prepare_arguments(waf_opts))

    if not WAF.execute(waf_args, env=expand(env)):
        err('failed to configure waf project: {}', opts.name)
        return False

    return True
