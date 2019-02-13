#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from .log import *
import sys

def exit(msg=None, code=0):
    """
    exit out of the releng-tool process

    Provides a convenience method to help invoke a system exit call without
    needing to explicitly use ``sys``. A caller can provide a message to
    indicate the reason for the exit. The provide message will output to
    standard error.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        releng_exit('there was an error performing this task')

    Args:
        msg (optional): error message to print
        code (optional): exit code (default: 0)

    Raises:
        SystemExit: always raised
    """

    if msg:
        err(msg)
    sys.exit(code)
