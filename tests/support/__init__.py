# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

from tests import find_test_base
import os

def fetch_unittest_assets_dir():
    """
    fetch the unit tests assets directory

    Will return the full path for the unit testing's asset directory.

    Returns:
        the directory
    """
    base_dir = find_test_base()
    return os.path.join(base_dir, 'unit-tests', 'assets')
