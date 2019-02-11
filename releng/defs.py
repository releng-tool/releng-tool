#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from enum import Enum

# configuration file keys
CONF_KEY_CACHE_EXT_TRANSFORM = 'cache_ext' #: cache extension transform
CONF_KEY_DEFINTERN = 'default_internal' #: packages are internal (implicitly)
CONF_KEY_EXTENSIONS = 'extensions' #: project releng-extension list
CONF_KEY_EXTEN_PKGS = 'external_packages' #: project external packages list
CONF_KEY_LICENSE_HEADER = 'license_header' #: license header information
CONF_KEY_OVERRIDE_REV = 'override_revisions' #: revision overriding dictionary
CONF_KEY_OVERRIDE_SITES = 'override_sites' #: site overriding dictionary
CONF_KEY_OVERRIDE_TOOLS = 'override_tools' #: tool overriding dictionary
CONF_KEY_PKGS = 'packages' #: project's package (name) list
CONF_KEY_SYSROOT_PREFIX = 'sysroot_prefix' #: project's default sys-root prefix
CONF_KEY_URL_MIRROR = 'url_mirror' #: mirror base site for url fetches

# releng package keys (postfixes)
RPK_BUILD_SUBDIR = 'BUILD_SUBDIR' #: sub-directory in fetched to find root src
RPK_DEPS = 'DEPENDENCIES' #: list of package dependencies
RPK_DEVMODE_REVISION = 'DEVMODE_REVISION' #: devmode-rev to acquire from srcs
RPK_EXTENSION = 'EXTENSION' #: filename extension for package (if needed)
RPK_EXTERNAL = 'EXTERNAL' #: whether or not package is considered "external"
RPK_EXTOPT = 'EXTOPT' #: extension-defined package modifiers (if any)
RPK_EXTRACT_TYPE = 'EXTRACT_TYPE' #: extraction type for sources
RPK_FIXED_JOBS = 'FIXED_JOBS' #: fixed job count for the project
RPK_INSTALL_TYPE = 'INSTALL_TYPE' #: install container target for the package
RPK_INTERNAL = 'INTERNAL' #: whether or not package is considered "internal"
RPK_LICENSE = 'LICENSE' #: license information for the package
RPK_LICENSE_FILES = 'LICENSE_FILES' #: source file(s) with license information
RPK_PREFIX = 'PREFIX' #: system root prefix override (if needed)
RPK_REVISION = 'REVISION' #: revision to acquire from sources (if any)
RPK_SITE = 'SITE' #: site where to fetch package sources
RPK_STRIP_COUNT = 'STRIP_COUNT' #: strip count for archive extract
RPK_TYPE = 'TYPE' #: type of project the package is
RPK_VCS_TYPE = 'VCS_TYPE' #: type of project the package's fetch source is
RPK_VERSION = 'VERSION' #: the version of the package
# (other - autotools)
RPK_AUTOTOOLS_AUTORECONF = 'AUTOTOOLS_AUTORECONF' #: autotools /w autoreconf
RPK_AUTOTOOLS_CONF_ENV = 'AUTOTOOLS_CONF_ENV' #: autotools conf env. values
RPK_AUTOTOOLS_CONF_OPTS = 'AUTOTOOLS_CONF_OPTS' #: autotools conf. options
RPK_AUTOTOOLS_ENV = 'AUTOTOOLS_ENV' #: autotools environment values
RPK_AUTOTOOLS_INSTALL_ENV = 'AUTOTOOLS_INSTALL_ENV' #: autotools install env.
RPK_AUTOTOOLS_INSTALL_OPTS = 'AUTOTOOLS_INSTALL_OPTS' #: autotools install opts
RPK_AUTOTOOLS_OPTS = 'AUTOTOOLS_OPTS' #: autotools options
# (other - cmake)
RPK_CMAKE_CONF_ENV = 'CMAKE_CONF_ENV' #: cmake configuration environment values
RPK_CMAKE_CONF_OPTS = 'CMAKE_CONF_OPTS' #: cmake configuration options
RPK_CMAKE_ENV = 'CMAKE_ENV' #: cmake environment values
RPK_CMAKE_INSTALL_ENV = 'CMAKE_INSTALL_ENV' #: cmake install environment values
RPK_CMAKE_INSTALL_OPTS = 'CMAKE_INSTALL_OPTS' #: cmake install options
RPK_CMAKE_OPTS = 'CMAKE_OPTS' #: cmake options
# (other - python)
RPK_PYTHON_ENV = 'PYTHON_ENV' #: python environment values
RPK_PYTHON_INSTALL_ENV = 'PYTHON_INSTALL_ENV' #: python install env. values
RPK_PYTHON_INSTALL_OPTS = 'PYTHON_INSTALL_OPTS' #: python install options
RPK_PYTHON_INTERPRETER = 'PYTHON_INTERPRETER' #: python interpreter
RPK_PYTHON_OPTS = 'PYTHON_OPTS' #: python options

class GlobalAction(Enum):
    """
    specific stage action to perform

    A user can request a (global) action to perform over the default process. For
    example, a user can request to "fetch" and only the fetching stage will occur
    for registered packages.

    Attributes:
        UNKNOWN: unknown action
        CLEAN: clean the working state
        EXTRACT: process all packages through extraction stage
        FETCH: process all packages through fetch stage
        LICENSES: generate license information for a project
        MRPROPER: pristine state clean (ex. configurations)
        PATCH: process all packages through patch stage
    """
    UNKNOWN = 0
    CLEAN = 1
    EXTRACT = 2
    FETCH = 3
    LICENSES = 4
    MRPROPER = 5
    PATCH = 6

class PkgAction(Enum):
    """
    package-specific stage action to perform

    A user can request a package action to perform over the default process. When a
    package-specific action is requested, the process will perform all dependencies
    for the target action's stage before completing the target stage. For example, a
    user can request to perform a package's "extract" stage, which will result in
    ensure the package's fetch stage is complete (and possibility other package
    dependencies) performing (and stopping after) the extraction stage.

    Attributes:
        UNKNOWN: unknown action
        BUILD: process a package till end of the build stage
        CLEAN: process a package till end of the clean stage
        CONFIGURE: process a package till end of the configure stage
        EXTRACT: process a package till end of the extraction stage
        FETCH: process a package till end of the fetch stage
        INSTALL: process a package till end of the install stage
        PATCH: process a package till end of the patch stage
        REBUILD: perform a re-build of a package
        RECONFIGURE: perform a re-configuration of a package
        REINSTALL: perform a re-install of a package
    """
    UNKNOWN = 0
    BUILD = 1
    CLEAN = 2
    CONFIGURE = 3
    EXTRACT = 4
    FETCH = 5
    INSTALL = 6
    PATCH = 7
    REBUILD = 8
    RECONFIGURE = 9
    REINSTALL = 10

class PackageType(Enum):
    """
    package types

    Defines supported package types for deciding which method if configuring,
    building and installing is performed.

    Attributes:
        UNKNOWN: unknown type
        AUTOTOOLS: autotools-based package
        CMAKE: cmake-based package
        PYTHON: python-based package
        SCRIPT: releng script-based package
    """
    UNKNOWN = 0
    AUTOTOOLS = 1
    CMAKE = 2
    PYTHON = 3
    SCRIPT = 4

class PackageInstallType(Enum):
    """
    package install types

    Defines supported package installation types for deciding which the location to
    push resources during the installation phase.

    Attributes:
        UNKNOWN: unknown type
        HOST: install to the host container
        IMAGES: install to the images container
        STAGING: install to the staging container
        STAGING_AND_TARGET: install to the staging and target containers
        TARGET: install to the target container
    """
    UNKNOWN = 0
    HOST = 1
    IMAGES = 2
    STAGING = 3
    STAGING_AND_TARGET = 4
    TARGET = 5

class VcsType(Enum):
    """
    version control system types

    Defines supported version control system types for decided which fetching
    processing is used when acquiring resources.

    Attributes:
        UNKNOWN: unknown type
        CVS: concurrent versions system
        GIT: git
        HG: mercurial
        NONE: no version control (placeholder package)
        SCP: secure copy
        SVN: subversion
        URL: url (http, https, ftp, file, etc.)
    """
    UNKNOWN = 0
    BZR = 1
    CVS = 2
    GIT = 3
    HG = 4
    NONE = 5
    SCP = 6
    SVN = 7
    URL = 8
