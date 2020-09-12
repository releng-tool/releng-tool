# -*- coding: utf-8 -*-
# Copyright 2018-2019 releng-tool

from collections import Sequence
import os

try:
    basestring
except NameError:
    basestring = str

def expand(obj, kv=None):
    """
    perform variable expansion on strings

    This expand utility method will attempt to expand variables in detected
    string types. For a detected string which contains substrings in the form of
    ``$value`` or ``${value}``, these substrings will be replaced with their
    respective key-value (if provided) or environment variable value. For
    substrings which do not have a matching variable value, the substrings will
    be replaced with an empty value. If a dictionary is provided, keys and
    values will be checked if they can be expanded on. If a list/set is
    provided, each value which be checked if it can be expanded on. If a
    dictionary key is expanded to match another key, a key-value pair can be
    dropped. If a set may result in a smaller set if expanded values result in
    duplicate entries.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        import os
        ...

        os.environ['MY_ENV'] = 'my-environment-variable'
        value = releng_expand('$MY_ENV')
        print(value)
        # will output: my-environment-variable

    Args:
        obj: the object
        kv (optional): key-values pairs to use

    Returns:
        the expanded object
    """
    if isinstance(obj, basestring):
        try:
            idx = obj.index('$')
        except:
            return obj

        if kv:
            final_kv = dict(os.environ)
            final_kv.update(kv)
        else:
            final_kv = os.environ

        rv = obj[:idx]
        objlen = len(obj)

        while idx < objlen:
            c = obj[idx:idx + 1]
            if c == '$':
                nc = obj[idx + 1:idx + 2]
                if not nc or nc == '$' or nc.isspace():
                    rv += c
                    idx += 1
                elif nc == '{':
                    try:
                        eidx = obj.index('}', idx + 1)
                        var = obj[idx + 2:eidx]
                        if var in final_kv:
                            rv += final_kv[var]
                        idx = eidx
                    except:
                        rv += obj[idx:]
                        break
                else:
                    var = nc
                    idx += 1

                    nc = obj[idx + 1:idx + 2]
                    while nc and nc != '$' and (nc.isalnum() or nc == '_'):
                        var += nc
                        idx += 1
                        nc = obj[idx + 1:idx + 2]

                    if var in final_kv:
                        rv += final_kv[var]
            else:
                rv += c
            idx += 1
    elif isinstance(obj, dict):
        rv = {}
        for key, value in obj.items():
            rv[expand(key)] = expand(value)
    elif isinstance(obj, list):
        rv = []
        for value in obj:
            rv.append(expand(value))
    elif isinstance(obj, set):
        rv = set()
        for value in obj:
            rv.add(expand(value))
    else:
        rv = obj

    return rv

def interpretDictionaryStrings(obj):
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
            if not isinstance(key, basestring):
                rv = None
                break
            elif value is not None and not isinstance(value, basestring):
                rv = None
                break

    return rv

def interpretString(obj):
    """
    interpret a string, if any, from the provided object

    Attempts to interpret string from a provided object. If a string value is
    provided, it will be returned. In the case where an unexpected type is
    detected, this method will return ``None``.

    Args:
        obj: the object to interpret

    Returns:
        the string; otherwise ``None``
    """
    rv = None

    if isinstance(obj, basestring):
        rv = obj

    return rv

def interpretStrings(obj):
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

    if isinstance(obj, Sequence):
        if isinstance(obj, basestring):
            rv = [obj]
        else:
            rv = obj
            for child in obj:
                if not isinstance(child, basestring):
                    rv = None
                    break

    return rv

def interpretZeroToOneStrings(obj):
    """
    interpret a dictionary of zero-to-one strings from the provided object

    Attempts to interpret one or more zero-to-one strings from a provided
    object. A zero-to-one string is a string-based key which may or may not have
    an associated value assigned to it. If a key-value string dictionary value
    is provided, it will be returned. If the sequence of strings or a single
    string is provided, a dictionary will be populated with matching keys to
    provided names with ``None`` values. In the case where an unexpected type is
    detected, this method will return ``None``.

    Args:
        obj: the object to interpret

    Returns:
        the dictionary; otherwise ``None``
    """
    rv = None

    if isinstance(obj, dict):
        rv = obj
        for key, value in obj.items():
            if not isinstance(key, basestring):
                rv = None
                break
            elif value is not None and not isinstance(value, basestring):
                rv = None
                break
    elif isinstance(obj, Sequence):
        rv = {}
        if isinstance(obj, basestring):
            rv[obj] = None
        else:
            for child in obj:
                if not isinstance(child, basestring):
                    rv = None
                    break
                rv[child] = ''

    return rv

def isSequenceNotString(obj):
    """
    return whether or not the provided object is a non-string sequence

    Returns ``True`` if the provided ``obj`` is a sequence type but is also not
    a string; ``False`` otherwise.

    Args:
        obj: the object to interpret

    Returns:
        whether or not a non-string sequence
    """
    return isinstance(obj, Sequence) and not isinstance(obj, basestring)
