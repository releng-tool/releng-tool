# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from collections.abc import Sequence


def interpret_dict_strs(obj):
    """
    interpret a dictionary of key-value strings from the provided object

    Attempts to interpret one or more key-value string pairs from a provided
    object. If a key-value string dictionary value is provided, it will be
    returned. In the case where an unexpected type is detected, this method will
    return ``None``.

    Args:
        obj: the object to interpret

    Returns:
        the dictionary; otherwise ``None``
    """

    rv = None

    if isinstance(obj, dict):
        rv = obj

        for key, value in obj.items():
            if not isinstance(key, str):
                rv = None
                break

            if value is not None and not isinstance(value, str):
                rv = None
                break

    return rv


def interpret_strs(obj):
    """
    interpret strings, if any, from the provided object

    Attempts to interpret one or more strings from a provided object. Returned
    will be an iterable containing one or more strings. If a string value is
    provided, it will be returned inside iterable container. If an iterable
    container is provided, the same container will be returned. In the case
    where an unexpected type is detected, this method will return ``None``.

    Args:
        obj: the object to interpret

    Returns:
        sequence of zero or more strings; otherwise ``None``
    """

    rv = None

    if isinstance(obj, str):
        rv = [obj]
    elif isinstance(obj, Sequence):
        if all(isinstance(child, str) for child in obj):
            rv = obj

    return rv


def interpret_zero_to_one_strs(obj):
    """
    interpret a dictionary of zero-to-one strings from the provided object

    Attempts to interpret one or more zero-to-one strings from a provided
    object. A zero-to-one string is a string-based key which may or may not have
    an associated value assigned to it. If a key-value string dictionary value
    is provided, it will be returned. If the sequence of strings or a single
    string is provided, a dictionary will be populated with matching keys to
    provided names with empty string values. In the case where an unexpected
    type is detected, this method will return ``None``.

    Args:
        obj: the object to interpret

    Returns:
        the dictionary; otherwise ``None``
    """

    rv = None

    if isinstance(obj, dict):
        rv = interpret_dict_strs(obj)
    elif isinstance(obj, str):
        rv = {
            obj: '',
        }
    elif isinstance(obj, Sequence):
        if all(isinstance(child, str) for child in obj):
            rv = {child: '' for child in obj}

    return rv
