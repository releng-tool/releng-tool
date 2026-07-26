# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from inspect import signature
from releng_tool.defs import ConfKey
from releng_tool.defs import GlobalAction
from releng_tool.defs import PkgAction
from releng_tool.defs import SbomFormatType
from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from releng_tool.exceptions import RelengToolMissingPackagesError
from releng_tool.opts import RelengEngineOptions
from releng_tool.registry import RelengRegistry
from releng_tool.util.interpret import interpret_dict
from releng_tool.util.interpret import interpret_seq
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
from releng_tool.util.string import expand
from releng_tool.util.version import str_to_version
from typing import Any
import os
import ssl
import traceback


def get_package_names(opts: RelengEngineOptions, settings: dict[str, Any],
        cfg_args: dict[str, Any]) -> list[str]:
    """
    acquire list of project package names to process

    From a dictionary of user-defined settings, extract the known list of
    package names from the package configuration key ``ConfKey.PKGS``. This
    method will return a (duplicate-removed) list of packages (if any) to be
    processed.

    Args:
        opts: the engine options
        settings: user settings to pull package information from
        cfg_args: settings a user has provided via a `releng_config` call

    Returns:
        list of package names to be processed

    Raises:
        RelengToolInvalidConfigurationSettings: invalid package list is detected
        RelengToolMissingPackagesError: no packages are detected
    """
    pkg_names: list[str] = []
    bad_pkgs_value = False

    is_linting = opts.gbl_action == GlobalAction.LINT or \
        opts.pkg_action == PkgAction.LINT

    raw_pkgs_value = None

    if cfg_args:
        if not is_linting and ConfKey.PKGS in settings:
            warn(f'project option `{ConfKey.PKGS}` ignored since this project '
                  'uses `releng_config`')

        if ConfKey.PKGS in cfg_args:
            raw_pkgs_value = cfg_args[ConfKey.PKGS]
    elif ConfKey.PKGS in settings:
        raw_pkgs_value = settings[ConfKey.PKGS]

    if raw_pkgs_value is not None:
        detected_pkg_names = interpret_seq(raw_pkgs_value, str)
        if detected_pkg_names is None:
            bad_pkgs_value = True
        else:
            pkg_names = detected_pkg_names

    if cfg_args:
        example_pkgnames = f'''\
```
releng_config(
    {ConfKey.PKGS} = [
        'liba',
        'libb',
        'libc',
    ],
    ...
)
```'''
    else:
        example_pkgnames = f'''\
```
{ConfKey.PKGS} = [
    'liba',
    'libb',
    'libc',
]
```'''

    if bad_pkgs_value:
        err(f'''\
bad package list definition

The configuration file does not have a properly formed list of defined packages.
Ensure a package list exists with the string-based names of packages to be
included in a run. For example, this file:

    {opts.conf_point}

Should have a package list such as:

{example_pkgnames}''')
        raise RelengToolInvalidConfigurationSettings

    if not pkg_names:
        err(f'''\
no defined packages

The configuration file does not have any defined packages. Ensure a package
list exists with the name of packages to be included in a run. For example,
this file:

    {opts.conf_point}

Should have a package list such as:

{example_pkgnames}''')
        raise RelengToolMissingPackagesError

    # remove duplicates (but maintain pre-sorted ordered)
    return list(dict.fromkeys(pkg_names))


def process_settings(opts: RelengEngineOptions, registry: RelengRegistry,
        settings: dict[str, Any], cfg_args: dict[str, Any]) -> bool:
    """
    process global settings provided from the user

    For all known file flags, see if either respective flag options are set
    and/or configure file flags for which have been explicitly set to be
    enabled.

    Args:
        opts: the engine options to populate
        registry: the registry to populate
        settings: user settings to pull global information from
        cfg_args: settings a user has provided via a `releng_config` call

    Returns:
        ``True`` if settings have been processed; ``False`` if an issue with
        the settings have been detected
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

    is_linting = opts.gbl_action == GlobalAction.LINT or \
        opts.pkg_action == PkgAction.LINT

    def fetch(key: str) -> Any:
        if cfg_args:
            if not is_linting and key in settings:
                warn(f'project option `{key}` ignored since this project '
                      'uses `releng_config`')

            if key in cfg_args:
                return cfg_args[key]

        elif key in settings:
            return settings[key]

        return None

    cet = fetch(ConfKey.CACHE_EXT_TRANSFORM)
    if cet is not None:
        if not callable(cet):
            notify_invalid_type(ConfKey.CACHE_EXT_TRANSFORM, 'callable')
            return False
        opts.cache_ext_transform = cet

    is_default_internal = fetch(ConfKey.DEFINTERN)
    if is_default_internal is not None:
        if not isinstance(is_default_internal, bool):
            notify_invalid_type(ConfKey.DEFINTERN, 'bool')
            return False
        opts.default_internal_pkgs = is_default_internal

    default_cmake_build_type = fetch(ConfKey.DEF_CMAKE_BUILD_TYPE)
    if default_cmake_build_type is not None:
        if not isinstance(default_cmake_build_type, str):
            notify_invalid_type(ConfKey.DEF_CMAKE_BUILD_TYPE, 'str')
            return False
        opts.default_cmake_build_type = default_cmake_build_type

    default_dev_ignore_cache = fetch(ConfKey.DEF_DEV_IGNORE_CACHE)
    if default_dev_ignore_cache is not None:
        if not isinstance(default_dev_ignore_cache, bool):
            notify_invalid_type(ConfKey.DEF_DEV_IGNORE_CACHE, 'bool')
            return False
        opts.default_dev_ignore_cache = default_dev_ignore_cache

    default_meson_build_type = fetch(ConfKey.DEF_MESON_BUILD_TYPE)
    if default_meson_build_type is not None:
        if not isinstance(default_meson_build_type, str):
            notify_invalid_type(ConfKey.DEF_MESON_BUILD_TYPE, 'str')
            return False
        opts.default_meson_build_type = default_meson_build_type

    default_xmake_build_type = fetch(ConfKey.DEF_XMAKE_BUILD_TYPE)
    if default_xmake_build_type is not None:
        if not isinstance(default_xmake_build_type, str):
            notify_invalid_type(ConfKey.DEF_XMAKE_BUILD_TYPE, 'str')
            return False
        opts.default_xmake_build_type = default_xmake_build_type

    project_env = fetch(ConfKey.ENVIRONMENT)
    if project_env is not None:
        v = interpret_dict(project_env, str)
        if v is None:
            notify_invalid_type(ConfKey.ENVIRONMENT, 'dict(str,str)')
            return False
        opts.environment.update(expand(v))

    extra_lexcepts = fetch(ConfKey.EXTRA_LEXCEPTS)
    if extra_lexcepts is not None:
        d = interpret_dict(extra_lexcepts, str)
        if d is None:
            notify_invalid_type(ConfKey.EXTRA_LEXCEPTS, 'dict(str,str)')
            return False

        for key, val in d.items():
            opts.spdx['exceptions'][key] = {
                'name': val,
                'deprecated': False,
            }

    extra_licenses = fetch(ConfKey.EXTRA_LICENSES)
    if extra_licenses is not None:
        d = interpret_dict(extra_licenses, str)
        if d is None:
            notify_invalid_type(ConfKey.EXTRA_LICENSES, 'dict(str,str)')
            return False

        for key, val in d.items():
            opts.spdx['licenses'][key] = {
                'name': val,
                'deprecated': False,
            }

    license_header = fetch(ConfKey.LICENSE_HEADER)
    if license_header is not None:
        if not isinstance(license_header, str):
            notify_invalid_type(ConfKey.LICENSE_HEADER, 'str')
            return False
        opts.license_header = license_header

    raw_lint_max_version = fetch(ConfKey.LINT_MAX_VERSION)
    if not opts.lint_max_version and raw_lint_max_version:
        raw_max_version = raw_lint_max_version
        if not isinstance(raw_max_version, str):
            notify_invalid_type(ConfKey.LINT_MAX_VERSION, 'version-str')
            return False
        try:
            opts.lint_max_version = str_to_version(raw_max_version)
        except ValueError:
            notify_invalid_type(ConfKey.LINT_MAX_VERSION, 'version-str')
            return False

    is_network_isolation = fetch(ConfKey.NETWORK_ISOLATION)
    if is_network_isolation is not None:
        if not isinstance(is_network_isolation, bool):
            notify_invalid_type(ConfKey.NETWORK_ISOLATION, 'bool')
            return False
        opts.network_isolation = is_network_isolation

    override_tools = fetch(ConfKey.OVERRIDE_TOOLS)
    if override_tools is not None:
        v = interpret_dict(override_tools, str)
        if v is None:
            notify_invalid_type(ConfKey.OVERRIDE_TOOLS, 'dict(str,str)')
            return False
        opts.extract_override = v

    raw_prerequisites = fetch(ConfKey.PREREQUISITES)
    if raw_prerequisites is not None:
        prerequisites = interpret_seq(raw_prerequisites, str)
        if prerequisites is None:
            notify_invalid_type(ConfKey.PREREQUISITES, 'str or list(str)')
            return False
        opts.prerequisites.extend(prerequisites)

    raw_quirks = fetch(ConfKey.QUIRKS)
    if raw_quirks is not None:
        quirks = interpret_seq(raw_quirks, str)
        if quirks is None:
            notify_invalid_type(ConfKey.QUIRKS, 'str or list(str)')
            return False
        opts.quirks.extend(quirks)
        for quirk in quirks:
            verbose('configuration quirk applied: ' + quirk)

    raw_revisions = fetch(ConfKey.REVISIONS)
    if raw_revisions is not None:
        revz = interpret_dict(raw_revisions, str)
        if revz is None:
            notify_invalid_type(ConfKey.REVISIONS, 'dict(str,str)')
            return False
        opts.revisions = revz

    raw_sbom_format = fetch(ConfKey.SBOM_FORMAT)
    if raw_sbom_format is not None:
        sbom_format = interpret_seq(raw_sbom_format, str)
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
        if not opts.sbom_format:
            opts.sbom_format = sbom_format

    sysroot_prefix = fetch(ConfKey.SYSROOT_PREFIX)
    if sysroot_prefix is not None:
        if not isinstance(sysroot_prefix, (str, bytes, os.PathLike)):
            notify_invalid_type(
                ConfKey.SYSROOT_PREFIX, 'string or path-like')
            return False
        sysroot_prefix = os.fsdecode(sysroot_prefix)
        if not sysroot_prefix.startswith('/'):
            sysroot_prefix = '/' + sysroot_prefix
        opts.sysroot_prefix = sysroot_prefix

    url_mirror = fetch(ConfKey.URL_MIRROR)
    if url_mirror is not None:
        if not isinstance(url_mirror, str):
            notify_invalid_type(ConfKey.URL_MIRROR, 'str')
            return False
        opts.url_mirror = url_mirror

    urlopen_context = fetch(ConfKey.URLOPEN_CONTEXT)
    if urlopen_context is not None:
        if not isinstance(urlopen_context, ssl.SSLContext):
            notify_invalid_type(ConfKey.URLOPEN_CONTEXT, 'ssl.SSLContext')
            return False
        opts.urlopen_context = urlopen_context

    vsdevcmd = fetch(ConfKey.VSDEVCMD)
    if vsdevcmd is not None:
        if not isinstance(vsdevcmd, (bool, str)):
            notify_invalid_type(ConfKey.VSDEVCMD, 'bool or str')
            return False
        opts.vsdevcmd = vsdevcmd

    vsdevcmd_products = fetch(ConfKey.VSDEVCMD_PRODUCTS)
    if vsdevcmd_products is not None:
        if not isinstance(vsdevcmd_products, str):
            notify_invalid_type(ConfKey.VSDEVCMD_PRODUCTS, 'str')
            return False
        opts.vsdevcmd_products = vsdevcmd_products

    raw_exten_pkgs = fetch(ConfKey.EXTEN_PKGS)
    if raw_exten_pkgs is not None:
        epd = interpret_seq(raw_exten_pkgs, str)
        if epd is None:
            notify_invalid_type(ConfKey.EXTEN_PKGS, 'str or list(str)')
            return False
        opts.extern_pkg_dirs = epd

    ext_names = []
    raw_extensions = fetch(ConfKey.EXTENSIONS)
    if raw_extensions is not None:
        ext_names = interpret_seq(raw_extensions, str)
        if ext_names is None:
            notify_invalid_type(ConfKey.EXTENSIONS, 'str or list(str)')
            return False

    # load extensions; stop if there was an issue
    extensions_loaded = registry.load_all_extensions(ext_names)
    if not extensions_loaded and \
            'releng.ignore_failed_extensions' not in opts.quirks:
        return False

    # if the settings files has a `releng_setup` hook for extension-like
    # overrides, invoke the setup call
    if 'releng_setup' in settings:
        setup_hook = settings['releng_setup']
        setup_hook_sig = signature(setup_hook)
        try:
            setup_hook_sig.bind(registry)
        except TypeError:
            debug(f'''\
failed to bind to releng_setup hook

{traceback.format_exc()}''')

            err('''\
releng_setup hook in the project configuration has an invalid signature

When preparing to invoke a project's `releng_setup` call, it has been
detected that the call's signature is invalid. Please refer to the API
documentation for more information.''')
            return False
        else:
            setup_hook(registry)

    return True
