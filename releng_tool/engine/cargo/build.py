# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import VcsType
from releng_tool.engine.cargo import CARGO_COMMON_TARGET
from releng_tool.tool.cargo import CARGO
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand
import os


def build(opts):
    """
    support building cargo projects

    With provided build options (``RelengBuildOptions``), the build stage will
    be processed.

    Args:
        opts: build options

    Returns:
        ``True`` if the building stage is completed; ``False`` otherwise
    """

    if not CARGO.exists():
        err('unable to build package; cargo is not installed')
        return False

    # definitions
    cargo_defs = {
    }
    if opts.build_defs:
        cargo_defs.update(expand(opts.build_defs))

    # options
    cargo_opts = {
    }
    if opts.build_opts:
        cargo_opts.update(expand(opts.build_opts))

    # argument building
    cargo_args = [
        'build',
        # provide an explicit cargo path (to prevent cargo from searching)
        '--manifest-path',
        'Cargo.toml',
        # never perform online interaction in build stage
        '--offline',
        # configure target directory to this package's output folder
        '--target-dir',
        os.path.join(opts.build_base_dir, CARGO_COMMON_TARGET),
    ]
    cargo_args.extend(opts._cargo_depargs)

    # controlled dependencies... but be flexible for local projects
    if opts._vcs_type != VcsType.LOCAL:
        cargo_args.append('--locked')

    # If the package does not define a specific profile to run, assume a
    # default "release" build.
    if not opts.build_opts or '--profile' not in opts.build_opts:
        cargo_args.append('--release')

    cargo_args.extend(prepare_definitions(cargo_defs))
    cargo_args.extend(prepare_arguments(cargo_opts))

    # default environment
    env = {
    }
    if opts.build_env:
        env.update(expand(opts.build_env))

    # enable specific number of parallel jobs is set
    if opts.jobsconf != 1 and opts.jobs > 1:
        env['CARGO_BUILD_JOBS'] = str(opts.jobs)

    if not CARGO.execute(cargo_args, env=env):
        err('failed to build cargo project: {}', opts.name)
        return False

    return True
