# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool import __version__ as releng_version
from releng_tool.defs import GlobalAction
from releng_tool.defs import PkgAction
from releng_tool.support import releng_include
from releng_tool.support import require_version
from releng_tool.util.env import env_value
from releng_tool.util.env import env_wrap
from releng_tool.util.io import execute
from releng_tool.util.io import execute_rv
from releng_tool.util.io_cat import cat
from releng_tool.util.io_copy import path_copy
from releng_tool.util.io_copy import path_copy_into
from releng_tool.util.io_exists import path_exists
from releng_tool.util.io_ls import ls
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.io_move import path_move
from releng_tool.util.io_move import path_move_into
from releng_tool.util.io_remove import path_remove
from releng_tool.util.io_symlink import symlink
from releng_tool.util.io_temp_dir import temp_dir
from releng_tool.util.io_touch import touch
from releng_tool.util.io_wd import wd
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import hint
from releng_tool.util.log import log
from releng_tool.util.log import note
from releng_tool.util.log import success
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
from releng_tool.util.path import P
from releng_tool.util.platform import platform_exit
from releng_tool.util.string import expand
import os


def prepare_script_environment(env, opts):
    """
    prepare a script environment with common project values

    A package stage will be invoked with a tailored environment variables.
    This method is used to prepare an environment dictionary with common
    variables such the the staging directory, target directory and more.

    Args:
        env: environment dictionary to prepare
        opts: options used to configure the engine
    """

    # always register optional flags in script environment
    env['RELENG_CLEAN'] = None
    env['RELENG_DEBUG'] = None
    env['RELENG_DEVMODE'] = None
    env['RELENG_DISTCLEAN'] = None
    env['RELENG_EXEC'] = None
    env['RELENG_FORCE'] = None
    env['RELENG_LOCALSRCS'] = None
    env['RELENG_MRPROPER'] = None
    env['RELENG_PROFILES'] = []
    env['RELENG_REBUILD'] = None
    env['RELENG_RECONFIGURE'] = None
    env['RELENG_REINSTALL'] = None
    env['RELENG_TARGET_PKG'] = None
    env['RELENG_VERBOSE'] = None

    #: default lib container directory
    nprefix = os.path.normpath(opts.sysroot_prefix)
    host_pdir = os.path.normpath(opts.host_dir + nprefix)
    staging_pdir = os.path.normpath(opts.staging_dir + nprefix)
    target_pdir = os.path.normpath(opts.target_dir + nprefix)
    host_bin_dir = os.path.join(host_pdir, 'bin')
    host_include_dir = os.path.join(host_pdir, 'include')
    host_lib_dir = os.path.join(host_pdir, 'lib')
    host_share_dir = os.path.join(host_pdir, 'share')
    staging_bin_dir = os.path.join(staging_pdir, 'bin')
    staging_include_dir = os.path.join(staging_pdir, 'include')
    staging_lib_dir = os.path.join(staging_pdir, 'lib')
    staging_share_dir = os.path.join(staging_pdir, 'share')
    target_bin_dir = os.path.join(target_pdir, 'bin')
    target_include_dir = os.path.join(target_pdir, 'include')
    target_lib_dir = os.path.join(target_pdir, 'lib')
    target_share_dir = os.path.join(target_pdir, 'share')

    # global variables
    for env_ in (env_wrap(), env):
        env_['BUILD_DIR'] = P(opts.build_dir)
        env_['CACHE_DIR'] = P(opts.cache_dir)
        env_['DL_DIR'] = P(opts.dl_dir)
        env_['HOST_BIN_DIR'] = P(host_bin_dir)
        env_['HOST_DIR'] = P(opts.host_dir)
        env_['HOST_INCLUDE_DIR'] = P(host_include_dir)
        env_['HOST_LIB_DIR'] = P(host_lib_dir)
        env_['HOST_SHARE_DIR'] = P(host_share_dir)
        env_['IMAGES_DIR'] = P(opts.images_dir)
        env_['LICENSE_DIR'] = P(opts.license_dir)
        env_['NJOBS'] = opts.jobs
        env_['NJOBSCONF'] = opts.jobsconf
        env_['OUTPUT_DIR'] = P(opts.out_dir)
        env_['PREFIX'] = opts.sysroot_prefix
        env_['PREFIXED_HOST_DIR'] = P(host_pdir)
        env_['PREFIXED_STAGING_DIR'] = P(staging_pdir)
        env_['PREFIXED_TARGET_DIR'] = P(target_pdir)
        env_['RELENG_VERSION'] = releng_version
        env_['ROOT_DIR'] = P(opts.root_dir)
        env_['STAGING_BIN_DIR'] = P(staging_bin_dir)
        env_['STAGING_DIR'] = P(opts.staging_dir)
        env_['STAGING_INCLUDE_DIR'] = P(staging_include_dir)
        env_['STAGING_LIB_DIR'] = P(staging_lib_dir)
        env_['STAGING_SHARE_DIR'] = P(staging_share_dir)
        env_['SYMBOLS_DIR'] = P(opts.symbols_dir)
        env_['TARGET_BIN_DIR'] = P(target_bin_dir)
        env_['TARGET_DIR'] = P(opts.target_dir)
        env_['TARGET_INCLUDE_DIR'] = P(target_include_dir)
        env_['TARGET_LIB_DIR'] = P(target_lib_dir)
        env_['TARGET_SHARE_DIR'] = P(target_share_dir)

        if opts.target_action:
            env_['RELENG_TARGET_PKG'] = opts.target_action

        if opts.gbl_action == GlobalAction.CLEAN or \
                opts.pkg_action in (PkgAction.FRESH, PkgAction.CLEAN):
            env_['RELENG_CLEAN'] = True
        elif opts.gbl_action == GlobalAction.DISTCLEAN or \
                opts.pkg_action == PkgAction.DISTCLEAN:
            env_['RELENG_CLEAN'] = True  # also set clean flag
            env_['RELENG_DISTCLEAN'] = True
            env_['RELENG_MRPROPER'] = True  # also set mrproper flag
        elif opts.gbl_action == GlobalAction.MRPROPER:
            env_['RELENG_CLEAN'] = True  # also set clean flag
            env_['RELENG_MRPROPER'] = True

        if opts.pkg_action == PkgAction.EXEC:
            env_['RELENG_EXEC'] = True

        if opts.pkg_action in (PkgAction.RECONFIGURE, PkgAction.REBUILD,
                PkgAction.REBUILD_ONLY):
            env_['RELENG_REBUILD'] = True
        if opts.pkg_action in (PkgAction.RECONFIGURE,
                PkgAction.RECONFIGURE_ONLY):
            env_['RELENG_RECONFIGURE'] = True
        if opts.pkg_action in (PkgAction.RECONFIGURE, PkgAction.REBUILD,
                PkgAction.REINSTALL):
            env_['RELENG_REINSTALL'] = True

        if opts.debug:
            env_['RELENG_DEBUG'] = True
        if opts.devmode:
            if opts.devmode is True:
                env_['RELENG_DEVMODE'] = True
            else:
                env_['RELENG_DEVMODE'] = opts.devmode
        if opts.gbl_action == GlobalAction.PUNCH or opts.force:
            env_['RELENG_FORCE'] = True
        if opts.local_srcs:
            env_['RELENG_LOCALSRCS'] = True
        if opts.profiles:
            env_['RELENG_PROFILES'] = opts.profiles
        if opts.verbose:
            env_['RELENG_VERBOSE'] = True

    # utility methods (if adjusting, see also `releng_tool.__init__`)
    env['debug'] = debug
    env['err'] = err
    env['hint'] = hint
    env['log'] = log
    env['note'] = note
    env['releng_cat'] = cat
    env['releng_copy'] = path_copy
    env['releng_copy_into'] = path_copy_into
    env['releng_env'] = env_value
    env['releng_execute'] = execute
    env['releng_execute_rv'] = execute_rv
    env['releng_exists'] = path_exists
    env['releng_exit'] = platform_exit
    env['releng_expand'] = expand
    env['releng_include'] = releng_include
    env['releng_join'] = os.path.join
    env['releng_ls'] = ls
    env['releng_mkdir'] = mkdir
    env['releng_move'] = path_move
    env['releng_move_into'] = path_move_into
    env['releng_path'] = Path
    env['releng_remove'] = path_remove
    env['releng_require_version'] = require_version
    env['releng_symlink'] = symlink
    env['releng_tmpdir'] = temp_dir
    env['releng_touch'] = touch
    env['releng_wd'] = wd
    env['success'] = success
    env['verbose'] = verbose
    env['warn'] = warn
