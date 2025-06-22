# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import GBL_LSRCS
from releng_tool.defs import GlobalAction
from releng_tool.defs import PkgAction
from releng_tool.defs import UNSET_VALUES
from releng_tool.util.string import normalize
import contextlib
import multiprocessing
import os
import re
import sys

# default directory/file paths
DEFAULT_BUILD_DIR = 'build'       # default build container directory
DEFAULT_CACHE_DIR = 'cache'       # default cache container directory
DEFAULT_DL_DIR = 'dl'             # default download container directory
DEFAULT_HOST_DIR = 'host'         # default host container directory
DEFAULT_IMAGES_DIR = 'images'     # default images container directory
DEFAULT_LICENSE_DIR = 'licenses'  # default licenses container directory
DEFAULT_OUTPUT_DIR = 'output'     # default output container directory
DEFAULT_PKG_DIR = 'package'       # default package container directory
DEFAULT_STAGING_DIR = 'staging'   # default staging container directory
DEFAULT_SYMBOLS_DIR = 'symbols'   # default symbols container directory
DEFAULT_TARGET_DIR = 'target'     # default target container directory

# default directory/file paths
RELENG_CONF_EXTENDED_NAME = '.releng-tool'       # extended conf. script
RELENG_CONF_NAME = 'releng-tool'                 # conf. script filename
RELENG_CONF_OVERRIDES_NAME = 'releng-overrides'  # conf. overrides filename
FF_PREFIX = '.releng-flag-'          # prefix for all file flags
FF_DEVMODE_NAME = 'devmode'          # postfix for development mode file flag
FF_LOCALSRCS_NAME = 'local-sources'  # postfix for local sources mode file flag

# default sysroot prefix
if sys.platform == 'win32':
    DEFAULT_SYSROOT_PREFIX = ''
else:
    DEFAULT_SYSROOT_PREFIX = os.sep + 'usr'


class RelengEngineOptions:
    """
    engine options

    Configuration options to be passed into an engine instance.

    Args:
        args (optional): handle user-provided configuration options (argparse)
            and apply them to respective attributes
        forward_args (optional): handle arguments provided by the user which can
            be forwarded to the releng-tool project's configuration

    Attributes:
        assets_dir: directory container for cache/download directories
        build_dir: directory container for all builds
        cache_dir: directory container for cache (vcs bare sources)
        cache_ext_transform: transform for cache extension from site path
        conf_point: releng project's configuration
        conf_point_overrides: releng project's configuration overrides
        debug: whether or not debug messages are shown
        debug_extended: whether extended debug mode is enabled
        default_dev_ignore_cache: default flag state for devmode ignore cache
        default_internal_pkgs: whether or not packages are implicitly internal
        default_pkg_dir: default package directory
        devmode: whether or not development mode is enabled
        dl_dir: directory container for download (archives)
        environment: environment options to apply
        extern_pkg_dirs: external package directories (if any)
        extract_override: dictionary to override extraction commands
        ff_devmode: the file flag path for development mode detection
        ff_local_srcs: the file flag path for local sources mode detection
        force: whether or not the force flag is set
        forward_args: command line arguments forwarded to configuration script
        gbl_action: the specific global-action to perform (if any)
        host_dir: directory container for host tools
        images_dir: directory container for (final) images
        injected_kv: injected key-value entries for script/env context
        jobs: number of calculated jobs to allow at a given time
        jobsconf: number of jobs to allow at a given time (0: auto)
        license_dir: directory container for license information
        license_header: header content for a generated license file (if any)
        local_srcs: dictionary of local source configurations
        no_color_out: whether or not colored messages are shown
        only_mirror: require mirror for external packages
        out_dir: directory container for all output data
        pkg_action: the specific package-action to perform (if any)
        prerequisites: list of required host tools (if any)
        profiles: the active profiles for this run
        quirks: advanced configuration quirks for the running instance
        revision_override: dictionary to override revision values
        root_dir: directory container for all (configuration, output, etc.)
        sbom_format: format(s) to use for sbom generation
        sites_override: dictionary to override site values
        spdx: spdx license database
        staging_dir: directory container for staged content
        symbols_dir: directory container for symbols content
        sysroot_prefix: system root prefix
        target_action: the specific package to work on (if any)
        target_action_exec: package-specific executable command (if any)
        target_dir: directory container for target content
        url_mirror: mirror base site for url fetches
        urlopen_context: context to apply for all url open calls
        verbose: whether or not verbose messages are shown
        vsdevcmd: configuration for loading vsdevcmd environment variables
        vsdevcmd_products: vswhere products to search for
    """
    def __init__(self, args=None, forward_args=None):
        self.assets_dir = None
        self.build_dir = None
        self.cache_dir = None
        self.cache_ext_transform = None
        self.conf_point = None
        self.conf_point_overrides = None
        self.debug = False
        self.debug_extended = False
        self.default_dev_ignore_cache = None
        self.default_internal_pkgs = False
        self.default_pkg_dir = None
        self.devmode = None
        self.dl_dir = None
        self.environment = {}
        self.extern_pkg_dirs = []
        self.extract_override = None
        self.ff_devmode = None
        self.ff_local_srcs = None
        self.force = False
        self.forward_args = forward_args
        self.gbl_action = None
        self.host_dir = None
        self.images_dir = None
        self.injected_kv = {}
        self.jobs = 1
        self.jobsconf = 0
        self.license_dir = None
        self.license_header = None
        self.local_srcs = {}
        self.no_color_out = False
        self.only_mirror = False
        self.out_dir = None
        self.pkg_action = None
        self.prerequisites = []
        self.profiles = []
        self.quirks = []
        self.revision_override = None
        self.root_dir = None
        self.sbom_format = []
        self.sites_override = None
        self.spdx = {}
        self.staging_dir = None
        self.symbols_dir = None
        self.sysroot_prefix = DEFAULT_SYSROOT_PREFIX
        self.target_action = None
        self.target_action_exec = None
        self.target_dir = None
        self.url_mirror = None
        self.urlopen_context = None
        self.verbose = False
        self.vsdevcmd = None
        self.vsdevcmd_products = None

        # default have an empty license/exception entries, until SPDX data
        # is loaded into the options
        self.spdx['exceptions'] = {}
        self.spdx['licenses'] = {}

        if args:
            self._handle_arguments(args)
        self._handle_environment_opts()
        self._finalize_options()

    def _handle_arguments(self, args):
        """
        handle argparse-processed arguments to populate engine options

        Accepts the result of an argparse's parsed arguments and updates
        engine options with respective argument options.

        Args:
            args: the arguments
        """
        if args.assets_dir:
            self.assets_dir = os.path.abspath(args.assets_dir)
        if args.cache_dir:
            self.cache_dir = os.path.abspath(args.cache_dir)
        if args.dl_dir:
            self.dl_dir = os.path.abspath(args.dl_dir)
        if args.images_dir:
            self.images_dir = os.path.abspath(args.images_dir)
        if args.out_dir:
            self.out_dir = os.path.abspath(args.out_dir)
        elif args.output_dir:
            self.out_dir = os.path.abspath(args.output_dir)
        if args.root_dir:
            self.root_dir = os.path.abspath(args.root_dir)

        self.conf_point = args.config
        self.debug = args.debug
        self.debug_extended = args.debug_extended
        self.force = args.force
        self.jobs = self.jobsconf = (args.jobs or 0)
        self.no_color_out = args.nocolorout
        self.only_mirror = args.only_mirror
        self.verbose = args.verbose

        if args.development:
            self.devmode = args.development
        if args.injected_kv:
            self.injected_kv = args.injected_kv
        if args.sbom_format:
            self.sbom_format = args.sbom_format

        # add any new profile entries
        if args.profile:
            for entry in args.profile:
                for subentry in re.split(',|;', entry):
                    profile = normalize(subentry)
                    if profile not in self.profiles:
                        self.profiles.append(profile)

        # add any new quirks
        if args.quirk:
            for entry in args.quirk:
                quirk = entry.strip()
                if quirk not in self.quirks:
                    self.quirks.append(quirk)

        # cycle through the provided local source arguments to configure
        # global and package-specific local sources modes; we use the `:`/`@`
        # character to indicate module-specific paths, which if the trailing
        # portion is empty being an indicate to not fetch the specific
        # package locally; note that `local_src_ref` may be set to `None`,
        # which is a special indication to activate for local sources mode,
        # but we are targeting "default" paths found in the folder/container
        # of the configured root path (the "original" local sources mode)
        if args.local_sources:
            for local_src_ref in args.local_sources:
                module = GBL_LSRCS
                path = local_src_ref

                # if an absolute path is provided, just use it for the path;
                # avoiding the need to check/extract for a module-specific
                # path, as well as preventing path extraction issues on win32
                # with drive prefix values (that use `:`)
                if path and os.path.isabs(path):
                    pass
                elif path and any(sep in path for sep in [':', '@']):
                    module, path = re.split(':|@', path, maxsplit=1)

                    # path provided in a shell environment may not resolve
                    # `~` when prefixed with the leading `<pkg>@` hint;
                    # attempt to expand a user hint after extracting the path
                    path = os.path.expanduser(path)

                # acquire the absolute path for the part, to prevent
                # issues associated with the path if the working directory
                # changes (ignoring unset values)
                if path and path not in UNSET_VALUES:
                    path = os.path.abspath(path)

                # remove any package-prefix on a module to allow users to
                # easily use shell completion to populate packages when
                # populating a local-sources argument on the command line
                module = module\
                    .replace(os.sep, '/') \
                    .removeprefix(f'{DEFAULT_PKG_DIR}/')

                self.local_srcs[module] = path if path else None

        if args.action:
            action_val = args.action.lower().replace('-', '_')
            if action_val in GlobalAction:
                self.gbl_action = action_val
            else:
                target_action = None

                for subaction_val in PkgAction:
                    if action_val.endswith('_' + subaction_val):
                        self.pkg_action = subaction_val
                        idx = action_val.rindex(subaction_val) - 1
                        target_action = args.action[:idx]
                        break

                if self.pkg_action == PkgAction.EXEC:
                    if args.action_exec:
                        self.target_action_exec = args.action_exec
                    elif self.forward_args:
                        self.target_action_exec = self.forward_args
                elif not self.pkg_action:
                    target_action = args.action

                # if a provided action starts with a "package/" prefix
                # (a result of shell completion of users looking for a
                #  specific packaging in the file system), strip the
                # package folder prefix and use the resulting value as
                # the target
                target_action = target_action\
                    .replace(os.sep, '/') \
                    .removeprefix(f'{DEFAULT_PKG_DIR}/')

                self.target_action = target_action

    def _handle_environment_opts(self):
        """
        handle environment variables to populate engine options

        Configure various options which support assignment from an
        environment variable.
        """

        if not self.assets_dir:
            self.assets_dir = os.environ.get('RELENG_ASSETS_DIR')
        if not self.cache_dir:
            self.cache_dir = os.environ.get('RELENG_CACHE_DIR')
        if not self.dl_dir:
            self.dl_dir = os.environ.get('RELENG_DL_DIR')
        if not self.images_dir:
            self.images_dir = os.environ.get('RELENG_IMAGES_DIR')
        if not self.out_dir:
            self.out_dir = os.environ.get('RELENG_OUTPUT_DIR')

        if not self.jobs and 'RELENG_PARALLEL_LEVEL' in os.environ:
            with contextlib.suppress(ValueError):
                self.jobs = int(os.environ.get('RELENG_PARALLEL_LEVEL'))

    def _finalize_options(self):
        """
        finalize all engine options for use

        Ensures all options are properly configured to expected values to ensure
        default values are set which may depend on other currently provided
        options.
        """
        if not self.root_dir:
            self.root_dir = os.getcwd()

        join = os.path.join
        root = self.root_dir

        # asset container
        if self.assets_dir:
            if not self.cache_dir:
                self.cache_dir = join(self.assets_dir, DEFAULT_CACHE_DIR)
            if not self.dl_dir:
                self.dl_dir = join(self.assets_dir, DEFAULT_DL_DIR)

        # special output directory override
        if not self.out_dir:
            container_dir = os.environ.get('RELENG_GLOBAL_OUTPUT_CONTAINER_DIR')
            if container_dir:
                project_folder = os.path.basename(root)
                self.out_dir = join(container_dir, project_folder)

        # root container
        if not self.cache_dir:
            self.cache_dir = join(root, DEFAULT_CACHE_DIR)
        if not self.default_pkg_dir:
            self.default_pkg_dir = join(root, DEFAULT_PKG_DIR)
        if not self.dl_dir:
            self.dl_dir = join(root, DEFAULT_DL_DIR)
        if not self.out_dir:
            self.out_dir = join(root, DEFAULT_OUTPUT_DIR)

        # output container
        if not self.build_dir:
            self.build_dir = join(self.out_dir, DEFAULT_BUILD_DIR)
        if not self.host_dir:
            self.host_dir = join(self.out_dir, DEFAULT_HOST_DIR)
        if not self.images_dir:
            self.images_dir = join(self.out_dir, DEFAULT_IMAGES_DIR)
        if not self.license_dir:
            self.license_dir = join(self.out_dir, DEFAULT_LICENSE_DIR)
        if not self.staging_dir:
            self.staging_dir = join(self.out_dir, DEFAULT_STAGING_DIR)
        if not self.symbols_dir:
            self.symbols_dir = join(self.out_dir, DEFAULT_SYMBOLS_DIR)
        if not self.target_dir:
            self.target_dir = join(self.out_dir, DEFAULT_TARGET_DIR)

        # files
        if not self.conf_point_overrides:
            self.conf_point_overrides = join(root, RELENG_CONF_OVERRIDES_NAME)
        if not self.ff_devmode:
            self.ff_devmode = join(root, FF_PREFIX + FF_DEVMODE_NAME)
        if not self.ff_local_srcs:
            self.ff_local_srcs = join(root, FF_PREFIX + FF_LOCALSRCS_NAME)

        # provided fixed job count with auto-configuration (value: 0)
        #
        # The option ``jobsconf`` defines the number of jobs the user wants to
        # use for the process. When providing this information to tools, a value
        # of zero allows a tool to configure its own automatic parallel
        # processing. In some scenarios, a tool may not provide the ability to
        # automatically determine job count to use. For these cases, the value
        # ``jobs`` can be used which either be a value matching ``jobsconf`` if
        # non-zero, or the value will be a non-zero value matching the CPU count
        # of the running system.
        if not self.jobs:
            try:
                # if `sched_getaffinity` is available, use the call the acquire
                # the number of physical cores on the system
                self.jobs = len(os.sched_getaffinity(0))
            except AttributeError:
                # if we cannot guarantee the number of physical cores, make an
                # assumption that the physical core count is half of the
                # (possible logical) core count provided by `cpu_count`
                cpu_count = multiprocessing.cpu_count()
                fuzzy_phy_cores = max(int(cpu_count / 2), 1)
                self.jobs = fuzzy_phy_cores
