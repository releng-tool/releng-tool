# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from collections import OrderedDict
from datetime import datetime
from releng_tool import __version__ as releng_version
from releng_tool.defs import CONF_KEY_CACHE_EXT_TRANSFORM
from releng_tool.defs import CONF_KEY_DEFINTERN
from releng_tool.defs import CONF_KEY_EXTENSIONS
from releng_tool.defs import CONF_KEY_EXTEN_PKGS
from releng_tool.defs import CONF_KEY_LICENSE_HEADER
from releng_tool.defs import CONF_KEY_OVERRIDE_REV
from releng_tool.defs import CONF_KEY_OVERRIDE_SITES
from releng_tool.defs import CONF_KEY_OVERRIDE_TOOLS
from releng_tool.defs import CONF_KEY_PKGS
from releng_tool.defs import CONF_KEY_PREREQUISITES
from releng_tool.defs import CONF_KEY_QUIRKS
from releng_tool.defs import CONF_KEY_SYSROOT_PREFIX
from releng_tool.defs import CONF_KEY_URL_MIRROR
from releng_tool.defs import CONF_KEY_URLOPEN_CONTEXT
from releng_tool.defs import GlobalAction
from releng_tool.defs import PkgAction
from releng_tool.defs import VcsType
from releng_tool.engine.fetch import stage as fetch_stage
from releng_tool.engine.init import initialize_sample
from releng_tool.exceptions import RelengToolMissingConfigurationError
from releng_tool.exceptions import RelengToolMissingPackagesError
from releng_tool.opts import RELENG_POST_BUILD_NAME
from releng_tool.packages.exceptions import RelengToolStageFailure
from releng_tool.packages.manager import RelengPackageManager
from releng_tool.packages.pipeline import RelengPackagePipeline
from releng_tool.prerequisites import RelengPrerequisites
from releng_tool.registry import RelengRegistry
from releng_tool.stats import RelengStats
from releng_tool.support import require_version
from releng_tool.util.env import env_value
from releng_tool.util.env import extend_script_env
from releng_tool.util.file_flags import FileFlag
from releng_tool.util.file_flags import check_file_flag
from releng_tool.util.file_flags import process_file_flag
from releng_tool.util.io import FailedToPrepareWorkingDirectoryError
from releng_tool.util.io import ensure_dir_exists
from releng_tool.util.io import execute
from releng_tool.util.io import execute_rv
from releng_tool.util.io import generate_temp_dir
from releng_tool.util.io import interim_working_dir
from releng_tool.util.io import opt_file
from releng_tool.util.io import path_copy
from releng_tool.util.io import path_exists
from releng_tool.util.io import path_move
from releng_tool.util.io import path_remove
from releng_tool.util.io import run_script
from releng_tool.util.io import touch
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import note
from releng_tool.util.log import success
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
from releng_tool.util.platform import platform_exit
from releng_tool.util.string import expand
from releng_tool.util.string import interpret_dictionary_strings
from releng_tool.util.string import interpret_string
from releng_tool.util.string import interpret_strings
from shutil import copyfileobj
import os
import ssl
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
        self.pkgman = RelengPackageManager(opts, self.registry, dvcs_cache=True)
        self.stats = RelengStats(opts)

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
        opts = self.opts
        gaction = opts.gbl_action
        if gaction == GlobalAction.INIT:
            return initialize_sample(opts)

        start_time = datetime.now().replace(microsecond=0)
        gbls = {
            'releng_args': opts.forward_args,
            'releng_version': releng_version,
        }

        debug('loading statistics...')
        self.stats.load()

        # inform the user of any active running modes
        if self.opts.devmode:
            verbose('running in development mode')

        if self.opts.local_srcs:
            verbose('running in local-sources mode')

        # register the project's root directory as a system path; permits a
        # project to import locally created modules in their build/etc. scripts
        debug('registering root directory in path...')
        sys.path.append(opts.root_dir)

        # register the project's host directory as a system path; lazily permits
        # loading host tools (not following prefix or bin container) built by a
        # project over the system
        debug('registering host directory in path...')
        sys.path.insert(0, opts.host_dir)
        os.environ['PATH'] = opts.host_dir + os.pathsep + os.environ['PATH']

        # prepare script environment to make helpers available to configuration
        # script(s)
        #
        # Note that some options prepared for the configuration script may
        # need to be updated after running the project's configuration (e.g.
        # possibly needing to update the `PREFIX` variable if `sysroot_prefix`
        # was configured). This is peformed later in the engine run call.
        self._prepare_script_environment(gbls, gaction, opts.pkg_action)

        verbose("loading user's configuration...")
        conf_point, conf_point_exists = opt_file(opts.conf_point)
        if not conf_point_exists:
            raise RelengToolMissingConfigurationError(conf_point)

        settings = run_script(conf_point, gbls, subject='configuration')
        if not settings:
            return False

        script_env = gbls.copy()
        extend_script_env(script_env, settings)
        self.pkgman.script_env = script_env
        verbose('configuration file loaded')

        # configuration overrides file for builders
        if os.path.isfile(opts.conf_point_overrides):
            warn('detected configuration overrides file')

            overrides = run_script(opts.conf_point_overrides, gbls,
                subject='configuration overrides')
            if not overrides:
                return False

            extend_script_env(script_env, overrides)
            extend_script_env(settings, overrides)
            verbose('configuration overrides file loaded')

        # handle cleaning requests
        if (gaction == GlobalAction.CLEAN or gaction == GlobalAction.MRPROPER
                or gaction == GlobalAction.DISTCLEAN):
            self._handle_clean_request(gaction)
            return True

        # file flag processing
        state = self._process_file_flags()
        if state is not None:
            debug('file-flag processing has triggered closure')
            return state

        # determine package name(s) extraction
        #
        # Compile a (minimum) list of package names to be processed; either from
        # the user explicitly provided package target or from the user's
        # configuration file.
        if opts.target_action:
            pkg_names = [opts.target_action]
        else:
            pkg_names = self._get_package_names(settings)
        if not pkg_names:
            return False
        debug('target packages)')
        for pkg_name in pkg_names:
            debug(' {}', pkg_name)

        # processing additional settings
        if not self._process_settings(settings):
            return False

        # register the project's host-bin directory as a system path; lazily
        # permits loading host tools built by a project over the system
        debug('registering host bin directory in path...')
        host_bin_dir = os.path.join(opts.host_dir + opts.sysroot_prefix, 'bin')
        sys.path.insert(0, host_bin_dir)
        os.environ['PATH'] = host_bin_dir + os.pathsep + os.environ['PATH']

        # load and process packages
        pkgs = self.pkgman.load(pkg_names)
        if not pkgs:
            return False

        try:
            pa = opts.pkg_action
            license_files = {}

            # if cleaning a package, remove it's build output directory and stop
            if pa in (PkgAction.CLEAN, PkgAction.DISTCLEAN):
                for pkg in pkgs:
                    if pkg.name == opts.target_action:
                        def pkg_verbose_clean(desc):
                            verbose('{} for package: {}', desc, pkg.name)
                        pkg_verbose_clean('removing output directory')
                        path_remove(pkg.build_output_dir)

                        if pa == PkgAction.DISTCLEAN:
                            if os.path.exists(pkg.cache_file):
                                pkg_verbose_clean('removing cache file')
                                path_remove(pkg.cache_file)
                            if os.path.isdir(pkg.cache_dir):
                                pkg_verbose_clean('removing cache directory')
                                path_remove(pkg.cache_dir)

                        return True
                assert False # should not reach here

            # ensure any of required host tools do exist
            if 'releng.disable_prerequisites_check' not in opts.quirks:
                prerequisites = RelengPrerequisites(pkgs, opts.prerequisites)
                if not prerequisites.check():
                    return False

            # track if this action is "pre-configuration", where a package
            # dependency chain can be ignored
            requested_preconfig = pa in [
                PkgAction.EXTRACT,
                PkgAction.FETCH,
                PkgAction.LICENSE,
                PkgAction.PATCH,
            ]

            # determine if an explicit fetch request has been made
            requested_fetch = None
            if gaction == GlobalAction.FETCH or pa == PkgAction.FETCH:
                requested_fetch = True

            # ensure all package sources are acquired first
            for pkg in pkgs:
                if not self._stage_init(pkg):
                    return False

                # if this is a package-specific pre-configure action, only
                # ensure a fetched this specific package
                if requested_preconfig and pkg.name != opts.target_action:
                    continue

                # none/local-vcs-type packages do not need to fetch
                if pkg.vcs_type in (VcsType.LOCAL, VcsType.NONE):
                    continue

                # in the event that we not not explicit fetching and the package
                # has already been extracted, completely skip the fetching stage
                if not requested_fetch:
                    flag = pkg._ff_extract
                    if check_file_flag(flag) == FileFlag.EXISTS:
                        continue

                self.stats.track_duration_start(pkg.name, 'fetch')
                fetched = fetch_stage(
                    self, pkg, requested_fetch, pkg.fetch_opts)
                self.stats.track_duration_end(pkg.name, 'fetch')
                if not fetched:
                    return False

            # re-apply script environment to ensure previous script environment
            # changes have not manipulated the environment (from standard
            # helpers).
            self._prepare_script_environment(
                script_env, gaction, opts.pkg_action)

            # process each package (configuring, building, etc.)
            if gaction != GlobalAction.FETCH and pa != PkgAction.FETCH:

                # ensure the symbols directory exists, as a package may wish to
                # populate it anytime between a configuration stage to a
                # post-package stage
                if not ensure_dir_exists(opts.symbols_dir):
                    return False

                pipeline = RelengPackagePipeline(self, opts, script_env)
                for pkg in pkgs:
                    # if this is a package-specific pre-configure action, only
                    # process the specific action
                    if requested_preconfig and pkg.name != opts.target_action:
                        continue

                    verbose('processing package: {}', pkg.name)
                    if not pipeline.process(pkg):
                        return False
                license_files = pipeline.license_files

        except RelengToolStageFailure:
            return False
        except FailedToPrepareWorkingDirectoryError as e:
            err('''\
unable to prepare a package's working directory

An attempt to prepare and move into a working directory for a package process
has failed. Ensure the following path is accessible for this user:

    {}''', e)
            return False

        is_action = (gaction or pa or opts.target_action is not None)

        # perform license generation
        if gaction == GlobalAction.LICENSES or pa == PkgAction.LICENSE \
                or not is_action:
            note('generating license information...')

            if not self._perform_license_generation(license_files):
                return False

        # perform post-processing and completion message if not performing a
        # specific action
        if not is_action:
            if not self._post_processing(script_env):
                err('failed to perform post-processing')
                return False

            end_time = datetime.now().replace(microsecond=0)
            success('completed ({})', end_time - start_time)

        # attempt to generate a report at the end of a run
        self.stats.generate()

        return True

    def _stage_init(self, pkg):
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

        # forced request
        #
        # When a forced request is made, clear all file flags so these stages
        # can be invoked again.
        if self.opts.force:
            path_remove(pkg._ff_bootstrap)
            path_remove(pkg._ff_configure)
            path_remove(pkg._ff_build)
            path_remove(pkg._ff_install)
            path_remove(pkg._ff_post)

        # user invoking a package-specific override
        #
        # If the user is invoking a package rebuild, reconfiguration, etc.,
        # ensure existing file flags are cleared to ensure these stages are
        # invoked again.
        elif pkg.name == self.opts.target_action:
            if (self.opts.pkg_action in
                    (PkgAction.REBUILD, PkgAction.REBUILD_ONLY)):
                path_remove(pkg._ff_build)
                path_remove(pkg._ff_install)
                path_remove(pkg._ff_post)
            elif (self.opts.pkg_action in
                    (PkgAction.RECONFIGURE, PkgAction.RECONFIGURE_ONLY)):
                path_remove(pkg._ff_bootstrap)
                path_remove(pkg._ff_configure)
                path_remove(pkg._ff_build)
                path_remove(pkg._ff_install)
                path_remove(pkg._ff_post)
            elif self.opts.pkg_action == PkgAction.REINSTALL:
                path_remove(pkg._ff_install)
                path_remove(pkg._ff_post)

        return True

    def _get_package_names(self, settings):
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
        bad_pkgs_value = False

        if CONF_KEY_PKGS in settings:
            pkg_names = interpret_strings(settings[CONF_KEY_PKGS])
            if pkg_names is None:
                bad_pkgs_value = True

        # remove duplicates (but maintain pre-sorted ordered)
        pkg_names = OrderedDict.fromkeys(pkg_names)

        if bad_pkgs_value:
            err('''\
bad package list definition

The configuration file does not have a properly formed list of defined packages.
Ensure a package list exists with the string-based names of packages to be part
of the releng process:

    {}
        {} = ['liba', 'libb', 'libc']''',
                self.opts.conf_point,
                CONF_KEY_PKGS)
        elif not pkg_names:
            raise RelengToolMissingPackagesError(
                self.opts.conf_point, CONF_KEY_PKGS)

        return pkg_names

    def _handle_clean_request(self, gaction):
        """
        handle a global clean request

        Performs a clean request for the working environment. A standard clean
        request will remove generated build, host, staging and target
        directories. In the event of "proper"-based cleans are requested,
        additional content such as the entire output directory (along with known
        file flags) can be removed.

        Args:
            gaction: the specific clean action being requested
        """

        if gaction == GlobalAction.DISTCLEAN:
            verbose('removing cache directory')
            path_remove(self.opts.cache_dir)
            verbose('removing download directory')
            path_remove(self.opts.dl_dir)

        if gaction in (GlobalAction.MRPROPER, GlobalAction.DISTCLEAN):
            verbose('removing output directory')
            path_remove(self.opts.out_dir)

            verbose('removing file flags')
            if os.path.exists(self.opts.ff_devmode):
                if path_remove(self.opts.ff_devmode):
                    warn('development mode has been unconfigured')
            if os.path.exists(self.opts.ff_local_srcs):
                if path_remove(self.opts.ff_local_srcs):
                    warn('local-sources mode has been unconfigured')
        else:
            verbose('removing build directory')
            path_remove(self.opts.build_dir)
            verbose('removing host directory')
            path_remove(self.opts.host_dir)
            verbose('removing license directory')
            path_remove(self.opts.license_dir)
            verbose('removing staging directory')
            path_remove(self.opts.staging_dir)
            verbose('removing symbols directory')
            path_remove(self.opts.symbols_dir)
            verbose('removing target directory')
            path_remove(self.opts.target_dir)

    def _perform_license_generation(self, license_files):
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
        if not ensure_dir_exists(self.opts.license_dir):
            return False

        license_file = os.path.join(self.opts.license_dir, 'licenses')
        try:
            with open(license_file, 'w') as dst:
                license_header = expand(self.opts.license_header)
                if not license_header:
                    license_header = 'license(s)'

                # output license header
                dst.write('''{}
################################################################################
'''.format(license_header))

                # output license header
                for license_name, license_data in sorted(license_files.items()):
                    license_files = license_data['files']
                    license_version = license_data['version']
                    dst.write('''
{}-{}
--------------------------------------------------------------------------------
'''.format(license_name, license_version))
                    for pkg_license_file in sorted(license_files):
                        verbose('writing license file ({}): {}',
                            license_name, pkg_license_file)
                        with open(pkg_license_file, 'r') as f:
                            copyfileobj(f, dst)
                        dst.write('')

            verbose('license file has been written')
        except IOError as e:
            err('unable to populate license information\n'
                '    {}', e)
            return False

        return True

    def _post_processing(self, env):
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
        build_script, postbuild_exists = opt_file(self.opts.post_build_point)

        # TODO remove deprecated configuration load in (at maximum) v1.0
        if not postbuild_exists:
            deprecated_posts = [
                'releng-post',
                'post.py',
            ]

            for script_name in deprecated_posts:
                build_script = os.path.join(self.opts.root_dir, script_name)
                if os.path.isfile(build_script):
                    warn('using deprecated post-processing file {} -- switch '
                         'to {} for future projects', script_name,
                         RELENG_POST_BUILD_NAME)
                    postbuild_exists = True
                    break

        if postbuild_exists:
            verbose('performing post-processing (build)...')

            # ensure images directory exists (as the post-processing script will
            # most likely populate it)
            if not ensure_dir_exists(self.opts.images_dir):
                return False

            if not run_script(build_script, env, subject='post-build'):
                return False

            verbose('post-processing (build) completed')

        return True

    def _prepare_script_environment(self, script_env, gaction, paction):
        """
        prepare the script environment with common project values

        A package stage will be invoked with a tailored environment variables.
        This method is used to prepare an environment dictionary with common
        variables such the the staging directory, target directory and more.

        Args:
            script_env: environment dictionary to prepare
            gaction: the global action invoked (if any)
            paction: the package-specific action invoked (if any)
        """

        # always register optional flags in script environment
        script_env['RELENG_CLEAN'] = None
        script_env['RELENG_DEBUG'] = None
        script_env['RELENG_DEVMODE'] = None
        script_env['RELENG_DISTCLEAN'] = None
        script_env['RELENG_FORCE'] = None
        script_env['RELENG_LOCALSRCS'] = None
        script_env['RELENG_MRPROPER'] = None
        script_env['RELENG_REBUILD'] = None
        script_env['RELENG_RECONFIGURE'] = None
        script_env['RELENG_REINSTALL'] = None
        script_env['RELENG_VERBOSE'] = None

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
            env['PREFIX'] = self.opts.sysroot_prefix
            env['RELENG_VERSION'] = releng_version
            env['ROOT_DIR'] = self.opts.root_dir
            env['STAGING_DIR'] = self.opts.staging_dir
            env['SYMBOLS_DIR'] = self.opts.symbols_dir
            env['TARGET_DIR'] = self.opts.target_dir

            if gaction == GlobalAction.CLEAN:
                env['RELENG_CLEAN'] = '1'
            elif gaction == GlobalAction.DISTCLEAN:
                env['RELENG_CLEAN'] = '1' # also set clean flag
                env['RELENG_DISTCLEAN'] = '1'
                env['RELENG_MRPROPER'] = '1' # also set mrproper flag
            elif gaction == GlobalAction.MRPROPER:
                env['RELENG_CLEAN'] = '1' # also set clean flag
                env['RELENG_MRPROPER'] = '1'

            if paction in (PkgAction.REBUILD, PkgAction.REBUILD_ONLY):
                env['RELENG_REBUILD'] = '1'
            elif paction in (PkgAction.RECONFIGURE, PkgAction.RECONFIGURE_ONLY):
                env['RELENG_RECONFIGURE'] = '1'
            elif paction == PkgAction.REINSTALL:
                env['RELENG_REINSTALL'] = '1'

            if self.opts.debug:
                env['RELENG_DEBUG'] = '1'
            if self.opts.devmode:
                env['RELENG_DEVMODE'] = '1'
            if self.opts.force:
                env['RELENG_FORCE'] = '1'
            if self.opts.local_srcs:
                env['RELENG_LOCALSRCS'] = '1'
            if self.opts.verbose:
                env['RELENG_VERBOSE'] = '1'

        # utility methods (if adjusting, see also `releng_tool.__init__`)
        script_env['debug'] = debug
        script_env['err'] = err
        script_env['log'] = log
        script_env['note'] = note
        script_env['releng_copy'] = path_copy
        script_env['releng_env'] = env_value
        script_env['releng_execute'] = execute
        script_env['releng_execute_rv'] = execute_rv
        script_env['releng_exists'] = path_exists
        script_env['releng_exit'] = platform_exit
        script_env['releng_expand'] = expand
        script_env['releng_join'] = os.path.join
        script_env['releng_mkdir'] = ensure_dir_exists
        script_env['releng_move'] = path_move
        script_env['releng_remove'] = path_remove
        script_env['releng_require_version'] = require_version
        script_env['releng_tmpdir'] = generate_temp_dir
        script_env['releng_touch'] = touch
        script_env['releng_wd'] = interim_working_dir
        script_env['success'] = success
        script_env['verbose'] = verbose
        script_env['warn'] = warn

    def _process_file_flags(self):
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
        err_flag = False

        state = process_file_flag(opts.devmode, opts.ff_devmode)
        if state == FileFlag.CONFIGURED:
            success('configured root for development mode')
            configured = True
        elif state == FileFlag.NOT_CONFIGURED:
            err_flag = True
        opts.devmode = (state == FileFlag.EXISTS)
        if opts.devmode:
            verbose('development mode enabled')

        state = process_file_flag(opts.local_srcs, opts.ff_local_srcs)
        if state == FileFlag.CONFIGURED:
            success('configured root for local-sources mode')
            configured = True
        elif state == FileFlag.NOT_CONFIGURED:
            err_flag = True
        opts.local_srcs = (state == FileFlag.EXISTS)
        if opts.local_srcs:
            verbose('local-sources mode enabled')

        if err_flag:
            return False
        elif configured:
            return True
        else:
            return None

    def _process_settings(self, settings):
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
        def notify_invalid_value(key, expected):
            err('''\
invalid configuration value provided

The configuration file defines a key with an unexpected type. Correct the
following key entry and re-try again.

    Key: {}
    Expected Type: {}''', key, expected)

        if CONF_KEY_CACHE_EXT_TRANSFORM in settings:
            cet = None
            if callable(settings[CONF_KEY_CACHE_EXT_TRANSFORM]):
                cet = settings[CONF_KEY_CACHE_EXT_TRANSFORM]
            if cet is None:
                notify_invalid_value(CONF_KEY_CACHE_EXT_TRANSFORM, 'callable')
                return False
            self.opts.cache_ext_transform = cet

        if CONF_KEY_DEFINTERN in settings:
            is_default_internal = settings[CONF_KEY_DEFINTERN]
            if not isinstance(is_default_internal, bool):
                notify_invalid_value(CONF_KEY_DEFINTERN, 'bool')
                return False
            self.opts.default_internal_pkgs = is_default_internal

        if CONF_KEY_LICENSE_HEADER in settings:
            license_header = interpret_string(settings[CONF_KEY_LICENSE_HEADER])
            if license_header is None:
                notify_invalid_value(CONF_KEY_LICENSE_HEADER, 'str')
                return False
            self.opts.license_header = license_header

        if CONF_KEY_OVERRIDE_REV in settings:
            orz = interpret_dictionary_strings(settings[CONF_KEY_OVERRIDE_REV])
            if orz is None:
                notify_invalid_value(CONF_KEY_OVERRIDE_REV, 'dict(str,str)')
                return False
            self.opts.revision_override = orz

        if CONF_KEY_OVERRIDE_SITES in settings:
            v = interpret_dictionary_strings(settings[CONF_KEY_OVERRIDE_SITES])
            if v is None:
                notify_invalid_value(CONF_KEY_OVERRIDE_SITES, 'dict(str,str)')
                return False
            self.opts.sites_override = v

        if CONF_KEY_OVERRIDE_TOOLS in settings:
            v = interpret_dictionary_strings(settings[CONF_KEY_OVERRIDE_TOOLS])
            if v is None:
                notify_invalid_value(CONF_KEY_OVERRIDE_TOOLS, 'dict(str,str)')
                return False
            self.opts.extract_override = v

        if CONF_KEY_PREREQUISITES in settings:
            prerequisites = interpret_strings(settings[CONF_KEY_PREREQUISITES])
            if prerequisites is None:
                notify_invalid_value(CONF_KEY_PREREQUISITES, 'str or list(str)')
                return False
            self.opts.prerequisites.extend(prerequisites)

        if CONF_KEY_QUIRKS in settings:
            quirks = interpret_strings(settings[CONF_KEY_QUIRKS])
            if quirks is None:
                notify_invalid_value(CONF_KEY_QUIRKS, 'str or list(str)')
                return False
            self.opts.quirks.extend(quirks)
            for quirk in quirks:
                verbose('configuration quirk applied: ' + quirk)

        if CONF_KEY_SYSROOT_PREFIX in settings:
            sysroot_prefix = interpret_string(settings[CONF_KEY_SYSROOT_PREFIX])
            if sysroot_prefix is None:
                notify_invalid_value(CONF_KEY_SYSROOT_PREFIX, 'str')
                return False
            if not sysroot_prefix.startswith('/'):
                sysroot_prefix = '/' + sysroot_prefix
            self.opts.sysroot_prefix = sysroot_prefix

        if CONF_KEY_URL_MIRROR in settings:
            url_mirror = interpret_string(settings[CONF_KEY_URL_MIRROR])
            if url_mirror is None:
                notify_invalid_value(CONF_KEY_URL_MIRROR, 'str')
                return False
            self.opts.url_mirror = url_mirror

        if CONF_KEY_URLOPEN_CONTEXT in settings:
            urlopen_context = None
            if isinstance(settings[CONF_KEY_URLOPEN_CONTEXT], ssl.SSLContext):
                urlopen_context = settings[CONF_KEY_URLOPEN_CONTEXT]
            if urlopen_context is None:
                notify_invalid_value(CONF_KEY_URLOPEN_CONTEXT, 'ssl.SSLContext')
                return False
            self.opts.urlopen_context = urlopen_context

        if CONF_KEY_EXTEN_PKGS in settings:
            epd = interpret_strings(settings[CONF_KEY_EXTEN_PKGS])
            if epd is None:
                notify_invalid_value(CONF_KEY_EXTEN_PKGS, 'str or list(str)')
                return False
            self.opts.extern_pkg_dirs = epd

        ext_names = []
        if CONF_KEY_EXTENSIONS in settings:
            ext_names = interpret_strings(settings[CONF_KEY_EXTENSIONS])
            if ext_names is None:
                notify_invalid_value(CONF_KEY_EXTENSIONS, 'str or list(str)')
                return False

        self.registry.load_all_extensions(ext_names)
        return True
