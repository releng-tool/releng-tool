# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from collections.abc import Sequence
import os
import re


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
    if isinstance(obj, str):
        try:
            idx = obj.index('$')
        except ValueError:
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
                    except ValueError:
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
            rv[expand(key, kv=kv)] = expand(value, kv=kv)
    elif isinstance(obj, list):
        rv = []
        for value in obj:
            rv.append(expand(value, kv=kv))
    elif isinstance(obj, set):
        rv = set()
        for value in obj:
            rv.add(expand(value, kv=kv))
    else:
        rv = obj

    return rv


def is_sequence_not_string(obj):
    """
    return whether or not the provided object is a non-string sequence

    Returns ``True`` if the provided ``obj`` is a sequence type but is also not
    a string; ``False`` otherwise.

    Args:
        obj: the object to interpret

    Returns:
        whether or not a non-string sequence
    """
    return isinstance(obj, Sequence) and not isinstance(obj, str)


def normalize(name):
    """
    return a normalized name

    Returns a consistent name representation for a given string. This replaces
    various characters from a value with a ``-`` character and strips the name.

    Args:
        name: the name to be normalized

    Returns:
        the normalized name
    """
    return re.sub(r'[ *\-_,.:;?!|\\]+', '-', name.strip(' -')).lower()
