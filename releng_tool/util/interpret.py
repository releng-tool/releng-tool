# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from collections.abc import Sequence
from releng_tool.defs import VOID


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


def interpret_opts(obj, classinfo):
    """
    interpret a dictionary of option values with a class hint

    This call will return a dictionary based on the provided object. If a
    dictionary is provided, typically the same dictionary is returned. All
    keys in the resulting dictionary will be of a str class type. All values
    in the resulting dictionary will be of a class type based on the provided
    class hint or an ``VOID`` value. If any object is of a non-matching
    class type, this call will always return ``None``. Providing an empty
    dictionary will return the same dictionary.

    An option value is a string-based key which may or may not have
    an associated value assigned to it. The value will either be set to an
    expected type, hold an ``VOID`` value indicating the option does not
    associate with a given value or holds a ``None`` value typically
    indicating the option does not apply (e.g. "subject to removal").

    For example, the option ``--opt`` has a value of ``val``:

        {
            '--opt': 'val',
        }

    Where the option ``--flag`` has no value associated to it:

        {
            '--flag': VOID,
        }

    And the option ``--flag`` indicates the flag should not be used:

        {
            '--flag': None,
        }

    Args:
        obj: the object to interpret
        classinfo: the class hint

    Returns:
        dictionary of options; otherwise ``None``
    """

    rv = None

    if isinstance(obj, dict):
        rv = interpret_dict(obj, classinfo)
    elif isinstance(obj, classinfo):
        rv = {
            obj: VOID,
        }
    elif isinstance(obj, Sequence):
        if all(isinstance(child, classinfo) for child in obj):
            rv = dict.fromkeys(obj, VOID)

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
