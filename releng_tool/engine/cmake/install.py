# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.cmake import CMAKE
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand


def install(opts):
    """
    support installation cmake projects

    With provided installation options (``RelengInstallOptions``), the
    installation stage will be processed.

    Args:
        opts: installation options

    Returns:
        ``True`` if the installation stage is completed; ``False`` otherwise
    """

    if not CMAKE.exists():
        err('unable to install package; cmake is not installed')
        return False

    # default definitions
    cmake_defs = {
    }
    if opts.install_defs:
        cmake_defs.update(expand(opts.install_defs))

    # default options
    cmake_opts = {
        '--config': opts._cmake_build_type,
        # default install using the install target
        '--target': 'install',
    }
    if opts.install_opts:
        cmake_opts.update(expand(opts.install_opts))

    # argument building
    cmake_args = [
        '--build',
        opts.build_output_dir,
    ]
    cmake_args.extend(prepare_definitions(cmake_defs, '-D'))
    cmake_args.extend(prepare_arguments(cmake_opts))

    # default environment
    env = {
        # always force an install to avoid possible issues with file time
        # installation checks; releng-tool already wraps the installation
        # event with its own control flags, so forcing an install should
        # not cause any major issues
        'CMAKE_INSTALL_ALWAYS': '1',
    }

    if opts.install_env:
        env.update(expand(opts.install_env))

    # install to each destination
    for dest_dir in opts.dest_dirs:
        env['DESTDIR'] = dest_dir
        if not CMAKE.execute(cmake_args, env=env):
            err('failed to install cmake project: {}', opts.name)
            return False

    return True
