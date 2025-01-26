# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import find_test_base
import os


def fetch_unittest_assets_dir(*args):
    """
    fetch the unit tests assets directory

    Will return the full path for the unit testing's asset directory.

    Args:
        *args (optional): path entries to append to the asset directory

    Returns:
        the directory
    """
    base_dir = find_test_base()
    return os.path.join(base_dir, 'unit-tests', 'assets', *args)
