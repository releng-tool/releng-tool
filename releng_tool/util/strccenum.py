# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool
#
# Provides a compatibility helper for the use of `StrEnum` with containment
# check support. Since releng-tool supports running LTS versions older
# than Python 3.12, `StrEnum` with containment check support may not be
# available. Instead, use a compatibility variant for what this tool needs.

import sys


if sys.version_info >= (3, 12):
    from enum import StrEnum as StrCcEnum
else:
    class MetaEnum(type):
        """
        metaclass for an enum class

        Provides the ability for an enum-like class to be treated as a
        container for its defined class variables.
        """
        def __contains__(cls, item):
            return item in cls.__iter__()  # pylint: disable=E1120

        def __iter__(cls):
            return iter(
                [getattr(cls, a) for a in vars(cls) if not a.startswith('_')])

    """
    basic enum class
    """
    StrCcEnum = MetaEnum(  # type: ignore  # noqa: PGH003
        'Enum', (object,), {'__slots__': ()})
