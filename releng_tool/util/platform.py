# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.log import err
import sys


def platform_exit(msg=None, code=None):
    """
    exit out of the releng-tool process

    Provides a convenience method to help invoke a system exit call without
    needing to explicitly use ``sys``. A caller can provide a message to
    indicate the reason for the exit. The provide message will output to
    standard error. The exit code, if not explicit set, will vary on other
    arguments. If a message is provided to this call, the default exit code will
    be ``1``. If no message is provided, the default exit code will be ``0``.
    In any case, if the caller explicitly sets a code value, the provided code
    value will be used.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        releng_exit('there was an error performing this task')

    Args:
        msg (optional): error message to print
        code (optional): exit code; defaults to 0 if no message or defaults to 1
            if a message is set

    Raises:
        SystemExit: always raised
    """

    if msg:
        err(msg)
        if code is None:
            code = 1
    elif code is None:
        code = 0
    sys.exit(code)
