#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018-2019 releng-tool

from .. import __version__ as releng_version
from ..defs import *
from ..opts import RelengEngineOptions
from ..packages import RelengPackageManager
from ..registry import RelengRegistry
from ..util.env import extendScriptEnv
from ..util.file_flags import FileFlag
from ..util.file_flags import checkFileFlag
from ..util.file_flags import processFileFlag
from ..util.io import FailedToPrepareWorkingDirectoryError
from ..util.io import ensureDirectoryExists
from ..util.io import execute
from ..util.io import generateTempDir
from ..util.io import interimWorkingDirectory
from ..util.io import pathCopy
from ..util.io import pathExists
from ..util.io import pathMove
from ..util.io import pathRemove
from ..util.io import run_script
from ..util.io import touch
from ..util.log import *
from ..util.platform import exit as releng_exit
from ..util.string import expand
from ..util.string import interpretDictionaryStrings
from ..util.string import interpretString
from ..util.string import interpretStrings
from .bootstrap import stage as bootstrapStage
from .build import stage as buildStage
from .configure import stage as configureStage
from .extract import stage as extractStage
from .fetch import stage as fetchStage
from .install import stage as installStage
from .patch import stage as patchStage
from .post import stage as postStage
from collections import OrderedDict
from datetime import datetime
from enum import Enum
from shutil import copyfileobj
import os
import sys

class RelengEngine:
    """
    releng tool's engine

    The "engine" invokes the main components of a releng process such as
    downloading, configuring, building and more.

    Args:
        opts: options used to configure the engine

    Attributes:
        opts: options used to configure the engine
        pkgman: manager for package-related tasks
        registry: extension registry
    """
    def __init__(self, opts):
        self.registry = RelengRegistry()
        self.opts = opts
        self.pkgman = RelengPackageManager(opts, self.registry)

    def run(self):
        """
        run the engine

        Starts the actual processing of the release engineering steps. When this
        method is returned, the process is completed.

        Returns:
            ``True`` if the engine has completed without error; ``False`` if an
            issue has occurred when interpreting or running the user's
            configuration/package definitions
        """
        self.start_time = datetime.now().replace(microsecond=0)
        verbose("loading user's configuration...")
        gbls={
            'releng_args': self.opts.forward_args,
            'releng_version': releng_version,
        }

        # prepare script environment to make helpers available to configuration
        # script(s)
        self._prepareScriptEnvironment(gbls, self.opts.pkg_action)

        conf_point = self.opts.conf_point

        # TODO remove deprecated configuration load in v0.3+
        # if post-processing is missing, attempt to load deprecated filename
        if not os.path.isfile(self.opts.conf_point):
            conf_point = os.path.join(self.opts.root_dir, 'releng.py')
            if os.path.isfile(conf_point):
                warn('using deprecated configuration file releng.py -- switch '
                     'to releng for future projects')

        if not os.path.isfile(conf_point):
            err('missing configuration file')
            err("""\
The configuration file cannot be found. Ensure the configuration file exists
in the working directory or the provided root directory:

    {}""".format(self.opts.conf_point))
            return False

        settings = run_script(conf_point, gbls,
            subject='configuration')
        if not settings:
            return False

        script_env = gbls.copy()
        extendScriptEnv(script_env, settings)
        self.pkgman.script_env = script_env
        verbose('configuration file loaded')

        # configuration overrides file for builders
        if os.path.isfile(self.opts.conf_point_overrides):
            warn('detected configuration overrides file')

            overrides = run_script(self.opts.conf_point_overrides, gbls,
                subject='configuration overrides')
            if not overrides:
                return False

            extendScriptEnv(script_env, overrides)
            extendScriptEnv(settings, overrides)
            verbose('configuration overrides file loaded')

        # handle cleaning requests
        gaction = self.opts.gbl_action
        if gaction == GlobalAction.CLEAN or gaction == GlobalAction.MRPROPER:
            self._handleCleanRequest(gaction == GlobalAction.MRPROPER)
            return True

        # file flag processing
        state = self._processFileFlags()
        if state is not None:
            debug('file-flag processing has triggered closure')
            return state

        # determine package name(s) extraction
        #
        # Compile a (minimum) list of package names to be processed; either from
        # the user explicitly provided package target or from the user's
        # configuration file.
        if self.opts.target_action:
            pkg_names = [self.opts.target_action]
        else:
            pkg_names = self._getPackageNames(settings)
        if not pkg_names:
            return False
        debug('target packages)')
        for pkg_name in pkg_names:
            debug(' {}'.format(pkg_name))

        # processing additional settings
        if not self._processSettings(settings):
            return False

        # load and process packages
        pkgs = self.pkgman.load(pkg_names)
        if not pkgs:
            return False

        try:
            pa = self.opts.pkg_action
            license_files = {}

            # if cleaning a package, remove it's build output directory and stop
            if pa == PkgAction.CLEAN:
                for pkg in pkgs:
                    if pkg.name == self.opts.target_action:
                        verbose('removing output directory for package: ' +
                            pkg.name)
                        pathRemove(pkg.build_output_dir)
                        return True
                assert False # should not reach here
                return True

            # ensure all package sources are acquired first
            for pkg in pkgs:
                if not self._stageInit(pkg):
                    return False

                # none-vcs-type packages do not need to fetch
                if pkg.vcs_type is VcsType.NONE:
                    continue

                # in the event that we not not explicit fetching and the package
                # has already been extracted, completely skip the fetching stage
                if gaction != GlobalAction.FETCH and pa != PkgAction.FETCH:
                    flag = pkg.__ff_extract
                    if checkFileFlag(flag) == FileFlag.EXISTS:
                        continue

                if not fetchStage(self, pkg):
                    return False

            # prepend project's host directory to path
            host_bin = os.path.join(self.opts.host_dir, 'bin')
            os.environ['PATH'] = host_bin + os.pathsep + os.environ['PATH']

            # re-apply script environment to ensure previous script environment
            # changes have not manipulated the environment (from standard
            # helpers).
            self._prepareScriptEnvironment(script_env, self.opts.pkg_action)

            # process each package (configuring, building, etc.)
            if gaction != GlobalAction.FETCH and pa != PkgAction.FETCH:

                # ensure the symbols directory exists, as a package may wish to
                # populate it anytime between a configuration stage to a
                # post-package stage
                if not ensureDirectoryExists(self.opts.symbols_dir):
                    return False

                target = self.opts.target_action
                for pkg in pkgs:
                    verbose('processing package: {}'.format(pkg.name))

                    # skip if generating license information and no license
                    # files exist for this package
                    if (gaction == GlobalAction.LICENSES and
                            not pkg.license_files):
                        continue

                    # prepare environment
                    pkg_env = self._stageEnv(pkg, script_env)

                    # extracting
                    flag = pkg.__ff_extract
                    if checkFileFlag(flag) == FileFlag.NO_EXIST:
                        # none-vcs-type packages do not need to extract
                        if pkg.vcs_type is VcsType.NONE:
                            pass
                        elif not extractStage(self, pkg):
                            return False
                        # now that the extraction stage has (most likely)
                        # created a build directory, ensure the output directory
                        # exists as well (for file flags and other content)
                        if not ensureDirectoryExists(pkg.build_output_dir):
                            return False
                        if processFileFlag(True, flag) != FileFlag.CONFIGURED:
                            return False
                    if gaction == GlobalAction.EXTRACT:
                        continue
                    if pa == PkgAction.EXTRACT and pkg.name == target:
                        break

                    # patching
                    flag = pkg.__ff_patch
                    if checkFileFlag(flag) == FileFlag.NO_EXIST:
                        if not patchStage(self, pkg, pkg_env):
                            return False
                        if processFileFlag(True, flag) != FileFlag.CONFIGURED:
                            return False
                    if gaction == GlobalAction.PATCH:
                        continue
                    if pa == PkgAction.PATCH and pkg.name == target:
                        break

                    # handle license generation request
                    #
                    # If the user has requested to generate license information,
                    # pull license assets from the extract package content.
                    # license(s)
                    flag = pkg.__ff_license
                    if checkFileFlag(flag) == FileFlag.NO_EXIST:
                        if not self._stageLicense(pkg):
                            return False
                        if processFileFlag(True, flag) != FileFlag.CONFIGURED:
                            return False

                    if pkg.license_files:
                        license_files[pkg.name] = []
                        for file in pkg.license_files:
                            file = os.path.join(pkg.build_dir, file)
                            license_files[pkg.name].append(file)

                    if gaction == GlobalAction.LICENSES:
                        continue

                    # bootstrapping
                    flag = pkg.__ff_bootstrap
                    if checkFileFlag(flag) == FileFlag.NO_EXIST:
                        if not bootstrapStage(self, pkg, pkg_env):
                            return False
                        if processFileFlag(True, flag) != FileFlag.CONFIGURED:
                            return False

                    # configuring
                    flag = pkg.__ff_configure
                    if checkFileFlag(flag) == FileFlag.NO_EXIST:
                        if not configureStage(self, pkg, pkg_env):
                            return False
                        if processFileFlag(True, flag) != FileFlag.CONFIGURED:
                            return False
                    if pa in (PkgAction.CONFIGURE, PkgAction.RECONFIGURE):
                        if pkg.name == target:
                            break

                    # building
                    flag = pkg.__ff_build
                    if checkFileFlag(flag) == FileFlag.NO_EXIST:
                        if not buildStage(self, pkg, pkg_env):
                            return False
                        if processFileFlag(True, flag) != FileFlag.CONFIGURED:
                            return False
                    if pa in (PkgAction.BUILD, PkgAction.REBUILD):
                        if pkg.name == target:
                            break

                    # installing
                    flag = pkg.__ff_install
                    if checkFileFlag(flag) == FileFlag.NO_EXIST:
                        if not installStage(self, pkg, pkg_env):
                            return False
                        if processFileFlag(True, flag) != FileFlag.CONFIGURED:
                            return False
                    # (note: re-install requests will re-invoke package-specific
                    # post-processing)

                    # package-specific post-processing
                    flag = pkg.__ff_post
                    if checkFileFlag(flag) == FileFlag.NO_EXIST:
                        if not postStage(self, pkg, pkg_env):
                            return False
                        if processFileFlag(True, flag) != FileFlag.CONFIGURED:
                            return False
                    if pa in (PkgAction.INSTALL, PkgAction.REINSTALL):
                        if pkg.name == target:
                            break
        except FailedToPrepareWorkingDirectoryError as e:
            err("unable to prepare a package's working directory")
            err("""\
An attempt to prepare and move into a working directory for a package process
has failed. Ensure the following path is accessible for this user:

    {}""".format(e))
            return False

        is_action = (gaction != GlobalAction.UNKNOWN or pa != PkgAction.UNKNOWN
            or self.opts.target_action is not None)

        # perform license generation
        if gaction == GlobalAction.LICENSES or not is_action:
            note('generating license information...')

            if not self._performLicenseGeneration(license_files):
                return False

        # perform post-processing and completion message if not performing a
        # specific action
        if not is_action:
            if not self._postProcessing(script_env):
                err('failed to perform post-processing')
                return False

            self.end_time = datetime.now().replace(microsecond=0)
            success('completed ({})'.format(self.end_time - self.start_time))

        return True

    def _stageInit(self, pkg):
        """
        initialize the package environment for processing

        Performs initializations steps when processing a package. For example,
        tracking/pre-cleanup of package-specific file flags.

        Args:
            pkg: the package being processed

        Returns:
            ``True`` if the stage has been properly initialized; ``False``
            otherwise
        """
        prefix = '.stage_'
        outdir = pkg.build_output_dir
        pkg.__ff_bootstrap = os.path.join(outdir, prefix + 'bootstrap')
        pkg.__ff_build = os.path.join(outdir, prefix + 'build')
        pkg.__ff_configure = os.path.join(outdir, prefix + 'configure')
        pkg.__ff_extract = os.path.join(outdir, prefix + 'extract')
        pkg.__ff_install = os.path.join(outdir, prefix + 'install')
        pkg.__ff_license = os.path.join(outdir, prefix + 'license')
        pkg.__ff_patch = os.path.join(outdir, prefix + 'patch')
        pkg.__ff_post = os.path.join(outdir, prefix + 'post')

        # user invoking a package-specific override
        #
        # If the user is invoking a package rebuild, reconfiguration, etc.,
        # ensure existing file flags are cleared to ensure these stages are
        # invoked again.
        if pkg.name == self.opts.target_action:
            if self.opts.pkg_action == PkgAction.REBUILD:
                pathRemove(pkg.__ff_build)
                pathRemove(pkg.__ff_install)
                pathRemove(pkg.__ff_post)
            elif self.opts.pkg_action == PkgAction.RECONFIGURE:
                pathRemove(pkg.__ff_bootstrap)
                pathRemove(pkg.__ff_configure)
                pathRemove(pkg.__ff_build)
                pathRemove(pkg.__ff_install)
                pathRemove(pkg.__ff_post)
            elif self.opts.pkg_action == PkgAction.REINSTALL:
                pathRemove(pkg.__ff_install)
                pathRemove(pkg.__ff_post)

        return True

    def _stageEnv(self, pkg, script_env):
        """
        prepare environment variables for a specific package processing

        When a package is being processed (configuration, building, etc.), a
        unique set of environment variables may be provided specifically for the
        package. These are provided out of convenience as an alternative to
        needing to rely on the Python-provided stage options.

        Args:
            pkg: the package being processed
            script_env: global environment settings to use

        Returns:
            the prepared package-enhanced environment variables
        """

        # copy environment since packages do not share values
        pkg_env = script_env.copy()

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
            env['PREFIX'] = pkg.prefix

            if pkg.fixed_jobs:
                env['NJOBS'] = str(pkg.fixed_jobs)
                env['NJOBSCONF'] = str(pkg.fixed_jobs)

            if pkg.is_internal:
                env['PKG_INTERNAL'] = '1'

        return pkg_env

    def _stageLicense(self, pkg):
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
        if not ensureDirectoryExists(pkg_license_dir):
            return False

        # copy over each license files
        for file in pkg.license_files:
            src = os.path.join(pkg.build_dir, file)
            dst = os.path.join(pkg_license_dir, file)

            if not pathCopy(src, dst, critical=False):
                err('unable to copy license information: ' + pkg.name)
                return False

        return True

    def _getPackageNames(self, settings):
        """
        acquire list of project package names to process

        From a dictionary of user-defined settings, extract the known list of
        package names from the package configuration key ``CONF_KEY_PKGS``. This
        method will return a (duplicate-removed) list of packages (if any) to be
        processed.

        Args:
            settings: user settings to pull package information from

        Returns:
            list of package names to be processed; empty or ``None`` if no
            packages exist or an issue has occurred when attempting to extract
            package names
        """
        pkg_names = []
        badPkgsValue = False

        if CONF_KEY_PKGS in settings:
            pkg_names = interpretStrings(settings[CONF_KEY_PKGS])
            if pkg_names is None:
                badPkgsValue = True

        # remove duplicates (but maintain pre-sorted ordered)
        pkg_names = OrderedDict.fromkeys(pkg_names)

        if badPkgsValue:
            err('bad package list definition')
            err("""\
The configuration file does not have a properly formed list of defined packages.
Ensure a package list exists with the string-based names of packages to be part
of the releng process:

    {}
        {} = ['liba', 'libb', 'libc']""".format(
            self.opts.conf_point, CONF_KEY_PKGS))
        elif not pkg_names:
            err('no defined packages')
            err("""\
The configuration file does not have any defined packages. Ensure a package
list exists with the name of packages to be part of the releng process:

    {}
        {} = ['liba', 'libb', 'libc']""".format(
            self.opts.conf_point, CONF_KEY_PKGS))

        return pkg_names

    def _handleCleanRequest(self, proper=False):
        """
        handle a global clean request

        Performs a clean request for the working environment. A standard clean
        request will remove generated build, host, staging and target
        directories. In the event a "proper" clean is requested, the entire
        output directory (along with known file flags) will be removed.

        Args:
            proper (optional): whether this is a proper (complete) clean request
        """
        if proper:
            verbose('removing output directory')
            pathRemove(self.opts.out_dir)

            verbose('removing file flags')
            pathRemove(self.opts.ff_local_srcs)
            pathRemove(self.opts.ff_devmode)
        else:
            verbose('removing build directory')
            pathRemove(self.opts.build_dir)
            verbose('removing host directory')
            pathRemove(self.opts.host_dir)
            verbose('removing license directory')
            pathRemove(self.opts.license_dir)
            verbose('removing staging directory')
            pathRemove(self.opts.staging_dir)
            verbose('removing symbols directory')
            pathRemove(self.opts.symbols_dir)
            verbose('removing target directory')
            pathRemove(self.opts.target_dir)

    def _performLicenseGeneration(self, license_files):
        """
        generate a license file for the project

        Compiles a document containing all the license information for a
        configured project. License information defined by each package will be
        populated into a single file after each package is examined. Returned
        will be a dictionary where keys are the package names and the values are
        the list of one or more license files for the package.

        Args:
            license_files: dictionary of each package's license files

        Returns:
            ``True`` if the license file was generated; ``False`` if the license
            file could not be generated
        """
        if not ensureDirectoryExists(self.opts.license_dir):
            return False

        license_file = os.path.join(self.opts.license_dir, 'licenses')
        try:
            with open(license_file, 'w') as dst:
                license_header = expand(self.opts.license_header)
                if not license_header:
                    license_header = 'license(s)'

                # output license header
                dst.write("""{}
################################################################################
""".format(license_header))

                # output license header
                for key, val in sorted(license_files.items()):
                    dst.write("""
{}
--------------------------------------------------------------------------------
""".format(key))
                    for pkg_license_file in sorted(val):
                        verbose('writing license file ({}): {}'.format(
                            key, pkg_license_file))
                        with open(pkg_license_file, 'r') as f:
                            copyfileobj(f, dst)
                        dst.write('')

            verbose('license file has been written')
        except IOError as e:
            err('unable to populate license information')
            err('    {}'.format(e))
            return False

        return True

    def _postProcessing(self, env):
        """
        perform post-processing of a release engineering process

        After processing all packages configured for a release engineering
        process, post-processing can be performed as the final stage (if the
        script exists). Typically, a build process will use this stage to
        package any generated results into a "final image".

        Args:
            env: environment settings to apply for processing script

        Returns:
            ``True`` if the post-processing script has executed correctly or no
            post-processing script exists; ``False`` if an error has occurred
            when processing the post-processing script
        """
        script = self.opts.post_point

        # TODO remove deprecated configuration load in v0.3+
        # if post-processing is missing, attempt to load deprecated filename
        if not os.path.isfile(script):
            script = os.path.join(self.opts.root_dir, 'post.py')
            if os.path.isfile(script):
                warn('using deprecated post-processing file post.py -- switch '
                     'to releng-post for future projects')

        if os.path.isfile(script):
            verbose('performing post-processing...')

            # ensure images directory exists (as the post-processing script will
            # most likely populate it)
            if not ensureDirectoryExists(self.opts.images_dir):
                return False

            if not run_script(script, env, subject='post-processing'):
                return False

            verbose('post-processing completed')

        return True

    def _prepareScriptEnvironment(self, script_env, action):
        """
        prepare the script environment with common project values

        A package stage will be invoked with a tailored environment variables.
        This method is used to prepare an environment dictionary with common
        variables such the the staging directory, target directory and more.

        Args:
            script_env: environment dictionary to prepare
            action: the package-specific invoked
        """

        # global variables
        for env in (os.environ, script_env):
            env['BUILD_DIR'] = self.opts.build_dir
            env['CACHE_DIR'] = self.opts.cache_dir
            env['DL_DIR'] = self.opts.dl_dir
            env['HOST_DIR'] = self.opts.host_dir
            env['IMAGES_DIR'] = self.opts.images_dir
            env['LICENSE_DIR'] = self.opts.license_dir
            env['NJOBS'] = str(self.opts.jobs)
            env['NJOBSCONF'] = str(self.opts.jobsconf)
            env['OUTPUT_DIR'] = self.opts.out_dir
            env['ROOT_DIR'] = self.opts.root_dir
            env['STAGING_DIR'] = self.opts.staging_dir
            env['SYMBOLS_DIR'] = self.opts.symbols_dir
            env['TARGET_DIR'] = self.opts.target_dir

            if action == PkgAction.REBUILD:
                env['RELENG_REBUILD'] = '1'
            elif action == PkgAction.RECONFIGURE:
                env['RELENG_RECONFIGURE'] = '1'
            elif action == PkgAction.REINSTALL:
                env['RELENG_REINSTALL'] = '1'

            if self.opts.devmode:
                env['RELENG_DEVMODE'] = '1'
            if self.opts.local_srcs:
                env['RELENG_LOCALSRCS'] = '1'

        # utility methods (if adjusting, see also `releng.__init__`)
        script_env['debug'] = debug
        script_env['err'] = err
        script_env['log'] = log
        script_env['note'] = note
        script_env['releng_copy'] = pathCopy
        script_env['releng_execute'] = execute
        script_env['releng_exists'] = pathExists
        script_env['releng_exit'] = releng_exit
        script_env['releng_expand'] = expand
        script_env['releng_join'] = os.path.join
        script_env['releng_mkdir'] = ensureDirectoryExists
        script_env['releng_move'] = pathMove
        script_env['releng_remove'] = pathRemove
        script_env['releng_tmpdir'] = generateTempDir
        script_env['releng_touch'] = touch
        script_env['releng_wd'] = interimWorkingDirectory
        script_env['success'] = success
        script_env['verbose'] = verbose
        script_env['warn'] = warn

    def _processFileFlags(self):
        """
        check or configure known file flags

        For all known file flags, see if either respective flag options are set
        and/or configure file flags for which have been explicitly set to be
        enabled.

        Returns:
            ``None`` if the file flags has been processed and the options have
            been updated accordingly; ``True`` if the request to configure file
            flags has completed with no errors; ``False`` if the request to
            configure file flags failed to be performed
        """
        opts = self.opts
        configured = False
        err = False

        state = processFileFlag(opts.devmode, opts.ff_devmode)
        if state == FileFlag.CONFIGURED:
            success('configured root for development mode')
            configured = True
        elif state == FileFlag.NOT_CONFIGURED:
            err = True
        opts.devmode = (state == FileFlag.EXISTS)
        if opts.devmode:
            verbose('development mode enabled')

        state = processFileFlag(opts.local_srcs, opts.ff_local_srcs)
        if state == FileFlag.CONFIGURED:
            success('configured root for local-sources mode')
            configured = True
        elif state == FileFlag.NOT_CONFIGURED:
            err = True
        opts.local_srcs = (state == FileFlag.EXISTS)
        if opts.local_srcs:
            verbose('local-sources mode enabled')

        if err:
            return False
        elif configured:
            return True
        else:
            return None

    def _processSettings(self, settings):
        """
        process global settings provided from the user

        For all known file flags, see if either respective flag options are set
        and/or configure file flags for which have been explicitly set to be
        enabled.

        Args:
            settings: user settings to pull global information from

        Returns:
            ``None`` if the file flags has been processed and the options have
            been updated accordingly; ``True`` if the request to configure file
            flags has completed with no errors; ``False`` if the request to
            configure file flags failed to be performed
        """
        def notifyInvalidValue(key, expected):
            err('invalid configuration value provided')
            err("""\
The configuration file defines a key with an unexpected type. Correct the
following key entry and re-try again.

    Key: {}
    Expected Type: {}""".format(key, expected))

        if CONF_KEY_CACHE_EXT_TRANSFORM in settings:
            cet = None
            if callable(settings[CONF_KEY_CACHE_EXT_TRANSFORM]):
                cet = settings[CONF_KEY_CACHE_EXT_TRANSFORM]
            if cet is None:
                notifyInvalidValue(CONF_KEY_CACHE_EXT_TRANSFORM, 'callable')
                return False
            self.opts.cache_ext_transform = cet

        if CONF_KEY_DEFINTERN in settings:
            is_default_internal = settings[CONF_KEY_DEFINTERN]
            if not isinstance(is_default_internal, bool):
                notifyInvalidValue(CONF_KEY_DEFINTERN, 'bool')
                return False
            self.opts.default_internal_pkgs = is_default_internal

        if CONF_KEY_LICENSE_HEADER in settings:
            license_header = interpretString(settings[CONF_KEY_LICENSE_HEADER])
            if license_header is None:
                notifyInvalidValue(CONF_KEY_LICENSE_HEADER, 'str')
                return False
            self.opts.license_header = license_header

        if CONF_KEY_OVERRIDE_REV in settings:
            orz = interpretDictionaryStrings(settings[CONF_KEY_OVERRIDE_REV])
            if orz is None:
                notifyInvalidValue(CONF_KEY_OVERRIDE_REV, 'dict(str,str)')
                return False
            self.opts.revision_override = orz

        if CONF_KEY_OVERRIDE_SITES in settings:
            osz = interpretDictionaryStrings(settings[CONF_KEY_OVERRIDE_SITES])
            if osz is None:
                notifyInvalidValue(CONF_KEY_OVERRIDE_SITES, 'dict(str,str)')
                return False
            self.opts.sites_override = osz

        if CONF_KEY_OVERRIDE_TOOLS in settings:
            otz = interpretDictionaryStrings(settings[CONF_KEY_OVERRIDE_TOOLS])
            if otz is None:
                notifyInvalidValue(CONF_KEY_OVERRIDE_TOOLS, 'dict(str,str)')
                return False
            self.opts.extract_override = otz

        if CONF_KEY_QUIRKS in settings:
            quirks = interpretStrings(settings[CONF_KEY_QUIRKS])
            if quirks is None:
                notifyInvalidValue(CONF_KEY_QUIRKS, 'str or list(str)')
                return False
            self.opts.quirks = quirks
            for quirk in quirks:
                verbose('configuration quirk applied: ' + quirk)

        if CONF_KEY_SYSROOT_PREFIX in settings:
            sysroot_prefix = interpretString(settings[CONF_KEY_SYSROOT_PREFIX])
            if sysroot_prefix is None:
                notifyInvalidValue(CONF_KEY_SYSROOT_PREFIX, 'str')
                return False
            if not sysroot_prefix.startswith('/'):
                sysroot_prefix = '/' + sysroot_prefix
            self.opts.sysroot_prefix = sysroot_prefix

        if CONF_KEY_URL_MIRROR in settings:
            url_mirror = interpretString(settings[CONF_KEY_URL_MIRROR])
            if url_mirror is None:
                notifyInvalidValue(CONF_KEY_URL_MIRROR, 'str')
                return False
            self.opts.url_mirror = url_mirror

        if CONF_KEY_EXTEN_PKGS in settings:
            epd = interpretStrings(settings[CONF_KEY_EXTEN_PKGS])
            if epd is None:
                notifyInvalidValue(CONF_KEY_EXTEN_PKGS, 'str or list(str)')
                return False
            self.opts.extern_pkg_dirs = epd

        ext_names = []
        if CONF_KEY_EXTENSIONS in settings:
            ext_names = interpretStrings(settings[CONF_KEY_EXTENSIONS])
            if ext_names is None:
                notifyInvalidValue(CONF_KEY_EXTENSIONS, 'str or list(str)')
                return False

        self.registry.loadAllExtensions(ext_names)
        return True
