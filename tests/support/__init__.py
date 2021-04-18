# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

import os

def fetch_unittest_assets_dir():
    """
    fetch the unit tests assets directory

    Will return the full path for the unit testing's asset directory.

    Returns:
        the directory
    """
    support_dir = os.path.dirname(os.path.realpath(__file__))
    base_dir = os.path.dirname(support_dir)
    return os.path.join(base_dir, 'unit-tests', 'assets')
