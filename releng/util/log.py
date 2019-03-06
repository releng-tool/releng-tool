#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018-2019 releng-tool

from __future__ import print_function
import sys

#: flag to track the enablement of debug messages
RELENG_LOG_DEBUG_FLAG = False

#: flag to track the disablement of colorized messages
RELENG_LOG_NOCOLOR_FLAG = False

#: flag to track the enablement of verbose messages
RELENG_LOG_VERBOSE_FLAG = False

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
    global RELENG_LOG_DEBUG_FLAG
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
    __log('(error) ', '\033[1;31m', msg, sys.stderr, *args)

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
    global RELENG_LOG_VERBOSE_FLAG
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
    """
    __log('(warn) ', '\033[1;35m', msg, sys.stderr, *args)

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
    global RELENG_LOG_NOCOLOR_FLAG
    if RELENG_LOG_NOCOLOR_FLAG:
        color = ''
        post = ''
    else:
        post = '\033[0m'
    print('{}{}{}{}'.format(color, prefix, msg.format(*args), post), file=file)

def releng_log_configuration(debug, nocolor, verbose):
    """
    configure the global logging state of the running instance

    Adjusts the running instance's active state for logging-related
    configuration values. This method is best invoked near the start of the
    process's life cycle to provide consistent logging output. This method does
    not required to be invoked to invoke provided logging methods.

    Args:
        debug: toggle the enablement of debug messages
        nocolor: toggle the disablement of colorized messages
        verbose: toggle the enablement of verbose messages
    """
    global RELENG_LOG_DEBUG_FLAG
    global RELENG_LOG_NOCOLOR_FLAG
    global RELENG_LOG_VERBOSE_FLAG
    RELENG_LOG_DEBUG_FLAG = debug
    RELENG_LOG_NOCOLOR_FLAG = nocolor
    RELENG_LOG_VERBOSE_FLAG = verbose
