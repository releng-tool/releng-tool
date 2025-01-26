# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from datetime import timedelta
from datetime import tzinfo
import sys

# ######################################################################
# various python compatible classes/functions

if sys.version_info >= (3, 2):
    from datetime import timezone
    utc_timezone = timezone.utc
else:
    ZERO_TIME_DELTA = timedelta(0)

    class LegacyUtc(tzinfo):
        def dst(self, dt):
            return ZERO_TIME_DELTA

        def tzname(self, dt):
            return 'UTC'

        def utcoffset(self, dt):
            return ZERO_TIME_DELTA

    utc_timezone = LegacyUtc()
