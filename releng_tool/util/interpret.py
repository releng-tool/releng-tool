# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from collections.abc import Sequence


def interpret_dict(obj, classinfo):
    """
    interpret a dictionary for a class hint, if any, from the provided object

    This call will return a dictionary based on the provided object. If a
    dictionary is provided, typically the same dictionary is returned. All
    keys in the resulting dictionary will be of a str class type. All values
    in the resulting dictionary will be of a class type based on the provided
    class hint. If any object is of a non-matching class type, this call
    will always return ``None``. Providing an empty dictionary will return
    the same dictionary.

    Args:
        obj: the object to interpret
        classinfo: the class hint

    Returns:
        dictionary of zero or more entries; otherwise ``None``
    """

    rv = None

    if isinstance(obj, dict):
        rv = obj

        for key, value in obj.items():
            if not isinstance(key, str):
                rv = None
                break

            if value is not None and not isinstance(value, classinfo):
                rv = None
                break

    return rv


def interpret_seq(obj, classinfo):
    """
    interpret a sequence for a class hint, if any, from the provided object

    This call will return a sequence based on the provided object(s). If a
    sequence is provided, typically the same sequence is returned. If a single
    object is provided, it will be returned as an entry of a new sequence.
    All objects in the resulting sequence will be of a class type based on the
    provided class hint. If any object is of a non-matching class type, this
    call will always return ``None``. Providing an empty sequence will return
    the same sequence.

    Args:
        obj: the object to interpret
        classinfo: the class hint

    Returns:
        sequence of zero or more objects; otherwise ``None``
    """

    rv = None

    if isinstance(obj, classinfo):
        rv = [obj]
    elif isinstance(obj, Sequence):
        if all(isinstance(child, classinfo) for child in obj):
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
        rv = interpret_dict(obj, str)
    elif isinstance(obj, str):
        rv = {
            obj: '',
        }
    elif isinstance(obj, Sequence):
        if all(isinstance(child, str) for child in obj):
            rv = {child: '' for child in obj}

    return rv
