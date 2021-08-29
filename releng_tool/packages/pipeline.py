# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

from releng_tool.defs import GlobalAction
from releng_tool.defs import PkgAction
from releng_tool.defs import VcsType
from releng_tool.engine.bootstrap import stage as bootstrap_stage
from releng_tool.engine.build import stage as build_stage
from releng_tool.engine.configure import stage as configure_stage
from releng_tool.engine.extract import stage as extract_stage
from releng_tool.engine.install import stage as install_stage
from releng_tool.engine.patch import stage as patch_stage
from releng_tool.engine.post import stage as post_stage
from releng_tool.packages.exceptions import RelengToolBootstrapStageFailure
from releng_tool.packages.exceptions import RelengToolBuildStageFailure
from releng_tool.packages.exceptions import RelengToolConfigurationStageFailure
from releng_tool.packages.exceptions import RelengToolExtractionStageFailure
from releng_tool.packages.exceptions import RelengToolInstallStageFailure
from releng_tool.packages.exceptions import RelengToolLicenseStageFailure
from releng_tool.packages.exceptions import RelengToolPatchStageFailure
from releng_tool.packages.exceptions import RelengToolPostStageFailure
from releng_tool.util.file_flags import FileFlag
from releng_tool.util.file_flags import check_file_flag
from releng_tool.util.file_flags import process_file_flag
from releng_tool.util.io import ensure_dir_exists
from releng_tool.util.io import path_copy
from releng_tool.util.log import err
from releng_tool.util.log import warn
import os

class RelengPackagePipeline:
    """
    a releng package pipeline

    A pipeline will process a provide package through the various stages of its
    life (extractiong, patching, configuring, etc.).

    Args:
        engine: the package engine
        opts: options used to configure the engine
        script_env: the script environment to load

    Attributes:
        license_files: dictionary of package-to-license enties found when
                        processing packages
        opts: options used to configure the engine
        script_env: the script environment to load
    """
    def __init__(self, engine, opts, script_env):
        self.engine = engine
        self.license_files = {}
        self.opts = opts
        self.script_env = script_env

    def process(self, pkg):
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

        Returns:
            returns whether or not the pipeline should continue processing
        """
        gaction = self.opts.gbl_action
        paction = self.opts.pkg_action
        target = self.opts.target_action

        # skip if generating license information and no license
        # files exist for this package
        if gaction == GlobalAction.LICENSES and not pkg.license_files:
            return True

        # prepare environment
        pkg_env = self._stage_env(pkg)

        # extracting
        flag = pkg._ff_extract
        if check_file_flag(flag) == FileFlag.NO_EXIST:
            self.engine.stats.track_duration_start(pkg.name, 'extract')
            # none/local-vcs-type packages do not need to fetch
            if pkg.vcs_type in (VcsType.LOCAL, VcsType.NONE):
                pass
            elif not extract_stage(self.engine, pkg):
                raise RelengToolExtractionStageFailure
            # now that the extraction stage has (most likely)
            # created a build directory, ensure the output directory
            # exists as well (for file flags and other content)
            if not ensure_dir_exists(pkg.build_output_dir):
                raise RelengToolExtractionStageFailure
            self.engine.stats.track_duration_end(pkg.name, 'extract')
            if process_file_flag(True, flag) != FileFlag.CONFIGURED:
                return False
        if gaction == GlobalAction.EXTRACT:
            return True
        if paction == PkgAction.EXTRACT and pkg.name == target:
            return False

        # patching
        flag = pkg._ff_patch
        if check_file_flag(flag) == FileFlag.NO_EXIST:
            self.engine.stats.track_duration_start(pkg.name, 'patch')
            # local-vcs-type packages do not need to patch
            if pkg.vcs_type is VcsType.LOCAL:
                pass
            elif not patch_stage(self.engine, pkg, pkg_env):
                raise RelengToolPatchStageFailure
            self.engine.stats.track_duration_end(pkg.name, 'patch')
            if process_file_flag(True, flag) != FileFlag.CONFIGURED:
                return False
        if gaction == GlobalAction.PATCH:
            return True
        if paction == PkgAction.PATCH and pkg.name == target:
            return False

        # handle license generation request
        #
        # If the user has requested to generate license information,
        # pull license assets from the extract package content.
        # license(s)
        flag = pkg._ff_license
        if check_file_flag(flag) == FileFlag.NO_EXIST:
            if not self._stage_license(pkg):
                raise RelengToolLicenseStageFailure
            if process_file_flag(True, flag) != FileFlag.CONFIGURED:
                return False

        if pkg.license_files:
            self.license_files[pkg.name] = {
                'files': [],
                'version': pkg.version,
            }
            for file in pkg.license_files:
                file = os.path.join(pkg.build_dir, file)
                self.license_files[pkg.name]['files'].append(file)

        if gaction == GlobalAction.LICENSES:
            return True
        if paction == PkgAction.LICENSE and pkg.name == target:
            return False

        # load any late-stage configuration options from the remote
        # sources
        if (not pkg.skip_remote_config and
                'releng.disable_remote_configs' not in self.opts.quirks):
            self.engine.pkgman.load_remote_configuration(pkg)

        # finalize package environment
        self._stage_env_finalize(pkg, pkg_env)

        # bootstrapping
        flag = pkg._ff_bootstrap
        if check_file_flag(flag) == FileFlag.NO_EXIST:
            self.engine.stats.track_duration_start(pkg.name, 'boot')
            if not bootstrap_stage(self.engine, pkg, pkg_env):
                raise RelengToolBootstrapStageFailure
            self.engine.stats.track_duration_end(pkg.name, 'boot')
            if process_file_flag(True, flag) != FileFlag.CONFIGURED:
                return False

        # configuring
        flag = pkg._ff_configure
        if check_file_flag(flag) == FileFlag.NO_EXIST:
            self.engine.stats.track_duration_start(pkg.name, 'configure')
            if not configure_stage(self.engine, pkg, pkg_env):
                raise RelengToolConfigurationStageFailure
            self.engine.stats.track_duration_end(pkg.name, 'configure')
            if process_file_flag(True, flag) != FileFlag.CONFIGURED:
                return False
        if paction in (PkgAction.CONFIGURE, PkgAction.RECONFIGURE_ONLY):
            if pkg.name == target:
                return False

        # building
        flag = pkg._ff_build
        if check_file_flag(flag) == FileFlag.NO_EXIST:
            self.engine.stats.track_duration_start(pkg.name, 'build')
            if not build_stage(self.engine, pkg, pkg_env):
                raise RelengToolBuildStageFailure
            self.engine.stats.track_duration_end(pkg.name, 'build')
            if process_file_flag(True, flag) != FileFlag.CONFIGURED:
                return False
        if paction in (PkgAction.BUILD, PkgAction.REBUILD_ONLY):
            if pkg.name == target:
                return False

        # installing
        flag = pkg._ff_install
        if check_file_flag(flag) == FileFlag.NO_EXIST:
            self.engine.stats.track_duration_start(pkg.name, 'install')
            if not install_stage(self.engine, pkg, pkg_env):
                raise RelengToolInstallStageFailure
            self.engine.stats.track_duration_end(pkg.name, 'install')
            if process_file_flag(True, flag) != FileFlag.CONFIGURED:
                return False
        # (note: re-install requests will re-invoke package-specific
        # post-processing)

        # package-specific post-processing
        flag = pkg._ff_post
        if check_file_flag(flag) == FileFlag.NO_EXIST:
            self.engine.stats.track_duration_start(pkg.name, 'post')
            if not post_stage(self.engine, pkg, pkg_env):
                raise RelengToolPostStageFailure
            self.engine.stats.track_duration_end(pkg.name, 'post')
            if process_file_flag(True, flag) != FileFlag.CONFIGURED:
                return False
        if paction in (
                PkgAction.INSTALL,
                PkgAction.REBUILD_ONLY,
                PkgAction.RECONFIGURE_ONLY,
                PkgAction.REINSTALL):
            if pkg.name == target:
                return False

        return True

    def _stage_env(self, pkg):
        """
        prepare environment variables for a specific package processing

        When a package is being processed (configuration, building, etc.), a
        unique set of environment variables may be provided specifically for the
        package. These are provided out of convenience as an alternative to
        needing to rely on the Python-provided stage options.

        Args:
            pkg: the package being processed

        Returns:
            the prepared package-enhanced environment variables
        """

        # copy environment since packages do not share values
        pkg_env = self.script_env.copy()

        if pkg.build_subdir:
            build_dir = pkg.build_subdir
        else:
            build_dir = pkg.build_dir

        # package variables
        for env in (os.environ, pkg_env):
            env['PKG_BUILD_DIR'] = build_dir
            env['PKG_BUILD_OUTPUT_DIR'] = pkg.build_output_dir
            env['PKG_CACHE_DIR'] = pkg.cache_dir
            env['PKG_CACHE_FILE'] = pkg.cache_file
            env['PKG_DEFDIR'] = pkg.def_dir
            env['PKG_NAME'] = pkg.name
            env['PKG_SITE'] = pkg.site if pkg.site else ''
            env['PKG_REVISION'] = pkg.revision
            env['PKG_VERSION'] = pkg.version

            if pkg.is_internal:
                env['PKG_INTERNAL'] = '1'

        return pkg_env

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
        """

        for env in (os.environ, pkg_env):
            if pkg.prefix is not None:
                env['PREFIX'] = pkg.prefix # will override existing prefix

            if pkg.fixed_jobs:
                env['NJOBS'] = str(pkg.fixed_jobs)
                env['NJOBSCONF'] = str(pkg.fixed_jobs)

    def _stage_license(self, pkg):
        """
        process license files for a specific package processing

        If a package contains one or more files containing licenses information,
        this information will be populated in the package's license folder.

        Args:
            pkg: the package being processed

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
        if not ensure_dir_exists(pkg_license_dir):
            return False

        # copy over each license files
        for file in pkg.license_files:
            src = os.path.join(pkg.build_dir, file)
            dst = os.path.join(pkg_license_dir, file)

            if not path_copy(src, dst, critical=False):
                err('unable to copy license information: ' + pkg.name)
                return False

        return True