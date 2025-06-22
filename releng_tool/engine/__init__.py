# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from collections import OrderedDict
from datetime import datetime
from releng_tool import __version__ as releng_version
from releng_tool.defs import ConfKey
from releng_tool.defs import GBL_LSRCS
from releng_tool.defs import GlobalAction
from releng_tool.defs import PackageType
from releng_tool.defs import PkgAction
from releng_tool.defs import SbomFormatType
from releng_tool.defs import UNSET_VALUES
from releng_tool.defs import VcsType
from releng_tool.engine.cargo import cargo_package_clean
from releng_tool.engine.cargo import cargo_register_pkg_paths
from releng_tool.engine.fetch import stage as fetch_stage
from releng_tool.engine.init import initialize_sample
from releng_tool.engine.license import LicenseManager
from releng_tool.engine.sbom import SbomManager
from releng_tool.engine.script_env import prepare_script_environment
from releng_tool.engine.suggest import suggest
from releng_tool.engine.vsdevcmd import vsdevcmd_initialize
from releng_tool.exceptions import RelengToolInvalidConfigurationScript
from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from releng_tool.exceptions import RelengToolInvalidOverrideConfigurationScript
from releng_tool.exceptions import RelengToolMissingConfigurationError
from releng_tool.exceptions import RelengToolMissingPackagesError
from releng_tool.exceptions import RelengToolUnknownAction
from releng_tool.opts import RELENG_CONF_NAME
from releng_tool.packages.exceptions import RelengToolMissingPackageScript
from releng_tool.packages.exceptions import RelengToolStageFailure
from releng_tool.packages.manager import RelengPackageManager
from releng_tool.packages.pipeline import PipelineResult
from releng_tool.packages.pipeline import RelengPackagePipeline
from releng_tool.prerequisites import RelengPrerequisites
from releng_tool.registry import RelengRegistry
from releng_tool.stats import RelengStats
from releng_tool.tool.python import PYTHON
from releng_tool.util import nullish_coalescing as NC
from releng_tool.util.env import extend_script_env
from releng_tool.util.file_flags import FileFlag
from releng_tool.util.file_flags import check_file_flag
from releng_tool.util.file_flags import process_file_flag
from releng_tool.util.interpret import interpret_dict
from releng_tool.util.interpret import interpret_seq
from releng_tool.util.io import run_script
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.io_opt_file import opt_file
from releng_tool.util.io_remove import path_remove
from releng_tool.util.io_wd import FailedToPrepareWorkingDirectoryError
from releng_tool.util.io_wd import wd
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import hint
from releng_tool.util.log import log
from releng_tool.util.log import note
from releng_tool.util.log import releng_log_tag
from releng_tool.util.log import success
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
from releng_tool.util.log import warn_wrap
from releng_tool.util.string import expand
import json
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
        stats: statistics tracker
    """
    def __init__(self, opts):
        self.registry = RelengRegistry()
        self.opts = opts
        self.pkgman = RelengPackageManager(opts, self.registry, dvcs_cache=True)
        self.stats = RelengStats(opts)

        # load spdx license data
        engine_dir = os.path.dirname(__file__)
        self._base_dir = os.path.dirname(engine_dir)

        data_dir = os.path.join(self._base_dir, 'data')
        licenses_file = os.path.join(data_dir, 'licenses', 'data.json')

        debug('loading spdx license database: {}', licenses_file)
        with open(licenses_file) as f:
            self.opts.spdx = json.load(f)

        # enable execute environment logging if the quirk is set
        if opts.debug_extended or 'releng.log.execute_args' in opts.quirks:
            releng_log_tag('execute-args')

        if opts.debug_extended or 'releng.log.execute_env' in opts.quirks:
            releng_log_tag('execute-env')

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
        pa = opts.pkg_action

        if gaction == GlobalAction.INIT:
            return initialize_sample(opts)

        # share detected foward argument, unless this is an exec call
        forward_args = [] if pa == PkgAction.EXEC else opts.forward_args

        start_time = datetime.now().replace(microsecond=0)  # noqa: DTZ005
        gbls = {
            'releng_args': forward_args,
            'releng_version': releng_version,
        }

        if opts.profiles:
            debug('operating with profiles: {}', ', '.join(opts.profiles))

        # if any injected key-value entries are provided, attempt to add them
        # into the global context
        if opts.injected_kv:
            debug('injecting key-value arguments into global context')
            gbls.update(opts.injected_kv)

        debug('total job count configured: {}', self.opts.jobs)

        debug('loading statistics...')
        self.stats.load()

        # verify the project's configuration exists before performing any
        # actions
        verbose('detecting project configuration...')
        if opts.conf_point:
            conf_point, conf_point_exists = opt_file(opts.conf_point)
        else:
            script_name = os.path.join(self.opts.root_dir, RELENG_CONF_NAME)
            conf_point, conf_point_exists = opt_file(script_name)

            if not conf_point_exists:
                deprecated_cfgs = [
                    'releng',  # deprecated
                ]

                for dcfg in deprecated_cfgs:
                    script_name = os.path.join(self.opts.root_dir, dcfg)
                    conf_point, conf_point_exists = opt_file(script_name)
                    if os.path.isfile(conf_point):
                        warn('using deprecated configuration file {} -- switch '
                             'to {}.rt when possible',
                             os.path.basename(conf_point),
                             RELENG_CONF_NAME)
                        break

            if not conf_point_exists:
                conf_point = 'releng-tool.rt'

        if not conf_point_exists:
            raise RelengToolMissingConfigurationError(conf_point)

        # file flag processing
        state = self._process_file_flags()
        if state is not None:
            debug('file-flag processing has triggered closure')
            return state

        # dump state information to the standard output stream
        if gaction == GlobalAction.STATE:
            self._dump_state()
            return True

        # inform the user of any active running modes
        if self.opts.devmode:
            if self.opts.devmode is True:
                postfix = ''
            else:
                postfix = f' ({self.opts.devmode})'
            hint('running in development mode' + postfix)

        if self.opts.local_srcs:
            hint('running in local-sources mode')

        # register the project's root directory as a system path; permits a
        # project to import locally created modules in their build/etc. scripts
        debug('registering root directory in path...')
        sys.path.append(str(opts.root_dir))
        os.environ['PATH'] = os.environ['PATH'] + os.pathsep + opts.root_dir

        # prepare script environment to make helpers available to configuration
        # script(s)
        #
        # Note that some options prepared for the configuration script may
        # need to be updated after running the project's configuration (e.g.
        # possibly needing to update the `PREFIX` variable if `sysroot_prefix`
        # was configured). This is peformed later in the engine run call.
        prepare_script_environment(gbls, opts)

        verbose(f'loading project configuration: {conf_point}')
        settings = run_script(conf_point, gbls, subject='configuration')
        if not settings:
            raise RelengToolInvalidConfigurationScript

        script_env = gbls.copy()
        extend_script_env(script_env, settings)
        self.pkgman.script_env = script_env
        verbose('configuration file loaded')

        # configuration overrides file for builders
        if os.path.isfile(opts.conf_point_overrides):
            warn('detected deprecated configuration overrides file')

            overrides = run_script(opts.conf_point_overrides, gbls,
                subject='configuration overrides')
            if not overrides:
                raise RelengToolInvalidOverrideConfigurationScript

            extend_script_env(script_env, overrides)
            extend_script_env(settings, overrides)
            verbose('configuration overrides file loaded')

        # handle cleaning requests
        clean_actions = [
            GlobalAction.CLEAN,
            GlobalAction.DISTCLEAN,
            GlobalAction.MRPROPER,
        ]

        if gaction in clean_actions:
            return self._handle_clean_request(gaction)

        # determine package name(s) extraction
        #
        # Compile a (minimum) list of package names to be processed; either from
        # the user explicitly provided package target or from the user's
        # configuration file.
        if opts.target_action:
            pkg_names = [opts.target_action]
        else:
            pkg_names = self._get_package_names(conf_point, settings)
        if not pkg_names:
            return False
        debug('target packages)')
        for pkg_name in pkg_names:
            debug(' {}', pkg_name)

        # processing additional settings
        if not self._process_settings(settings):
            raise RelengToolInvalidConfigurationSettings

        # check if we should preload environment variables from vsdevcmd
        if opts.vsdevcmd and sys.platform == 'win32':
            debug('attempting to load vsdevcmd variables')
            vsdevcmd_initialize(
                prodstr=opts.vsdevcmd_products,
                verstr=opts.vsdevcmd,
                env=os.environ,
            )

        # load project-defined environment options
        for key, val in opts.environment.items():
            os.environ[key] = val

        # notify extensions that configuration options have been processed
        with wd(opts.root_dir):
            self.registry.emit('config-loaded', env=script_env)

        # register the project's host directory as a system path; lazily permits
        # loading host tools (not following prefix or bin container) built by a
        # project over the system
        debug(f'registering host directory in path: {opts.host_dir}')
        sys.path.insert(0, str(opts.host_dir))
        os.environ['PATH'] = opts.host_dir + os.pathsep + os.environ['PATH']

        # register the project's host-bin directory as a system path; lazily
        # permits loading host tools built by a project over the system
        host_sysroot_dir = opts.host_dir + opts.sysroot_prefix
        host_bin_dir = os.path.join(host_sysroot_dir, 'bin')
        debug(f'registering host bin directory in path: {host_bin_dir}')
        sys.path.insert(0, str(host_bin_dir))
        os.environ['PATH'] = host_bin_dir + os.pathsep + os.environ['PATH']

        # load and process packages
        try:
            pkgs = self.pkgman.load(pkg_names)
            if not pkgs:
                return False
        except RelengToolMissingPackageScript as ex:
            if not opts.target_action:
                raise

            extra = ''

            detected = suggest(opts, opts.target_action)
            if detected:
                if len(detected) == 1:
                    alt = '"{}"'.format(detected[0])
                elif len(detected) == 2:  # noqa: PLR2004
                    alt = '"{}" or "{}"'.format(detected[0], detected[1])
                else:
                    alt = '"{}" or "{}"'.format(
                        '", "'.join(detected[:-1]), detected[-1])

                extra = f'\n  Did you mean {alt}?'

            raise RelengToolUnknownAction({
                'action': opts.target_action,
                'extra': extra,
            }) from ex

        # if cleaning a package, remove it's build output directory and stop
        if pa in (PkgAction.CLEAN, PkgAction.DISTCLEAN, PkgAction.FRESH):
            for pkg in pkgs:
                if pkg.name != opts.target_action:
                    continue

                def pkg_verbose_clean(desc):
                    pkg_name = pkg.name  # noqa: B023
                    verbose('{} for package: {}', desc, pkg_name)

                # cargo packages need to perform a custom pre-clean task
                if pkg.type == PackageType.CARGO:
                    pkg_verbose_clean('cleaning cargo output')
                    cargo_package_clean(opts, pkg)

                pkg_verbose_clean('removing output directory')
                rv = path_remove(pkg.build_output_dir)

                if pa == PkgAction.DISTCLEAN:
                    if os.path.exists(pkg.cache_file):
                        pkg_verbose_clean('removing cache file')
                        rv &= path_remove(pkg.cache_file)
                    if os.path.isdir(pkg.cache_dir):
                        pkg_verbose_clean('removing cache directory')
                        rv &= path_remove(pkg.cache_dir)

                if rv and pa == PkgAction.FRESH:
                    break

                return rv

        # ensure any of required host tools do exist
        pcheck = 'releng.disable_prerequisites_check' not in opts.quirks
        requested_sbom = gaction == GlobalAction.SBOM

        if pcheck and not requested_sbom:
            exclude_host_check = set()
            for pkg in pkgs:
                if pkg.host_provides:
                    exclude_host_check.update(pkg.host_provides)

            prerequisites = RelengPrerequisites(pkgs, opts.prerequisites)
            if not prerequisites.check(exclude=exclude_host_check):
                return False

        # track if this action is "pre-configuration", where a package
        # dependency chain can be ignored
        requested_preconfig = pa in [
            PkgAction.EXTRACT,
            PkgAction.FETCH,
            PkgAction.FRESH,
            PkgAction.LICENSE,
            PkgAction.PATCH,
        ]

        # track if the run is a "specific action", where only a subset of
        # work will be done; do not consider the "punch" action a specific
        # action as we want to do everything in this case
        if self.opts.gbl_action == GlobalAction.PUNCH:
            is_action = False
        else:
            is_action = (gaction or pa or opts.target_action is not None)

        # determine if an explicit fetch request has been made
        only_fetch = None
        if gaction == GlobalAction.FETCH or pa == PkgAction.FETCH:
            only_fetch = True

        req_fetch = only_fetch
        if gaction == GlobalAction.FETCH_FULL or pa == PkgAction.FETCH_FULL:
            req_fetch = True

        try:
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

                # skip if already fetched
                #
                # In the event that we are not explicitly fetching and the
                # package has already been fetched, skip the fetching stage.
                # We want to rely on a fetch-specific flag since we do not
                # want to constantly re-fetch unprocessed packages in certain
                # development mode states. For example, if a build fails,
                # a user re-triggers a build and all ignore-cache packages
                # will be re-fetched again (where really, we only want to
                # have the ignore-cache flag fetch once from a cleaned state).
                fflag = pkg._ff_fetch
                if not req_fetch and not pkg.local_srcs:
                    if check_file_flag(fflag) == FileFlag.EXISTS:
                        continue

                self.stats.track_duration_start(pkg.name, 'fetch')
                fetched = fetch_stage(self, pkg, req_fetch, pkg.fetch_opts)
                self.stats.track_duration_end(pkg.name, 'fetch')
                if not fetched:
                    return False

                if process_file_flag(fflag, flag=True) != FileFlag.CONFIGURED:
                    return False

            # re-apply script environment to ensure previous script environment
            # changes have not manipulated the environment (from standard
            # helpers).
            prepare_script_environment(script_env, opts)

            # process each package (configuring, building, etc.)
            if not only_fetch and not requested_sbom:
                # pre-populate "common" directories
                #
                # The following will attempt to pre-populate common directories
                # before attempting to process a package pipeline. A package
                # configured in this pipeline may wish to populate any one of
                # these directories anytime between a configuration stage to a
                # post-package stage. Ensuring these directories exist ahead of
                # time can help prevent scenarios where developers try to file
                # a file into a directory, but instead create a file as the
                # common directory name (e.g. `TARGET_DIR` points to a file).
                common_dirs = [
                    opts.host_dir,
                    opts.staging_dir,
                    opts.symbols_dir,
                    opts.target_dir,
                ]
                for common_dir in common_dirs:
                    if not mkdir(common_dir):
                        return False

                pipeline = RelengPackagePipeline(self, opts, script_env)

                # if we have any cargo actions, we will automatically process
                # them up to the patch stage; as we need each package to have
                # their `Cargo.toml` configurations ready so that releng-tool
                # can provide path overrides
                if not requested_preconfig:
                    cargo_pkgs = []

                    for pkg in pkgs:
                        if pkg.type != PackageType.CARGO:
                            continue

                        verbose('processing package '
                                '(cargo pre-process): {}', pkg.name)
                        prv = pipeline.process(pkg, GlobalAction.PATCH)
                        if prv == PipelineResult.ERROR:
                            return False

                        cargo_pkgs.append(pkg)

                    cargo_register_pkg_paths(cargo_pkgs)

                # main package processing stage
                for pkg in pkgs:
                    # if this is a package-specific pre-configure action, only
                    # process the specific action
                    if requested_preconfig and pkg.name != opts.target_action:
                        continue

                    # if this was a host targeted python package, attempt to
                    # register additional host directories into the path to
                    # allow them to be used by later packages/post-scripts;
                    # only adds new paths if the package has a custom prefix
                    if pkg.type == PackageType.PYTHON and \
                            pkg.install_type == 'host' and \
                            not pkg.python_installer_scheme:
                        pfx = NC(pkg.prefix, opts.sysroot_prefix)
                        PYTHON.register_host_python(opts.host_dir, pfx)

                    verbose('processing package: {}', pkg.name)
                    prv = pipeline.process(pkg)
                    if prv == PipelineResult.ERROR:
                        return False

                    if prv == PipelineResult.STOP:
                        return True

                if not is_action:
                    note('all packages have been processed')

        except RelengToolStageFailure:
            return False
        except FailedToPrepareWorkingDirectoryError as e:
            err('''\
unable to prepare a package's working directory

An attempt to prepare and move into a working directory for a package process
has failed. Ensure the following path is accessible for this user:

    {}''', e)
            return False

        # perform sbom generation
        generated_sboms = None
        if gaction == GlobalAction.SBOM or not is_action:
            note('generating sbom information...')
            sbom_manager = SbomManager(opts)
            sbom_cache = sbom_manager.build_cache(pkgs)
            if not sbom_manager.generate(sbom_cache):
                return False

            generated_sboms = list(sbom_manager.generated)

        # perform license generation
        generated_licenses = None
        if gaction == GlobalAction.LICENSES or pa == PkgAction.LICENSE \
                or not is_action:
            note('generating license information...')
            license_manager = LicenseManager(opts)
            license_cache = license_manager.build_cache(pkgs)
            if not license_manager.generate(license_cache):
                return False

            generated_licenses = list(license_manager.generated)

        # add extra script-env information before post-processing
        script_env['RELENG_GENERATED_SBOMS'] = generated_sboms
        script_env['RELENG_GENERATED_LICENSES'] = generated_licenses

        # perform post-processing and completion message if not performing a
        # specific action
        if not is_action:
            if not self._post_processing(script_env):
                err('failed to perform post-processing')
                return False

            end_time = datetime.now().replace(microsecond=0)  # noqa: DTZ005
            success('completed ({})', end_time - start_time)

        # attempt to generate a report at the end of a run
        self.stats.generate()

        return True

    def _dump_state(self):
        log('releng-tool {}', releng_version)
        log('Python {}', sys.version)
        log('Tool: {}', self._base_dir)
        log('Root: {}', self.opts.root_dir)

        if self.opts.devmode:
            if self.opts.devmode is True:
                postfix = ''
            else:
                postfix = f' ({self.opts.devmode})'
            log('Development mode: Enabled' + postfix)
            log(' (invoke `releng-tool --development unset` to unconfigure)')
        else:
            log('Development mode: Disabled')

        if self.opts.local_srcs:
            log('Local-sources mode: Enabled')

            for key, val in sorted(self.opts.local_srcs.items()):
                if not val:
                    val = '<parent>' if key == GBL_LSRCS else '<unset>'

                entry = val
                if key != GBL_LSRCS and not os.path.exists(val):
                    entry += warn_wrap('  (path does not exist)')

                log(' {}: {}', key, entry)

            log(' (invoke `releng-tool --local-sources unset` to unconfigure)')
        else:
            log('Local-sources mode: Disabled')

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

        rv = True

        # punch/forced request
        #
        # When a punch/forced request is made, clear all file flags so these
        # stages can be invoked again.
        if self.opts.gbl_action == GlobalAction.PUNCH or self.opts.force:
            rv &= path_remove(pkg._ff_fetch)
            rv &= path_remove(pkg._ff_bootstrap)
            rv &= path_remove(pkg._ff_configure)
            rv &= path_remove(pkg._ff_build)
            rv &= path_remove(pkg._ff_install)
            rv &= path_remove(pkg._ff_post)

        # user invoking a package-specific override
        #
        # If the user is invoking a package rebuild, reconfiguration, etc.,
        # ensure existing file flags are cleared to ensure these stages are
        # invoked again.
        elif pkg.name == self.opts.target_action:
            if (self.opts.pkg_action in
                    (PkgAction.REBUILD, PkgAction.REBUILD_ONLY)):
                rv &= path_remove(pkg._ff_build)
                rv &= path_remove(pkg._ff_install)
                rv &= path_remove(pkg._ff_post)
            elif (self.opts.pkg_action in
                    (PkgAction.RECONFIGURE, PkgAction.RECONFIGURE_ONLY)):
                rv &= path_remove(pkg._ff_bootstrap)
                rv &= path_remove(pkg._ff_configure)
                rv &= path_remove(pkg._ff_build)
                rv &= path_remove(pkg._ff_install)
                rv &= path_remove(pkg._ff_post)
            elif self.opts.pkg_action == PkgAction.REINSTALL:
                rv &= path_remove(pkg._ff_install)
                rv &= path_remove(pkg._ff_post)

        return rv

    def _get_package_names(self, conf_point, settings):
        """
        acquire list of project package names to process

        From a dictionary of user-defined settings, extract the known list of
        package names from the package configuration key ``ConfKey.PKGS``. This
        method will return a (duplicate-removed) list of packages (if any) to be
        processed.

        Args:
            conf_point: the configuration file used to pull package names
            settings: user settings to pull package information from

        Returns:
            list of package names to be processed; empty or ``None`` if no
            packages exist or an issue has occurred when attempting to extract
            package names
        """
        pkg_names = []
        bad_pkgs_value = False

        if ConfKey.PKGS in settings:
            pkg_names = interpret_seq(settings[ConfKey.PKGS], str)
            if pkg_names is None:
                bad_pkgs_value = True

        if bad_pkgs_value:
            err('''\
bad package list definition

The configuration file does not have a properly formed list of defined packages.
Ensure a package list exists with the string-based names of packages to be part
of the releng process:

    {}
        {} = ['liba', 'libb', 'libc']''', conf_point, ConfKey.PKGS)
        elif not pkg_names:
            raise RelengToolMissingPackagesError(conf_point, ConfKey.PKGS)
        else:
            # remove duplicates (but maintain pre-sorted ordered)
            pkg_names = OrderedDict.fromkeys(pkg_names)

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

        rv = True

        if gaction == GlobalAction.DISTCLEAN:
            verbose('removing cache directory')
            rv &= path_remove(self.opts.cache_dir)
            verbose('removing download directory')
            rv &= path_remove(self.opts.dl_dir)

        if gaction in (GlobalAction.MRPROPER, GlobalAction.DISTCLEAN):
            verbose('removing output directory')
            rv &= path_remove(self.opts.out_dir)

            verbose('removing file flags')
            if os.path.exists(self.opts.ff_devmode):
                if path_remove(self.opts.ff_devmode):
                    warn('development mode has been unconfigured')
                else:
                    rv = False
            if os.path.exists(self.opts.ff_local_srcs):
                if path_remove(self.opts.ff_local_srcs):
                    warn('local-sources mode has been unconfigured')
                else:
                    rv = False
        else:
            verbose('removing build directory')
            rv &= path_remove(self.opts.build_dir)
            verbose('removing host directory')
            rv &= path_remove(self.opts.host_dir)
            verbose('removing license directory')
            rv &= path_remove(self.opts.license_dir)
            verbose('removing staging directory')
            rv &= path_remove(self.opts.staging_dir)
            verbose('removing symbols directory')
            rv &= path_remove(self.opts.symbols_dir)
            verbose('removing target directory')
            rv &= path_remove(self.opts.target_dir)

        return rv

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

        # notify extensions that a post-build event has started
        with wd(self.opts.target_dir):
            self.registry.emit('post-build-started', env=env)

        RELENG_POST_BUILD_NAME = 'releng-tool-post-build'
        script_name = os.path.join(self.opts.root_dir, RELENG_POST_BUILD_NAME)
        build_script, postbuild_exists = opt_file(script_name)

        if not postbuild_exists:
            deprecated_posts = [
                'releng-post-build',
                'releng-post',
                'post.py',
            ]

            for deprecated_post in deprecated_posts:
                script_name = os.path.join(self.opts.root_dir, deprecated_post)
                build_script, postbuild_exists = opt_file(script_name)
                if os.path.isfile(build_script):
                    warn('using deprecated post-processing file {} -- switch '
                         'to {}.rt when possible',
                         os.path.basename(build_script),
                         RELENG_POST_BUILD_NAME)
                    break

        if postbuild_exists:
            verbose('performing post-processing (build)...')

            # ensure images directory exists (as the post-processing script will
            # most likely populate it)
            if not mkdir(self.opts.images_dir):
                return False

            if not run_script(build_script, env, subject='post-build'):
                return False

            verbose('post-processing (build) completed')

        # notify extensions that a post-build event has completed
        with wd(self.opts.target_dir):
            self.registry.emit('post-build-finished', env=env)

        return True

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

        # parse and populate development mode configuration
        devmode_changed = bool(opts.devmode)

        devmode_cfg = {}
        if os.path.exists(opts.ff_devmode):
            # if we have an empty file, assume this is an old "file flag"
            # for development mode -- if we are not in a configured
            # development mode, enable it now
            if os.stat(opts.ff_devmode).st_size == 0:
                if not devmode_changed:
                    opts.devmode = True
            else:
                with open(opts.ff_devmode) as f:
                    try:
                        devmode_cfg = json.load(f)
                        if not devmode_changed:
                            opts.devmode = devmode_cfg['mode']
                    except Exception as e:
                        # inform user of error, unless we are overwriting
                        if not devmode_changed:
                            err_flag = True
                            err('''\
failed to parse development mode file

The file used to track `--development` options cannot be read. It is
recommended to remove the file manually and reconfigure the environment
for any desired locally sourced packages.

     File: {}
    Error: {}''', opts.ff_devmode, e)

        if devmode_changed:
            # check if the user is unconfiguring this mode
            if opts.devmode in UNSET_VALUES:
                if os.path.exists(self.opts.ff_devmode):
                    path_remove(self.opts.ff_devmode)

                warn('development mode has been unconfigured')
                configured = True
            else:
                devmode_cfg['mode'] = opts.devmode

                try:
                    with open(opts.ff_devmode, 'w') as f:
                        json.dump(devmode_cfg, f, indent=4)

                        if opts.devmode is True:
                            dms = ''
                        else:
                            dms = f' ({opts.devmode})'

                        success('configured root for development mode' + dms)
                        configured = True
                except Exception as e:
                    err_flag = True
                    err('''\
failed to write development mode file

The file used to track `--development` options cannot be written to.

     File: {}
    Error: {}''', opts.ff_devmode, e)

        # parse and populate local sources configurations
        local_srcs_changed = bool(opts.local_srcs)

        if os.path.exists(opts.ff_local_srcs):
            # if we have an empty file, assume this is an old "file flag"
            # local sources configuration
            if os.stat(opts.ff_local_srcs).st_size == 0:
                if GBL_LSRCS not in opts.local_srcs:
                    opts.local_srcs[GBL_LSRCS] = None
            else:
                with open(opts.ff_local_srcs) as f:
                    try:
                        # cache any new local sources configurations, pull in
                        # the configure local sources content and apply any new
                        # configuration to the options
                        new_local_srcs = opts.local_srcs
                        opts.local_srcs = json.load(f)
                        opts.local_srcs.update(new_local_srcs)

                    # if we failed to load the file, assume this is an old
                    # "file flag" local sources configuration
                    except Exception as e:
                        # inform user of error, unless we are overwriting
                        if not local_srcs_changed:
                            err_flag = True
                            err('''\
failed to parse local sources file

The file used to track `--local-sources` options cannot be read. It is
recommended to remove the file manually and reconfigure the environment
for any desired locally sourced packages.

     File: {}
    Error: {}''', opts.ff_local_srcs, e)

        # check if the user is unconfiguring
        if local_srcs_changed:
            local_srcs_unconfigured = False

            # if an unset value is set to the "default" entry, we clear
            # all local-sources settings; as we want a `--local-sources unset`
            # set to be an easy unconfiguration event
            gbl_lsrcs = opts.local_srcs.get(GBL_LSRCS)
            if gbl_lsrcs in UNSET_VALUES:
                opts.local_srcs.clear()
                local_srcs_unconfigured = True
            else:
                for key in list(opts.local_srcs.keys()):
                    if opts.local_srcs[key] in UNSET_VALUES:
                        del opts.local_srcs[key]
                        local_srcs_unconfigured = True

            if local_srcs_unconfigured and not opts.local_srcs:
                if os.path.exists(self.opts.ff_local_srcs):
                    path_remove(self.opts.ff_local_srcs)

                warn('local-sources mode has been unconfigured')
                configured = True
                local_srcs_changed = False

        if local_srcs_changed:
            try:
                with open(opts.ff_local_srcs, 'w') as f:
                    json.dump(opts.local_srcs, f, indent=4)

                    log('[local sources configuration]')
                    for key, val in sorted(opts.local_srcs.items()):
                        if not val:
                            val = '<parent>' if key == GBL_LSRCS else '<unset>'

                        entry = val
                        if key != GBL_LSRCS and not os.path.exists(val):
                            entry += warn_wrap('  (path does not exist)')

                        log(' {}: {}', key, entry)

                    success('configured root for local-sources mode')
                    configured = True
            except Exception as e:
                err_flag = True
                err('''\
failed to write local sources file

The file used to track `--local-sources` options cannot be written to.

     File: {}
    Error: {}''', opts.ff_local_srcs, e)

        if err_flag:
            return False

        if configured:
            return True

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

        def notify_invalid_type(key, expected):
            err('''\
invalid configuration type provided

The configuration file defines a key with an unexpected type. Correct the
following key entry and re-try again.

    Key: {}
    Expected Type: {}''', key, expected)

        def notify_invalid_value(key, value, expected):
            err('''\
invalid configuration value provided

The configuration file defines a key with an unexpected value. Correct the
following key entry and re-try again.

    Key: {}
    Unknown value: {}
    Expected: {}''', key, value, expected)

        if ConfKey.CACHE_EXT_TRANSFORM in settings:
            cet = None
            if callable(settings[ConfKey.CACHE_EXT_TRANSFORM]):
                cet = settings[ConfKey.CACHE_EXT_TRANSFORM]
            if cet is None:
                notify_invalid_type(ConfKey.CACHE_EXT_TRANSFORM, 'callable')
                return False
            self.opts.cache_ext_transform = cet

        if ConfKey.DEFINTERN in settings:
            is_default_internal = settings[ConfKey.DEFINTERN]
            if not isinstance(is_default_internal, bool):
                notify_invalid_type(ConfKey.DEFINTERN, 'bool')
                return False
            self.opts.default_internal_pkgs = is_default_internal

        if ConfKey.DEF_DEV_IGNORE_CACHE in settings:
            default_dev_ignore_cache = settings[ConfKey.DEF_DEV_IGNORE_CACHE]
            if not isinstance(default_dev_ignore_cache, bool):
                notify_invalid_type(ConfKey.DEF_DEV_IGNORE_CACHE, 'bool')
                return False
            self.opts.default_dev_ignore_cache = default_dev_ignore_cache

        if ConfKey.ENVIRONMENT in settings:
            env = interpret_dict(settings[ConfKey.ENVIRONMENT], str)
            if env is None:
                notify_invalid_type(ConfKey.ENVIRONMENT, 'dict(str,str)')
                return False
            self.opts.environment.update(expand(env))

        if ConfKey.EXTRA_LEXCEPTS in settings:
            d = interpret_dict(settings[ConfKey.EXTRA_LEXCEPTS], str)
            if d is None:
                notify_invalid_type(ConfKey.EXTRA_LEXCEPTS, 'dict(str,str)')
                return False

            for key, val in d.items():
                self.opts.spdx['exceptions'][key] = {
                    'name': val,
                    'deprecated': False,
                }

        if ConfKey.EXTRA_LICENSES in settings:
            d = interpret_dict(settings[ConfKey.EXTRA_LICENSES], str)
            if d is None:
                notify_invalid_type(ConfKey.EXTRA_LICENSES, 'dict(str,str)')
                return False

            for key, val in d.items():
                self.opts.spdx['licenses'][key] = {
                    'name': val,
                    'deprecated': False,
                }

        if ConfKey.LICENSE_HEADER in settings:
            license_header = settings[ConfKey.LICENSE_HEADER]
            if not isinstance(license_header, str):
                notify_invalid_type(ConfKey.LICENSE_HEADER, 'str')
                return False
            self.opts.license_header = license_header

        if ConfKey.OVERRIDE_REV in settings:
            orz = interpret_dict(settings[ConfKey.OVERRIDE_REV], str)
            if orz is None:
                notify_invalid_type(ConfKey.OVERRIDE_REV, 'dict(str,str)')
                return False
            self.opts.revision_override = orz
            if self.opts.revision_override:
                warn('configuration "{}" is deprecated', ConfKey.OVERRIDE_REV)

        if ConfKey.OVERRIDE_SITES in settings:
            v = interpret_dict(settings[ConfKey.OVERRIDE_SITES], str)
            if v is None:
                notify_invalid_type(ConfKey.OVERRIDE_SITES, 'dict(str,str)')
                return False
            self.opts.sites_override = v
            if self.opts.sites_override:
                warn('configuration "{}" is deprecated', ConfKey.OVERRIDE_SITES)

        if ConfKey.OVERRIDE_TOOLS in settings:
            v = interpret_dict(settings[ConfKey.OVERRIDE_TOOLS], str)
            if v is None:
                notify_invalid_type(ConfKey.OVERRIDE_TOOLS, 'dict(str,str)')
                return False
            self.opts.extract_override = v

        if ConfKey.PREREQUISITES in settings:
            prerequisites = interpret_seq(settings[ConfKey.PREREQUISITES], str)
            if prerequisites is None:
                notify_invalid_type(ConfKey.PREREQUISITES, 'str or list(str)')
                return False
            self.opts.prerequisites.extend(prerequisites)

        if ConfKey.QUIRKS in settings:
            quirks = interpret_seq(settings[ConfKey.QUIRKS], str)
            if quirks is None:
                notify_invalid_type(ConfKey.QUIRKS, 'str or list(str)')
                return False
            self.opts.quirks.extend(quirks)
            for quirk in quirks:
                verbose('configuration quirk applied: ' + quirk)

        if ConfKey.SBOM_FORMAT in settings:
            sbom_format = interpret_seq(settings[ConfKey.SBOM_FORMAT], str)
            if sbom_format is None:
                notify_invalid_type(ConfKey.SBOM_FORMAT, 'str or list(str)')
                return False
            for entry in sbom_format:
                if entry not in SbomFormatType:
                    notify_invalid_value(
                        ConfKey.SBOM_FORMAT,
                        entry,
                        ', '.join([
                            x for x in SbomFormatType
                            if x != SbomFormatType.RDP_SPDX],
                        ),
                    )
                    return False
            if not self.opts.sbom_format:
                self.opts.sbom_format = sbom_format

        if ConfKey.SYSROOT_PREFIX in settings:
            sysroot_prefix = settings[ConfKey.SYSROOT_PREFIX]
            if not isinstance(sysroot_prefix, str):
                notify_invalid_type(ConfKey.SYSROOT_PREFIX, 'str')
                return False
            if not sysroot_prefix.startswith('/'):
                sysroot_prefix = '/' + sysroot_prefix
            self.opts.sysroot_prefix = sysroot_prefix

        if ConfKey.URL_MIRROR in settings:
            url_mirror = settings[ConfKey.URL_MIRROR]
            if not isinstance(url_mirror, str):
                notify_invalid_type(ConfKey.URL_MIRROR, 'str')
                return False
            self.opts.url_mirror = url_mirror

        if ConfKey.URLOPEN_CONTEXT in settings:
            urlopen_context = None
            if isinstance(settings[ConfKey.URLOPEN_CONTEXT], ssl.SSLContext):
                urlopen_context = settings[ConfKey.URLOPEN_CONTEXT]
            if urlopen_context is None:
                notify_invalid_type(ConfKey.URLOPEN_CONTEXT, 'ssl.SSLContext')
                return False
            self.opts.urlopen_context = urlopen_context

        if ConfKey.VSDEVCMD in settings:
            vsdevcmd = settings[ConfKey.VSDEVCMD]
            if not isinstance(vsdevcmd, (bool, str)):
                notify_invalid_type(ConfKey.VSDEVCMD, 'bool or str')
                return False
            self.opts.vsdevcmd = vsdevcmd

        if ConfKey.VSDEVCMD_PRODUCTS in settings:
            vsdevcmd_products = settings[ConfKey.VSDEVCMD_PRODUCTS]
            if not isinstance(vsdevcmd_products, str):
                notify_invalid_type(ConfKey.VSDEVCMD_PRODUCTS, 'str')
                return False
            self.opts.vsdevcmd_products = vsdevcmd

        if ConfKey.EXTEN_PKGS in settings:
            epd = interpret_seq(settings[ConfKey.EXTEN_PKGS], str)
            if epd is None:
                notify_invalid_type(ConfKey.EXTEN_PKGS, 'str or list(str)')
                return False
            self.opts.extern_pkg_dirs = epd

        ext_names = []
        if ConfKey.EXTENSIONS in settings:
            ext_names = interpret_seq(settings[ConfKey.EXTENSIONS], str)
            if ext_names is None:
                notify_invalid_type(ConfKey.EXTENSIONS, 'str or list(str)')
                return False

        self.registry.load_all_extensions(ext_names)
        return True
