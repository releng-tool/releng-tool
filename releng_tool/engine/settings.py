# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from inspect import signature
from releng_tool.defs import ConfKey
from releng_tool.defs import SbomFormatType
from releng_tool.opts import RelengEngineOptions
from releng_tool.registry import RelengRegistry
from releng_tool.util.interpret import interpret_dict
from releng_tool.util.interpret import interpret_seq
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import verbose
from releng_tool.util.string import expand
from releng_tool.util.version import str_to_version
from typing import Any
import os
import ssl
import traceback


def process_settings(opts: RelengEngineOptions, registry: RelengRegistry,
        settings: dict[str, Any]) -> bool:
    """
    process global settings provided from the user

    For all known file flags, see if either respective flag options are set
    and/or configure file flags for which have been explicitly set to be
    enabled.

    Args:
        opts: the engine options to populate
        registry: the registry to populate
        settings: user settings to pull global information from

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

    if ConfKey.CACHE_EXT_TRANSFORM in settings:
        cet = None
        if callable(settings[ConfKey.CACHE_EXT_TRANSFORM]):
            cet = settings[ConfKey.CACHE_EXT_TRANSFORM]
        if cet is None:
            notify_invalid_type(ConfKey.CACHE_EXT_TRANSFORM, 'callable')
            return False
        opts.cache_ext_transform = cet

    if ConfKey.DEFINTERN in settings:
        is_default_internal = settings[ConfKey.DEFINTERN]
        if not isinstance(is_default_internal, bool):
            notify_invalid_type(ConfKey.DEFINTERN, 'bool')
            return False
        opts.default_internal_pkgs = is_default_internal

    if ConfKey.DEF_CMAKE_BUILD_TYPE in settings:
        default_cmake_build_type = settings[ConfKey.DEF_CMAKE_BUILD_TYPE]
        if not isinstance(default_cmake_build_type, str):
            notify_invalid_type(ConfKey.DEF_CMAKE_BUILD_TYPE, 'str')
            return False
        opts.default_cmake_build_type = default_cmake_build_type

    if ConfKey.DEF_DEV_IGNORE_CACHE in settings:
        default_dev_ignore_cache = settings[ConfKey.DEF_DEV_IGNORE_CACHE]
        if not isinstance(default_dev_ignore_cache, bool):
            notify_invalid_type(ConfKey.DEF_DEV_IGNORE_CACHE, 'bool')
            return False
        opts.default_dev_ignore_cache = default_dev_ignore_cache

    if ConfKey.DEF_MESON_BUILD_TYPE in settings:
        default_meson_build_type = settings[ConfKey.DEF_MESON_BUILD_TYPE]
        if not isinstance(default_meson_build_type, str):
            notify_invalid_type(ConfKey.DEF_MESON_BUILD_TYPE, 'str')
            return False
        opts.default_meson_build_type = default_meson_build_type

    if ConfKey.DEF_XMAKE_BUILD_TYPE in settings:
        default_xmake_build_type = settings[ConfKey.DEF_XMAKE_BUILD_TYPE]
        if not isinstance(default_xmake_build_type, str):
            notify_invalid_type(ConfKey.DEF_XMAKE_BUILD_TYPE, 'str')
            return False
        opts.default_xmake_build_type = default_xmake_build_type

    if ConfKey.ENVIRONMENT in settings:
        env = interpret_dict(settings[ConfKey.ENVIRONMENT], str)
        if env is None:
            notify_invalid_type(ConfKey.ENVIRONMENT, 'dict(str,str)')
            return False
        opts.environment.update(expand(env))

    if ConfKey.EXTRA_LEXCEPTS in settings:
        d = interpret_dict(settings[ConfKey.EXTRA_LEXCEPTS], str)
        if d is None:
            notify_invalid_type(ConfKey.EXTRA_LEXCEPTS, 'dict(str,str)')
            return False

        for key, val in d.items():
            opts.spdx['exceptions'][key] = {
                'name': val,
                'deprecated': False,
            }

    if ConfKey.EXTRA_LICENSES in settings:
        d = interpret_dict(settings[ConfKey.EXTRA_LICENSES], str)
        if d is None:
            notify_invalid_type(ConfKey.EXTRA_LICENSES, 'dict(str,str)')
            return False

        for key, val in d.items():
            opts.spdx['licenses'][key] = {
                'name': val,
                'deprecated': False,
            }

    if ConfKey.LICENSE_HEADER in settings:
        license_header = settings[ConfKey.LICENSE_HEADER]
        if not isinstance(license_header, str):
            notify_invalid_type(ConfKey.LICENSE_HEADER, 'str')
            return False
        opts.license_header = license_header

    if not opts.lint_max_version and \
            ConfKey.LINT_MAX_VERSION in settings:
        raw_max_version = settings[ConfKey.LINT_MAX_VERSION]
        if not isinstance(raw_max_version, str):
            notify_invalid_type(ConfKey.LINT_MAX_VERSION, 'version-str')
            return False
        try:
            opts.lint_max_version = str_to_version(raw_max_version)
        except ValueError:
            notify_invalid_type(ConfKey.LINT_MAX_VERSION, 'version-str')
            return False

    if ConfKey.NETWORK_ISOLATION in settings:
        is_network_isolation = settings[ConfKey.NETWORK_ISOLATION]
        if not isinstance(is_network_isolation, bool):
            notify_invalid_type(ConfKey.NETWORK_ISOLATION, 'bool')
            return False
        opts.network_isolation = is_network_isolation

    if ConfKey.OVERRIDE_TOOLS in settings:
        v = interpret_dict(settings[ConfKey.OVERRIDE_TOOLS], str)
        if v is None:
            notify_invalid_type(ConfKey.OVERRIDE_TOOLS, 'dict(str,str)')
            return False
        opts.extract_override = v

    if ConfKey.PREREQUISITES in settings:
        prerequisites = interpret_seq(settings[ConfKey.PREREQUISITES], str)
        if prerequisites is None:
            notify_invalid_type(ConfKey.PREREQUISITES, 'str or list(str)')
            return False
        opts.prerequisites.extend(prerequisites)

    if ConfKey.QUIRKS in settings:
        quirks = interpret_seq(settings[ConfKey.QUIRKS], str)
        if quirks is None:
            notify_invalid_type(ConfKey.QUIRKS, 'str or list(str)')
            return False
        opts.quirks.extend(quirks)
        for quirk in quirks:
            verbose('configuration quirk applied: ' + quirk)

    if ConfKey.REVISIONS in settings:
        revz = interpret_dict(settings[ConfKey.REVISIONS], str)
        if revz is None:
            notify_invalid_type(ConfKey.REVISIONS, 'dict(str,str)')
            return False
        opts.revisions = revz

    if ConfKey.SBOM_FORMAT in settings:
        sbom_format = interpret_seq(settings[ConfKey.SBOM_FORMAT], str)
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

    if ConfKey.SYSROOT_PREFIX in settings:
        sysroot_prefix = settings[ConfKey.SYSROOT_PREFIX]
        if not isinstance(sysroot_prefix, (str, bytes, os.PathLike)):
            notify_invalid_type(
                ConfKey.SYSROOT_PREFIX, 'string or path-like')
            return False
        sysroot_prefix = os.fsdecode(sysroot_prefix)
        if not sysroot_prefix.startswith('/'):
            sysroot_prefix = '/' + sysroot_prefix
        opts.sysroot_prefix = sysroot_prefix

    if ConfKey.URL_MIRROR in settings:
        url_mirror = settings[ConfKey.URL_MIRROR]
        if not isinstance(url_mirror, str):
            notify_invalid_type(ConfKey.URL_MIRROR, 'str')
            return False
        opts.url_mirror = url_mirror

    if ConfKey.URLOPEN_CONTEXT in settings:
        urlopen_context = None
        if isinstance(settings[ConfKey.URLOPEN_CONTEXT], ssl.SSLContext):
            urlopen_context = settings[ConfKey.URLOPEN_CONTEXT]
        if urlopen_context is None:
            notify_invalid_type(ConfKey.URLOPEN_CONTEXT, 'ssl.SSLContext')
            return False
        opts.urlopen_context = urlopen_context

    if ConfKey.VSDEVCMD in settings:
        vsdevcmd = settings[ConfKey.VSDEVCMD]
        if not isinstance(vsdevcmd, (bool, str)):
            notify_invalid_type(ConfKey.VSDEVCMD, 'bool or str')
            return False
        opts.vsdevcmd = vsdevcmd

    if ConfKey.VSDEVCMD_PRODUCTS in settings:
        vsdevcmd_products = settings[ConfKey.VSDEVCMD_PRODUCTS]
        if not isinstance(vsdevcmd_products, str):
            notify_invalid_type(ConfKey.VSDEVCMD_PRODUCTS, 'str')
            return False
        opts.vsdevcmd_products = vsdevcmd

    if ConfKey.EXTEN_PKGS in settings:
        epd = interpret_seq(settings[ConfKey.EXTEN_PKGS], str)
        if epd is None:
            notify_invalid_type(ConfKey.EXTEN_PKGS, 'str or list(str)')
            return False
        opts.extern_pkg_dirs = epd

    ext_names = []
    if ConfKey.EXTENSIONS in settings:
        ext_names = interpret_seq(settings[ConfKey.EXTENSIONS], str)
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
