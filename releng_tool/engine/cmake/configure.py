# -*- coding: utf-8 -*-
# Copyright 2018-2022 releng-tool

from releng_tool.defs import PackageInstallType
from releng_tool.tool.cmake import CMAKE
from releng_tool.util.io import ensure_dir_exists
from releng_tool.util.io import interim_working_dir
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand
import os
import posixpath

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

    base_locs = []
    if opts._install_type == PackageInstallType.HOST:
        base_locs.append(opts.host_dir)
    else:
        base_locs.append(opts.staging_dir)

        # only reference/pre-create the target directory if this package is
        # aimed to use the target directory
        target_area_types = [
            PackageInstallType.STAGING_AND_TARGET,
            PackageInstallType.TARGET,
        ]
        if opts._install_type in target_area_types:
            base_locs.append(opts.target_dir)

    include_locs = []
    library_locs = []
    prefix_locs = []
    for base_loc in base_locs:
        prefixed_base = base_loc + prefix
        include_locs.append(os.path.join(prefixed_base, 'include'))
        library_locs.append(os.path.join(prefixed_base, DEFAULT_LIB_DIR))
        prefix_locs.append(prefixed_base)

    lib_dir = os.path.join(prefix, DEFAULT_LIB_DIR)

    # ensure the non-full prefix options are passed in a posix style, or
    # some versions of CMake/projects may treat the path separators as
    # escape characters
    posix_prefix = prefix.replace(os.sep, posixpath.sep)
    posix_lib_dir = lib_dir.replace(os.sep, posixpath.sep)

    # definitions
    cmake_defs = {
        # configure as RelWithDebInfo (when using multi-configuration projects)
        'CMAKE_BUILD_TYPE': 'RelWithDebInfo',
        # common paths for releng-tool sysroots
        'CMAKE_INCLUDE_PATH': ';'.join(include_locs),
        'CMAKE_INSTALL_PREFIX': posix_prefix,
        'CMAKE_LIBRARY_PATH': ';'.join(library_locs),
        'CMAKE_PREFIX_PATH': ';'.join(prefix_locs),
        # releng-tool's sysroot assumes a `lib` directory. CMake's
        # GNUInstallDirs may adjust the expected lib directory based on the
        # detected system name (as a project may not necessarily be
        # cross-compiling), which may implicitly set the library directory to
        # `lib64`.
        'CMAKE_INSTALL_LIBDIR': posix_lib_dir,
    }
    if opts.conf_defs:
        cmake_defs.update(expand(opts.conf_defs))

    # options
    cmake_opts = {
    }
    if opts.conf_opts:
        cmake_opts.update(expand(opts.conf_opts))

    # argument building
    cmake_args = [
        '--no-warn-unused-cli',  # suppress common opts if not used in project
    ]
    cmake_args.extend(prepare_definitions(cmake_defs, '-D'))
    cmake_args.extend(prepare_arguments(cmake_opts))

    # output directory
    cmake_args.append(opts.build_dir)

    # ensure provided include/library targets exists ahead of time to help
    # reduce the risk of CMake projects creating files for these directory paths
    populate_dirs = []
    if 'CMAKE_INCLUDE_PATH' in cmake_defs:
        populate_dirs.extend(cmake_defs['CMAKE_INCLUDE_PATH'].split(';'))
    if 'CMAKE_LIBRARY_PATH' in cmake_defs:
        populate_dirs.extend(cmake_defs['CMAKE_LIBRARY_PATH'].split(';'))
    for dir_ in populate_dirs:
        if not ensure_dir_exists(dir_):
            return False

    # cmake prepares build scripts out-of-source; move into the build output
    # directory and generate scripts from the build directory
    with interim_working_dir(opts.build_output_dir):
        if not CMAKE.execute(cmake_args, env=expand(opts.conf_env)):
            err('failed to prepare cmake project: {}', opts.name)
            return False

    return True
