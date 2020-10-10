# -*- coding: utf-8 -*-
# Copyright 2018-2020 releng-tool

from .. import __version__ as releng_version
from ..defs import CONF_KEY_CACHE_EXT_TRANSFORM
from ..defs import CONF_KEY_DEFINTERN
from ..defs import CONF_KEY_EXTENSIONS
from ..defs import CONF_KEY_EXTEN_PKGS
from ..defs import CONF_KEY_LICENSE_HEADER
from ..defs import CONF_KEY_OVERRIDE_REV
from ..defs import CONF_KEY_OVERRIDE_SITES
from ..defs import CONF_KEY_OVERRIDE_TOOLS
from ..defs import CONF_KEY_PKGS
from ..defs import CONF_KEY_PREREQUISITES
from ..defs import CONF_KEY_QUIRKS
from ..defs import CONF_KEY_SYSROOT_PREFIX
from ..defs import CONF_KEY_URL_MIRROR
from ..defs import GlobalAction
from ..defs import PkgAction
from ..defs import VcsType
from ..packages import RelengPackageManager
from ..prerequisites import RelengPrerequisites
from ..registry import RelengRegistry
from ..util.env import extend_script_env
from ..util.env import set_env_value
from ..util.file_flags import FileFlag
from ..util.file_flags import check_file_flag
from ..util.file_flags import process_file_flag
from ..util.io import FailedToPrepareWorkingDirectoryError
from ..util.io import ensure_dir_exists
from ..util.io import execute
from ..util.io import generate_temp_dir
from ..util.io import interim_working_dir
from ..util.io import opt_file
from ..util.io import path_copy
from ..util.io import path_exists
from ..util.io import path_move
from ..util.io import path_remove
from ..util.io import run_script
from ..util.io import touch
from ..util.log import debug
from ..util.log import err
from ..util.log import log
from ..util.log import note
from ..util.log import success
from ..util.log import verbose
from ..util.log import warn
from ..util.platform import platform_exit
from ..util.string import expand
from ..util.string import interpret_dictionary_strings
from ..util.string import interpret_string
from ..util.string import interpret_strings
from .bootstrap import stage as bootstrap_stage
from .build import stage as build_stage
from .configure import stage as configure_stage
from .extract import stage as extract_stage
from .fetch import stage as fetch_stage
from .init import initialize_sample
from .install import stage as install_stage
from .patch import stage as patch_stage
from .post import stage as post_stage
from collections import OrderedDict
from datetime import datetime
from shutil import copyfileobj
import os

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
        opts = self.opts
        gaction = opts.gbl_action
        if gaction == GlobalAction.INIT:
            return initialize_sample(opts)

        self.start_time = datetime.now().replace(microsecond=0)
        verbose("loading user's configuration...")
        gbls = {
            'releng_args': opts.forward_args,
            'releng_version': releng_version,
        }

        # prepare script environment to make helpers available to configuration
        # script(s)
        self._prepare_script_environment(gbls, opts.pkg_action)

        conf_point, conf_point_exists = opt_file(opts.conf_point)
        if not conf_point_exists:
            err('missing configuration file')
            err("""\
The configuration file cannot be found. Ensure the configuration file exists
in the working directory or the provided root directory:

    {}""".format(conf_point))
            return False

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
        if gaction == GlobalAction.CLEAN or gaction == GlobalAction.MRPROPER:
            self._handle_clean_request(gaction == GlobalAction.MRPROPER)
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
            debug(' {}'.format(pkg_name))

        # processing additional settings
        if not self._process_settings(settings):
            return False

        # load and process packages
        pkgs = self.pkgman.load(pkg_names)
        if not pkgs:
            return False

        try:
            pa = opts.pkg_action
            license_files = {}

            # if cleaning a package, remove it's build output directory and stop
            if pa == PkgAction.CLEAN:
                for pkg in pkgs:
                    if pkg.name == opts.target_action:
                        verbose('removing output directory for package: ' +
                            pkg.name)
                        path_remove(pkg.build_output_dir)
                        return True
                assert False # should not reach here

            # ensure any of required host tools do exist
            if 'releng.disable_prerequisites_check' not in opts.quirks:
                prerequisites = RelengPrerequisites(pkgs, opts.prerequisites)
                if not prerequisites.check():
                    return False

            # ensure all package sources are acquired first
            for pkg in pkgs:
                if not self._stage_init(pkg):
                    return False

                # none/local-vcs-type packages do not need to fetch
                if pkg.vcs_type in (VcsType.LOCAL, VcsType.NONE):
                    continue

                # in the event that we not not explicit fetching and the package
                # has already been extracted, completely skip the fetching stage
                if gaction != GlobalAction.FETCH and pa != PkgAction.FETCH:
                    flag = pkg.__ff_extract
                    if check_file_flag(flag) == FileFlag.EXISTS:
                        continue

                if not fetch_stage(self, pkg):
                    return False

            # prepend project's host directory to path
            host_bin = os.path.join(opts.host_dir, 'bin')
            os.environ['PATH'] = host_bin + os.pathsep + os.environ['PATH']

            # re-apply script environment to ensure previous script environment
            # changes have not manipulated the environment (from standard
            # helpers).
            self._prepare_script_environment(script_env, opts.pkg_action)

            # process each package (configuring, building, etc.)
            if gaction != GlobalAction.FETCH and pa != PkgAction.FETCH:

                # ensure the symbols directory exists, as a package may wish to
                # populate it anytime between a configuration stage to a
                # post-package stage
                if not ensure_dir_exists(opts.symbols_dir):
                    return False

                target = opts.target_action
                for pkg in pkgs:
                    verbose('processing package: {}'.format(pkg.name))

                    # skip if generating license information and no license
                    # files exist for this package
                    if (gaction == GlobalAction.LICENSES and
                            not pkg.license_files):
                        continue

                    # prepare environment
                    pkg_env = self._stage_env(pkg, script_env)

                    # extracting
                    flag = pkg.__ff_extract
                    if check_file_flag(flag) == FileFlag.NO_EXIST:
                        # none/local-vcs-type packages do not need to fetch
                        if pkg.vcs_type in (VcsType.LOCAL, VcsType.NONE):
                            pass
                        elif not extract_stage(self, pkg):
                            return False
                        # now that the extraction stage has (most likely)
                        # created a build directory, ensure the output directory
                        # exists as well (for file flags and other content)
                        if not ensure_dir_exists(pkg.build_output_dir):
                            return False
                        if process_file_flag(True, flag) != FileFlag.CONFIGURED:
                            return False
                    if gaction == GlobalAction.EXTRACT:
                        continue
                    if pa == PkgAction.EXTRACT and pkg.name == target:
                        break

                    # patching
                    flag = pkg.__ff_patch
                    if check_file_flag(flag) == FileFlag.NO_EXIST:
                        # local-vcs-type packages do not need to patch
                        if pkg.vcs_type is VcsType.LOCAL:
                            pass
                        elif not patch_stage(self, pkg, pkg_env):
                            return False
                        if process_file_flag(True, flag) != FileFlag.CONFIGURED:
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
                    if check_file_flag(flag) == FileFlag.NO_EXIST:
                        if not self._stage_license(pkg):
                            return False
                        if process_file_flag(True, flag) != FileFlag.CONFIGURED:
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
                    if check_file_flag(flag) == FileFlag.NO_EXIST:
                        if not bootstrap_stage(self, pkg, pkg_env):
                            return False
                        if process_file_flag(True, flag) != FileFlag.CONFIGURED:
                            return False

                    # configuring
                    flag = pkg.__ff_configure
                    if check_file_flag(flag) == FileFlag.NO_EXIST:
                        if not configure_stage(self, pkg, pkg_env):
                            return False
                        if process_file_flag(True, flag) != FileFlag.CONFIGURED:
                            return False
                    if pa in (PkgAction.CONFIGURE, PkgAction.RECONFIGURE):
                        if pkg.name == target:
                            break

                    # building
                    flag = pkg.__ff_build
                    if check_file_flag(flag) == FileFlag.NO_EXIST:
                        if not build_stage(self, pkg, pkg_env):
                            return False
                        if process_file_flag(True, flag) != FileFlag.CONFIGURED:
                            return False
                    if pa in (PkgAction.BUILD, PkgAction.REBUILD):
                        if pkg.name == target:
                            break

                    # installing
                    flag = pkg.__ff_install
                    if check_file_flag(flag) == FileFlag.NO_EXIST:
                        if not install_stage(self, pkg, pkg_env):
                            return False
                        if process_file_flag(True, flag) != FileFlag.CONFIGURED:
                            return False
                    # (note: re-install requests will re-invoke package-specific
                    # post-processing)

                    # package-specific post-processing
                    flag = pkg.__ff_post
                    if check_file_flag(flag) == FileFlag.NO_EXIST:
                        if not post_stage(self, pkg, pkg_env):
                            return False
                        if process_file_flag(True, flag) != FileFlag.CONFIGURED:
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
            or opts.target_action is not None)

        # perform license generation
        if gaction == GlobalAction.LICENSES or not is_action:
            note('generating license information...')

            if not self._perform_license_generation(license_files):
                return False

        # perform post-processing and completion message if not performing a
        # specific action
        if not is_action:
            if not self._post_processing(script_env):
                err('failed to perform post-processing')
                return False

            self.end_time = datetime.now().replace(microsecond=0)
            success('completed ({})'.format(self.end_time - self.start_time))

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
                path_remove(pkg.__ff_build)
                path_remove(pkg.__ff_install)
                path_remove(pkg.__ff_post)
            elif self.opts.pkg_action == PkgAction.RECONFIGURE:
                path_remove(pkg.__ff_bootstrap)
                path_remove(pkg.__ff_configure)
                path_remove(pkg.__ff_build)
                path_remove(pkg.__ff_install)
                path_remove(pkg.__ff_post)
            elif self.opts.pkg_action == PkgAction.REINSTALL:
                path_remove(pkg.__ff_install)
                path_remove(pkg.__ff_post)

        return True

    def _stage_env(self, pkg, script_env):
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
            env['PREFIX'] = pkg.prefix # will override existing prefix

            if pkg.fixed_jobs:
                env['NJOBS'] = str(pkg.fixed_jobs)
                env['NJOBSCONF'] = str(pkg.fixed_jobs)

            if pkg.is_internal:
                env['PKG_INTERNAL'] = '1'

        return pkg_env

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

    def _handle_clean_request(self, proper=False):
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
            path_remove(self.opts.out_dir)

            verbose('removing file flags')
            path_remove(self.opts.ff_local_srcs)
            path_remove(self.opts.ff_devmode)
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
        script, script_exists = opt_file(self.opts.post_point)

        # TODO remove deprecated configuration load in (at maximum) v1.0
        if not script_exists:
            script = os.path.join(self.opts.root_dir, 'post.py')
            if os.path.isfile(script):
                warn('using deprecated post-processing file post.py -- switch '
                     'to releng-post for future projects')
                script_exists = True

        if script_exists:
            verbose('performing post-processing...')

            # ensure images directory exists (as the post-processing script will
            # most likely populate it)
            if not ensure_dir_exists(self.opts.images_dir):
                return False

            if not run_script(script, env, subject='post-processing'):
                return False

            verbose('post-processing completed')

        return True

    def _prepare_script_environment(self, script_env, action):
        """
        prepare the script environment with common project values

        A package stage will be invoked with a tailored environment variables.
        This method is used to prepare an environment dictionary with common
        variables such the the staging directory, target directory and more.

        Args:
            script_env: environment dictionary to prepare
            action: the package-specific invoked
        """

        # always register optional flags in script environment
        script_env['RELENG_DEVMODE'] = None
        script_env['RELENG_LOCALSRCS'] = None
        script_env['RELENG_REBUILD'] = None
        script_env['RELENG_RECONFIGURE'] = None
        script_env['RELENG_REINSTALL'] = None

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
        script_env['releng_copy'] = path_copy
        script_env['releng_env'] = set_env_value
        script_env['releng_execute'] = execute
        script_env['releng_exists'] = path_exists
        script_env['releng_exit'] = platform_exit
        script_env['releng_expand'] = expand
        script_env['releng_join'] = os.path.join
        script_env['releng_mkdir'] = ensure_dir_exists
        script_env['releng_move'] = path_move
        script_env['releng_remove'] = path_remove
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
            osz = interpret_dictionary_strings(settings[CONF_KEY_OVERRIDE_SITES])
            if osz is None:
                notify_invalid_value(CONF_KEY_OVERRIDE_SITES, 'dict(str,str)')
                return False
            self.opts.sites_override = osz

        if CONF_KEY_OVERRIDE_TOOLS in settings:
            otz = interpret_dictionary_strings(settings[CONF_KEY_OVERRIDE_TOOLS])
            if otz is None:
                notify_invalid_value(CONF_KEY_OVERRIDE_TOOLS, 'dict(str,str)')
                return False
            self.opts.extract_override = otz

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
