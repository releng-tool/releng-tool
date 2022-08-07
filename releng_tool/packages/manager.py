# -*- coding: utf-8 -*-
# Copyright 2018-2022 releng-tool

from collections import OrderedDict
from releng_tool.defs import GBL_LSRCS
from releng_tool.defs import PackageInstallType
from releng_tool.defs import PackageType
from releng_tool.defs import Rpk
from releng_tool.defs import VcsType
from releng_tool.packages import PkgKeyType
from releng_tool.packages import pkg_cache_key
from releng_tool.packages import pkg_key
from releng_tool.packages.exceptions import RelengToolConflictingConfiguration
from releng_tool.packages.exceptions import RelengToolConflictingLocalSrcsPath
from releng_tool.packages.exceptions import RelengToolCyclicPackageDependency
from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from releng_tool.packages.exceptions import RelengToolInvalidPackageScript
from releng_tool.packages.exceptions import RelengToolMissingPackageRevision
from releng_tool.packages.exceptions import RelengToolMissingPackageScript
from releng_tool.packages.exceptions import RelengToolMissingPackageSite
from releng_tool.packages.exceptions import RelengToolUnknownExtractType
from releng_tool.packages.exceptions import RelengToolUnknownInstallType
from releng_tool.packages.exceptions import RelengToolUnknownPackageType
from releng_tool.packages.exceptions import RelengToolUnknownVcsType
from releng_tool.packages.package import RelengPackage
from releng_tool.opts import RELENG_CONF_EXTENDED_NAME
from releng_tool.util.env import extend_script_env
from releng_tool.util.io import ensure_dir_exists
from releng_tool.util.io import interpret_stem_extension
from releng_tool.util.io import opt_file
from releng_tool.util.io import run_script
from releng_tool.util.log import debug
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
from releng_tool.util.sort import TopologicalSorter
from releng_tool.util.string import expand
from releng_tool.util.string import interpret_dictionary_strings
from releng_tool.util.string import interpret_string
from releng_tool.util.string import interpret_strings
from releng_tool.util.string import interpret_zero_to_one_strings
import pickle
import posixpath
import pprint
import os
import traceback
import sys

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

# special value for a "default" entry in a dictionary
DEFAULT_ENTRY = '*'

#: default strip-count value for packages
DEFAULT_STRIP_COUNT = 1

# cache name for dvcs database
DVCS_CACHE_FNAME = '.dvcsdb'

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
        dvcs_cache (optional): whether or not to permit dvcs caching

    Attributes:
        opts: options used to configure the package manager
        registry: registry for extension information
        script_env: package script environment dictionary
    """
    def __init__(self, opts, registry, dvcs_cache=False):
        self.opts = opts
        self.registry = registry
        self.script_env = {}
        self._dvcs_cache = {}
        self._dvcs_cache_enabled = dvcs_cache
        self._dvcs_cache_fname = os.path.join(opts.cache_dir, DVCS_CACHE_FNAME)
        self._key_types = {}

        # load any cached dvcs information
        self._load_dvcs_cache()

        # register expected types for each configuration
        self._register_conf(Rpk.AUTOTOOLS_AUTORECONF, PkgKeyType.BOOL)
        self._register_conf(Rpk.BUILD_DEFS, PkgKeyType.DICT_STR_STR)
        self._register_conf(Rpk.BUILD_ENV, PkgKeyType.DICT_STR_STR)
        self._register_conf(Rpk.BUILD_OPTS, PkgKeyType.DICT_STR_STR_OR_STRS)
        self._register_conf(Rpk.BUILD_SUBDIR, PkgKeyType.STR)
        self._register_conf(Rpk.CMAKE_NOINSTALL, PkgKeyType.BOOL)
        self._register_conf(Rpk.CONF_DEFS, PkgKeyType.DICT_STR_STR)
        self._register_conf(Rpk.CONF_ENV, PkgKeyType.DICT_STR_STR)
        self._register_conf(Rpk.CONF_OPTS, PkgKeyType.DICT_STR_STR_OR_STRS)
        self._register_conf(Rpk.DEPS, PkgKeyType.STRS)
        self._register_conf(Rpk.DEVMODE_IGNORE_CACHE, PkgKeyType.BOOL)
        self._register_conf(Rpk.DEVMODE_REVISION, PkgKeyType.STR)
        self._register_conf(Rpk.EXTENSION, PkgKeyType.STR)
        self._register_conf(Rpk.EXTERNAL, PkgKeyType.BOOL)
        self._register_conf(Rpk.EXTOPT, PkgKeyType.DICT)
        self._register_conf(Rpk.EXTRACT_TYPE, PkgKeyType.STR)
        self._register_conf(Rpk.FETCH_OPTS, PkgKeyType.DICT_STR_STR_OR_STRS)
        self._register_conf(Rpk.FIXED_JOBS, PkgKeyType.INT_POSITIVE)
        self._register_conf(Rpk.GIT_CONFIG, PkgKeyType.DICT_STR_STR)
        self._register_conf(Rpk.GIT_DEPTH, PkgKeyType.INT_NONNEGATIVE)
        self._register_conf(Rpk.GIT_REFSPECS, PkgKeyType.STRS)
        self._register_conf(Rpk.GIT_SUBMODULES, PkgKeyType.BOOL)
        self._register_conf(Rpk.GIT_VERIFY_REVISION, PkgKeyType.BOOL)
        self._register_conf(Rpk.HOST_PROVIDES, PkgKeyType.STRS)
        self._register_conf(Rpk.INSTALL_DEFS, PkgKeyType.DICT_STR_STR)
        self._register_conf(Rpk.INSTALL_ENV, PkgKeyType.DICT_STR_STR)
        self._register_conf(Rpk.INSTALL_OPTS, PkgKeyType.DICT_STR_STR_OR_STRS)
        self._register_conf(Rpk.INSTALL_TYPE, PkgKeyType.STR)
        self._register_conf(Rpk.INTERNAL, PkgKeyType.BOOL)
        self._register_conf(Rpk.LICENSE, PkgKeyType.STRS)
        self._register_conf(Rpk.LICENSE_FILES, PkgKeyType.STRS)
        self._register_conf(Rpk.MAKE_NOINSTALL, PkgKeyType.BOOL)
        self._register_conf(Rpk.NO_EXTRACTION, PkgKeyType.BOOL)
        self._register_conf(Rpk.PREFIX, PkgKeyType.STR)
        self._register_conf(Rpk.PYTHON_INTERPRETER, PkgKeyType.STR)
        self._register_conf(Rpk.REVISION, PkgKeyType.DICT_STR_STR_OR_STR)
        self._register_conf(Rpk.SCONS_NOINSTALL, PkgKeyType.BOOL)
        self._register_conf(Rpk.SITE, PkgKeyType.DICT_STR_STR_OR_STR)
        self._register_conf(Rpk.SKIP_REMOTE_CONFIG, PkgKeyType.BOOL)
        self._register_conf(Rpk.SKIP_REMOTE_SCRIPTS, PkgKeyType.BOOL)
        self._register_conf(Rpk.STRIP_COUNT, PkgKeyType.INT_NONNEGATIVE)
        self._register_conf(Rpk.TYPE, PkgKeyType.STR)
        self._register_conf(Rpk.VCS_TYPE, PkgKeyType.DICT_STR_STR_OR_STR)
        self._register_conf(Rpk.VERSION, PkgKeyType.STR)

        # sanity check that check option is properly registered
        for key in Rpk:
            assert key in self._key_types, 'key {} is missing'.format(key)

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
        first-configured first-returned approach is used.

        Args:
            names: the names of packages to load

        Returns:
            returns an ordered list of packages to use

        Raises:
            RelengToolInvalidPackageConfiguration: when an error has been
                                                    detected loading the package
        """
        pkgs = OrderedDict()
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

            # if a package location has not been found, finally check the
            # default package directory
            if not pkg:
                pkg_script = os.path.join(self.opts.default_pkg_dir, name, name)
                pkg_script, _ = opt_file(pkg_script)

                pkg, env, deps = self.load_package(name, pkg_script)

            pkgs[pkg.name] = pkg
            for dep in deps:
                # if this is an unknown package and is not in out current list,
                # append it to the list of names to process
                if dep == name:
                    raise RelengToolCyclicPackageDependency({
                        'pkg_name': name,
                    })
                elif dep not in pkgs:
                    if dep not in names_left:
                        verbose('adding implicitly defined package: {}', dep)
                        names_left.append(dep)

                    if pkg not in final_deps:
                        final_deps[pkg] = []
                    final_deps[pkg].append(dep)
                else:
                    pkg.deps.append(pkgs[dep])
            extend_script_env(self.script_env, env)

        # for packages which have a dependency but have not been bound yet,
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
            if sorted_pkgs is None:
                raise RelengToolCyclicPackageDependency({
                    'pkg_name': name,
                })
        debug('sorted packages)')
        for pkg in sorted_pkgs:
            debug(' {}', pkg.name)

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
            known package dependencies

        Raises:
            RelengToolInvalidPackageConfiguration: when an error has been
                                                    detected loading the package
        """
        verbose('loading package: {}', name)
        debug('script {}', script)
        opts = self.opts

        if not os.path.isfile(script):
            raise RelengToolMissingPackageScript({
                'pkg_name': name,
                'script': script,
            })

        pkg_def_dir = os.path.abspath(os.path.join(script, os.pardir))
        self.script_env['DEFAULT_REVISION'] = DEFAULT_ENTRY
        self.script_env['DEFAULT_SITE'] = DEFAULT_ENTRY
        self.script_env['PKG_DEFDIR'] = pkg_def_dir

        try:
            env = run_script(script, self.script_env, catch=False)
        except Exception as e:
            raise RelengToolInvalidPackageScript({
                'description': str(e),
                'script': script,
                'traceback': traceback.format_exc(),
            })

        self._active_package = name
        self._active_env = env

        # prepare helper expand values
        expand_extra = {
        }

        # version/revision extraction first
        #
        # Pull the version/revision(s) information first. This information can
        # be used for pulling specific revisions for sources and other minor
        # things such where projects may be extracted to, etc. The "version"
        # value is typically used for naming output folders, display, etc.;
        # where as a "revision" value is typically for identify what sources
        # to clone from (for DVCS). If a revision value is not specified, it
        # will be populated with the same value as the version value.
        #
        # A package may have multiple revisions. Typically a "default" (`*`)
        # revision or other revisions which may be triggered based of a user
        # configuring for "development mode". At the end of parsing, the
        # `pkg_revision` value should be a single string value (even empty).
        #
        # Support still exists for a development revision (`DEVMODE_REVISION`)
        # value (although deprecated). The package's revision may be overriden
        # with this value based on various scenarios.

        # version
        pkg_version = self._fetch(Rpk.VERSION, default='')

        pkg_version_key = pkg_key(name, Rpk.VERSION)
        expand_extra[pkg_version_key] = pkg_version

        # development mode revision (may deprecate)
        pkg_devmode_revision = self._fetch(Rpk.DEVMODE_REVISION,
            allow_expand=True, expand_extra=expand_extra)

        # revisions
        pkg_devmode = False
        pkg_revision = None

        if opts.revision_override:
            pkg_revision = opts.revision_override.get(name)
            pkg_devmode = True if pkg_revision else False

        if not pkg_revision:
            pkg_revision_raw = self._fetch(Rpk.REVISION,
                allow_expand=True, expand_extra=expand_extra)
            if pkg_revision_raw:
                # user has a defined a series of revision entries -- find the
                # revision value based off out current mode (i.e. if in
                # development mode, use the approriate key; otherwise default
                # to a `*` key, if it exists)
                if isinstance(pkg_revision_raw, dict):
                    pkg_revision = pkg_revision_raw.get(opts.devmode)
                    pkg_devmode = True if pkg_revision else False

                    # no explicit revision, check the "default/any" revision
                    if not pkg_revision:
                        pkg_revision = pkg_revision_raw.get(DEFAULT_ENTRY)

                    # no default revision to use for this mode, check if the
                    # deprecated devmode-revision value is set
                    if not pkg_revision and \
                            opts.devmode and pkg_devmode_revision:
                        pkg_revision = pkg_devmode_revision
                        pkg_devmode = True if pkg_revision else False

                    # lastly, if no revision has been found, default to the
                    # package's version
                    if not pkg_revision:
                        pkg_revision = pkg_version

                # if this is a single revision string, use this value for
                # the revision; with the exception if we are in development
                # mode and the deprecated devmode-revision value is set
                else:
                    if opts.devmode and pkg_devmode_revision:
                        pkg_revision = pkg_devmode_revision
                        pkg_devmode = True
                    else:
                        pkg_revision = pkg_revision_raw

            # if we do not have package revision information provided, we
            # will default to the using the package's version; with the
            # exception if we are in development mode and the deprecated
            # devmode-revision value is set
            else:
                if opts.devmode and pkg_devmode_revision:
                    pkg_revision = pkg_devmode_revision
                    pkg_devmode = True
                else:
                    pkg_revision = pkg_version

        # always ensure a revision is set; use the version value if no
        # explicit revision is provided
        if not pkg_revision:
            pkg_revision = pkg_version

        pkg_revision_key = pkg_key(name, Rpk.REVISION)
        expand_extra[pkg_revision_key] = pkg_revision

        # if we have replaced the revision with a development-specific value,
        # also replace the package's version to better reflect the version of
        # the package is not expected
        if pkg_devmode:
            pkg_version = pkg_revision
            expand_extra[pkg_version_key] = pkg_version

        # site / vcs-site detection
        #
        # After extracted required version information, the site / VCS type
        # needs to be checked next. This will allow the manage to early detect
        # if a version/revision field is required, and fail early if we have
        # not detected one from above.

        # site
        if opts.sites_override and name in opts.sites_override:
            # Site overriding is permitted to help in scenarios where a builder
            # is unable to acquire a package's source from the defined site.
            # This includes firewall settings or a desire to use a mirrored
            # source when experiencing network connectivity issues.
            pkg_site = opts.sites_override[name]
        else:
            pkg_site = None
            pkg_site_raw = self._fetch(Rpk.SITE,
                allow_expand=True, expand_extra=expand_extra)

            if pkg_site_raw:
                # user has a defined a series of site entries -- find the
                # site value based off out current mode (i.e. if in
                # development mode, use the approriate key; otherwise default
                # to a `*` key, if it exists)
                if isinstance(pkg_site_raw, dict):
                    pkg_site = pkg_site_raw.get(opts.devmode)

                    # no explicit site, check the "default/any" site
                    if not pkg_site:
                        pkg_site = pkg_site_raw.get(DEFAULT_ENTRY)
                else:
                    pkg_site = pkg_site_raw

        # On Windows, if a file site is provided, ensure the path value is
        # converted to a posix-styled path, to prevent issues with `urlopen`
        # being provided an unescaped path string
        if sys.platform == 'win32' and \
                pkg_site and pkg_site.startswith('file://'):
            pkg_site = pkg_site[len('file://'):]
            abs_site = os.path.isabs(pkg_site)
            pkg_site = pkg_site.replace(os.sep, posixpath.sep)
            if abs_site:
                pkg_site = '/' + pkg_site
            pkg_site = 'file://' + pkg_site

        # vcs-type
        pkg_vcs_type = None
        pkg_vcs_type_raw = self._fetch(Rpk.VCS_TYPE)
        if pkg_vcs_type_raw:
            # user has a defined a series of vcs-type entries -- find the
            # vcs-type value based off out current mode (i.e. if in
            # development mode, use the approriate key; otherwise default
            # to a `*` key, if it exists)
            if isinstance(pkg_vcs_type_raw, dict):
                if pkg_vcs_type_raw.get(opts.devmode):
                    pkg_vcs_type_raw = pkg_vcs_type_raw.get(opts.devmode)
                # no explicit site, check the "default/any" site
                else:
                    pkg_vcs_type_raw = pkg_vcs_type_raw.get(DEFAULT_ENTRY)

            if pkg_vcs_type_raw:
                pkg_vcs_type_raw = pkg_vcs_type_raw.lower()
                if pkg_vcs_type_raw in VcsType:
                    pkg_vcs_type = pkg_vcs_type_raw
                elif pkg_vcs_type_raw in self.registry.fetch_types:
                    pkg_vcs_type = pkg_vcs_type_raw
                else:
                    raise RelengToolUnknownVcsType({
                        'pkg_name': name,
                        'pkg_key': pkg_key(name, Rpk.VCS_TYPE),
                    })

        if not pkg_vcs_type:
            if pkg_site:
                site_lc = pkg_site.lower()
                if site_lc.startswith('bzr+'):
                    pkg_site = pkg_site[4:]
                    pkg_vcs_type = VcsType.BZR
                elif site_lc.startswith('cvs+'):
                    pkg_site = pkg_site[4:]
                    pkg_vcs_type = VcsType.CVS
                elif site_lc.startswith((
                        ':ext:',
                        ':extssh:',
                        ':gserver:',
                        ':kserver:',
                        ':pserver:',
                        )):
                    pkg_vcs_type = VcsType.CVS
                elif site_lc.startswith('git+'):
                    pkg_site = pkg_site[4:]
                    pkg_vcs_type = VcsType.GIT
                elif site_lc.endswith('.git'):
                    pkg_vcs_type = VcsType.GIT
                elif site_lc.startswith('hg+'):
                    pkg_site = pkg_site[3:]
                    pkg_vcs_type = VcsType.HG
                elif site_lc.startswith('rsync+'):
                    pkg_site = pkg_site[6:]
                    pkg_vcs_type = VcsType.RSYNC
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

        if pkg_vcs_type == VcsType.LOCAL:
            warn('package using local content: {}', name)

        # check if the detected vcs type needs a revision, and fail if we do
        # not have one
        if not pkg_revision and pkg_vcs_type in (
                VcsType.BZR,
                VcsType.CVS,
                VcsType.GIT,
                VcsType.HG,
                VcsType.SVN,
                ):
            raise RelengToolMissingPackageRevision({
                'pkg_name': name,
                'pkg_key1': pkg_key(name, Rpk.VERSION),
                'pkg_key2': pkg_key(name, Rpk.REVISION),
                'vcs_type': pkg_vcs_type,
            })

        # archive extraction strip count
        pkg_strip_count = self._fetch(Rpk.STRIP_COUNT,
            default=DEFAULT_STRIP_COUNT)

        # build subdirectory
        pkg_build_subdir = self._fetch(Rpk.BUILD_SUBDIR)

        # dependencies
        deps = self._fetch(Rpk.DEPS, default=[])

        # ignore cache
        pkg_devmode_ignore_cache = self._fetch(Rpk.DEVMODE_IGNORE_CACHE)

        # extension (override)
        pkg_filename_ext = self._fetch(Rpk.EXTENSION)

        # extract type
        pkg_extract_type = self._fetch(Rpk.EXTRACT_TYPE)
        if pkg_extract_type:
            pkg_extract_type = pkg_extract_type.lower()

            if pkg_extract_type not in self.registry.extract_types:
                raise RelengToolUnknownExtractType({
                    'pkg_name': name,
                    'pkg_key': pkg_key(name, Rpk.EXTRACT_TYPE),
                })

        # host tools provided
        pkg_host_provides = self._fetch(Rpk.HOST_PROVIDES)

        # is-external
        pkg_is_external = self._fetch(Rpk.EXTERNAL)

        # is-internal
        pkg_is_internal = self._fetch(Rpk.INTERNAL)

        # no extraction
        pkg_no_extraction = self._fetch(Rpk.NO_EXTRACTION)

        # skip any remote configuration
        pkg_skip_remote_config = self._fetch(Rpk.SKIP_REMOTE_CONFIG)

        # skip any remote scripts
        pkg_skip_remote_scripts = self._fetch(Rpk.SKIP_REMOTE_SCRIPTS)

        # type
        pkg_type = None
        pkg_type_raw = self._fetch(Rpk.TYPE)
        if pkg_type_raw:
            pkg_type_raw = pkg_type_raw.lower()
            if pkg_type_raw in PackageType:
                pkg_type = pkg_type_raw
            elif pkg_type_raw in self.registry.package_types:
                pkg_type = pkg_type_raw
            else:
                raise RelengToolUnknownPackageType({
                    'pkg_name': name,
                    'pkg_key': pkg_key(name, Rpk.TYPE),
                })

        if not pkg_type:
            pkg_type = PackageType.SCRIPT

        # ######################################################################

        # git configuration options for a repository
        pkg_git_config = self._fetch(Rpk.GIT_CONFIG)

        # git-depth
        pkg_git_depth = self._fetch(Rpk.GIT_DEPTH)

        # git-refspecs
        pkg_git_refspecs = self._fetch(Rpk.GIT_REFSPECS)

        # git-submodules
        pkg_git_submodules = self._fetch(Rpk.GIT_SUBMODULES)

        # git-verify
        pkg_git_verify_revision = self._fetch(Rpk.GIT_VERIFY_REVISION)

        # ######################################################################

        # checks
        if pkg_is_external is not None and pkg_is_internal is not None:
            if pkg_is_external == pkg_is_internal:
                raise RelengToolConflictingConfiguration({
                    'pkg_name': name,
                    'pkg_key1': pkg_key(name, Rpk.EXTERNAL),
                    'pkg_key2': pkg_key(name, Rpk.INTERNAL),
                    'desc': 'package flagged as external and internal',
                })
        elif pkg_is_external is not None:
            pkg_is_internal = not pkg_is_external
        elif pkg_is_internal is not None:
            pass
        elif opts.default_internal_pkgs:
            pkg_is_internal = True
        else:
            pkg_is_internal = False

        # check a site is defined for vcs types which require it
        if not pkg_site and pkg_vcs_type in (
                VcsType.BZR,
                VcsType.CVS,
                VcsType.GIT,
                VcsType.HG,
                VcsType.RSYNC,
                VcsType.SCP,
                VcsType.SVN,
                VcsType.URL,
                ):
            raise RelengToolMissingPackageSite({
                'pkg_name': name,
                'pkg_key': pkg_key(name, Rpk.SITE),
                'vcs_type': pkg_vcs_type,
            })

        # list of support dvcs types
        SUPPORTED_DVCS = [
            VcsType.GIT,
            VcsType.HG,
        ]
        is_pkg_dvcs = (pkg_vcs_type in SUPPORTED_DVCS)

        # find possible extension for a cache file
        #
        # non-dvcs's will be always gzip-tar'ed.
        if pkg_vcs_type in (
                VcsType.BZR,
                VcsType.CVS,
                VcsType.RSYNC,
                VcsType.SVN,
                ):
            cache_ext = 'tgz'
        # dvcs's will not have an extension type
        elif is_pkg_dvcs:
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

        # prepare package container and directory locations
        #
        # The container folder for a package will typically be a combination of
        # a package's name plus version. If no version is set, the container
        # will be only use the package's name. We try to use the version entry
        # when possible to help manage multiple versions of output (e.g. to
        # avoid conflicts when bumping versions).
        #
        # When the version value is used, we will attempt to cleanup/minimize
        # the version to help provide the container a more "sane" path. For
        # instance, if a version references a path-styled branch names (e.g.
        # `bugfix/my-bug`, we want to avoid promoting a container name which
        # can result in a sub-directory being made (e.g. `pkg-bugfix/my-bug/`).
        if pkg_version:
            pkg_nv = '{}-{}'.format(name, ''.join(
                x if (x.isalnum() or x in '-._') else '_' for x in pkg_version))
        else:
            pkg_nv = name

        pkg_build_output_dir = os.path.join(opts.build_dir, pkg_nv)

        pkg_is_local = pkg_vcs_type == VcsType.LOCAL
        if pkg_is_local:
            pkg_build_dir = pkg_def_dir
        else:
            pkg_build_dir = pkg_build_output_dir

        # check if an internal package is configured to point to a local
        # directory for sources
        pkg_local_srcs = False
        if pkg_is_internal and not pkg_is_local and opts.local_srcs:
            # specific package name reference in the local sources; either is
            # set to the path to use, or is set to `None` to indicate at this
            # package should not be retrieved locally
            if name in opts.local_srcs:
                if opts.local_srcs[name]:
                    pkg_build_dir = opts.local_srcs[name]
                    pkg_local_srcs = True

            # check if the "global" local sources path exists; either set to
            # a specific path, or set to `None` to indicate that it will use
            # the parent path based off the root directory
            elif GBL_LSRCS in opts.local_srcs:
                if opts.local_srcs[GBL_LSRCS]:
                    container_dir = opts.local_srcs[GBL_LSRCS]
                else:
                    container_dir = os.path.dirname(opts.root_dir)

                pkg_build_dir = os.path.join(container_dir, name)
                pkg_local_srcs = True

            if pkg_build_dir == opts.root_dir:
                raise RelengToolConflictingLocalSrcsPath({
                    'pkg_name': name,
                    'root': opts.root_dir,
                    'path': pkg_build_dir,
                })

        if pkg_build_subdir:
            pkg_build_subdir = os.path.join(pkg_build_dir, pkg_build_subdir)

        cache_dir = os.path.join(opts.dl_dir, name)
        if cache_ext:
            pkg_cache_file = os.path.join(cache_dir, pkg_nv + '.' + cache_ext)
        else:
            pkg_cache_file = os.path.join(cache_dir, pkg_nv)

        # Select sources (like CMake-based projects) may wish to be using
        # out-of-source tree builds. For supported project types, adjust the
        # build output directory to a sub-folder of the originally assumed
        # output folder.
        if pkg_type == PackageType.CMAKE:
            pkg_build_output_dir = os.path.join(
                pkg_build_output_dir, 'releng-output')

        # determine the build tree for a package
        #
        # A build tree (introduced for the libfoo-exec action), tracks the
        # directory where build commands would typically be executed for a
        # package on a host system. In most cases, this will be set to the
        # same path as `pkg_build_dir` (or the sub-directory, if provided);
        # however, some package types may have a better working directory
        # for build commands. For example, CMake projects will generate a
        # build package in an out-of-source directory (e.g.
        # `pkg_build_output_dir`), which is a better make to issue commands
        # such as "cmake --build .".
        if pkg_type == PackageType.CMAKE:
            pkg_build_tree = pkg_build_output_dir
        elif pkg_build_subdir:
            pkg_build_tree = pkg_build_subdir
        else:
            pkg_build_tree = pkg_build_dir

        # determine the package directory for this package
        #
        # Typically, a package's "cache directory" will be stored in the output
        # folder's "cache/<pkg-name>" path. However, having package-name driven
        # cache folder targets does not provide an easy way to manage sharing
        # caches between projects if they share the same content (either the
        # same site or sharing submodules). Cache targets for packages will be
        # stored in a database and can be used here to decide if a package's
        # cache will actually be stored in a different container.
        pkg_cache_dir = os.path.join(opts.cache_dir, name)
        if is_pkg_dvcs:
            ckey = pkg_cache_key(pkg_site)

            pkg_cache_dirname = name

            # if the default cache directory exists, always prioritize it (and
            # force update the cache location)
            if os.path.exists(pkg_cache_dir):
                self._dvcs_cache[name] = name
            # if the cache content is stored in another container, use it
            elif ckey in self._dvcs_cache:
                pkg_cache_dirname = self._dvcs_cache[ckey]
                verbose('alternative cache path for package: {} -> {}',
                    name, pkg_cache_dirname)

            # track ckey entry to point to our cache container
            #
            # This package's "ckey" will be used to cache the target folder
            # being used for this package, so other packages with matching site
            # values could use it. In the rare case that the "ckey" entry
            # already exists but is pointing to another folder that our target
            # one, leave it as is (assume ownership of key is managed by another
            # package).
            if ckey not in self._dvcs_cache:
                self._dvcs_cache[ckey] = pkg_cache_dirname

            # adjust the cache directory and save any new cache changes
            pkg_cache_dir = os.path.join(opts.cache_dir, pkg_cache_dirname)
            self._save_dvcs_cache()

        # (commons)
        pkg = RelengPackage(name, pkg_version)
        pkg.asc_file = os.path.join(pkg_def_dir, name + '.asc')
        pkg.build_dir = pkg_build_dir
        pkg.build_output_dir = pkg_build_output_dir
        pkg.build_subdir = pkg_build_subdir
        pkg.build_tree = pkg_build_tree
        pkg.cache_dir = pkg_cache_dir
        pkg.cache_file = pkg_cache_file
        pkg.def_dir = pkg_def_dir
        pkg.devmode = pkg_devmode
        pkg.devmode_ignore_cache = pkg_devmode_ignore_cache
        pkg.extract_type = pkg_extract_type
        pkg.git_config = pkg_git_config
        pkg.git_depth = pkg_git_depth
        pkg.git_refspecs = pkg_git_refspecs
        pkg.git_submodules = pkg_git_submodules
        pkg.git_verify_revision = pkg_git_verify_revision
        pkg.hash_file = os.path.join(pkg_def_dir, name + '.hash')
        pkg.host_provides = pkg_host_provides
        pkg.is_internal = pkg_is_internal
        pkg.local_srcs = pkg_local_srcs
        pkg.no_extraction = pkg_no_extraction
        pkg.revision = pkg_revision
        pkg.site = pkg_site
        pkg.skip_remote_config = pkg_skip_remote_config
        pkg.skip_remote_scripts = pkg_skip_remote_scripts
        pkg.strip_count = pkg_strip_count
        pkg.type = pkg_type
        pkg.vcs_type = pkg_vcs_type

        self._apply_postinit_options(pkg)

        # (additional environment helpers)
        for env in (os.environ, env):
            env[pkg_key(name, 'BUILD_DIR')] = pkg_build_dir
            env[pkg_key(name, 'BUILD_OUTPUT_DIR')] = pkg_build_output_dir
            env[pkg_key(name, 'DEFDIR')] = pkg_def_dir
            env[pkg_key(name, 'NAME')] = name
            env[pkg_key(name, 'REVISION')] = pkg_revision
        os.environ[pkg_key(name, Rpk.VERSION)] = pkg_version

        # (internals)
        prefix = '.releng_tool-stage-'
        outdir = pkg.build_output_dir
        pkg._ff_bootstrap = os.path.join(outdir, prefix + 'bootstrap')
        pkg._ff_build = os.path.join(outdir, prefix + 'build')
        pkg._ff_configure = os.path.join(outdir, prefix + 'configure')
        pkg._ff_extract = os.path.join(outdir, prefix + 'extract')
        pkg._ff_install = os.path.join(outdir, prefix + 'install')
        pkg._ff_license = os.path.join(outdir, prefix + 'license')
        pkg._ff_patch = os.path.join(outdir, prefix + 'patch')
        pkg._ff_post = os.path.join(outdir, prefix + 'post')

        # dump package attributes if running in a debug mode
        if opts.debug:
            info = {}
            for key, value in pkg.__dict__.items():
                if not key.startswith('_'):
                    info[key] = value

            debug('''package-data: {}
==============================
{}
==============================''', name, pprint.pformat(info))

        return pkg, env, deps

    def _apply_postinit_options(self, pkg):
        """
        apply post-initialization package options

        Using the active package instance/environment, this call will fetch a
        subset of post-initialization-supported package configuration options
        and apply them onto the package instance. This call will set a package
        attribute only if the attribute has yet to be configured. This allows
        applying package options with multiple environments where an additional
        environment may have additional information to "complete" a package's
        configuration state.

        Args:
            pkg: the package

        Raises:
            RelengToolInvalidPackageConfiguration: when an error has been
                                                    detected loading a package
                                                    option
        """

        # ######################################################################
        # (common)
        # ######################################################################

        # extension modifiers
        if pkg.ext_modifiers is None:
            pkg.ext_modifiers = self._fetch(Rpk.EXTOPT)

        # fetch options
        if pkg.fetch_opts is None:
            pkg.fetch_opts = self._fetch(Rpk.FETCH_OPTS)

        # fixed jobs
        if pkg.fixed_jobs is None:
            pkg.fixed_jobs = self._fetch(Rpk.FIXED_JOBS)

        # install type
        if pkg.install_type is None:
            pkg_install_type_raw = self._fetch(Rpk.INSTALL_TYPE)
            if pkg_install_type_raw:
                pkg_install_type_raw = pkg_install_type_raw.lower()
                if pkg_install_type_raw in PackageInstallType:
                    pkg.install_type = pkg_install_type_raw
                else:
                    raise RelengToolUnknownInstallType({
                        'pkg_name': pkg.name,
                        'pkg_key': pkg_key(pkg.name, Rpk.INSTALL_TYPE),
                    })

        # license
        if pkg.license is None:
            pkg.license = self._fetch(Rpk.LICENSE)

        # license files
        if pkg.license_files is None:
            pkg.license_files = self._fetch(Rpk.LICENSE_FILES)

        # prefix
        if pkg.prefix is None:
            pkg.prefix = self._fetch(Rpk.PREFIX)

        # ######################################################################
        # (package type - shared)
        # ######################################################################

        # package-type build definitions
        if pkg.build_defs is None:
            pkg.build_defs = self._fetch(Rpk.BUILD_DEFS)

        # package-type build environment options
        if pkg.build_env is None:
            pkg.build_env = self._fetch(Rpk.BUILD_ENV)

        # package-type build options
        if pkg.build_opts is None:
            pkg.build_opts = self._fetch(Rpk.BUILD_OPTS)

        # package-type configuration definitions
        if pkg.conf_defs is None:
            pkg.conf_defs = self._fetch(Rpk.CONF_DEFS)

        # package-type configuration environment options
        if pkg.conf_env is None:
            pkg.conf_env = self._fetch(Rpk.CONF_ENV)

        # package-type configuration options
        if pkg.conf_opts is None:
            pkg.conf_opts = self._fetch(Rpk.CONF_OPTS)

        # package-type installation definitions
        if pkg.install_defs is None:
            pkg.install_defs = self._fetch(Rpk.INSTALL_DEFS)

        # package-type installation environment options
        if pkg.install_env is None:
            pkg.install_env = self._fetch(Rpk.INSTALL_ENV)

        # package-type installation options
        if pkg.install_opts is None:
            pkg.install_opts = self._fetch(Rpk.INSTALL_OPTS)

        # ######################################################################
        # (package type - autotools)
        # ######################################################################

        # autotools autoreconf flag
        if pkg.autotools_autoreconf is None:
            pkg.autotools_autoreconf = self._fetch(Rpk.AUTOTOOLS_AUTORECONF)

        # ######################################################################
        # (package type - cmake)
        # ######################################################################

        # cmake noinstall flag
        if pkg.cmake_noinstall is None:
            pkg.cmake_noinstall = self._fetch(Rpk.CMAKE_NOINSTALL)

        # ######################################################################
        # (package type - make)
        # ######################################################################

        # make noinstall flag
        if pkg.make_noinstall is None:
            pkg.make_noinstall = self._fetch(Rpk.MAKE_NOINSTALL)

        # ######################################################################
        # (package type - python)
        # ######################################################################

        # python interpreter
        if pkg.python_interpreter is None:
            pkg_python_interpreter = self._fetch(Rpk.PYTHON_INTERPRETER)
            pkg.python_interpreter = pkg_python_interpreter

        # ######################################################################
        # (package type - scons)
        # ######################################################################

        # scons noinstall flag
        if pkg.scons_noinstall is None:
            pkg.scons_noinstall = self._fetch(Rpk.SCONS_NOINSTALL)

        # ######################################################################
        # (post checks)
        # ######################################################################

        if pkg.host_provides and pkg.install_type != PackageInstallType.HOST:
            warn('non-host package providing host package: {}', pkg.name)
            pkg.host_provides = None

    def load_remote_configuration(self, pkg):
        """
        attempt to load any remote configuration options for a package

        This call will scan select output locations of a package's content for
        any releng-tool-specific package configurations to late-load into a
        package definition.

        Args:
            pkg: the package

        Raises:
            RelengToolInvalidPackageConfiguration: when an error has been
                                                    detected loading any of the
                                                    package's extended options
        """

        target_remote_configurations = [
            os.path.join(pkg.build_dir, RELENG_CONF_EXTENDED_NAME)
        ]

        if pkg.build_subdir:
            target_remote_configurations.append(
                os.path.join(pkg.build_subdir, RELENG_CONF_EXTENDED_NAME))

        # find the first available script to load from
        for target in target_remote_configurations:
            pkg_script, pkg_script_exists = opt_file(target)
            if pkg_script_exists:
                # attempt to finalize the package
                self.finalize_package(pkg, pkg_script)
                break

    def finalize_package(self, pkg, script):
        """
        finalize configuration for a package

        Attempts to finalize any configuration entries of an already populated
        package instance with options provided at a later stage in the
        releng-tool process. This is to support projects where select
        configuration options are defined in the package's source content,
        instead of the main releng-tool project.

        This call will accept as package instance to update and the script file
        which may include a series of configuration options to apply to a
        package. Note that any configuration option already set on the package
        will be used over any new detected package option.

        Args:
            pkg: the package
            script: the package script to load

        Raises:
            RelengToolInvalidPackageConfiguration: when an error has been
                                                    detected loading any of the
                                                    package's extended options
        """
        verbose('finalize package configuration: {}', pkg.name)
        debug('script {}', script)

        if not os.path.isfile(script):
            raise RelengToolMissingPackageScript({
                'pkg_name': pkg.name,
                'script': script,
            })

        try:
            env = run_script(script, self.script_env, catch=False)
        except Exception as e:
            raise RelengToolInvalidPackageScript({
                'description': str(e),
                'script': script,
                'traceback': traceback.format_exc(),
            })

        # apply any options to unset configuration entries
        self._active_package = pkg.name
        self._active_env = env
        self._apply_postinit_options(pkg)

        # extend the active script environment if the post-init call succeeds
        extend_script_env(self.script_env, env)

    def _fetch(self, key, default=None, allow_expand=False,
            expand_extra=None):
        """
        fetch a configuration value from a provided key

        Package definitions will define one or more key-value configurations for
        the release engineering process to use. For specific keys, there will be
        expected value types where a key is provided. The fetch operation can be
        provided a key and will return the desired value; however, if the value
        is of a value that is not supported, an exception
        ``RelengToolInvalidPackageKeyValue`` is raised.

        Args:
            key: the key
            default (optional): default value to use if the key does not exist
            allow_expand (optional): whether or not to expand the value
            expand_extra (optional): extra expand defines to use

        Returns:
            the value

        Raises:
            RelengToolInvalidPackageKeyValue: value type is invalid for the key
        """

        self._active_key = key
        type_ = self._key_types[key]
        value = default

        pkg_name = self._active_package
        pkg_key_ = pkg_key(pkg_name, key)

        def raise_kv_exception(type_):
            raise RelengToolInvalidPackageKeyValue({
                'pkg_name': pkg_name,
                'pkg_key': pkg_key_,
                'expected_type': type_,
            })

        # check if this package key has been explicitly overridden; if so,
        # use its contents for the raw value to process
        raw_value = self.opts.injected_kv.get(pkg_key_, None)

        # if no raw value was injected, pull the key's value (if any) from the
        # active environment
        if raw_value is None:
            raw_value = self._active_env.get(pkg_key_, None)

        if raw_value is not None:
            if type_ == PkgKeyType.BOOL:
                value = raw_value
                if not isinstance(value, bool):
                    raise_kv_exception('bool')
            elif type_ == PkgKeyType.DICT:
                value = raw_value
                if allow_expand:
                    value = expand(value, expand_extra)
                if not isinstance(value, dict):
                    raise_kv_exception('dictionary')
            elif type_ == PkgKeyType.DICT_STR_STR:
                value = interpret_dictionary_strings(raw_value)
                if allow_expand:
                    value = expand(value, expand_extra)
                if value is None:
                    raise_kv_exception('dict(str,str)')
            elif type_ == PkgKeyType.DICT_STR_STR_OR_STR:
                value = interpret_string(raw_value)
                if not value:
                    value = raw_value
                    if not isinstance(value, dict):
                        raise_kv_exception('dict(str,str) or string')
                if allow_expand:
                    value = expand(value, expand_extra)
            elif type_ == PkgKeyType.DICT_STR_STR_OR_STRS:
                value = interpret_zero_to_one_strings(raw_value)
                if allow_expand:
                    value = expand(value, expand_extra)
                if value is None:
                    raise_kv_exception('dict(str,str) or string(s)')
            elif type_ == PkgKeyType.STR:
                value = interpret_string(raw_value)
                if allow_expand:
                    value = expand(value, expand_extra)
                if value is None:
                    raise_kv_exception('string')
            elif type_ == PkgKeyType.STRS:
                value = interpret_strings(raw_value)
                if allow_expand:
                    value = expand(value, expand_extra)
                if value is None:
                    raise_kv_exception('string(s)')
            elif type_ == PkgKeyType.INT_NONNEGATIVE:
                value = raw_value
                if not isinstance(value, int) or value < 0:
                    raise_kv_exception('non-negative int')
            elif type_ == PkgKeyType.INT_POSITIVE:
                value = raw_value
                if not isinstance(value, int) or value <= 0:
                    raise_kv_exception('positive int')
            else:
                raise_kv_exception('<unsupported key-value>')

        return value

    def _load_dvcs_cache(self):
        """
        load any persisted dvcs cache information

        DVCS can be cached and shared over multiple projects. The following
        loads any cached DVCS database stored in the project's output folder
        where may hint the folder name for a project's cache.
        """

        if not self._dvcs_cache_enabled:
            return

        if os.path.exists(self._dvcs_cache_fname):
            try:
                with open(self._dvcs_cache_fname, 'rb') as f:
                    self._dvcs_cache = pickle.load(f)
                debug('loaded dvcs cache database')
            except IOError:
                verbose('failed to load dvcs cache database (io error)')
            except ValueError:
                verbose('failed to load dvcs cache database (pickle error)')

    def _save_dvcs_cache(self):
        """
        save dvcs cache information

        Will save any DVCS cache information which future runs of releng-tool
        can be used to hint where package cache data is stored.
        """

        if not self._dvcs_cache_enabled:
            return

        if not ensure_dir_exists(self.opts.cache_dir):
            verbose('unable to generate output directory for dvcs cache')
            return

        try:
            with open(self._dvcs_cache_fname, 'wb') as f:
                pickle.dump(self._dvcs_cache, f,
                    protocol=2) # 2 for py2/py3 support
            debug('saved dvcs cache')
        except IOError:
            verbose('failed to save dvcs cache')

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

        assert key not in self._key_types, 'key {} is registered'.format(key)
        self._key_types[key] = type_
