# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.util.enum import Enum
import hashlib


class PkgKeyType(Enum):
    """
    package key type

    Enumeration of types supported when fetching configuration values defined by
    a package definition.

    Attributes:
        BOOL: boolean value
        BOOL_OR_STR: boolean value or a string value
        DICT: dictionary value
        DICT_STR_STR: dictionary of string pairs value
        DICT_STR_STR_OR_STR: dictionary of string pairs or a string value
        DICT_STR_STR_OR_STRS: dictionary of string pairs or strings value
        STR: single string value
        STRS: one or more strings value
        INT_NONNEGATIVE: non-negative integer value
        INT_POSITIVE: positive integer value
    """
    BOOL = 'bool'
    BOOL_OR_STR = 'bool_or_str'
    DICT = 'dict'
    DICT_STR_STR = 'dict_str_str'
    DICT_STR_STR_OR_STR = 'dict_str_str_or_str'
    DICT_STR_STR_OR_STRS = 'dict_str_str_or_strs'
    STR = 'str'
    STRS = 'strs'
    INT_NONNEGATIVE = 'int_nonnegative'
    INT_POSITIVE = 'int_positive'


def pkg_cache_key(site):
    """
    generate a cache key for a provided package's site

    Package's may share caching data if their sites match. This call returns a
    calculated "cache key" for a provided cache site.

    Returns:
        the cache key
    """
    return hashlib.sha1(site.encode('utf_8')).hexdigest()  # noqa: S324


def pkg_key(pkg, type_):
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
        type_: the package key type

    Returns:
        the completed package key
    """
    clean = pkg
    for c in [' ', '*', '-', '.', ':', '?', '|']:
        clean = clean.replace(c, '_')
    return '{}_{}'.format(clean.upper(), type_)
