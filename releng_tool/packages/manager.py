# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from releng_tool.defs import PackageInstallType
from releng_tool.defs import PackageType
from releng_tool.defs import RPK_AUTOTOOLS_AUTORECONF
from releng_tool.defs import RPK_BUILD_DEFS
from releng_tool.defs import RPK_BUILD_ENV
from releng_tool.defs import RPK_BUILD_OPTS
from releng_tool.defs import RPK_BUILD_SUBDIR
from releng_tool.defs import RPK_CONF_DEFS
from releng_tool.defs import RPK_CONF_ENV
from releng_tool.defs import RPK_CONF_OPTS
from releng_tool.defs import RPK_DEPS
from releng_tool.defs import RPK_DEVMODE_IGNORE_CACHE
from releng_tool.defs import RPK_DEVMODE_REVISION
from releng_tool.defs import RPK_EXTENSION
from releng_tool.defs import RPK_EXTERNAL
from releng_tool.defs import RPK_EXTOPT
from releng_tool.defs import RPK_EXTRACT_TYPE
from releng_tool.defs import RPK_FIXED_JOBS
from releng_tool.defs import RPK_GIT_CONFIG
from releng_tool.defs import RPK_GIT_DEPTH
from releng_tool.defs import RPK_GIT_REFSPECS
from releng_tool.defs import RPK_INSTALL_DEFS
from releng_tool.defs import RPK_INSTALL_ENV
from releng_tool.defs import RPK_INSTALL_OPTS
from releng_tool.defs import RPK_INSTALL_TYPE
from releng_tool.defs import RPK_INTERNAL
from releng_tool.defs import RPK_LICENSE
from releng_tool.defs import RPK_LICENSE_FILES
from releng_tool.defs import RPK_NO_EXTRACTION
from releng_tool.defs import RPK_PREFIX
from releng_tool.defs import RPK_PYTHON_INTERPRETER
from releng_tool.defs import RPK_REVISION
from releng_tool.defs import RPK_SITE
from releng_tool.defs import RPK_STRIP_COUNT
from releng_tool.defs import RPK_TYPE
from releng_tool.defs import RPK_VCS_TYPE
from releng_tool.defs import RPK_VERSION
from releng_tool.defs import VcsType
from releng_tool.packages import InvalidPackageKeyValue
from releng_tool.packages import PkgKeyType
from releng_tool.packages import pkg_key
from releng_tool.packages.package import RelengPackage
from releng_tool.util.env import extend_script_env
from releng_tool.util.io import interpret_stem_extension
from releng_tool.util.io import opt_file
from releng_tool.util.io import run_script
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
from releng_tool.util.sort import TopologicalSorter
from releng_tool.util.string import expand
from releng_tool.util.string import interpret_dictionary_strings
from releng_tool.util.string import interpret_string
from releng_tool.util.string import interpret_strings
from releng_tool.util.string import interpret_zero_to_one_strings
import os

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

#: default strip-count value for packages
DEFAULT_STRIP_COUNT = 1

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
        self._key_types = {}

        # register expected types for each configuration
        self._register_conf(RPK_AUTOTOOLS_AUTORECONF, PkgKeyType.BOOL)
        self._register_conf(RPK_BUILD_DEFS, PkgKeyType.DICT_STR_STR)
        self._register_conf(RPK_BUILD_ENV, PkgKeyType.DICT_STR_STR)
        self._register_conf(RPK_BUILD_OPTS, PkgKeyType.DICT_STR_STR_OR_STRS)
        self._register_conf(RPK_BUILD_SUBDIR, PkgKeyType.STR)
        self._register_conf(RPK_CONF_DEFS, PkgKeyType.DICT_STR_STR)
        self._register_conf(RPK_CONF_ENV, PkgKeyType.DICT_STR_STR)
        self._register_conf(RPK_CONF_OPTS, PkgKeyType.DICT_STR_STR_OR_STRS)
        self._register_conf(RPK_DEPS, PkgKeyType.STRS)
        self._register_conf(RPK_DEVMODE_IGNORE_CACHE, PkgKeyType.BOOL)
        self._register_conf(RPK_DEVMODE_REVISION, PkgKeyType.STR)
        self._register_conf(RPK_EXTENSION, PkgKeyType.STR)
        self._register_conf(RPK_EXTERNAL, PkgKeyType.BOOL)
        self._register_conf(RPK_EXTOPT, PkgKeyType.DICT)
        self._register_conf(RPK_EXTRACT_TYPE, PkgKeyType.STR)
        self._register_conf(RPK_FIXED_JOBS, PkgKeyType.INT_POSITIVE)
        self._register_conf(RPK_GIT_CONFIG, PkgKeyType.DICT_STR_STR)
        self._register_conf(RPK_GIT_DEPTH, PkgKeyType.INT_NONNEGATIVE)
        self._register_conf(RPK_GIT_REFSPECS, PkgKeyType.STRS)
        self._register_conf(RPK_INSTALL_DEFS, PkgKeyType.DICT_STR_STR)
        self._register_conf(RPK_INSTALL_ENV, PkgKeyType.DICT_STR_STR)
        self._register_conf(RPK_INSTALL_OPTS, PkgKeyType.DICT_STR_STR_OR_STRS)
        self._register_conf(RPK_INSTALL_TYPE, PkgKeyType.STR)
        self._register_conf(RPK_INTERNAL, PkgKeyType.BOOL)
        self._register_conf(RPK_LICENSE, PkgKeyType.STRS)
        self._register_conf(RPK_LICENSE_FILES, PkgKeyType.STRS)
        self._register_conf(RPK_NO_EXTRACTION, PkgKeyType.BOOL)
        self._register_conf(RPK_PREFIX, PkgKeyType.STR)
        self._register_conf(RPK_PYTHON_INTERPRETER, PkgKeyType.STR)
        self._register_conf(RPK_REVISION, PkgKeyType.STR)
        self._register_conf(RPK_SITE, PkgKeyType.STR)
        self._register_conf(RPK_STRIP_COUNT, PkgKeyType.INT_NONNEGATIVE)
        self._register_conf(RPK_TYPE, PkgKeyType.STR)
        self._register_conf(RPK_VCS_TYPE, PkgKeyType.STR)

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
                pkg_script, pkg_script_exists = opt_file(pkg_script)
                if pkg_script_exists:
                    pkg, env, deps = self.load_package(name, pkg_script)
                    if pkg:
                        break

            # if a package location has not been found, finally check the
            # default package directory
            if not pkg:
                pkg_script = os.path.join(self.opts.default_pkg_dir, name, name)
                pkg_script, _ = opt_file(pkg_script)

                pkg, env, deps = self.load_package(name, pkg_script)
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

                    if pkg not in final_deps:
                        final_deps[pkg] = []
                    final_deps[pkg].append(dep)
                else:
                    pkg.deps.append(pkgs[dep])
            extend_script_env(self.script_env, env)

        # for packages which have a dependency but have not been binded yet,
        # bind the dependencies now
        for pkg, deps in final_deps.items():
            for dep in deps:
                assert pkgs[dep]
                pkg.deps.append(pkgs[dep])

        debug('sorting packages...')
        def fetch_deps(pkg):
            return pkg.deps
        sorter = TopologicalSorter(fetch_deps)
        sorted_pkgs = []
        for pkg in pkgs.values():
            sorted_pkgs = sorter.sort(pkg)
            if not sorted:
                err('cyclic package dependency detected: {}'.format(name))
                return None
        debug('sorted packages)')
        for pkg in sorted_pkgs:
            debug(' {}'.format(pkg.name))

        return sorted_pkgs

    def load_package(self, name, script):
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

        def notify_invalid_value(name, key, expected):
            err('package configuration has an invalid value: {}'.format(name))
            err(' (key: {}, expects: {})'.format(pkg_key(name, key), expected))

        BAD_RV = (None, None, None)
        if not os.path.isfile(script):
            err('unknown package provided: {}'.format(name))
            err(' (script) {}'.format(script))
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
        key = pkg_key(name, RPK_VERSION)
        if key not in env or not env[key]:
            err('package has no version defined: {}'.format(name))
            err(' (missing key: {})'.format(key))
            return BAD_RV
        pkg_version = interpret_string(env[key])
        if pkg_version is None:
            notify_invalid_value(name, key, 'string')
            return BAD_RV

        try:
            # development mode revision
            #
            # Always check for a development-mode revision after the version, as
            # this value may override the package's version value if development
            # mode is enabled.
            pkg_has_devmode_option = False
            pkg_devmode_revision = self._fetch(RPK_DEVMODE_REVISION)

            if pkg_devmode_revision:
                pkg_has_devmode_option = True

                if opts.revision_override and name in opts.revision_override:
                    pkg_devmode_revision = opts.revision_override[name]

                if opts.devmode:
                    pkg_version = pkg_devmode_revision

            # prepare helper expand values
            expand_extra = {
                key: pkg_version,
            }

            # archive extraction strip count
            pkg_strip_count = self._fetch(RPK_STRIP_COUNT,
                default=DEFAULT_STRIP_COUNT)

            # build subdirectory
            pkg_build_subdir = self._fetch(RPK_BUILD_SUBDIR)

            # dependencies
            deps = self._fetch(RPK_DEPS, default=[])

            # ignore cache
            pkg_devmode_ignore_cache = self._fetch(RPK_DEVMODE_IGNORE_CACHE)

            # install type
            pkg_install_type = self._fetch(RPK_INSTALL_TYPE)
            if pkg_install_type:
                pkg_install_type = pkg_install_type.upper()
                if pkg_install_type in PackageInstallType.__members__:
                    pkg_install_type = PackageInstallType[pkg_install_type]
                else:
                    err('unknown install type value provided: {}'.format(name))
                    err(' (key: {})'.format(pkg_key(name, RPK_INSTALL_TYPE)))
                    return BAD_RV

            if not pkg_install_type:
                pkg_install_type = PackageInstallType.TARGET

            # extension (override)
            pkg_filename_ext = self._fetch(RPK_EXTENSION)

            # extract type
            pkg_extract_type = self._fetch(RPK_EXTRACT_TYPE)
            if pkg_extract_type:
                pkg_extract_type = pkg_extract_type.upper()

                if pkg_extract_type not in self.registry.extract_types:
                    err('unknown extract-type value provided: {}'.format(name))
                    err(' (key: {})'.format(pkg_key(name, RPK_EXTRACT_TYPE)))
                    return BAD_RV

            # fixed jobs
            pkg_fixed_jobs = self._fetch(RPK_FIXED_JOBS)

            # is-external
            pkg_is_external = self._fetch(RPK_EXTERNAL)

            # is-internal
            pkg_is_internal = self._fetch(RPK_INTERNAL)

            # license
            pkg_license = self._fetch(RPK_LICENSE)

            # license files
            pkg_license_files = self._fetch(RPK_LICENSE_FILES)

            # no extraction
            pkg_no_extraction = self._fetch(RPK_NO_EXTRACTION)

            # prefix
            pkg_prefix = self._fetch(RPK_PREFIX)

            # revision
            if opts.revision_override and name in opts.revision_override:
                pkg_revision = opts.revision_override[name]
            else:
                pkg_revision = self._fetch(RPK_REVISION,
                    allow_expand=True, expand_extra=expand_extra)

            # site
            if opts.sites_override and name in opts.sites_override:
                # Site overriding is permitted to help in scenarios where a builder
                # is unable to acquire a package's source from the defined site.
                # This includes firewall settings or a desire to use a mirrored
                # source when experiencing network connectivity issues.
                pkg_site = opts.sites_override[name]
            else:
                pkg_site = self._fetch(RPK_SITE,
                    allow_expand=True, expand_extra=expand_extra)

            # type
            pkg_type = self._fetch(RPK_TYPE)
            if pkg_type:
                pkg_type = pkg_type.upper()
                if pkg_type in PackageType.__members__:
                    pkg_type = PackageType[pkg_type]
                elif pkg_type not in self.registry.package_types:
                    err('unknown package type value provided: {}'.format(name))
                    err(' (key: {})'.format(pkg_key(name, RPK_TYPE)))
                    return BAD_RV

            if not pkg_type:
                pkg_type = PackageType.SCRIPT

            # vcs-type
            pkg_vcs_type = self._fetch(RPK_VCS_TYPE)
            if pkg_vcs_type:
                pkg_vcs_type = pkg_vcs_type.upper()

                if pkg_vcs_type in VcsType.__members__:
                    pkg_vcs_type = VcsType[pkg_vcs_type]
                elif pkg_vcs_type not in self.registry.fetch_types:
                    err('unknown vcs-type value provided: {}'.format(name))
                    err(' (key: {})'.format(pkg_key(name, RPK_VCS_TYPE)))
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
                    elif site_lc == 'local':
                        pkg_vcs_type = VcsType.LOCAL
                    else:
                        pkg_vcs_type = VcsType.URL
                else:
                    pkg_vcs_type = VcsType.NONE

            if pkg_vcs_type is VcsType.LOCAL:
                warn('package using local content: {}'.format(name))

            # ##################################################################

            # package-type build definitions
            pkg_build_defs = self._fetch(RPK_BUILD_DEFS)

            # package-type build environment options
            pkg_build_env = self._fetch(RPK_BUILD_ENV)

            # package-type build options
            pkg_build_opts = self._fetch(RPK_BUILD_OPTS)

            # package-type configuration definitions
            pkg_conf_defs = self._fetch(RPK_CONF_DEFS)

            # package-type configuration environment options
            pkg_conf_env = self._fetch(RPK_CONF_ENV)

            # package-type configuration options
            pkg_conf_opts = self._fetch(RPK_CONF_OPTS)

            # package-type installation definitions
            pkg_install_defs = self._fetch(RPK_INSTALL_DEFS)

            # package-type installation environment options
            pkg_install_env = self._fetch(RPK_INSTALL_ENV)

            # package-type installation options
            pkg_install_opts = self._fetch(RPK_INSTALL_OPTS)

            # ##################################################################

            # autotools autoreconf flag
            pkg_autotools_autoreconf = self._fetch(RPK_AUTOTOOLS_AUTORECONF)

            # ##################################################################

            # git configuration options for a repository
            pkg_git_config = self._fetch(RPK_GIT_CONFIG)

            # git-depth
            pkg_git_depth = self._fetch(RPK_GIT_DEPTH)

            # git-refspecs
            pkg_git_refspecs = self._fetch(RPK_GIT_REFSPECS, default=[])

            # ##################################################################

            # python interpreter
            pkg_python_interpreter = self._fetch(RPK_PYTHON_INTERPRETER)

            # ##################################################################

            # extension modifiers
            pkg_ext_modifiers = self._fetch(RPK_EXTOPT)

        # notify and return if a key uses an unsupported value
        except InvalidPackageKeyValue as ex:
            notify_invalid_value(name, self._active_key, ex)
            return BAD_RV

        # ######################################################################

        # checks
        if pkg_is_external and pkg_is_internal:
            key1 = pkg_key(name, RPK_EXTERNAL)
            key2 = pkg_key(name, RPK_INTERNAL)
            err('package has conflicting configuration values: {}'.format(name))
            err(' (package flagged as external and internal)')
            err(' (keys: {}, {})'.format(key1, key2))
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
        elif pkg_vcs_type in (VcsType.LOCAL, VcsType.NONE):
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
                    __, cache_ext = interpret_stem_extension(basename)

        # finalization
        pkg_nv = '{}-{}'.format(name, pkg_version)
        pkg_build_output_dir = os.path.join(opts.build_dir, pkg_nv)
        pkg_def_dir = os.path.abspath(os.path.join(script, os.pardir))
        if pkg_vcs_type is VcsType.LOCAL:
            pkg_build_dir = pkg_def_dir
        elif opts.local_srcs and pkg_is_internal:
            container_dir = os.path.dirname(opts.root_dir)
            pkg_build_dir = os.path.join(container_dir, name)

            if pkg_build_dir == opts.root_dir:
                err('conflicting local-sources package path and root directory')
                err(' (root: {})'.format(opts.root_dir))
                err(' ({} path: {})'.format(name, pkg_build_dir))
                return BAD_RV
        else:
            pkg_build_dir = pkg_build_output_dir
        if pkg_build_subdir:
            pkg_build_subdir = os.path.join(pkg_build_dir, pkg_build_subdir)
        if cache_ext:
            pkg_cache_file = os.path.join(opts.dl_dir, pkg_nv + '.' + cache_ext)
        else:
            pkg_cache_file = os.path.join(opts.dl_dir, pkg_nv)
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
        pkg.devmode_ignore_cache = pkg_devmode_ignore_cache
        pkg.ext_modifiers = pkg_ext_modifiers
        pkg.extract_type = pkg_extract_type
        pkg.fixed_jobs = pkg_fixed_jobs
        pkg.git_config = pkg_git_config
        pkg.git_depth = pkg_git_depth
        pkg.git_refspecs = pkg_git_refspecs
        pkg.has_devmode_option = pkg_has_devmode_option
        pkg.hash_file = os.path.join(pkg_def_dir, name + '.hash')
        pkg.install_type = pkg_install_type
        pkg.is_internal = pkg_is_internal
        pkg.license = pkg_license
        pkg.license_files = pkg_license_files
        pkg.no_extraction = pkg_no_extraction
        pkg.prefix = pkg_prefix
        pkg.revision = pkg_revision
        pkg.site = pkg_site
        pkg.strip_count = pkg_strip_count
        pkg.type = pkg_type
        pkg.vcs_type = pkg_vcs_type
        # (package type - common)
        pkg.build_defs = pkg_build_defs
        pkg.build_env = pkg_build_env
        pkg.build_opts = pkg_build_opts
        pkg.conf_defs = pkg_conf_defs
        pkg.conf_env = pkg_conf_env
        pkg.conf_opts = pkg_conf_opts
        pkg.install_defs = pkg_install_defs
        pkg.install_env = pkg_install_env
        pkg.install_opts = pkg_install_opts
        # (package type - autotools)
        pkg.autotools_autoreconf = pkg_autotools_autoreconf is True
        # (package type - python)
        pkg.python_interpreter = pkg_python_interpreter
        # (additional environment helpers)
        for env in (os.environ, env):
            env[pkg_key(name, 'BUILD_DIR')] = pkg_build_dir
            env[pkg_key(name, 'BUILD_OUTPUT_DIR')] = pkg_build_output_dir
            env[pkg_key(name, 'NAME')] = name
            env[pkg_key(name, 'REVISION')] = pkg_revision
        os.environ[pkg_key(name, RPK_VERSION)] = pkg_version

        return pkg, env, deps

    def _fetch(self, key, default=None, allow_expand=False,
            expand_extra=None):
        """
        fetch a configuration value from a provided key

        Package definitions will define one or more key-value configurations for
        the release engineering process to use. For specific keys, there will be
        expected value types where a key is provided. The fetch operation can be
        provided a key and will return the desired value; however, if the value
        is of a value that is not supported, an exception
        ``InvalidPackageKeyValue`` is raised.

        Args:
            key: the key
            default (optional): default value to use if the key does not exist
            allow_expand (optional): whether or not to expand the value
            expand_extra (optional): extra expand defines to use

        Returns:
            the value

        Raises:
            InvalidPackageKeyValue: value type is invalid for the key
        """
        assert key in self._key_types

        self._active_key = key
        type_ = self._key_types[key]
        value = default

        key = pkg_key(self._active_package, key)
        if key in self._active_env:
            if type_ == PkgKeyType.BOOL:
                value = self._active_env[key]
                if not isinstance(value, bool):
                    raise InvalidPackageKeyValue('bool')
            elif type_ == PkgKeyType.DICT:
                value = self._active_env[key]
                if allow_expand:
                    value = expand(value, expand_extra)
                if not isinstance(value, dict):
                    raise InvalidPackageKeyValue('dictionary')
            elif type_ == PkgKeyType.DICT_STR_STR:
                value = interpret_dictionary_strings(self._active_env[key])
                if allow_expand:
                    value = expand(value, expand_extra)
                if value is None:
                    raise InvalidPackageKeyValue('dict(str,str)')
            elif type_ == PkgKeyType.DICT_STR_STR_OR_STRS:
                value = interpret_zero_to_one_strings(self._active_env[key])
                if allow_expand:
                    value = expand(value, expand_extra)
                if value is None:
                    raise InvalidPackageKeyValue('dict(str,str) or string(s)')
            elif type_ == PkgKeyType.STR:
                value = interpret_string(self._active_env[key])
                if allow_expand:
                    value = expand(value, expand_extra)
                if value is None:
                    raise InvalidPackageKeyValue('string')
            elif type_ == PkgKeyType.STRS:
                value = interpret_strings(self._active_env[key])
                if allow_expand:
                    value = expand(value, expand_extra)
                if value is None:
                    raise InvalidPackageKeyValue('string(s)')
            elif type_ == PkgKeyType.INT_NONNEGATIVE:
                value = self._active_env[key]
                if not isinstance(value, int) or value < 0:
                    raise InvalidPackageKeyValue('non-negative int')
            elif type_ == PkgKeyType.INT_POSITIVE:
                value = self._active_env[key]
                if not isinstance(value, int) or value <= 0:
                    raise InvalidPackageKeyValue('positive int')
            else:
                raise InvalidPackageKeyValue('<unsupported key-value>')

        return value

    def _register_conf(self, key, type_):
        """
        register an expected configure type for a provided configuration key

        When attempting to fetch a configuration value for a specific key, the
        fetch process will sanity check the type based off a specific PkgKeyType
        type. This call registers the expected type for a key which can later
        be used when fetching.

        Args:
            key: the key
            type_: the expected configuration type
        """
        assert key not in self._key_types
        self._key_types[key] = type_
