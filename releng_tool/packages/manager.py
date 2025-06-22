# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from collections import OrderedDict
from releng_tool.defs import DEFAULT_CMAKE_BUILD_TYPE
from releng_tool.defs import GBL_LSRCS
from releng_tool.defs import PackageInstallType
from releng_tool.defs import PackageType
from releng_tool.defs import PythonSetupType
from releng_tool.defs import Rpk
from releng_tool.defs import VcsType
from releng_tool.engine.bootstrap import BOOTSTRAP_SCRIPT
from releng_tool.engine.post import POST_SCRIPT
from releng_tool.engine.script.build import BUILD_SCRIPT
from releng_tool.engine.script.configure import CONFIGURE_SCRIPT
from releng_tool.engine.script.install import INSTALL_SCRIPT
from releng_tool.opts import RELENG_CONF_EXTENDED_NAME
from releng_tool.packages import PkgKeyType
from releng_tool.packages import pkg_cache_key
from releng_tool.packages import pkg_key
from releng_tool.packages import raw_value_parse
from releng_tool.packages.exceptions import RelengToolConflictingConfiguration
from releng_tool.packages.exceptions import RelengToolConflictingLocalSrcsPath
from releng_tool.packages.exceptions import RelengToolCyclicPackageDependency
from releng_tool.packages.exceptions import RelengToolInvalidPackageKeyValue
from releng_tool.packages.exceptions import RelengToolInvalidPackageScript
from releng_tool.packages.exceptions import RelengToolMissingPackageRevision
from releng_tool.packages.exceptions import RelengToolMissingPackageScript
from releng_tool.packages.exceptions import RelengToolMissingPackageSite
from releng_tool.packages.exceptions import RelengToolPathPackageTraversal
from releng_tool.packages.exceptions import RelengToolUnknownExtractType
from releng_tool.packages.exceptions import RelengToolUnknownInstallType
from releng_tool.packages.exceptions import RelengToolUnknownPackageType
from releng_tool.packages.exceptions import RelengToolUnknownPythonSetupType
from releng_tool.packages.exceptions import RelengToolUnknownVcsType
from releng_tool.packages.package import RelengPackage
from releng_tool.packages.site import site_vcs
from releng_tool.util.env import env_wrap
from releng_tool.util.env import extend_script_env
from releng_tool.util.io import interpret_stem_extension
from releng_tool.util.io import run_script
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.io_opt_file import opt_file
from releng_tool.util.log import debug
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
from releng_tool.util.path import P
from releng_tool.util.sort import TopologicalSorter
from releng_tool.util.spdx import spdx_extract
from releng_tool.util.spdx import spdx_license_identifier
from releng_tool.util.string import expand
from urllib.parse import urlparse
import os
import pickle
import posixpath
import pprint
import re
import sys
import traceback


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
        regval = [
            (Rpk.AUTOTOOLS_AUTORECONF, PkgKeyType.BOOL),
            (Rpk.BUILD_DEFS, PkgKeyType.DICT_STR_PSTR),
            (Rpk.BUILD_ENV, PkgKeyType.DICT_STR_PSTR),
            (Rpk.BUILD_OPTS, PkgKeyType.OPTS),
            (Rpk.BUILD_SUBDIR, PkgKeyType.PSTR),
            (Rpk.CARGO_NAME, PkgKeyType.STR),
            (Rpk.CARGO_NOINSTALL, PkgKeyType.BOOL),
            (Rpk.CMAKE_BUILD_TYPE, PkgKeyType.STR),
            (Rpk.CMAKE_NOINSTALL, PkgKeyType.BOOL),
            (Rpk.CONF_DEFS, PkgKeyType.DICT_STR_PSTR),
            (Rpk.CONF_ENV, PkgKeyType.DICT_STR_PSTR),
            (Rpk.CONF_OPTS, PkgKeyType.OPTS),
            (Rpk.DEPS, PkgKeyType.STRS),
            (Rpk.DEVMODE_IGNORE_CACHE, PkgKeyType.BOOL),
            (Rpk.DEVMODE_REVISION, PkgKeyType.STR),
            (Rpk.ENV, PkgKeyType.DICT_STR_PSTR),
            (Rpk.EXTENSION, PkgKeyType.STR),
            (Rpk.EXTERNAL, PkgKeyType.BOOL),
            (Rpk.EXTOPT, PkgKeyType.DICT),
            (Rpk.EXTRACT_TYPE, PkgKeyType.STR),
            (Rpk.FETCH_OPTS, PkgKeyType.OPTS),
            (Rpk.FIXED_JOBS, PkgKeyType.INT_POSITIVE),
            (Rpk.GIT_CONFIG, PkgKeyType.DICT_STR_PSTR),
            (Rpk.GIT_DEPTH, PkgKeyType.INT_NONNEGATIVE),
            (Rpk.GIT_REFSPECS, PkgKeyType.STRS),
            (Rpk.GIT_SUBMODULES, PkgKeyType.BOOL),
            (Rpk.GIT_VERIFY_REVISION, PkgKeyType.BOOL),
            (Rpk.HOST_PROVIDES, PkgKeyType.STRS),
            (Rpk.INSTALL_DEFS, PkgKeyType.DICT_STR_PSTR),
            (Rpk.INSTALL_ENV, PkgKeyType.DICT_STR_PSTR),
            (Rpk.INSTALL_OPTS, PkgKeyType.OPTS),
            (Rpk.INSTALL_TYPE, PkgKeyType.STR),
            (Rpk.INTERNAL, PkgKeyType.BOOL),
            (Rpk.LICENSE, PkgKeyType.STRS),
            (Rpk.LICENSE_FILES, PkgKeyType.STRS),
            (Rpk.MAKE_NOINSTALL, PkgKeyType.BOOL),
            (Rpk.MESON_NOINSTALL, PkgKeyType.BOOL),
            (Rpk.NEEDS, PkgKeyType.STRS),
            (Rpk.NO_EXTRACTION, PkgKeyType.BOOL),
            (Rpk.PATCH_SUBDIR, PkgKeyType.PSTR),
            (Rpk.PREFIX, PkgKeyType.PSTR),
            (Rpk.PYTHON_DIST_PATH, PkgKeyType.PSTR),
            (Rpk.PYTHON_INSTALLER_INTERPRETER, PkgKeyType.STR),
            (Rpk.PYTHON_INSTALLER_LAUNCHER_KIND, PkgKeyType.STR),
            (Rpk.PYTHON_INSTALLER_SCHEME, PkgKeyType.DICT_STR_STR_OR_STR),
            (Rpk.PYTHON_INTERPRETER, PkgKeyType.PSTR),
            (Rpk.PYTHON_SETUP_TYPE, PkgKeyType.STR),
            (Rpk.REMOTE_CONFIG, PkgKeyType.BOOL),
            (Rpk.REMOTE_SCRIPTS, PkgKeyType.BOOL),
            (Rpk.REVISION, PkgKeyType.DICT_STR_STR_OR_STR),
            (Rpk.SCONS_NOINSTALL, PkgKeyType.BOOL),
            (Rpk.SITE, PkgKeyType.DICT_STR_STR_OR_STR),
            (Rpk.SKIP_REMOTE_CONFIG, PkgKeyType.BOOL),
            (Rpk.SKIP_REMOTE_SCRIPTS, PkgKeyType.BOOL),
            (Rpk.STRIP_COUNT, PkgKeyType.INT_NONNEGATIVE),
            (Rpk.TYPE, PkgKeyType.STR),
            (Rpk.VCS_TYPE, PkgKeyType.DICT_STR_STR_OR_STR),
            (Rpk.VERSION, PkgKeyType.STR),
            (Rpk.VSDEVCMD, PkgKeyType.BOOL_OR_STR),
            (Rpk.VSDEVCMD_PRODUCTS, PkgKeyType.STR),
        ]
        for k, v in regval:
            self._register_conf(k, v)

        # sanity check that check option is properly registered
        for key in Rpk:
            assert key in self._key_types, f'key {key} is missing'

    def is_defless_package(self, pkg_def_dir, name):
        """
        determine if the provided package is considered a package

        The existence of a package's definition script is the main indication
        that a package exists. However, there is support for considering a
        folder as a package without a package definition script if other
        package scripts exist (e.g. a bootstrap, configuration, etc. script).
        This method will check for various package stage scripts based on
        the path of an expected package definition script. If any stage
        script exists, this call will return ``True``.

        Args:
            pkg_def_dir: the package definiton directory
            name: the name of the package

        Returns:
            returns whether the script reference is considered a package
        """

        package_hints = [
            BOOTSTRAP_SCRIPT,
            BUILD_SCRIPT,
            CONFIGURE_SCRIPT,
            INSTALL_SCRIPT,
            POST_SCRIPT,
        ]

        hint_script_exists = False
        for package_hint in package_hints:
            hint_script_name = f'{name}-{package_hint}'
            hint_script = os.path.join(pkg_def_dir, hint_script_name)
            _, hint_script_exists = opt_file(hint_script, warn_deprecated=False)
            if hint_script_exists:
                break

        return hint_script_exists

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

            pkg = None
            env = None
            deps = []

            # attempt to load the package from a user defined external directory
            for pkg_dir in self.opts.extern_pkg_dirs:
                pkg_def_dir = os.path.join(pkg_dir, name)
                pkg_script = os.path.join(pkg_def_dir, name)
                pkg_script, pkg_script_exists = opt_file(pkg_script)
                if pkg_script_exists or \
                        self.is_defless_package(pkg_def_dir, name):
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

                if dep not in pkgs:
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

        pkg_def_dir = os.path.abspath(os.path.join(script, os.pardir))
        self.script_env['DEFAULT_REVISION'] = DEFAULT_ENTRY
        self.script_env['DEFAULT_SITE'] = DEFAULT_ENTRY
        self.script_env['PKG_DEFDIR'] = P(pkg_def_dir)

        # Load a package's definition script if it exists. If one does not
        # exist, check if there are any other stage scripts defined (allowing
        # a developer to opt-out of defining an empty package definition). If
        # no other files are found, we will flag this not as a package.
        if os.path.isfile(script):
            debug('found package script ({})', name)
            env = self.load_package_script(name, script)
        elif self.is_defless_package(pkg_def_dir, name):
            debug('found package hint; treating as package ({})', name)
            env = self.script_env.copy()
        else:
            raise RelengToolMissingPackageScript({
                'pkg_name': name,
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
            pkg_devmode = bool(pkg_revision)

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
                    pkg_devmode = bool(pkg_revision)

                    # no explicit revision, check the "default/any" revision
                    if not pkg_revision:
                        pkg_revision = pkg_revision_raw.get(DEFAULT_ENTRY)

                    # no default revision to use for this mode, check if the
                    # deprecated devmode-revision value is set
                    if not pkg_revision and \
                            opts.devmode and pkg_devmode_revision:
                        pkg_revision = pkg_devmode_revision
                        pkg_devmode = bool(pkg_revision)

                    # lastly, if no revision has been found, default to the
                    # package's version
                    if not pkg_revision:
                        pkg_revision = pkg_version

                # if this is a single revision string, use this value for
                # the revision; with the exception if we are in development
                # mode and the deprecated devmode-revision value is set
                elif opts.devmode and pkg_devmode_revision:
                    pkg_revision = pkg_devmode_revision
                    pkg_devmode = True
                else:
                    pkg_revision = pkg_revision_raw

            # if we do not have package revision information provided, we
            # will default to the using the package's version; with the
            # exception if we are in development mode and the deprecated
            # devmode-revision value is set
            elif opts.devmode and pkg_devmode_revision:
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
            pkg_site = pkg_site.removeprefix('file://')
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
                pkg_site, pkg_vcs_type = site_vcs(pkg_site)
            else:
                pkg_vcs_type = VcsType.NONE

        if pkg_vcs_type == VcsType.BZR:
            warn('''\
use of GNU Bazaar is deprecated; see package: {}
 (consider switching to using Breezy; `brz`)''', name)

        if pkg_vcs_type == VcsType.URL and pkg_site and \
                pkg_site.startswith('file://'):
            pkg_vcs_type = VcsType.FILE
            warn('''\
explicit url vcs-type with files is deprecated: {}
 (update '{}' to 'file')\
''', name, pkg_key(name, Rpk.VCS_TYPE))

        # check if the detected vcs type needs a revision, and fail if we do
        # not have one
        if not pkg_revision and pkg_vcs_type in (
                VcsType.BRZ,
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
        # (use 'NEEDS' as the primary; fallback to 'DEPS')
        deps = self._fetch(Rpk.NEEDS)
        if deps is None:
            deps = self._fetch(Rpk.DEPS, default=[])
            if deps:
                warn('''\
using deprecated dependency configuration for package: {}
 (update '{}' to '{}')\
''', name, pkg_key(name, Rpk.DEPS), pkg_key(name, Rpk.NEEDS))

        # ignore cache
        pkg_devmode_ignore_cache = self._fetch(Rpk.DEVMODE_IGNORE_CACHE)
        if pkg_devmode_ignore_cache is None:
            if 'releng.disable_devmode_ignore_cache' not in opts.quirks:
                if opts.default_dev_ignore_cache is not None:
                    pkg_devmode_ignore_cache = opts.default_dev_ignore_cache

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

        # patch subdirectory
        pkg_patch_subdir = self._fetch(Rpk.PATCH_SUBDIR)

        # remote configuration
        pkg_remote_config = self._fetch(Rpk.REMOTE_CONFIG)
        if pkg_remote_config is None:
            pkg_skip_remote_config = self._fetch(Rpk.SKIP_REMOTE_CONFIG)
            if pkg_skip_remote_config is not None:
                pkg_remote_config = not pkg_skip_remote_config
                self._deprecated_replaced(name,
                    Rpk.SKIP_REMOTE_CONFIG, Rpk.REMOTE_CONFIG)

        # remote scripts
        pkg_remote_scripts = self._fetch(Rpk.REMOTE_SCRIPTS)
        if pkg_remote_scripts is None:
            pkg_skip_remote_scripts = self._fetch(Rpk.SKIP_REMOTE_SCRIPTS)
            if pkg_skip_remote_scripts is not None:
                pkg_remote_scripts = not pkg_skip_remote_scripts
                self._deprecated_replaced(name,
                    Rpk.SKIP_REMOTE_SCRIPTS, Rpk.REMOTE_SCRIPTS)

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
                VcsType.BRZ,
                VcsType.BZR,
                VcsType.CVS,
                VcsType.FILE,
                VcsType.GIT,
                VcsType.HG,
                VcsType.PERFORCE,
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
                VcsType.BRZ,
                VcsType.BZR,
                VcsType.CVS,
                VcsType.PERFORCE,
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
            new_local_dir = os.path.join(pkg_def_dir, 'local')
            if os.path.isdir(new_local_dir):
                pkg_build_dir = new_local_dir
            else:
                # deprecated local directory working inside definition folder
                warn('local-defined package missing local folder: {}', name)
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
            cprefix = os.path.commonprefix([pkg_build_dir, pkg_build_subdir])
            if cprefix != pkg_build_dir:
                raise RelengToolPathPackageTraversal({
                    'pkg_name': name,
                    'pkg_key': pkg_key(name, Rpk.BUILD_SUBDIR),
                })

        if pkg_patch_subdir:
            pkg_patch_subdir = os.path.join(pkg_build_dir, pkg_patch_subdir)
            cprefix = os.path.commonprefix([pkg_build_dir, pkg_patch_subdir])
            if cprefix != pkg_build_dir:
                raise RelengToolPathPackageTraversal({
                    'pkg_name': name,
                    'pkg_key': pkg_key(name, Rpk.PATCH_SUBDIR),
                })

        cache_dir = os.path.join(opts.dl_dir, name)
        if cache_ext:
            pkg_cache_file = os.path.join(cache_dir, pkg_nv + '.' + cache_ext)
        else:
            pkg_cache_file = os.path.join(cache_dir, pkg_nv)

        # Select sources (like CMake-based projects) may wish to be using
        # out-of-source tree builds. For supported project types, adjust the
        # build output directory to a sub-folder of the originally assumed
        # output folder.
        if pkg_type in [PackageType.CMAKE, PackageType.MESON]:
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
        if pkg_type in [PackageType.CMAKE, PackageType.MESON]:
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

        # relax hash check if a both operating in a development mode, this
        # package has development mode sources and is an internal package
        pkg_hash_relaxed = opts.devmode and pkg_devmode and pkg_is_internal

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
        pkg.hash_relaxed = pkg_hash_relaxed
        pkg.host_provides = pkg_host_provides
        pkg.is_internal = pkg_is_internal
        pkg.local_srcs = pkg_local_srcs
        pkg.no_extraction = pkg_no_extraction
        pkg.patch_subdir = pkg_patch_subdir
        pkg.remote_config = pkg_remote_config
        pkg.remote_scripts = pkg_remote_scripts
        pkg.revision = pkg_revision
        pkg.site = pkg_site
        pkg.strip_count = pkg_strip_count
        pkg.type = pkg_type
        pkg.vcs_type = pkg_vcs_type

        # if this package has a development mode variant, check if see if
        # there is an alternative hash file for this revision; if so, use it
        # over the default one
        if pkg.devmode:
            devfix = re.sub('\\W', '_', pkg_revision)
            alt_hash_file = f'{pkg.hash_file}-{devfix}'
            if os.path.isfile(alt_hash_file):
                pkg.hash_file = alt_hash_file

        self._apply_postinit_options(pkg)

        # (additional environment helpers)
        for ctx in (env_wrap(), env):
            ctx[pkg_key(name, 'BUILD_DIR')] = P(pkg_build_dir)
            ctx[pkg_key(name, 'BUILD_OUTPUT_DIR')] = P(pkg_build_output_dir)
            ctx[pkg_key(name, 'DEFDIR')] = P(pkg_def_dir)
            ctx[pkg_key(name, 'NAME')] = name
            ctx[pkg_key(name, 'REVISION')] = pkg_revision
        os.environ[pkg_key(name, Rpk.VERSION)] = pkg_version

        # (internals)
        prefix = '.releng_tool-stage-'

        ff_fetch = os.path.join(
            opts.build_dir, '.releng-tool', f'{prefix}fetch-{pkg_nv}')

        outdir = pkg.build_output_dir
        pkg._ff_bootstrap = os.path.join(outdir, prefix + 'bootstrap')
        pkg._ff_build = os.path.join(outdir, prefix + 'build')
        pkg._ff_configure = os.path.join(outdir, prefix + 'configure')
        pkg._ff_extract = os.path.join(outdir, prefix + 'extract')
        pkg._ff_fetch = os.path.join(outdir, ff_fetch)
        pkg._ff_fetch_post = os.path.join(outdir, prefix + 'fetch-post')
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

    def load_package_script(self, name, script):
        """
        load a package script

        Attempts to load a package definition script of a given ``name`` from
        the provided ``script`` location. The target script will be run and
        its environment will be returned on a successful execution. On failure,
        an ``RelengToolInvalidPackageScript`` exception will be thrown.

        Args:
            name: the package name
            script: the package script to load

        Returns:
            the extracted environment/globals from the package script

        Raises:
            RelengToolInvalidPackageScript: when an error has been detected
                                            loading the package script
        """

        # preallocate empty iterable entries so that packages can append
        # without needing to make sure the configuration dictionary already
        # exists
        interim_ids = set()
        for k, v in self._key_types.items():
            interim_obj = None

            if v in (PkgKeyType.DICT_STR_PSTR, PkgKeyType.OPTS):
                interim_obj = {}
            elif v == PkgKeyType.STRS:
                interim_obj = []

            if interim_obj is not None:
                pkg_cfg_key = pkg_key(name, k)
                if pkg_cfg_key not in self.script_env:
                    self.script_env[pkg_cfg_key] = interim_obj
                    interim_ids.add(id(interim_obj))

        # run the package script
        try:
            env = run_script(script, self.script_env, catch=False)
        except Exception as ex:
            raise RelengToolInvalidPackageScript({
                'description': str(ex),
                'script': script,
                'traceback': traceback.format_exc(),
            }) from ex

        # if an interim configuration has not been used, automatically remove
        # them from the environment as if it was ``None`` in the first place
        for k, v in self._key_types.items():
            if v in (PkgKeyType.DICT_STR_PSTR,
                     PkgKeyType.STRS,
                     PkgKeyType.OPTS):
                pkg_cfg_key = pkg_key(name, k)
                if env[pkg_cfg_key]:
                    continue

                ref_id = id(env[pkg_cfg_key])
                if ref_id in interim_ids:
                    env[pkg_cfg_key] = None
                    self.script_env[pkg_cfg_key] = None
                    interim_ids.remove(ref_id)

        return env

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

        opts = self.opts

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

        if pkg.license and 'releng.disable_spdx_check' not in opts.quirks:
            for license_entry in pkg.license:
                parsed, licenses, exceptions = spdx_extract(license_entry)

                for nested_license in licenses:
                    if spdx_license_identifier(nested_license):
                        continue

                    entry = opts.spdx['licenses'].get(nested_license, None)
                    if entry:
                        if entry['deprecated']:
                            warn('deprecated spdx license detected ({}): {}',
                                nested_license, pkg.name)
                    else:
                        warn('unknown spdx license detected ({}): {}',
                            nested_license, pkg.name)

                for exception in exceptions:
                    entry = opts.spdx['exceptions'].get(exception, None)
                    if entry:
                        if entry['deprecated']:
                            warn('deprecated spdx license exception detected '
                                 '({}): {}', exception, pkg.name)
                    else:
                        warn('unknown spdx license exception detected ({}): {}',
                            exception, pkg.name)

                if not parsed:
                    warn('unexpected spdx license format detected: {}',
                        pkg.name)

        # license files
        if pkg.license_files is None:
            pkg.license_files = self._fetch(Rpk.LICENSE_FILES)

        # prefix
        if pkg.prefix is None:
            pkg.prefix = self._fetch(Rpk.PREFIX)
            if pkg.prefix:
                target_dir = opts.target_dir
                target_pdir = os.path.normpath(target_dir + pkg.prefix)
                cprefix = os.path.commonprefix([target_dir, target_pdir])
                if cprefix != target_dir:
                    raise RelengToolPathPackageTraversal({
                        'pkg_name': pkg.name,
                        'pkg_key': pkg_key(pkg.name, Rpk.PREFIX),
                    })

        # vsdevcmd configuration
        if pkg.vsdevcmd is None:
            pkg.vsdevcmd = self._fetch(Rpk.VSDEVCMD)

        if pkg.vsdevcmd_products is None:
            pkg.vsdevcmd_products = self._fetch(Rpk.VSDEVCMD_PRODUCTS)

        # ######################################################################
        # (package type - shared)
        # ######################################################################

        # package-type environment options (all stages)
        pkg_env = self._fetch(Rpk.ENV)

        # package-type build definitions
        if pkg.build_defs is None:
            pkg.build_defs = self._fetch(Rpk.BUILD_DEFS)

        # package-type build environment options
        if pkg.build_env is None:
            pkg.build_env = dict(pkg_env) if pkg_env else None
            pkg.build_env_pkg = self._fetch(Rpk.BUILD_ENV)
            if pkg.build_env_pkg:
                if pkg.build_env is None:
                    pkg.build_env = {}
                pkg.build_env.update(pkg.build_env_pkg)

        # package-type build options
        if pkg.build_opts is None:
            pkg.build_opts = self._fetch(Rpk.BUILD_OPTS)

        # package-type configuration definitions
        if pkg.conf_defs is None:
            pkg.conf_defs = self._fetch(Rpk.CONF_DEFS)

        # package-type configuration environment options
        if pkg.conf_env is None:
            pkg.conf_env = dict(pkg_env) if pkg_env else None
            pkg.conf_env_pkg = self._fetch(Rpk.CONF_ENV)
            if pkg.conf_env_pkg:
                if pkg.conf_env is None:
                    pkg.conf_env = {}
                pkg.conf_env.update(pkg.conf_env_pkg)

        # package-type configuration options
        if pkg.conf_opts is None:
            pkg.conf_opts = self._fetch(Rpk.CONF_OPTS)

        # package-type installation definitions
        if pkg.install_defs is None:
            pkg.install_defs = self._fetch(Rpk.INSTALL_DEFS)

            if pkg.install_defs and pkg.type == PackageType.PYTHON:
                self._obsolete(pkg.name, Rpk.INSTALL_DEFS)

        # package-type installation environment options
        if pkg.install_env is None:
            pkg.install_env = dict(pkg_env) if pkg_env else None
            pkg.install_env_pkg = self._fetch(Rpk.INSTALL_ENV)
            if pkg.install_env_pkg:
                if pkg.install_env is None:
                    pkg.install_env = {}
                pkg.install_env.update(pkg.install_env_pkg)

            if pkg.install_env_pkg and pkg.type == PackageType.PYTHON:
                self._obsolete(pkg.name, Rpk.INSTALL_ENV)

        # package-type installation options
        if pkg.install_opts is None:
            pkg.install_opts = self._fetch(Rpk.INSTALL_OPTS)

            if pkg.install_opts and pkg.type == PackageType.PYTHON:
                self._obsolete(pkg.name, Rpk.INSTALL_OPTS)

        # ######################################################################
        # (package type - autotools)
        # ######################################################################

        # autotools autoreconf flag
        if pkg.autotools_autoreconf is None:
            pkg.autotools_autoreconf = self._fetch(Rpk.AUTOTOOLS_AUTORECONF)

        # ######################################################################
        # (package type - cargo)
        # ######################################################################

        # cargo name
        if pkg.cargo_name is None:
            pkg.cargo_name = self._fetch(Rpk.CARGO_NAME)

        if pkg.cargo_name is None:
            pkg.cargo_name = pkg.name

        # cargo noinstall flag
        if pkg.cargo_noinstall is None:
            pkg.cargo_noinstall = self._fetch(Rpk.CARGO_NOINSTALL)

        # ######################################################################
        # (package type - cmake)
        # ######################################################################

        # cmake build type
        if pkg.cmake_build_type is None:
            pkg.cmake_build_type = self._fetch(Rpk.CMAKE_BUILD_TYPE)

        if not pkg.cmake_build_type:
            pkg.cmake_build_type = DEFAULT_CMAKE_BUILD_TYPE

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
        # (package type - meson)
        # ######################################################################

        # meson noinstall flag
        if pkg.meson_noinstall is None:
            pkg.meson_noinstall = self._fetch(Rpk.MESON_NOINSTALL)

        # ######################################################################
        # (package type - python)
        # ######################################################################

        # python dist output path
        if pkg.python_dist_path is None:
            pkg.python_dist_path = self._fetch(Rpk.PYTHON_DIST_PATH)

        # python installer interpreter
        if pkg.python_installer_interpreter is None:
            pkg.python_installer_interpreter = \
                self._fetch(Rpk.PYTHON_INSTALLER_INTERPRETER)

        # python installer launcher kind
        if pkg.python_installer_launcher_kind is None:
            pkg.python_installer_launcher_kind = \
                self._fetch(Rpk.PYTHON_INSTALLER_LAUNCHER_KIND)

        # python installer scheme flag
        if pkg.python_installer_scheme is None:
            pkg.python_installer_scheme = \
                self._fetch(Rpk.PYTHON_INSTALLER_SCHEME)

        # python interpreter
        if pkg.python_interpreter is None:
            pkg.python_interpreter = self._fetch(Rpk.PYTHON_INTERPRETER)

        # python setup type
        if pkg.python_setup_type is None:
            python_setup_type_raw = self._fetch(Rpk.PYTHON_SETUP_TYPE)
            if python_setup_type_raw:
                python_setup_type_raw = python_setup_type_raw.lower()
                if python_setup_type_raw in PythonSetupType:
                    pkg.python_setup_type = python_setup_type_raw
                else:
                    raise RelengToolUnknownPythonSetupType({
                        'pkg_name': pkg.name,
                        'pkg_key': pkg_key(pkg.name, Rpk.PYTHON_SETUP_TYPE),
                    })

        if pkg.type == PackageType.PYTHON and not pkg.python_setup_type:
            warn('''\
missing setup type for Python package (required in future releases): {}
 (add a '{}' entry)''', pkg.name, pkg_key(pkg.name, Rpk.PYTHON_SETUP_TYPE))

        if pkg.python_setup_type == PythonSetupType.DISTUTILS:
            warn('''\
use of Python distutils is deprecated; see package: {}''', pkg.name)

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
            os.path.join(pkg.build_dir, RELENG_CONF_EXTENDED_NAME),
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
            })

        env = self.load_package_script(pkg.name, script)

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
            try:
                value = raw_value_parse(raw_value, type_)
            except (TypeError, ValueError) as ex:
                raise_kv_exception(str(ex))

            if allow_expand:
                value = expand(value, expand_extra)

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
            except OSError:
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

        if not mkdir(self.opts.cache_dir):
            verbose('unable to generate output directory for dvcs cache')
            return

        try:
            with open(self._dvcs_cache_fname, 'wb') as f:
                pickle.dump(self._dvcs_cache, f,
                    protocol=2)  # 2 for py2/py3 support
            debug('saved dvcs cache')
        except OSError:
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

        assert key not in self._key_types, f'key {key} is registered'
        self._key_types[key] = type_

    def _deprecated_replaced(self, name, old_key, new_key):
        """
        warn about the use of a replaced deprecated configuration key

        Args:
            name: the name of the package
            old_key: the old configuration key
            new_key: the new configuration key
        """

        warn('''\
using deprecated dependency configuration for package: {}
 (update '{}' to '{}')''', name, pkg_key(name, old_key), pkg_key(name, new_key))

    def _obsolete(self, name, key):
        """
        warn about the use of an obsolete configuration key

        Args:
            name: the name of the package
            key: the configuration key
        """

        warn('''\
using obsolete configuration for package: {}
 ('{}')''', name, pkg_key(name, key))
