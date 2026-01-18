# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

import inspect


def global_define(var, default=None):
    """
    enforce a define/variable in the global context

    .. versionadded:: 2.7

    Ensures a provided variable is defined in the caller's global context.
    If not, the variable will be defined with the provided default value.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        val = releng_define('MY_DEFINE', 'default-value')
        print(val)
        # (or)
        releng_define('MY_DEFINE', 'default-value')
        print(MY_DEFINE)

    Args:
        var: the define/variable name
        default (optional): the default value to use if the define is not set

    Returns:
        the set value for this define
    """

    caller_globals = inspect.currentframe().f_back.f_globals

    if var not in caller_globals:
        caller_globals[var] = default

    return caller_globals[var]


def nullish_coalescing(value, default):
    """
    nullish coalescing utility call

    Provides a return of the provided value unless the value is a ``None``,
    which instead the provided default value is returned instead.

    Args:
        value: the value
        default: the default value

    Returns:
        the provided value if not ``None``; otherwise, the default value
    """
    if value is None:
        return default

    return value
