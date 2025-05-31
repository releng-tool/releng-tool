# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from contextlib import contextmanager
from releng_tool.defs import GlobalAction
from releng_tool.defs import PkgAction
from releng_tool.engine.bootstrap import stage as bootstrap_stage
from releng_tool.engine.build import stage as build_stage
from releng_tool.engine.configure import stage as configure_stage
from releng_tool.engine.extract import stage as extract_stage
from releng_tool.engine.fetch_post import stage as fetch_post
from releng_tool.engine.install import stage as install_stage
from releng_tool.engine.patch import stage as patch_stage
from releng_tool.engine.post import stage as post_stage
from releng_tool.engine.vsdevcmd import vsdevcmd_initialize
from releng_tool.exceptions import RelengToolMissingExecCommand
from releng_tool.packages.exceptions import RelengToolBootstrapStageFailure
from releng_tool.packages.exceptions import RelengToolBuildStageFailure
from releng_tool.packages.exceptions import RelengToolConfigurationStageFailure
from releng_tool.packages.exceptions import RelengToolExecStageFailure
from releng_tool.packages.exceptions import RelengToolExtractionStageFailure
from releng_tool.packages.exceptions import RelengToolFetchPostStageFailure
from releng_tool.packages.exceptions import RelengToolInstallStageFailure
from releng_tool.packages.exceptions import RelengToolLicenseStageFailure
from releng_tool.packages.exceptions import RelengToolPatchStageFailure
from releng_tool.packages.exceptions import RelengToolPostStageFailure
from releng_tool.util.env import env_wrap
from releng_tool.util.file_flags import FileFlag
from releng_tool.util.file_flags import check_file_flag
from releng_tool.util.file_flags import process_file_flag
from releng_tool.util.io import cmd_args_to_str
from releng_tool.util.io_copy import path_copy
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import note
from releng_tool.util.log import warn
from releng_tool.util.path import P
from releng_tool.util.strccenum import StrCcEnum
import os
import subprocess
import sys


class PipelineResult(StrCcEnum):
    """
    pipeline process result

    The result state from processing a pipeline stage. This enumeration is
    primarily used to flag if a pipeline to continue processing stages
    until completion, or if the pipeline should stop processing. Note
    that a stopped pipeline does not indicate there was an error running
    the pipeline.

    Attributes:
        CONTINUE: pipeline should continue processing
        ERROR: an error has occurred processing the pipeline
        STOP: pipeline should stop processing
    """
    CONTINUE = 'continue'
    ERROR = 'error'
    STOP = 'stop'


class RelengPackagePipeline:
    """
    a releng package pipeline

    A pipeline will process a provide package through the various stages of its
    life (extracting, patching, configuring, etc.).

    Args:
        engine: the package engine
        opts: options used to configure the engine
        script_env: the script environment to load

    Attributes:
        opts: options used to configure the engine
        script_env: the script environment to load
    """
    def __init__(self, engine, opts, script_env):
        self.engine = engine
        self.opts = opts
        self.script_env = script_env

    def process(self, pkg, force_gaction=None):
        """
        process a provided package

        This request will process a package through the various stages (if these
        stages are applicable to the current run state and have yet been
        executed from a previous run). A package-specific script environment
        will be prepared and a package will go through the process of:

        - Extraction
        - Patching
        - License management (if needed)
        - Bootstrapping
        - Configuration
        - Building
        - Installing
        - Post-processing

        Args:
            pkg: the package to process
            force_gaction (optional): the global action to override with

        Returns:
            returns whether or not the pipeline should continue processing
        """

        gaction = force_gaction if force_gaction else self.opts.gbl_action
        paction = self.opts.pkg_action
        target = self.opts.target_action

        # skip if generating license information and no license
        # files exist for this package
        if gaction == GlobalAction.LICENSES and not pkg.license_files:
            return PipelineResult.CONTINUE

        # extracting
        fflag = pkg._ff_extract
        if check_file_flag(fflag) == FileFlag.NO_EXIST:
            self.engine.stats.track_duration_start(pkg.name, 'extract')
            if not extract_stage(self.engine, pkg):
                raise RelengToolExtractionStageFailure
            # now that the extraction stage has (most likely)
            # created a build directory, ensure the output directory
            # exists as well (for file flags and other content)
            if not mkdir(pkg.build_output_dir):
                raise RelengToolExtractionStageFailure
            self.engine.stats.track_duration_end(pkg.name, 'extract')
            if process_file_flag(fflag, flag=True) != FileFlag.CONFIGURED:
                return PipelineResult.ERROR
        if gaction == GlobalAction.EXTRACT:
            return PipelineResult.CONTINUE
        if paction == PkgAction.EXTRACT and pkg.name == target:
            return PipelineResult.STOP

        # process the package data with a package-specific environment
        with self._stage_env(pkg) as pkg_env:
            return self._process_data(pkg, pkg_env, gaction, paction, target)

    def _process_data(self, pkg, pkg_env, gaction, paction, target):
        """
        process a provided package (data)

        This request will process a package through the various stages (if these
        stages are applicable to the current run state and have yet been
        executed from a previous run). A package-specific script environment
        will be prepared and a package will go through the process of:

        - Patching
        - License management (if needed)
        - Bootstrapping
        - Configuration
        - Building
        - Installing
        - Post-processing

        Args:
            pkg: the package to process
            pkg_env: the package environment
            gaction: the global action requested
            paction: the package action requested
            target: the package action target

        Returns:
            returns whether or not the pipeline should continue processing
        """

        # patching
        fflag = pkg._ff_patch
        if check_file_flag(fflag) == FileFlag.NO_EXIST:
            self.engine.stats.track_duration_start(pkg.name, 'patch')
            if not patch_stage(self.engine, pkg, pkg_env):
                raise RelengToolPatchStageFailure
            self.engine.stats.track_duration_end(pkg.name, 'patch')
            if process_file_flag(fflag, flag=True) != FileFlag.CONFIGURED:
                return PipelineResult.ERROR
        if gaction == GlobalAction.PATCH:
            return PipelineResult.CONTINUE
        if paction in (PkgAction.FRESH, PkgAction.PATCH) and pkg.name == target:
            return PipelineResult.STOP

        # fetching (post)
        #
        # Note that we do post-fetching after the patching stage, to allow
        # developers to patch out possible source-defined dependencies (if
        # required).
        fetch_paction = paction == PkgAction.FETCH_FULL and pkg.name == target
        fflag = pkg._ff_fetch_post
        if gaction == GlobalAction.FETCH_FULL or fetch_paction or \
                check_file_flag(fflag) == FileFlag.NO_EXIST:
            self.engine.stats.track_duration_start(pkg.name, 'fetch-post')
            if not fetch_post(self.engine, pkg):
                raise RelengToolFetchPostStageFailure
            self.engine.stats.track_duration_end(pkg.name, 'fetch-post')
            if process_file_flag(fflag, flag=True) != FileFlag.CONFIGURED:
                return PipelineResult.ERROR
        if gaction == GlobalAction.FETCH_FULL:
            return PipelineResult.CONTINUE
        if fetch_paction:
            return PipelineResult.STOP

        # handle license generation request
        #
        # If the user has requested to generate license information,
        # pull license assets from the extract package content.
        # license(s)
        license_strict = (gaction == GlobalAction.LICENSES or
            (paction == PkgAction.LICENSE and pkg.name == target))
        fflag = pkg._ff_license
        if check_file_flag(fflag) == FileFlag.NO_EXIST:
            if not self._stage_license(pkg, license_strict):
                raise RelengToolLicenseStageFailure
            if process_file_flag(fflag, flag=True) != FileFlag.CONFIGURED:
                return PipelineResult.ERROR
        if gaction == GlobalAction.LICENSES:
            return PipelineResult.CONTINUE
        if paction == PkgAction.LICENSE and pkg.name == target:
            return PipelineResult.STOP

        # load any late-stage configuration options from the remote
        # sources
        if (pkg.remote_config and
                'releng.disable_remote_configs' not in self.opts.quirks):
            self.engine.pkgman.load_remote_configuration(pkg)

        # finalize package environment
        with self._stage_env_finalize(pkg, pkg_env):

            # custom execution command
            if paction == PkgAction.EXEC and pkg.name == target:
                self._stage_exec(pkg)
                return PipelineResult.STOP

            # bootstrapping
            fflag = pkg._ff_bootstrap
            if check_file_flag(fflag) == FileFlag.NO_EXIST:
                self.engine.stats.track_duration_start(pkg.name, 'boot')
                if not bootstrap_stage(self.engine, pkg, pkg_env):
                    raise RelengToolBootstrapStageFailure
                self.engine.stats.track_duration_end(pkg.name, 'boot')
                if process_file_flag(fflag, flag=True) != FileFlag.CONFIGURED:
                    return PipelineResult.ERROR

            # configuring
            fflag = pkg._ff_configure
            if check_file_flag(fflag) == FileFlag.NO_EXIST:
                self.engine.stats.track_duration_start(pkg.name, 'configure')
                if not configure_stage(self.engine, pkg, pkg_env):
                    raise RelengToolConfigurationStageFailure
                self.engine.stats.track_duration_end(pkg.name, 'configure')
                if process_file_flag(fflag, flag=True) != FileFlag.CONFIGURED:
                    return PipelineResult.ERROR
            if paction in (PkgAction.CONFIGURE, PkgAction.RECONFIGURE_ONLY):
                if pkg.name == target:
                    return PipelineResult.STOP

            # building
            fflag = pkg._ff_build
            if check_file_flag(fflag) == FileFlag.NO_EXIST:
                self.engine.stats.track_duration_start(pkg.name, 'build')
                if not build_stage(self.engine, pkg, pkg_env):
                    raise RelengToolBuildStageFailure
                self.engine.stats.track_duration_end(pkg.name, 'build')
                if process_file_flag(fflag, flag=True) != FileFlag.CONFIGURED:
                    return PipelineResult.ERROR
            if paction in (PkgAction.BUILD, PkgAction.REBUILD_ONLY):
                if pkg.name == target:
                    return PipelineResult.STOP

            # installing
            fflag = pkg._ff_install
            if check_file_flag(fflag) == FileFlag.NO_EXIST:
                self.engine.stats.track_duration_start(pkg.name, 'install')
                if not install_stage(self.engine, pkg, pkg_env):
                    raise RelengToolInstallStageFailure
                self.engine.stats.track_duration_end(pkg.name, 'install')
                if process_file_flag(fflag, flag=True) != FileFlag.CONFIGURED:
                    return PipelineResult.ERROR
            # (note: re-install requests will re-invoke package-specific
            # post-processing)

            # package-specific post-processing
            fflag = pkg._ff_post
            if check_file_flag(fflag) == FileFlag.NO_EXIST:
                self.engine.stats.track_duration_start(pkg.name, 'post')
                if not post_stage(self.engine, pkg, pkg_env):
                    raise RelengToolPostStageFailure
                self.engine.stats.track_duration_end(pkg.name, 'post')
                if process_file_flag(fflag, flag=True) != FileFlag.CONFIGURED:
                    return PipelineResult.ERROR
            if paction in (
                    PkgAction.INSTALL,
                    PkgAction.REBUILD_ONLY,
                    PkgAction.RECONFIGURE_ONLY,
                    PkgAction.REINSTALL):
                if pkg.name == target:
                    return PipelineResult.STOP

        if pkg.name == target:
            return PipelineResult.STOP

        return PipelineResult.CONTINUE

    @contextmanager
    def _stage_env(self, pkg):
        """
        prepare environment variables for a specific package processing

        When a package is being processed (configuration, building, etc.), a
        unique set of environment variables may be provided specifically for the
        package. These are provided out of convenience as an alternative to
        needing to rely on the Python-provided stage options.

        Args:
            pkg: the package being processed

        Yields:
            the prepared package-enhanced environment variables
        """

        pkg_keys = [
            'PKG_BUILD_BASE_DIR',
            'PKG_BUILD_DIR',
            'PKG_BUILD_OUTPUT_DIR',
            'PKG_CACHE_DIR',
            'PKG_CACHE_FILE',
            'PKG_DEFDIR',
            'PKG_DEVMODE',
            'PKG_INTERNAL',
            'PKG_LOCALSRCS',
            'PKG_NAME',
            'PKG_REVISION',
            'PKG_SITE',
            'PKG_VERSION',
        ]

        saved_env = {}
        for key in pkg_keys:
            saved_env[key] = os.environ.get(key, None)

        # copy environment since packages do not share values
        pkg_env = self.script_env.copy()

        if pkg.build_subdir:
            build_dir = pkg.build_subdir
        else:
            build_dir = pkg.build_dir

        # always register optional flags in script environment
        pkg_env['PKG_INTERNAL'] = None
        pkg_env['PKG_DEVMODE'] = None
        pkg_env['PKG_LOCALSRCS'] = None

        try:
            for env in (env_wrap(), pkg_env):
                env['PKG_BUILD_BASE_DIR'] = pkg.build_dir
                env['PKG_BUILD_DIR'] = P(build_dir)
                env['PKG_BUILD_OUTPUT_DIR'] = P(pkg.build_output_dir)
                env['PKG_CACHE_DIR'] = P(pkg.cache_dir)
                env['PKG_CACHE_FILE'] = P(pkg.cache_file)
                env['PKG_DEFDIR'] = P(pkg.def_dir)
                env['PKG_NAME'] = pkg.name
                env['PKG_SITE'] = pkg.site if pkg.site else ''
                env['PKG_REVISION'] = pkg.revision
                env['PKG_VERSION'] = pkg.version

                if pkg.devmode:
                    env['PKG_DEVMODE'] = True

                if pkg.is_internal:
                    env['PKG_INTERNAL'] = True

                if pkg.local_srcs:
                    env['PKG_LOCALSRCS'] = True

            yield pkg_env
        finally:
            # restore any overrides that may have been set
            for k, v in saved_env.items():
                if v is not None:
                    os.environ[k] = v
                else:
                    os.environ.pop(k, None)

    @contextmanager
    def _stage_env_finalize(self, pkg, pkg_env):
        """
        finalize environment variables for a specific package processing

        While a `_stage_env` call will prepare the script environment for
        various stages of a package, some options of a package may be loaded in
        at a later stage. Options which can be late-loaded are populated into
        the existing environment in this call.

        Args:
            pkg: the package being processed
            pkg_env: the environment to populate

        Yields:
            the prepared package-enhanced environment variables
        """

        pkg_keys = [
            'HOST_BIN_DIR',
            'HOST_INCLUDE_DIR',
            'HOST_LIB_DIR',
            'HOST_SHARE_DIR',
            'NJOBS',
            'NJOBSCONF',
            'PREFIX',
            'PREFIXED_HOST_DIR',
            'PREFIXED_STAGING_DIR',
            'PREFIXED_TARGET_DIR',
            'STAGING_BIN_DIR',
            'STAGING_INCLUDE_DIR',
            'STAGING_LIB_DIR',
            'STAGING_SHARE_DIR',
            'TARGET_BIN_DIR',
            'TARGET_INCLUDE_DIR',
            'TARGET_LIB_DIR',
            'TARGET_SHARE_DIR',
        ]

        # check if we should preload environment variables from vsdevcmd
        extra_env = {}
        if pkg.vsdevcmd and sys.platform == 'win32':
            debug('attempting to load package-specific vsdevcmd variables')
            extra_env = vsdevcmd_initialize(
                prodstr=pkg.vsdevcmd_products,
                verstr=pkg.vsdevcmd,
            )
            pkg_keys.extend(extra_env)

        saved_env = {}
        for key in pkg_keys:
            saved_env[key] = os.environ.get(key, None)

        # apply package specific overrides into the OS environment and the
        # package/script environment
        try:
            os.environ.update(extra_env)

            for env in (env_wrap(), pkg_env):
                if pkg.prefix is not None:
                    opts = self.opts
                    nprefix = pkg.prefix
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

                    # will override existing prefix related variables
                    env['HOST_BIN_DIR'] = P(host_bin_dir)
                    env['HOST_INCLUDE_DIR'] = P(host_include_dir)
                    env['HOST_LIB_DIR'] = P(host_lib_dir)
                    env['HOST_SHARE_DIR'] = P(host_share_dir)
                    env['PREFIX'] = pkg.prefix
                    env['PREFIXED_HOST_DIR'] = P(host_pdir)
                    env['PREFIXED_STAGING_DIR'] = P(staging_pdir)
                    env['PREFIXED_TARGET_DIR'] = P(target_pdir)
                    env['STAGING_BIN_DIR'] = P(staging_bin_dir)
                    env['STAGING_INCLUDE_DIR'] = P(staging_include_dir)
                    env['STAGING_LIB_DIR'] = P(staging_lib_dir)
                    env['STAGING_SHARE_DIR'] = P(staging_share_dir)
                    env['TARGET_BIN_DIR'] = P(target_bin_dir)
                    env['TARGET_INCLUDE_DIR'] = P(target_include_dir)
                    env['TARGET_LIB_DIR'] = P(target_lib_dir)
                    env['TARGET_SHARE_DIR'] = P(target_share_dir)

                if pkg.fixed_jobs:
                    env['NJOBS'] = str(pkg.fixed_jobs)
                    env['NJOBSCONF'] = str(pkg.fixed_jobs)

            yield
        finally:
            # restore any overrides that may have been set
            for k, v in saved_env.items():
                if v is not None:
                    os.environ[k] = v
                else:
                    os.environ.pop(k, None)

    def _stage_exec(self, pkg):
        """
        execute a command for a specific package

        Provides a user the ability to invoke a command in a package's
        extracted directory. This is a helper if a user wishes to invoke/test
        commands for a package without needing to navigate to the package's
        build directory and invoking them their.

        Args:
            pkg: the package being processed

        Raises:
            RelengToolExecStageFailure: when the command returns non-zero value
            RelengToolMissingExecCommand: when no command is provided
        """

        exec_cmd = self.opts.target_action_exec
        if not exec_cmd:
            raise RelengToolMissingExecCommand(pkg.name)

        note('execution for {}...', pkg.name)
        debug('(wd) {}', pkg.build_tree)
        if isinstance(exec_cmd, list):
            exec_cmd = cmd_args_to_str(exec_cmd)
        debug('(cmd) {}', exec_cmd)

        proc = subprocess.Popen(
            exec_cmd,
            cwd=pkg.build_tree,
            shell=True,
        )
        proc.communicate()
        sys.stdout.flush()

        if proc.returncode != 0:
            raise RelengToolExecStageFailure

    def _stage_license(self, pkg, strict):
        """
        process license files for a specific package processing

        If a package contains one or more files containing licenses information,
        this information will be populated in the package's license folder.

        Args:
            pkg: the package being processed
            strict: whether there is a strict requirement the license file
                    can be processed

        Returns:
            ``True`` if the license information was copied; ``False`` if these
            license information could not be copied
        """

        # skip if package has no license files
        if not pkg.license_files:
            if pkg.license and not pkg.is_internal and not pkg.no_extraction:
                warn('package defines no license files: ' + pkg.name)
            return True

        # ensure package-specific license directory exists
        pkg_license_dir = os.path.join(self.opts.license_dir, pkg.nv)
        if not mkdir(pkg_license_dir):
            return False

        # copy over each license files
        for file in pkg.license_files:
            src = os.path.join(pkg.build_dir, file)
            dst = os.path.join(pkg_license_dir, file)

            if not path_copy(src, dst, quiet=(not strict), critical=False):
                if strict:
                    err('unable to copy license information: ' + pkg.name)
                else:
                    warn('unable to copy license information: ' + pkg.name)
                return not strict

        return True
