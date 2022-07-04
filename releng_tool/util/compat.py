# -*- coding: utf-8 -*-
# Copyright 2021-2022 releng-tool

import sys

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

which = _compat_which
