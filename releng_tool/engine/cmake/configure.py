# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.defs import PackageInstallType
from releng_tool.tool.cmake import CMAKE
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.io_wd import wd
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import verbose
from releng_tool.util.string import expand
import os
import posixpath

#: default lib container directory
DEFAULT_LIB_DIR = 'lib'

# cmake system include directories for various language types
CMAKE_INCLUDE_INJECT_OPTIONS = [
    'CMAKE_CUDA_STANDARD_INCLUDE_DIRECTORIES',
    'CMAKE_CXX_STANDARD_INCLUDE_DIRECTORIES',
    'CMAKE_C_STANDARD_INCLUDE_DIRECTORIES',
    'CMAKE_HIP_STANDARD_INCLUDE_DIRECTORIES',
    'CMAKE_OBJCXX_STANDARD_INCLUDE_DIRECTORIES',
    'CMAKE_OBJC_STANDARD_INCLUDE_DIRECTORIES',
]


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
    modules_locs = []
    prefix_locs = []
    for base_loc in base_locs:
        prefixed_base = Path(base_loc + prefix)
        cmake_modules = prefixed_base / 'share' / 'cmake' / 'Modules'
        include_locs.append((prefixed_base / 'include').as_posix())
        library_locs.append((prefixed_base / DEFAULT_LIB_DIR).as_posix())
        modules_locs.append(cmake_modules.as_posix())
        prefix_locs.append(prefixed_base.as_posix())

    # ensure the non-full prefix options are passed in a posix style, or
    # some versions of CMake/projects may treat the path separators as
    # escape characters
    posix_prefix = prefix.replace(os.sep, posixpath.sep)

    # definitions
    compiled_include_locs = ';'.join(include_locs)
    default_cmake_defs = {
        'CMAKE_BUILD_TYPE': opts._cmake_build_type,
        # common paths for releng-tool sysroots
        'CMAKE_INCLUDE_PATH': compiled_include_locs,
        'CMAKE_INSTALL_PREFIX': posix_prefix,
        'CMAKE_LIBRARY_PATH': ';'.join(library_locs),
        'CMAKE_MODULE_PATH': ';'.join(modules_locs),
        'CMAKE_PREFIX_PATH': ';'.join(prefix_locs),
        # releng-tool's sysroot assumes a `lib` directory. CMake's
        # GNUInstallDirs may adjust the expected lib directory based on the
        # detected system name (as a project may not necessarily be
        # cross-compiling), which may implicitly set the library directory to
        # `lib64`. Note that is it important to avoid providing an absolute
        # lib-directory, to allow CMake to inject a configurable
        # `_IMPORT_PREFIX` variable in any generated targets.
        'CMAKE_INSTALL_LIBDIR': DEFAULT_LIB_DIR,
        # disable a dependency in the installation stage to the build stage;
        # this is to prevent environments re-triggering the building of
        # sources during the installation stage due to an assumed detection
        # that compiled sources are stale
        'CMAKE_SKIP_INSTALL_ALL_DEPENDENCY': 'ON',
    }

    if 'releng.cmake.disable_direct_includes' not in opts._quirks:
        for option in CMAKE_INCLUDE_INJECT_OPTIONS:
            default_cmake_defs[option] = compiled_include_locs
    else:
        verbose('cmake direct includes disabled by quirk')

    # compile a list of package-provided defines
    cmake_defs = {}
    if opts.conf_defs:
        cmake_defs.update(expand(opts.conf_defs))

    # untrack any "default defines" that a package may have explicitly set
    for cmake_def_key in cmake_defs:
        default_cmake_defs.pop(cmake_def_key, None)

    # compile a list of releng-tool default defines into a CMake cache file;
    # we foward releng-tool configurations using an initial cache file to
    # help avoid CLI warning events if a project does not accept all of the
    # generic options configured by default
    cmake_pre_cache = Path(opts.build_output_dir) / '.releng-tool-cmake-cache'
    debug(f'building initial cache for cmake project: {cmake_pre_cache}')
    with cmake_pre_cache.open('w') as fp:
        for k, v in default_cmake_defs.items():
            debug(f' {k}={v}')
            fp.write(f'set({k} "{v}" CACHE INTERNAL "releng-tool generated")\n')

    # options
    cmake_opts = {
    }
    if opts.conf_opts:
        cmake_opts.update(expand(opts.conf_opts))

    # argument building
    cmake_args = [
        # add releng-tool's initial cache outside of `cmake_opts`, since we
        # do not want a package to replace it; and to ensure a package can
        # define their own `-C` argument for their own purpose
        '-C', cmake_pre_cache.as_posix(),
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
        if not mkdir(dir_):
            return False

    # cmake prepares build scripts out-of-source; move into the build output
    # directory and generate scripts from the build directory
    with wd(opts.build_output_dir):
        if not CMAKE.execute(cmake_args, env=expand(opts.conf_env)):
            err('failed to prepare cmake project: {}', opts.name)
            return False

    return True
