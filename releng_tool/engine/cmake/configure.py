# -*- coding: utf-8 -*-
# Copyright 2018-2019 releng-tool

from ...defs import PackageInstallType
from ...tool.cmake import *
from ...util.io import interimWorkingDirectory
from ...util.io import prepare_arguments
from ...util.io import prepare_definitions
from ...util.log import *
from ...util.string import expand as EXP
from os.path import join

#: default lib container directory
DEFAULT_LIB_DIR = 'lib'

def configure(opts):
    """
    support configuration for cmake projects

    With provided configuration options (``RelengConfigureOptions``), the
    configuration stage will be processed.

    Args:
        opts: configuration options

    Returns:
        ``True`` if the configuration stage is completed; ``False`` otherwise
    """

    if not CMAKE.exists():
        err('unable to configure package; cmake is not installed')
        return False

    prefix = opts.prefix
    if opts._install_type == PackageInstallType.HOST:
        include_loc = join(opts.host_dir + prefix, 'include')
        library_loc = join(opts.host_dir + prefix, DEFAULT_LIB_DIR)
        prefix_loc = join(opts.host_dir + prefix)
    else:
        include_loc = (
            join(opts.staging_dir + prefix, 'include') + ';' +
            join(opts.target_dir + prefix, 'include'))
        library_loc = (
            join(opts.staging_dir + prefix, DEFAULT_LIB_DIR) + ';' +
            join(opts.target_dir + prefix, DEFAULT_LIB_DIR))
        prefix_loc = (
            join(opts.staging_dir + prefix) + ';' +
            join(opts.target_dir + prefix))

    # definitions
    cmakeDefs = {
        # configure as RelWithDebInfo (when using multi-configuration projects)
        'CMAKE_BUILD_TYPE': 'RelWithDebInfo',
        # common paths for releng-tool sysroots
        'CMAKE_INCLUDE_PATH': include_loc,
        'CMAKE_INSTALL_PREFIX': prefix,
        'CMAKE_LIBRARY_PATH': library_loc,
        'CMAKE_PREFIX_PATH': prefix_loc,
        # releng-tool's sysroot assumes a `lib` directory. CMake's
        # GNUInstallDirs may adjust the expected lib directory based on the
        # detected system name (as a project may not necessarily be
        # cross-compiling), which may implicitly set the library directory to
        # `lib64`.
        'CMAKE_INSTALL_LIBDIR': join(prefix, DEFAULT_LIB_DIR),
    }
    if opts.conf_defs:
        cmakeDefs.update(EXP(opts.conf_defs))

    # options
    cmakeOpts = {
    }
    if opts.conf_opts:
        cmakeOpts.update(EXP(opts.conf_opts))

    # argument building
    cmakeArgs = [
        '--no-warn-unused-cli', # suppress common options if not used in project
    ]
    cmakeArgs.extend(prepare_definitions(cmakeDefs, '-D'))
    cmakeArgs.extend(prepare_arguments(cmakeOpts))

    # output directory
    cmakeArgs.append(opts.build_dir)

    # cmake prepares build scripts out-of-source; move into the build output
    # directory and generate scripts from the build directory
    with interimWorkingDirectory(opts.build_output_dir):
        if not CMAKE.execute(cmakeArgs, env=EXP(opts.conf_env)):
            err('failed to prepare cmake project: {}', opts.name)
            return False

    return True
