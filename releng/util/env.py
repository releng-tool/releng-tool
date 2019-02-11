#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

import types

def extendScriptEnv(env, extra):
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
    extraCopy = extra.copy()

    for key, value in extra.items():
        # remove python magic objects (if any)
        if key.startswith('__') and key.endswith('__'):
            extraCopy.pop(key)
        # remove imported built-in functions
        elif isinstance(value, types.BuiltinFunctionType):
            extraCopy.pop(key)
        # remove imported functions
        elif isinstance(value, types.FunctionType):
            extraCopy.pop(key)
        # remove imported modules
        elif isinstance(value, types.ModuleType):
            extraCopy.pop(key)

    env.update(extraCopy)
    return env
