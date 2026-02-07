# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import Rpk
from releng_tool.packages import pkg_key
from releng_tool.util.log import log


def printvars(pkgs, script_env):
    """
    request to print project/package variables to the output stream

    Provides a development helper to print various project/package variables
    to the output stream. This can be used to help determine which variables
    may be available, what variables had be set and more.

    Args:
        pkgs: the package names to print
        script_env: script environment information
    """

    for pkg in pkgs:
        for k, v in sorted(Rpk.__dict__.items()):
            if k.startswith('_'):
                continue

            key = pkg_key(pkg, v)
            suffix = ' (set)' if key in script_env else ''
            log(f'{key}{suffix}')
