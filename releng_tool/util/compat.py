# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

from functools import partial
import sys

# import compatible `copytree` calls, use shutil's copytree with dirs_exist_ok
# set; otherwise fallback to distutil's copy_tree call
if sys.version_info >= (3, 8):
    from shutil import copytree as shutil_copy_tree

    _CompatCopyTreeError = IOError
    _compat_copy_tree = partial(shutil_copy_tree, dirs_exist_ok=True)
else:
    from distutils.dir_util import DistutilsFileError
    from distutils.dir_util import copy_tree as distutils_copy_tree

    _CompatCopyTreeError = DistutilsFileError
    _compat_copy_tree = distutils_copy_tree

# import compatible `which` calls, use shutil's which if possible; otherwise
# fallback to distutil's find_executable call
if sys.version_info >= (3, 3):
    from shutil import which as shutil_which
    _compat_which = shutil_which
else:
    from distutils.spawn import find_executable as distutils_which
    _compat_which = distutils_which


# ######################################################################
# various python compatible classes/functions


class CopyTreeError(Exception):
    pass


def copy_tree(src, dst):
    try:
        _compat_copy_tree(src, dst)
    except _CompatCopyTreeError as e:
        raise CopyTreeError(str(e))


which = _compat_which
