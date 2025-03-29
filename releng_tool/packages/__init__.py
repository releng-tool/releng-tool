# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import VOID
from releng_tool.util.interpret import interpret_dict
from releng_tool.util.interpret import interpret_opts
from releng_tool.util.interpret import interpret_seq
from releng_tool.util.strccenum import StrCcEnum
import hashlib
import os


class PkgKeyType(StrCcEnum):
    """
    package key type

    Enumeration of types supported when fetching configuration values defined by
    a package definition.

    Attributes:
        BOOL: boolean value
        BOOL_OR_STR: boolean value or a string value
        DICT: dictionary value
        DICT_STR_PSTR: dictionary of string keys with string/path-like values
        DICT_STR_STR_OR_STR: dictionary of string pairs or a string value
        INT_NONNEGATIVE: non-negative integer value
        INT_POSITIVE: positive integer value
        OPTS: dictionary of (command line) options
        PSTR: single string or path-like value
        STR: single string value
        STRS: one or more strings value
    """
    BOOL = 'bool'
    BOOL_OR_STR = 'bool_or_str'
    DICT = 'dict'
    DICT_STR_PSTR = 'dict_str_pstr'
    DICT_STR_STR_OR_STR = 'dict_str_str_or_str'
    INT_NONNEGATIVE = 'int_nonnegative'
    INT_POSITIVE = 'int_positive'
    OPTS = 'opts'
    PSTR = 'pstr'
    STR = 'str'
    STRS = 'strs'


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


def raw_value_parse(value: object, type_: PkgKeyType) -> object:
    """
    accepts a raw value for a package type and verifies/parses the result

    This call accepts a raw object value that is associated with a specific
    package key-type. The provided object will be verified and returned with
    a final object compatible for the package key-type. In the event that
    the object is not supported for the provided package key-type, an
    exception will be thrown.

    Args:
        value: the value to verify/parse
        type_: the package key type

    Returns:
        the parsed value

    Raises:
        TypeError if an unexpected type is detected for the package key type
        ValueError if an unexpected value is detected for the package key type
    """

    if type_ == PkgKeyType.BOOL:
        if not isinstance(value, bool):
            raise TypeError('bool')
    elif type_ == PkgKeyType.BOOL_OR_STR:
        if not isinstance(value, (bool, str)):
            raise TypeError('bool or string')
    elif type_ == PkgKeyType.DICT:
        if not isinstance(value, dict):
            raise TypeError('dictionary')
    elif type_ == PkgKeyType.DICT_STR_PSTR:
        value = interpret_dict(value, (str, bytes, os.PathLike))
        if value is None:
            raise TypeError('dict(str,str/path-like)')
        value = { k: os.fsdecode(v) if v is not None else v
                  for k, v in value.items() }  # type: ignore[attr-defined]
    elif type_ == PkgKeyType.DICT_STR_STR_OR_STR:
        if not isinstance(value, str):
            value = interpret_dict(value, str)
            if value is None:
                raise TypeError('dict(str,str) or string')
    elif type_ == PkgKeyType.INT_NONNEGATIVE:
        if not isinstance(value, int):
            raise TypeError('non-negative int')

        if value < 0:
            raise ValueError('non-negative int')
    elif type_ == PkgKeyType.INT_POSITIVE:
        if not isinstance(value, int):
            raise TypeError('positive int')

        if value <= 0:
            raise ValueError('positive int')
    elif type_ == PkgKeyType.OPTS:
        value = interpret_opts(value, (str, bytes, os.PathLike, type(VOID)))
        if value is None:
            raise TypeError('dict(str,str/path-like), str(s) or path-like(s)')
        value = { os.fsdecode(k) if k is not None else k:
                  os.fsdecode(v) if v not in (VOID, None) else v
                  for k, v in value.items() }  # type: ignore[attr-defined]
    elif type_ == PkgKeyType.PSTR:
        if not isinstance(value, (str, bytes, os.PathLike)):
            raise TypeError('string or path-like')
        value = os.fsdecode(value)
    elif type_ == PkgKeyType.STR:
        if not isinstance(value, str):
            raise TypeError('string')
    elif type_ == PkgKeyType.STRS:
        value = interpret_seq(value, str)
        if value is None:
            raise TypeError('string(s)')
    else:
        raise TypeError('<unsupported key-value>')

    return value
