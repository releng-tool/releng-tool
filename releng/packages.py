#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from .defs import *
from .util.env import extendScriptEnv
from .util.io import interpretStemExtension
from .util.io import run_script
from .util.log import *
from .util.sort import TopologicalSorter
from .util.string import expand
from .util.string import interpretDictionaryStrings
from .util.string import interpretString
from .util.string import interpretStrings
from .util.string import interpretZeroToOneStrings
from enum import Enum
import os

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

#: default strip-count value for packages
DEFAULT_STRIP_COUNT=1

class RelengPackageManager:
    """
    a releng package manager

    A package manager is responsible for loading a list of sorted packages based
    off a set of package names. Packages will be searched in the configure root
    directory's package directory. Each package should have a initialization
    script (same name as the package directory). The script will be executed for
    options and saved in generated package objects. The loading process will
    allow a limited set of global values to be passed between each other.

    Args:
        opts: options used to configure the package manager (same as engine)
        registry: registry for extension information (same as engine)

    Attributes:
        opts: options used to configure the package manager
        registry: registry for extension information
        script_env: package script environment dictionary
    """
    def __init__(self, opts, registry):
        self.opts = opts
        self.registry = registry
        self.script_env = {}

    def load(self, names):
        """
        load one or more packages from the provided collection of names

        Attempts to load and return a series of ordered package instances using
        the collection of names provided. Each name will be used to find a
        package definition on the system. Package scripts are found, loaded and
        parsed. Packages with dependencies will have their dependent packages
        loaded as well (either from the explicitly from the ``names`` or
        implicitly from the package's configuration file). The returned package
        list will be an ordered package list based on configured dependencies
        outlined in the user's package definitions. When package dependencies do
        not play a role in the required order of the releng process, a
        first-configured first-returned approach is used. In the event that a
        package cannot be found or a cyclic dependency is detected, this call
        with return ``None``.

        Args:
            names: the names of packages to load

        Returns:
            returns an ordered list of packages to use; ``None`` on error
        """
        pkgs = {}
        final_deps = {}

        # cycle through all pending packages until the complete list is known
        names_left = list(names)
        while names_left:
            name = names_left.pop(0)

            # attempt to load the package from a user defined external directory
            pkg = None
            for pkg_dir in self.opts.extern_pkg_dirs:
                pkg_script = os.path.join(pkg_dir, name, name)
                if os.path.isfile(pkg_script):
                    pkg, env, deps = self.loadPackage(name, pkg_script)
                    if pkg:
                        break

            # if a package location has not been found, finally check the
            # default package directory
            if not pkg:
                pkg_script = os.path.join(self.opts.default_pkg_dir, name, name)
                pkg, env, deps = self.loadPackage(name, pkg_script)
                if not pkg:
                    return None

            pkgs[pkg.name] = pkg
            for dep in deps:
                # if this is an unknown package and is not in out current list,
                # append it to the list of names to process
                if dep == name:
                    err('cyclic package dependency detected with self: '
                        '{}'.format(name))
                    return None
                elif dep not in pkgs:
                    if dep not in names_left:
                        verbose(
                            'adding implicitly defined package: {}'.format(dep))
                        names_left.append(dep)

                    if not pkg in final_deps:
                        final_deps[pkg] = []
                    final_deps[pkg].append(dep)
                else:
                    pkg.deps.append(pkgs[dep])
            extendScriptEnv(self.script_env, env)

        # for packages which have a dependency but have not been binded yet,
        # bind the dependencies now
        for pkg, deps in final_deps.items():
            for dep in deps:
                assert pkgs[dep]
                pkg.deps.append(pkgs[dep])

        debug('sorting packages...')
        def fetchDeps(pkg):
            return pkg.deps
        sorter = TopologicalSorter(fetchDeps)
        sorted = []
        for pkg in pkgs.values():
            sorted = sorter.sort(pkg)
            if not sorted:
                err('cyclic package dependency detected: {}'.format(name))
                return None
        debug('sorted packages)')
        for pkg in sorted:
            debug(' {}'.format(pkg.name))

        return sorted

    def loadPackage(self, name, script):
        """
        load a package definition

        Attempts to load a package definition of a given ``name`` from the
        provided ``script`` location. The script will be examine for required
        and optional configuration keys. On a successful execution/parsing, a
        package object will be returned along with other meta information. On
        error, ``None`` types are returned.

        Args:
            name: the package name
            script: the package script to load

        Returns:
            returns a tuple of three (3) containing the package instance, the
            extracted environment/globals from the package script and a list of
            known package dependencies; a tuple of ``None`` types are returned
            on error
        """
        verbose('loading package: {}'.format(name))
        debug('script {}'.format(script))
        opts = self.opts

        def notifyInvalidValue(name, key, expected):
            err('package configuration has an invalid value: {}'.format(name))
            log(' (key: {}, expects: {})'.format(pkgKey(name, key), expected))

        BAD_RV = (None, None, None)
        if not os.path.isfile(script):
            err('unknown package provided: {}'.format(name))
            log(' (script) {}'.format(script))
            return BAD_RV

        env = run_script(script, self.script_env, subject='package')
        if not env:
            return BAD_RV

        self._active_package = name
        self._active_env = env

        # version
        #
        # Always check version first since it will be the most commonly used
        # package field -- rather initially fail on a simple field first (for
        # new packages and/or developers) than breaking on a possibly more
        # complex field below.
        key = pkgKey(name, RPK_VERSION)
        if key not in env or not env[key]:
            err('package has no version defined: {}'.format(name))
            log(' (missing key: {})'.format(key))
            return BAD_RV
        pkg_version = interpretString(env[key])
        if pkg_version is None:
            notifyInvalidValue(name, key, 'string')
            return BAD_RV

        try:
            # development mode revision
            #
            # Always check for a development-mode revision after the version, as
            # this value may override the package's version value if development
            # mode is enabled.
            pkg_has_devmode_option = False
            pkg_devmode_revision = self._fetch(
                RPK_DEVMODE_REVISION, PkgKeyType.STR)

            if pkg_devmode_revision:
                pkg_has_devmode_option = True

                if opts.revision_override and name in opts.revision_override:
                    pkg_devmode_revision = opts.revision_override[name]

                if opts.devmode:
                    pkg_version = pkg_devmode_revision

            # prepare helper expand values
            expandExtra = {
                key: pkg_version,
            }

            # archive extraction strip count
            pkg_strip_count = self._fetch(
                RPK_STRIP_COUNT, PkgKeyType.INT_NONNEGATIVE,
                default=DEFAULT_STRIP_COUNT)

            # build subdirectory
            pkg_build_subdir = self._fetch(RPK_BUILD_SUBDIR, PkgKeyType.STR)

            # dependencies
            deps = self._fetch(RPK_DEPS, PkgKeyType.STRS, default=[])

            # install type
            pkg_install_type = self._fetch(RPK_INSTALL_TYPE, PkgKeyType.STR)
            if pkg_install_type:
                pkg_install_type = pkg_install_type.upper()
                if pkg_install_type in PackageInstallType.__members__:
                    pkg_install_type = PackageInstallType[pkg_install_type]
                else:
                    err('unknown install type value provided: {}'.format(name))
                    log(' (key: {})'.format(pkgKey(name, RPK_INSTALL_TYPE)))
                    return BAD_RV

            if not pkg_install_type:
                pkg_install_type = PackageInstallType.TARGET

            # extension (override)
            pkg_filename_ext = self._fetch(RPK_EXTENSION, PkgKeyType.STR)

            # extract type
            pkg_extract_type = self._fetch(RPK_EXTRACT_TYPE, PkgKeyType.STR)
            if pkg_extract_type:
                pkg_extract_type = pkg_extract_type.upper()

                if pkg_extract_type not in self.registry.extract_types:
                    err('unknown extract-type value provided: {}'.format(name))
                    log(' (key: {})'.format(pkgKey(name, RPK_EXTRACT_TYPE)))
                    return BAD_RV

            # fixed jobs
            pkg_fixed_jobs = self._fetch(
                RPK_FIXED_JOBS, PkgKeyType.INT_POSITIVE)

            # is-external
            pkg_is_external = self._fetch(RPK_EXTERNAL, PkgKeyType.BOOL)

            # is-internal
            pkg_is_internal = self._fetch(RPK_INTERNAL, PkgKeyType.BOOL)

            # license
            pkg_license = self._fetch(RPK_LICENSE, PkgKeyType.STRS)

            # license files
            pkg_license_files = self._fetch(
                RPK_LICENSE_FILES, PkgKeyType.STRS)

            # prefix
            pkg_prefix = self._fetch(RPK_PREFIX, PkgKeyType.STR)

            # revision
            if opts.revision_override and name in opts.revision_override:
                pkg_revision = opts.revision_override[name]
            else:
                pkg_revision = self._fetch(RPK_REVISION, PkgKeyType.STR,
                    allowExpand=True, expandExtra=expandExtra)

            # site
            pkg_site = None
            if opts.sites_override and name in opts.sites_override:
                # Site overriding is permitted to help in scenarios where a builder
                # is unable to acquire a package's source from the defined site.
                # This includes firewall settings or a desire to use a mirrored
                # source when experiencing network connectivity issues.
                pkg_site = opts.sites_override[name]
            else:
                pkg_site = self._fetch(RPK_SITE, PkgKeyType.STR,
                    allowExpand=True, expandExtra=expandExtra)

            # type
            pkg_type = self._fetch(RPK_TYPE, PkgKeyType.STR)
            if pkg_type:
                pkg_type = pkg_type.upper()
                if pkg_type in PackageType.__members__:
                    pkg_type = PackageType[pkg_type]
                elif pkg_type not in self.registry.package_types:
                    err('unknown package type value provided: {}'.format(name))
                    log(' (key: {})'.format(pkgKey(name, RPK_TYPE)))
                    return BAD_RV

            if not pkg_type:
                pkg_type = PackageType.SCRIPT

            # vcs-type
            pkg_vcs_type = self._fetch(RPK_VCS_TYPE, PkgKeyType.STR)
            if pkg_vcs_type:
                pkg_vcs_type = pkg_vcs_type.upper()

                if pkg_vcs_type in VcsType.__members__:
                    pkg_vcs_type = VcsType[pkg_vcs_type]
                elif pkg_vcs_type not in self.registry.fetch_types:
                    err('unknown vcs-type value provided: {}'.format(name))
                    log(' (key: {})'.format(pkgKey(name, RPK_VCS_TYPE)))
                    return BAD_RV

            if not pkg_vcs_type:
                if pkg_site:
                    site_lc = pkg_site.lower()
                    if site_lc.startswith('bzr+'):
                        pkg_site = pkg_site[4:]
                        pkg_vcs_type = VcsType.BZR
                    elif site_lc.startswith('cvs+'):
                        pkg_site = pkg_site[4:]
                        pkg_vcs_type = VcsType.CVS
                    elif site_lc.startswith('git+'):
                        pkg_site = pkg_site[4:]
                        pkg_vcs_type = VcsType.GIT
                    elif site_lc.endswith('.git'):
                        pkg_vcs_type = VcsType.GIT
                    elif site_lc.startswith('hg+'):
                        pkg_site = pkg_site[3:]
                        pkg_vcs_type = VcsType.HG
                    elif site_lc.startswith('scp+'):
                        pkg_site = pkg_site[4:]
                        pkg_vcs_type = VcsType.SCP
                    elif site_lc.startswith('svn+'):
                        pkg_site = pkg_site[4:]
                        pkg_vcs_type = VcsType.SVN
                    else:
                        pkg_vcs_type = VcsType.URL
                else:
                    pkg_vcs_type = VcsType.NONE

            # ##################################################################

            pkg_autotools_autoreconf = self._fetch(RPK_AUTOTOOLS_AUTORECONF,
                PkgKeyType.BOOL, allowExpand=True, expandExtra=expandExtra)

            # autotools autoreconf flag
            pkg_autotools_autoreconf = self._fetch(
                RPK_AUTOTOOLS_AUTORECONF, PkgKeyType.BOOL)

            # autotools configuration environment options
            pkg_autotools_conf_env = self._fetch(
                RPK_AUTOTOOLS_CONF_ENV, PkgKeyType.DICT_STR_STR)

            # autotools configuration options
            pkg_autotools_conf_opts = self._fetch(
                RPK_AUTOTOOLS_CONF_OPTS, PkgKeyType.DICT_STR_STR_OR_STRS)

            # autotools (build) environment options
            pkg_autotools_env = self._fetch(
                RPK_AUTOTOOLS_ENV, PkgKeyType.DICT_STR_STR)

            # autotools (build) options
            pkg_autotools_opts = self._fetch(
                RPK_AUTOTOOLS_OPTS, PkgKeyType.DICT_STR_STR_OR_STRS)

            # autotools installation environment options
            pkg_autotools_install_env = self._fetch(
                RPK_AUTOTOOLS_INSTALL_ENV, PkgKeyType.DICT_STR_STR)

            # autotools installation options
            pkg_autotools_install_opts = self._fetch(
                RPK_AUTOTOOLS_INSTALL_OPTS, PkgKeyType.DICT_STR_STR_OR_STRS)

            # ##################################################################

            # cmake configuration definitions
            pkg_cmake_conf_defs = self._fetch(
                RPK_CMAKE_CONF_DEFS, PkgKeyType.DICT_STR_STR)

            # cmake configuration environment options
            pkg_cmake_conf_env = self._fetch(
                RPK_CMAKE_CONF_ENV, PkgKeyType.DICT_STR_STR)

            # cmake configuration options
            pkg_cmake_conf_opts = self._fetch(
                RPK_CMAKE_CONF_OPTS, PkgKeyType.DICT_STR_STR_OR_STRS)

            # cmake environment options
            pkg_cmake_env = self._fetch(
                RPK_CMAKE_ENV, PkgKeyType.DICT_STR_STR)

            # cmake options
            pkg_cmake_opts = self._fetch(
                RPK_CMAKE_OPTS, PkgKeyType.DICT_STR_STR_OR_STRS)

            # cmake installation environment options
            pkg_cmake_install_env = self._fetch(
                RPK_CMAKE_INSTALL_ENV, PkgKeyType.DICT_STR_STR)

            # cmake installation options
            pkg_cmake_install_opts = self._fetch(
                RPK_CMAKE_INSTALL_OPTS, PkgKeyType.DICT_STR_STR_OR_STRS)

            # ##################################################################

            # python environment options
            pkg_python_env = self._fetch(
                RPK_PYTHON_ENV, PkgKeyType.DICT_STR_STR)

            # python options
            pkg_python_opts = self._fetch(
                RPK_PYTHON_OPTS, PkgKeyType.DICT_STR_STR_OR_STRS)

            # python installation environment options
            pkg_python_install_env = self._fetch(
                RPK_PYTHON_INSTALL_ENV, PkgKeyType.DICT_STR_STR)

            # python installation options
            pkg_python_install_opts = self._fetch(
                RPK_PYTHON_INSTALL_OPTS, PkgKeyType.DICT_STR_STR_OR_STRS)

            # python interpreter
            pkg_python_interpreter = self._fetch(
                RPK_PYTHON_INTERPRETER, PkgKeyType.STR)

            # ##################################################################

            # extension modifiers
            pkg_ext_modifiers = self._fetch(RPK_EXTOPT, PkgKeyType.DICT)

        # notify and return if a key uses an unsupported value
        except InvalidPackageKeyValue as ex:
            notifyInvalidValue(name, self._active_key, ex)
            return BAD_RV

        # ######################################################################

        # checks
        if pkg_is_external and pkg_is_internal:
            key1 = pkgKey(name, RPK_EXTERNAL)
            key2 = pkgKey(name, RPK_INTERNAL)
            err('package has conflicting configuration values: {}'.format(name))
            log(' (package flagged as external and internal)')
            log(' (keys: {}, {})'.format(key1, key2))
            return BAD_RV
        elif pkg_is_internal:
            pkg_is_internal = True
        elif pkg_is_external:
            pkg_is_internal = False
        elif opts.default_internal_pkgs:
            pkg_is_internal = True
        else:
            pkg_is_internal = False

        # find possible extension for a cache file
        #
        # non-dvcs's will be always gzip-tar'ed.
        if pkg_vcs_type in (VcsType.BZR, VcsType.CVS, VcsType.SVN):
            cache_ext = 'tgz'
        # dvcs's will not have an extension type
        elif pkg_vcs_type in (VcsType.GIT, VcsType.HG):
            cache_ext = None
        # non-vcs type does not have an extension
        elif pkg_vcs_type is VcsType.NONE:
            cache_ext = None
        else:
            cache_ext = None
            url_parts = urlparse(pkg_site)

            if opts.cache_ext_transform:
                # Allow a configuration to override the target cache file's
                # extension based on the package's site path (for unique path
                # scenarios).
                cache_ext = opts.cache_ext_transform(url_parts.path)

            if not cache_ext:
                if pkg_filename_ext:
                    cache_ext = pkg_filename_ext
                else:
                    basename = os.path.basename(url_parts.path)
                    __, cache_ext = interpretStemExtension(basename)

        # finalization
        pkg_nv = '{}-{}'.format(name, pkg_version)
        pkg_build_output_dir = os.path.join(opts.build_dir, pkg_nv)
        if opts.local_srcs and pkg_is_internal:
            container_dir = os.path.dirname(opts.root_dir)
            pkg_build_dir = os.path.join(container_dir, name)

            if pkg_build_dir == opts.root_dir:
                err('conflicting local-sources package path and root directory')
                log(' (root: {})'.format(opts.root_dir))
                log(' ({} path: {})'.format(name, pkg_build_dir))
                return BAD_RV
        else:
            pkg_build_dir = pkg_build_output_dir
        pkg_def_dir = os.path.abspath(os.path.join(script, os.pardir))
        if pkg_build_subdir:
            pkg_build_subdir = os.path.join(pkg_build_dir, pkg_build_subdir)
        if cache_ext:
            pkg_cache_file = os.path.join(opts.dl_dir, pkg_nv + '.' + cache_ext)
        else:
            pkg_cache_file = os.path.join(opts.dl_dir, pkg_nv)
        if not pkg_prefix:
            pkg_prefix = opts.sysroot_prefix
        if opts.devmode and pkg_devmode_revision:
            pkg_revision = pkg_devmode_revision
        elif not pkg_revision:
            pkg_revision = pkg_version

        # Select sources (like CMake-based projects) may wish to be using
        # out-of-source tree builds. For supported project types, adjust the
        # build output directory to a sub-folder of the originally assumed
        # output folder.
        if pkg_type == PackageType.CMAKE:
            pkg_build_output_dir = os.path.join(
                pkg_build_output_dir, 'releng-output')

        # (commons)
        pkg = RelengPackage(name, pkg_version)
        pkg.build_dir = pkg_build_dir
        pkg.build_output_dir = pkg_build_output_dir
        pkg.build_subdir = pkg_build_subdir
        pkg.cache_dir = os.path.join(opts.cache_dir, name)
        pkg.cache_file = pkg_cache_file
        pkg.def_dir = pkg_def_dir
        pkg.ext_modifiers = pkg_ext_modifiers
        pkg.extract_type = pkg_extract_type
        pkg.fixed_jobs = pkg_fixed_jobs
        pkg.has_devmode_option = pkg_has_devmode_option
        pkg.hash_file = os.path.join(pkg_def_dir, name + '.hash')
        pkg.install_type = pkg_install_type
        pkg.is_internal = pkg_is_internal
        pkg.license = pkg_license
        pkg.license_files = pkg_license_files
        pkg.prefix = pkg_prefix
        pkg.revision = pkg_revision
        pkg.site = pkg_site
        pkg.strip_count = pkg_strip_count
        pkg.type = pkg_type
        pkg.vcs_type = pkg_vcs_type
        # (other - autotools)
        pkg.autotools_autoreconf = pkg_autotools_autoreconf is True
        pkg.autotools_conf_env = pkg_autotools_conf_env
        pkg.autotools_conf_opts = pkg_autotools_conf_opts
        pkg.autotools_env = pkg_autotools_env
        pkg.autotools_install_env = pkg_autotools_install_env
        pkg.autotools_install_opts = pkg_autotools_install_opts
        pkg.autotools_opts = pkg_autotools_opts
        # (other - cmake)
        pkg.cmake_conf_defs = pkg_cmake_conf_defs
        pkg.cmake_conf_env = pkg_cmake_conf_env
        pkg.cmake_conf_opts = pkg_cmake_conf_opts
        pkg.cmake_env = pkg_cmake_env
        pkg.cmake_install_env = pkg_cmake_install_env
        pkg.cmake_install_opts = pkg_cmake_install_opts
        pkg.cmake_opts = pkg_cmake_opts
        # (other - python)
        pkg.python_env = pkg_python_env
        pkg.python_install_env = pkg_python_install_env
        pkg.python_install_opts = pkg_python_install_opts
        pkg.python_interpreter = pkg_python_interpreter
        pkg.python_opts = pkg_python_opts
        # (additional environment helpers)
        for env in (os.environ, env):
            env[pkgKey(name, 'BUILD_DIR')] = pkg_build_dir
            env[pkgKey(name, 'BUILD_OUTPUT_DIR')] = pkg_build_output_dir
            env[pkgKey(name, 'NAME')] = name
        os.environ[pkgKey(name, RPK_VERSION)] = pkg_version

        return pkg, env, deps

    def _fetch(self, key, type, default=None, allowExpand=False,
            expandExtra=None):
        """
        fetch a configuration value from a provided key

        Package definitions will define one or more key-value configurations for
        the release engineering process to use. For specific keys, there will be
        expected value types where a key is provided. The fetch operation can be
        provided a key and will return the desired value; however, if the value
        is of a type/value that is not supported, an exception
        ``InvalidPackageKeyValue`` is raised.

        Args:
            key: the key
            type: the expected type for the key's value
            default (optional): default value to use if the key does not exist
            allowExpand (optional): whether or not to expand the value
            expandExtra (optional): extra expand defines to use

        Returns:
            the value

        Raises:
            InvalidPackageKeyValue: value type is invalid for the key
        """
        self._active_key = key
        value = default
        pkg_key = pkgKey(self._active_package, key)
        if pkg_key in self._active_env:
            if type == PkgKeyType.BOOL:
                value = self._active_env[pkg_key]
                if not isinstance(value, bool):
                    raise InvalidPackageKeyValue('bool')
            elif type == PkgKeyType.DICT:
                value = self._active_env[pkg_key]
                if allowExpand:
                    value = expand(value, expandExtra)
                if not isinstance(value, dict):
                    raise InvalidPackageKeyValue('dictionary')
            elif type == PkgKeyType.DICT_STR_STR:
                value = interpretDictionaryStrings(self._active_env[pkg_key])
                if allowExpand:
                    value = expand(value, expandExtra)
                if value is None:
                    raise InvalidPackageKeyValue('dict(str,str)')
            elif type == PkgKeyType.DICT_STR_STR_OR_STRS:
                value = interpretZeroToOneStrings(self._active_env[pkg_key])
                if allowExpand:
                    value = expand(value, expandExtra)
                if value is None:
                    raise InvalidPackageKeyValue('dict(str,str) or string(s)')
            elif type == PkgKeyType.STR:
                value = interpretString(self._active_env[pkg_key])
                if allowExpand:
                    value = expand(value, expandExtra)
                if value is None:
                    raise InvalidPackageKeyValue('string')
            elif type == PkgKeyType.STRS:
                value = interpretStrings(self._active_env[pkg_key])
                if allowExpand:
                    value = expand(value, expandExtra)
                if value is None:
                    raise InvalidPackageKeyValue('string(s)')
            elif type == PkgKeyType.INT_NONNEGATIVE:
                value = self._active_env[pkg_key]
                if not isinstance(value, int) or value < 0:
                    raise InvalidPackageKeyValue('non-negative int')
            elif type == PkgKeyType.INT_POSITIVE:
                value = self._active_env[pkg_key]
                if not isinstance(value, int) or value <= 0:
                    raise InvalidPackageKeyValue('positive int')
            else:
                raise InvalidPackageKeyValue('<unsupported key-value>')

        return value

class RelengPackage:
    """
    a releng package

    A package tracks the name, options and dependencies of the package.

    Args:
        name: the name of the package

    Attributes:
        build_dir: directory for a package's buildable content
        build_output_dir: build output directory for the package process
        build_subdir: override for a package's buildable content (if applicable)
        cache_dir: cache directory for the package (if applicable)
        cache_file: cache file for the package (if applicable)
        def_dir: directory for the package definition
        deps: list of dependencies for this package
        ext_modifiers: extension-defined modifiers (dict)
        extract_type: extraction type override (for extensions, if applicable)
        fixed_jobs: fixed job count for this specific package
        has_devmode_option: whether or not the package has a devmode revision
        hash_file: file containing hashes to validate this package
        install_type: install container for the package (target, staged, etc.)
        is_internal: whether or not this package is an project internal package
        license: license(s) of the package
        license_files: list of files in sources holding license information
        name: name of the package
        nv: name-version value of the package
        prefix: system root prefix override (if applicable)
        revision: revision to use to fetch from vcs (if applicable)
        site: site to acquire package assets
        strip_count: archive extraction strip count (if applicable)
        type: package type (script-based, cmake, etc.)
        vcs_type: vcs type of the package (git, file, etc.)
        version: package version
        (other - autotools)
        autotools_autoreconf: autotools | flag to invoke autoreconf
        autotools_conf_env: autotools | configuration environment overrides
        autotools_conf_opts: autotools | configuration option overrides
        autotools_env: autotools | build environment overrides
        autotools_install_env: autotools | installation environment overrides
        autotools_install_opts: autotools | installation option overrides
        autotools_opts: autotools | build option overrides
        (other - cmake)
        cmake_conf_env: cmake | configuration environment overrides
        cmake_conf_opts: cmake | configuration option overrides
        cmake_env: cmake | environment overrides
        cmake_install_env: cmake | installation environment overrides
        cmake_install_opts: cmake | installation option overrides
        cmake_opts: cmake | option overrides
        (other - python)
        python_env: python | environment overrides
        python_install_env: python | installation environment overrides
        python_install_opts: python | installation option overrides
        python_opts: python | option overrides
    """
    def __init__(self, name, version):
        self.name = name
        self.nv = '{}-{}'.format(name, version)
        self.version = version
        # (commons)
        self.build_dir = None
        self.build_subdir = None
        self.build_output_dir = None
        self.cache_dir = None
        self.cache_file = None
        self.def_dir = None
        self.deps = []
        self.fixed_jobs = None
        self.has_devmode_option = None
        self.hash_file = None
        self.ext_modifiers = None
        self.extract_type = None
        self.install_type = None
        self.is_internal = None
        self.license = None
        self.license_files = None
        self.prefix = None
        self.revision = None
        self.site = None
        self.strip_count = None
        self.type = None
        self.vcs_type = None
        # (other - autotools)
        self.autotools_autoreconf = None
        self.autotools_conf_env = None
        self.autotools_conf_opts = None
        self.autotools_env = None
        self.autotools_install_env = None
        self.autotools_install_opts = None
        self.autotools_opts = None
        # (other - cmake)
        self.cmake_conf_env = None
        self.cmake_conf_opts = None
        self.cmake_env = None
        self.cmake_install_env = None
        self.cmake_install_opts = None
        self.cmake_opts = None
        # (other - python)
        self.python_env = None
        self.python_install_env = None
        self.python_install_opts = None
        self.python_opts = None

    def __str__(self):
        return (
            'package "{}"\n'
            '      build: {}\n'
            '  build-out: {}\n'
            ' definition: {}\n'
            '       site: {}\n'
            '   vcs-type: {}\n'
            '    version: {}'
            ).format(
                self.name,
                self.build_dir,
                self.build_output_dir,
                self.def_dir,
                self.site,
                self.vcs_type,
                self.version,
                )

def pkgKey(pkg, type):
    """
    generate a package key for a given type string

    Generates a compatible "package key" for a unsanitized package name ``pkg``
    of a specific key ``type``. The package string is "cleaned" to replaces
    select characters (such as dashes) with underscores and becomes uppercase.
    For example, consider the package name "my-awesome-module". For a package
    key "VERSION", the complete key for this package is
    "MY_AWESOME_MODULE_VERSION".

    Args:
        pkg: the package name
        type: the package key type

    Returns:
        the completed package key
    """
    clean = pkg
    for c in [' ', '*', '-', '.', ':', '?', '|']:
        clean = clean.replace(c, '_')
    return '{}_{}'.format(clean.upper(), type)

class PkgKeyType(Enum):
    """
    package key type

    Enumeration of types supported when fetching configuration values defined by a
    package definition.

    Attributes:
        UNKNOWN: unknown type
        BOOL: boolean value
        DICT: dictionary value
        DICT_STR_STR: dictionary of string pairs value
        DICT_STR_STR_OR_STRS: dictionary of string pairs or strings value
        STR: single string value
        STRS: one or more strings value
        INT_NONNEGATIVE: non-negative integer value
        INT_POSITIVE: positive integer value
    """
    UNKNOWN = 0
    BOOL = 1
    DICT = 2
    DICT_STR_STR = 3
    DICT_STR_STR_OR_STRS = 4
    STR = 5
    STRS = 6
    INT_NONNEGATIVE = 7
    INT_POSITIVE = 8

class InvalidPackageKeyValue(Exception):
    """
    raised when a package key is using an unsupported value
    """
    pass
