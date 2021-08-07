# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from releng_tool.defs import GlobalAction
from releng_tool.defs import PkgAction
import multiprocessing
import os

# default directory/file paths
DEFAULT_BUILD_DIR    = 'build'     #: default build container directory
DEFAULT_CACHE_DIR    = 'cache'     #: default cache container directory
DEFAULT_DL_DIR       = 'dl'        #: default download container directory
DEFAULT_HOST_DIR     = 'host'      #: default host container directory
DEFAULT_IMAGES_DIR   = 'images'    #: default images container directory
DEFAULT_LICENSE_DIR  = 'licenses'  #: default licenses container directory
DEFAULT_OUTPUT_DIR   = 'output'    #: default output container directory
DEFAULT_PKG_DIR      = 'package'   #: default package container directory
DEFAULT_STAGING_DIR  = 'staging'   #: default staging container directory
DEFAULT_SYMBOLS_DIR  = 'symbols'   #: default symbols container directory
DEFAULT_TARGET_DIR   = 'target'    #: default target container directory

# default directory/file paths
RELENG_CONF_EXTENDED_NAME = '.releng-tool' #: extended configuration script
RELENG_CONF_NAME = 'releng' #: configuration script filename
RELENG_CONF_OVERRIDES_NAME = 'releng-overrides' #: conf. overrides filename
RELENG_POST_NAME = 'releng-post' #: post script filename
FF_PREFIX = '.releng-flag-' #: prefix for all file flags
FF_DEVMODE_NAME = 'devmode' #: postfix for development mode file flag
FF_LOCALSRCS_NAME = 'local-sources' #: postfix for local sources mode file flag

# default other
DEFAULT_SYSROOT_PREFIX = os.sep + 'usr' #: default system root prefix

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
        build_dir: directory container for all builds
        cache_dir: directory container for cache (vcs bare sources)
        cache_ext_transform: transform for cache extension from site path
        conf_point: releng project's configuration
        conf_point_overrides: releng project's configuration overrides
        debug: whether or not debug messages are shown
        default_internal_pkgs: whether or not packages are implicitly internal
        default_pkg_dir: default package directory
        devmode: whether or not development mode is enabled
        dl_dir: directory container for download (archives)
        extern_pkg_dirs: external package directories (if any)
        extract_override: dictionary to override extraction commands
        ff_devmode: the file flag path for development mode detection
        ff_local_srcs: the file flag path for local sources mode detection
        forward_args: command line arguments forwarded to configuration script
        gbl_action: the specific global-action to perform (if any)
        host_dir: directory container for host tools
        images_dir: directory container for (final) images
        jobs: number of calculated jobs to allow at a given time
        jobsconf: number of jobs to allow at a given time (0: auto)
        license_dir: directory container for license information
        license_header: header content for a generated license file (if any)
        local_srcs: whether or not local sources are used
        no_color_out: whether or not colored messages are shown
        out_dir: directory container for all output data
        pkg_action: the specific package-action to perform (if any)
        post_point: resource to process holding a releng project's post-work
        prerequisites: list of required host tools (if any)
        quirks: advanced configuration quirks for the running instance
        revision_override: dictionary to override revision values
        root_dir: directory container for all (configuration, output, etc.)
        sites_override: dictionary to override site values
        staging_dir: directory container for staged content
        symbols_dir: directory container for symbols content
        sysroot_prefix: system root prefix
        target_action: the specific package to work on (if any)
        target_dir: directory container for target content
        url_mirror: mirror base site for url fetches
        verbose: whether or not verbose messages are shown
    """
    def __init__(self, args=None, forward_args=None):
        self.build_dir = None
        self.cache_dir = None
        self.cache_ext_transform = None
        self.conf_point = None
        self.conf_point_overrides = None
        self.debug = False
        self.default_internal_pkgs = False
        self.default_pkg_dir = None
        self.devmode = None
        self.dl_dir = None
        self.extern_pkg_dirs = []
        self.extract_override = None
        self.ff_devmode = None
        self.ff_local_srcs = None
        self.forward_args = forward_args
        self.gbl_action = GlobalAction.UNKNOWN
        self.host_dir = None
        self.images_dir = None
        self.jobs = 1
        self.jobsconf = 0
        self.license_dir = None
        self.license_header = None
        self.local_srcs = None
        self.no_color_out = False
        self.out_dir = None
        self.pkg_action = PkgAction.UNKNOWN
        self.post_point = None
        self.prerequisites = []
        self.quirks = []
        self.revision_override = None
        self.root_dir = None
        self.sites_override = None
        self.staging_dir = None
        self.symbols_dir = None
        self.sysroot_prefix = DEFAULT_SYSROOT_PREFIX
        self.target_action = None
        self.target_dir = None
        self.url_mirror = None
        self.verbose = False

        if args:
            self._handle_arguments(args)
        self._finalize_options()

    def _handle_arguments(self, args):
        """
        handle argparse-processed arguments to populate engine options

        Accepts the result of an argparse's parsed arguments and updates
        engine options with respective argument options.

        Args:
            args: the arguments
        """
        if args.cache_dir:
            self.cache_dir = os.path.abspath(args.cache_dir)
        if args.dl_dir:
            self.dl_dir = os.path.abspath(args.dl_dir)
        if args.out_dir:
            self.out_dir = os.path.abspath(args.out_dir)
        if args.root_dir:
            self.root_dir = os.path.abspath(args.root_dir)

        self.debug = args.debug
        self.jobs = self.jobsconf = args.jobs
        self.no_color_out = args.nocolorout
        self.verbose = args.verbose

        if args.development:
            self.devmode = True
        if args.local_sources:
            self.local_srcs = True
        if args.quirk:
            self.quirks.extend(args.quirk)

        if args.action:
            action_val = args.action.upper().replace('-', '_')
            if action_val in GlobalAction.__members__:
                self.gbl_action = GlobalAction[action_val]
            else:
                for subaction_val in PkgAction.__members__:
                    if action_val.endswith('_' + subaction_val):
                        self.pkg_action = PkgAction[subaction_val]
                        idx = action_val.rindex(subaction_val) - 1
                        self.target_action = args.action[:idx]
                        break

                if self.pkg_action == PkgAction.UNKNOWN:
                    self.target_action = args.action

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
        if not self.conf_point:
            self.conf_point = join(root, RELENG_CONF_NAME)
        if not self.conf_point_overrides:
            self.conf_point_overrides = join(root, RELENG_CONF_OVERRIDES_NAME)
        if not self.ff_devmode:
            self.ff_devmode = join(root, FF_PREFIX + FF_DEVMODE_NAME)
        if not self.ff_local_srcs:
            self.ff_local_srcs = join(root, FF_PREFIX + FF_LOCALSRCS_NAME)
        if not self.post_point:
            self.post_point = join(root, RELENG_POST_NAME)

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
            self.jobs = multiprocessing.cpu_count()
