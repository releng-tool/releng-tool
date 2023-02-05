# -*- coding: utf-8 -*-
# Copyright 2021-2023 releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from datetime import timedelta
from datetime import tzinfo
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


if sys.version_info >= (3, 2):
    from datetime import timezone
    utc_timezone = timezone.utc
else:
    ZERO_TIME_DELTA = timedelta(0)

    class LegacyUtc(tzinfo):
        def dst(self, dt):  # noqa: ARG002
            return ZERO_TIME_DELTA

        def tzname(self, dt):  # noqa: ARG002
            return 'UTC'

        def utcoffset(self, dt):  # noqa: ARG002
            return ZERO_TIME_DELTA

    utc_timezone = LegacyUtc()
