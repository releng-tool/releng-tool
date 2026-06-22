# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.tool.xmake import XMAKE
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.string import expand


def build(opts):
    """
    support building xmake projects

    With provided build options (``RelengBuildOptions``), the build stage will
    be processed.

    Args:
        opts: build options

    Returns:
        ``True`` if the building stage is completed; ``False`` otherwise
    """

    if not XMAKE.exists():
        err('unable to build package; xmake is not installed')
        return False

    # definitions
    xmake_defs = {
    }
    if opts.build_defs:
        xmake_defs.update(expand(opts.build_defs))

    # options
    xmake_opts = {
    }
    if opts.build_opts:
        xmake_opts.update(expand(opts.build_opts))

    # argument building
    xmake_args = [
        'build',
    ]
    xmake_args.extend(prepare_definitions(xmake_defs))
    xmake_args.extend(prepare_arguments(xmake_opts))

    if opts.jobs > 1:
        xmake_args.append(f'--jobs={opts.jobs}')

    # default environment
    env = {
        'XMAKE_CONFIGDIR': opts.build_output_dir,
        'XMAKE_GLOBALDIR': f'{opts.build_base_dir}/.releng-tool-xmake-global',
        'XMAKE_TMPDIR': f'{opts.build_base_dir}/.releng-tool-xmake-tmp',
    }
    if opts.build_env:
        env.update(expand(opts.build_env))

    # pre-build target dependency folder paths; we observe (at least, on OS X)
    # that xmake can fail to build complaining objects cannot write due to
    # dependency paths not existing; workaround this for now by helping xmake
    # ensure they are built
    if 'releng.xmake.disable_deps_init' not in opts._quirks:
        ideps_script = Path(__file__).parent / 'init-deps.lua'

        rv, detected_targets = XMAKE.execute_rv('lua', ideps_script, env=env)
        if rv == 0:
            deps_dir = f'{opts.build_output_dir}/.deps'

            for target in detected_targets.splitlines():
                target_dir = f'{deps_dir}/{target}'
                debug(f'pre-building target dependency folder: {target_dir}')
                mkdir(target_dir)

            if not detected_targets:
                debug('no xmake targets detected')
        else:
            debug('failed to detect xmake targets')

    if not XMAKE.execute(xmake_args, env=env):
        err('failed to build xmake project: {}', opts.name)
        return False

    return True
