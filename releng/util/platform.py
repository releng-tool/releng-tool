#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from .log import *
import sys

def exit(msg=None, code=0):
    """
    exit out of the releng-tool process

    Provides a convenience method to help invoke a system exit call without
    needing to explicitly use ``sys``.

    Args:
        msg (optional): error message to print
        code (optional): exit code (default: 0)

    Raises:
        SystemExit: always raised
    """

    if msg:
        err(msg)
    sys.exit(code)
