# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import print_function
from releng_tool.exceptions import RelengToolWarningAsError
import sys

#: flag to track the enablement of debug messages
RELENG_LOG_DEBUG_FLAG = False

#: flag to track the disablement of colorized messages
RELENG_LOG_NOCOLOR_FLAG = False

#: flag to track the enablement of verbose messages
RELENG_LOG_VERBOSE_FLAG = False

#: flag to track if warnings should be treated as errors
RELENG_LOG_WERROR_FLAG = False


def log(msg, *args):
    """
    log a message

    Logs a (normal) message to standard out with a trailing new line.

    .. code-block:: python

        log('this is a message')

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    __log('', '', msg, sys.stdout, *args)


def debug(msg, *args):
    """
    log a debug message

    Logs a debug message to standard out with a trailing new line. By default,
    debug messages will not be output to standard out unless the instance is
    configured with debugging enabled.

    .. code-block:: python

        debug('this is a debug message')

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    if RELENG_LOG_DEBUG_FLAG:
        __log('(debug) ', '\033[2m', msg, sys.stdout, *args)


def err(msg, *args):
    """
    log an error message

    Logs an error message to standard error with a trailing new line and (if
    enabled) a red colorization.

    .. code-block:: python

        err('this is an error message')

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    sys.stdout.flush()
    __log('(error) ', '\033[1;31m', msg, sys.stderr, *args)
    sys.stderr.flush()


def hint(msg, *args):
    """
    log a hint message

    Logs a hint message to standard out with a trailing new line and (if
    enabled) a cyan colorization.

    .. code-block:: python

        hint('this is a hint message')

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    __log('', '\033[1;36m', msg, sys.stdout, *args)


def is_verbose():
    """
    report if the instance is configured with verbose messaging

    Allows a caller to determine whether or not the instance is actively
    configured with verbose messaging. This allow a caller to have the option to
    decide whether or not it needs to prepare a message for a ``verbose`` call,
    if the message to be built may include a performance cost.

    .. code-block:: python

        if is_verbose():
            msg = generate_info()
            verbose(msg)

    Returns:
        whether or not the instance is configured with verbose messaging
    """
    return RELENG_LOG_VERBOSE_FLAG


def note(msg, *args):
    """
    log a notification message

    Logs a notification message to standard out with a trailing new line and (if
    enabled) an inverted colorization.

    .. code-block:: python

        note('this is a note message')

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    __log('', '\033[7m', msg, sys.stdout, *args)


def success(msg, *args):
    """
    log a success message

    Logs a success message to standard error with a trailing new line and (if
    enabled) a green colorization.

    .. code-block:: python

        success('this is a success message')

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    __log('(success) ', '\033[1;32m', msg, sys.stdout, *args)


def verbose(msg, *args):
    """
    log a verbose message

    Logs a verbose message to standard out with a trailing new line and (if
    enabled) an inverted colorization. By default, verbose messages will not be
    output to standard out unless the instance is configured with verbosity.

    .. code-block:: python

        verbose('this is a verbose message')

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    if RELENG_LOG_VERBOSE_FLAG:
        __log('(verbose) ', '\033[2m', msg, sys.stdout, *args)


def warn(msg, *args):
    """
    log a warning message

    Logs a warning message to standard error with a trailing new line and (if
    enabled) a purple colorization.

    .. code-block:: python

        warn('this is a warning message')

    Args:
        msg: the message
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message

    Raises:
        RelengToolWarningAsError: when warnings-are-errors is configured
    """
    sys.stdout.flush()

    if RELENG_LOG_WERROR_FLAG:
        raise RelengToolWarningAsError(msg.format(*args))

    __log('(warn) ', '\033[1;35m', msg, sys.stderr, *args)
    sys.stderr.flush()


def __log(prefix, color, msg, file, *args):
    """
    utility logging method

    A log method to help format a message based on provided prefix and color.

    Args:
        prefix: prefix to add to the message
        color: the color to apply to the message
        msg: the message
        file: the file to write to
        *args: an arbitrary set of positional and keyword arguments used when
            generating a formatted message
    """
    if RELENG_LOG_NOCOLOR_FLAG:
        color = ''
        post = ''
    else:
        post = '\033[0m'
    msg = str(msg)
    if args:
        msg = msg.format(*args)
    print('{}{}{}{}'.format(color, prefix, msg, post), file=file)


def releng_log_configuration(debug_, nocolor, verbose_, werror):
    """
    configure the global logging state of the running instance

    Adjusts the running instance's active state for logging-related
    configuration values. This method is best invoked near the start of the
    process's life cycle to provide consistent logging output. This method does
    not required to be invoked to invoke provided logging methods.

    Args:
        debug_: toggle the enablement of debug messages
        nocolor: toggle the disablement of colorized messages
        verbose_: toggle the enablement of verbose messages
        werror: toggle the enablement of warnings-are-errors
    """
    global RELENG_LOG_DEBUG_FLAG
    global RELENG_LOG_NOCOLOR_FLAG
    global RELENG_LOG_VERBOSE_FLAG
    global RELENG_LOG_WERROR_FLAG
    RELENG_LOG_DEBUG_FLAG = debug_
    RELENG_LOG_NOCOLOR_FLAG = nocolor
    RELENG_LOG_VERBOSE_FLAG = verbose_
    RELENG_LOG_WERROR_FLAG = werror
