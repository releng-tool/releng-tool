# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from releng_tool.util.enum import Enum

# configuration file keys
CONF_KEY_CACHE_EXT_TRANSFORM = 'cache_ext' #: cache extension transform
CONF_KEY_DEFINTERN = 'default_internal' #: packages are internal (implicitly)
CONF_KEY_EXTENSIONS = 'extensions' #: project releng-extension list
CONF_KEY_EXTEN_PKGS = 'external_packages' #: project external packages list
CONF_KEY_LICENSE_HEADER = 'license_header' #: license header information
CONF_KEY_OVERRIDE_REV = 'override_revisions' #: revision overriding dictionary
CONF_KEY_OVERRIDE_SITES = 'override_sites' #: site overriding dictionary
CONF_KEY_OVERRIDE_TOOLS = 'override_extract_tools' #: extract-tool overriding
CONF_KEY_PKGS = 'packages' #: project's package (name) list
CONF_KEY_PREREQUISITES = 'prerequisites' #: project's host-tool prerequisites
CONF_KEY_QUIRKS = 'quirks' #: configure quirks to apply
CONF_KEY_SYSROOT_PREFIX = 'sysroot_prefix' #: project's default sys-root prefix
CONF_KEY_URL_MIRROR = 'url_mirror' #: mirror base site for url fetches

# releng package keys (postfixes)
RPK_BUILD_SUBDIR = 'BUILD_SUBDIR' #: sub-directory in fetched to find root src
RPK_DEPS = 'DEPENDENCIES' #: list of package dependencies
RPK_DEVMODE_IGNORE_CACHE = 'DEVMODE_IGNORE_CACHE' #: whether or not ignore cache
RPK_DEVMODE_REVISION = 'DEVMODE_REVISION' #: devmode-rev to acquire from srcs
RPK_EXTENSION = 'EXTENSION' #: filename extension for package (if needed)
RPK_EXTERNAL = 'EXTERNAL' #: whether or not package is considered "external"
RPK_EXTOPT = 'EXTOPT' #: extension-defined package modifiers (if any)
RPK_EXTRACT_TYPE = 'EXTRACT_TYPE' #: extraction type for sources
RPK_FIXED_JOBS = 'FIXED_JOBS' #: fixed job count for the project
RPK_GIT_CONFIG = 'GIT_CONFIG' #: git configurations to set (if any)
RPK_GIT_DEPTH = 'GIT_DEPTH' #: git fetch depth (if any)
RPK_GIT_REFSPECS = 'GIT_REFSPECS' #: additional git refspecs to fetch (if any)
RPK_GIT_SUBMODULES = 'GIT_SUBMODULES' #: fetch any submodules (if any)
RPK_INSTALL_TYPE = 'INSTALL_TYPE' #: install container target for the package
RPK_INTERNAL = 'INTERNAL' #: whether or not package is considered "internal"
RPK_LICENSE = 'LICENSE' #: license information for the package
RPK_LICENSE_FILES = 'LICENSE_FILES' #: source file(s) with license information
RPK_NO_EXTRACTION = 'NO_EXTRACTION' #: whether or not package extraction is done
RPK_PREFIX = 'PREFIX' #: system root prefix override (if needed)
RPK_REVISION = 'REVISION' #: revision to acquire from sources (if any)
RPK_SITE = 'SITE' #: site where to fetch package sources
RPK_SKIP_REMOTE_CONFIG = 'SKIP_REMOTE_CONFIG' #: skip any remote configuration
RPK_SKIP_REMOTE_SCRIPTS = 'SKIP_REMOTE_SCRIPTS' #: skip any remote scripts
RPK_STRIP_COUNT = 'STRIP_COUNT' #: strip count for archive extract
RPK_TYPE = 'TYPE' #: type of project the package is
RPK_VCS_TYPE = 'VCS_TYPE' #: type of project the package's fetch source is
RPK_VERSION = 'VERSION' #: the version of the package
# (package type - common)
RPK_CONF_DEFS = 'CONF_DEFS' #: package-type configuration definitions
RPK_CONF_ENV = 'CONF_ENV' #: package-type configuration environment values
RPK_CONF_OPTS = 'CONF_OPTS' #: package-type configuration options
RPK_BUILD_DEFS = 'BUILD_DEFS' #: package-type build definitions
RPK_BUILD_ENV = 'BUILD_ENV' #: package-type build environment values
RPK_BUILD_OPTS = 'BUILD_OPTS' #: package-type build options
RPK_INSTALL_DEFS = 'INSTALL_DEFS' #: package-type install definitions
RPK_INSTALL_ENV = 'INSTALL_ENV' #: package-type install environment values
RPK_INSTALL_OPTS = 'INSTALL_OPTS' #: package-type install options
# (package type - autotools)
RPK_AUTOTOOLS_AUTORECONF = 'AUTOTOOLS_AUTORECONF' #: autotools /w autoreconf
# (package type - python)
RPK_PYTHON_INTERPRETER = 'PYTHON_INTERPRETER' #: python interpreter

class GlobalAction(Enum):
    """
    specific stage action to perform

    A user can request a (global) action to perform over the default process.
    For example, a user can request to "fetch" and only the fetching stage will
    occur for registered packages.

    Attributes:
        CLEAN: clean the working state
        DISTCLEAN: pristine state clean with cache/dl clear
        EXTRACT: process all packages through extraction stage
        FETCH: process all packages through fetch stage
        INIT: initialize example structure
        LICENSES: generate license information for a project
        MRPROPER: pristine state clean (e.g. configurations)
        PATCH: process all packages through patch stage
    """
    CLEAN = 'clean'
    DISTCLEAN = 'distclean'
    EXTRACT = 'extract'
    FETCH = 'fetch'
    INIT = 'init'
    LICENSES = 'licenses'
    MRPROPER = 'mrproper'
    PATCH = 'patch'

class PkgAction(Enum):
    """
    package-specific stage action to perform

    A user can request a package action to perform over the default process.
    When a package-specific action is requested, the process will perform all
    dependencies for the target action's stage before completing the target
    stage. For example, a user can request to perform a package's "extract"
    stage, which will result in ensure the package's fetch stage is complete
    (and possibility other package dependencies) performing (and stopping after)
    the extraction stage.

    Attributes:
        BUILD: process a package till end of the build stage
        CLEAN: process a package till end of the clean stage
        CONFIGURE: process a package till end of the configure stage
        DISTCLEAN: pristine state clean state of the package with cache/dl clear
        EXTRACT: process a package till end of the extraction stage
        FETCH: process a package till end of the fetch stage
        INSTALL: process a package till end of the install stage
        PATCH: process a package till end of the patch stage
        REBUILD: perform a re-build of a package
        REBUILD_ONLY: perform a re-build of a package and stop
        RECONFIGURE: perform a re-configuration of a package
        RECONFIGURE_ONLY: perform a re-configuration of a package and stop
        REINSTALL: perform a re-install of a package
    """
    BUILD = 'build'
    CLEAN = 'clean'
    CONFIGURE = 'configure'
    DISTCLEAN = 'distclean'
    EXTRACT = 'extract'
    FETCH = 'fetch'
    INSTALL = 'install'
    PATCH = 'patch'
    REBUILD = 'rebuild'
    REBUILD_ONLY = 'rebuild_only'
    RECONFIGURE = 'reconfigure'
    RECONFIGURE_ONLY = 'reconfigure_only'
    REINSTALL = 'reinstall'

class PackageType(Enum):
    """
    package types

    Defines supported package types for deciding which method if configuring,
    building and installing is performed.

    Attributes:
        AUTOTOOLS: autotools-based package
        CMAKE: cmake-based package
        PYTHON: python-based package
        SCRIPT: releng script-based package
    """
    AUTOTOOLS = 'autotools'
    CMAKE = 'cmake'
    PYTHON = 'python'
    SCRIPT = 'script'

class PackageInstallType(Enum):
    """
    package install types

    Defines supported package installation types for deciding which the location
    to push resources during the installation phase.

    Attributes:
        HOST: install to the host container
        IMAGES: install to the images container
        STAGING: install to the staging container
        STAGING_AND_TARGET: install to the staging and target containers
        TARGET: install to the target container
    """
    HOST = 'host'
    IMAGES = 'images'
    STAGING = 'staging'
    STAGING_AND_TARGET = 'staging_and_target'
    TARGET = 'target'

class VcsType(Enum):
    """
    version control system types

    Defines supported version control system types for decided which fetching
    processing is used when acquiring resources.

    Attributes:
        CVS: concurrent versions system
        GIT: git
        HG: mercurial
        LOCAL: no version control (local interim-development package)
        NONE: no version control (placeholder package)
        SCP: secure copy
        SVN: subversion
        URL: url (http, https, ftp, file, etc.)
    """
    BZR = 'bzr'
    CVS = 'cvs'
    GIT = 'git'
    HG = 'hg'
    LOCAL = 'local'
    NONE = 'none'
    SCP = 'scp'
    SVN = 'svn'
    URL = 'url'
