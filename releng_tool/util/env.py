# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

import os
import types


def extend_script_env(env, extra):
    """
    extend a partially filtered environment (globals) for a run_path event

    When invoking ``run_path`` [1], a dictionary of globals is provided to
    pre-populate a script's globals before execution. Inside the releng process,
    the command ``run_path`` is invoked several times to help load settings and
    package-specific scripts. To exist in sharing releng-provided constants and
    also assisting in allow some-level of sharing user-defined constants, the
    list of globals to be populated can be extended each execution and be passed
    into a following script. Not all global options are desired to be passed.
    For example, Python magic options and referenced built-in functions. This
    method can be used to easily extend an existing dictionary of globals while
    also filtering out undesired entries output from external scripts.

    [1]: https://docs.python.org/3/library/runpy.html

    Args:
        env: the environment to update
        extra: the globals to add to the environment

    Returns:
        the same environment passed in
    """
    extra_copy = extra.copy()

    for key, value in extra.items():
        # remove python magic objects (if any)
        if key.startswith('__') and key.endswith('__'):
            extra_copy.pop(key)
        # remove imported built-in functions
        elif isinstance(value, types.BuiltinFunctionType):
            extra_copy.pop(key)
        # remove imported functions
        elif isinstance(value, types.FunctionType):
            extra_copy.pop(key)
        # remove imported modules
        elif isinstance(value, types.ModuleType):
            extra_copy.pop(key)

    env.update(extra_copy)
    return env


# unique default helper for env_value
__ENV_VALUE_DEFAULT = object()


def env_value(key, value=__ENV_VALUE_DEFAULT):
    """
    helper to easily fetch or configure an environment variable

    .. versionadded:: 0.3

    Provides a caller a simple method to fetch or configure an environment
    variable for the current context. This call is the same as if one directly
    fetched from or managed a key-value with ``os.environ``. If ``value`` is not
    provided, the environment variable's value (if set) will be returned. If
    ``value`` is set to a value of ``None``, any set environment variable will
    be removed.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        # get an environment variable
        value = releng_env('KEY')

        # set an environment variable
        releng_env('KEY', 'VALUE')

    Args:
        key: the environment key
        value (optional): the environment value to set

    Returns:
        the value of the environment variable
    """
    if value is __ENV_VALUE_DEFAULT:
        return os.environ.get(key)

    if value is None:
        if key in os.environ:
            del os.environ[key]
    else:
        os.environ[key] = value

    return value
