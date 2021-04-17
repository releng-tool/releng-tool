# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from enum import Enum
from releng_tool.exceptions import RelengToolException

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

"""
raised when a package key is using an unsupported value
"""
class RelengToolInvalidPackageKeyValue(RelengToolException):
    def __init__(self, name, key, type_):
        RelengToolException.__init__(self, """\
package configuration has an invalid value: {}
 (key: {}, expects: {})\
""".format(name, key, type_))

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
