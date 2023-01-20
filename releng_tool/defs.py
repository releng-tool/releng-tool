# -*- coding: utf-8 -*-
# Copyright 2018-2023 releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.util.enum import Enum


class ConfKey(Enum):
    """
    configuration file keys

    Defines a series of attributes which define every support project
    configuration key supported by this tool. Project configuration keys
    are in a lowercase format.

    Attributes:
        CACHE_EXT_TRANSFORM: cache extension transform
        DEFINTERN: packages are internal (implicitly)
        EXTENSIONS: project releng-extension list
        EXTEN_PKGS: project external packages list
        LICENSE_HEADER: license header information
        OVERRIDE_REV: revision overriding dictionary
        OVERRIDE_SITES: site overriding dictionary
        OVERRIDE_TOOLS: extract-tool overriding
        PKGS: project's package (name) list
        PREREQUISITES: project's host-tool prerequisites
        QUIRKS: configure quirks to apply
        SYSROOT_PREFIX: project's default sys-root prefix
        URL_MIRROR: mirror base site for url fetches
        URLOPEN_CONTEXT: context to use for urlopen
    """
    CACHE_EXT_TRANSFORM = 'cache_ext'
    DEFINTERN = 'default_internal'
    EXTENSIONS = 'extensions'
    EXTEN_PKGS = 'external_packages'
    LICENSE_HEADER = 'license_header'
    OVERRIDE_REV = 'override_revisions'
    OVERRIDE_SITES = 'override_sites'
    OVERRIDE_TOOLS = 'override_extract_tools'
    PKGS = 'packages'
    PREREQUISITES = 'prerequisites'
    QUIRKS = 'quirks'
    SYSROOT_PREFIX = 'sysroot_prefix'
    URL_MIRROR = 'url_mirror'
    URLOPEN_CONTEXT = 'urlopen_context'


class Rpk(Enum):
    """
    releng package keys (postfixes)

    Defines a series of attributes which define every support package
    configuration key supported by this tool. Package configuration keys
    are in an uppercase format.

    Attributes:
        BUILD_SUBDIR: sub-directory in fetched to find root src
        DEPS: list of package dependencies
        DEVMODE_IGNORE_CACHE: whether or not ignore cache
        DEVMODE_REVISION: devmode-rev to acquire from srcs
        EXTENSION: filename extension for package (if needed)
        EXTERNAL: whether or not package is considered "external"
        EXTOPT: extension-defined package modifiers (if any)
        EXTRACT_TYPE: extraction type for sources
        FETCH_OPTS: fetch options (if any)
        FIXED_JOBS: fixed job count for the project
        GIT_CONFIG: git configurations to set (if any)
        GIT_DEPTH: git fetch depth (if any)
        GIT_REFSPECS: additional git refspecs to fetch (if any)
        GIT_SUBMODULES: fetch any submodules (if any)
        GIT_VERIFY_REVISION: verify signed revisions
        HOST_PROVIDES: host tools the package will provide
        INSTALL_TYPE: install container target for the package
        INTERNAL: whether or not package is considered "internal"
        LICENSE: license information for the package
        LICENSE_FILES: source file(s) with license information
        NO_EXTRACTION: whether or not package extraction is done
        PREFIX: system root prefix override (if needed)
        REVISION: revision to acquire from sources (if any)
        SITE: site where to fetch package sources
        SKIP_REMOTE_CONFIG: skip any remote configuration
        SKIP_REMOTE_SCRIPTS: skip any remote scripts
        STRIP_COUNT: strip count for archive extract
        TYPE: type of project the package is
        VCS_TYPE: type of project the package's fetch source is
        VERSION: the version of the package
        # (package type - common)
        CONF_DEFS: package-type configuration definitions
        CONF_ENV: package-type configuration environment values
        CONF_OPTS: package-type configuration options
        BUILD_DEFS: package-type build definitions
        BUILD_ENV: package-type build environment values
        BUILD_OPTS: package-type build options
        INSTALL_DEFS: package-type install definitions
        INSTALL_ENV: package-type install environment values
        INSTALL_OPTS: package-type install options
        # (package type - autotools)
        AUTOTOOLS_AUTORECONF: autotools /w autoreconf
        # (package type - cmake)
        CMAKE_NOINSTALL: skip cmake install stage
        # (package type - make)
        MAKE_NOINSTALL: skip make install stage
        # (package type - python)
        PYTHON_INTERPRETER: python interpreter
        PYTHON_SETUP_TYPE: python setup type to build/install with
        # (package type - scons)
        SCONS_NOINSTALL: skip scons install stage
    """
    BUILD_SUBDIR = 'BUILD_SUBDIR'
    DEPS = 'DEPENDENCIES'
    DEVMODE_IGNORE_CACHE = 'DEVMODE_IGNORE_CACHE'
    DEVMODE_REVISION = 'DEVMODE_REVISION'
    EXTENSION = 'EXTENSION'
    EXTERNAL = 'EXTERNAL'
    EXTOPT = 'EXTOPT'
    EXTRACT_TYPE = 'EXTRACT_TYPE'
    FETCH_OPTS = 'FETCH_OPTS'
    FIXED_JOBS = 'FIXED_JOBS'
    GIT_CONFIG = 'GIT_CONFIG'
    GIT_DEPTH = 'GIT_DEPTH'
    GIT_REFSPECS = 'GIT_REFSPECS'
    GIT_SUBMODULES = 'GIT_SUBMODULES'
    GIT_VERIFY_REVISION = 'GIT_VERIFY_REVISION'
    HOST_PROVIDES = 'HOST_PROVIDES'
    INSTALL_TYPE = 'INSTALL_TYPE'
    INTERNAL = 'INTERNAL'
    LICENSE = 'LICENSE'
    LICENSE_FILES = 'LICENSE_FILES'
    NO_EXTRACTION = 'NO_EXTRACTION'
    PREFIX = 'PREFIX'
    REVISION = 'REVISION'
    SITE = 'SITE'
    SKIP_REMOTE_CONFIG = 'SKIP_REMOTE_CONFIG'
    SKIP_REMOTE_SCRIPTS = 'SKIP_REMOTE_SCRIPTS'
    STRIP_COUNT = 'STRIP_COUNT'
    TYPE = 'TYPE'
    VCS_TYPE = 'VCS_TYPE'
    VERSION = 'VERSION'
    # (package type - common)
    CONF_DEFS = 'CONF_DEFS'
    CONF_ENV = 'CONF_ENV'
    CONF_OPTS = 'CONF_OPTS'
    BUILD_DEFS = 'BUILD_DEFS'
    BUILD_ENV = 'BUILD_ENV'
    BUILD_OPTS = 'BUILD_OPTS'
    INSTALL_DEFS = 'INSTALL_DEFS'
    INSTALL_ENV = 'INSTALL_ENV'
    INSTALL_OPTS = 'INSTALL_OPTS'
    # (package type - autotools)
    AUTOTOOLS_AUTORECONF = 'AUTOTOOLS_AUTORECONF'
    # (package type - cmake)
    CMAKE_NOINSTALL = 'CMAKE_NOINSTALL'
    # (package type - make)
    MAKE_NOINSTALL = 'MAKE_NOINSTALL'
    # (package type - python)
    PYTHON_INTERPRETER = 'PYTHON_INTERPRETER'
    PYTHON_SETUP_TYPE = 'PYTHON_SETUP_TYPE'
    # (package type - scons)
    SCONS_NOINSTALL = 'SCONS_NOINSTALL'


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
        EXEC: perform an action in the package's directory
        EXTRACT: process a package till end of the extraction stage
        FETCH: process a package till end of the fetch stage
        INSTALL: process a package till end of the install stage
        LICENSE: generate license information for a package
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
    EXEC = 'exec'
    EXTRACT = 'extract'
    FETCH = 'fetch'
    INSTALL = 'install'
    LICENSE = 'license'
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
        MAKE: make-based package
        PYTHON: python-based package
        SCONS: scons-based package
        SCRIPT: releng script-based package
    """
    AUTOTOOLS = 'autotools'
    CMAKE = 'cmake'
    MAKE = 'make'
    PYTHON = 'python'
    SCONS = 'scons'
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


class PythonSetupType(Enum):
    """
    python setup types

    Defines supported Python setup types for deciding which method build and
    install commands/arguments are utilized.

    Attributes:
        DISTUTILS: distutils build packager
        FLIT: Flit build packager
        HATCH: Hatch build packager
        PDM: PDM build packager
        PEP517: pep517 build packager
        POETRY: Poetry build packager
        SETUPTOOLS: setuptools build packager
    """
    DISTUTILS = 'distutils'
    FLIT = 'flit'
    HATCH = 'hatch'
    PDM = 'pdm'
    PEP517 = 'pep517'
    POETRY = 'poetry'
    SETUPTOOLS = 'setuptools'


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
        RSYNC: secure copy
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
    RSYNC = 'rsync'
    SCP = 'scp'
    SVN = 'svn'
    URL = 'url'


# key used to track "global" local sources configuration
GBL_LSRCS = '*'
