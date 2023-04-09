# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

class MetaEnum(type):
    """
    metaclass for an enum class

    Provides the ability for an enum-like class to be treated as a container for
    its defined class variables.
    """
    def __contains__(cls, item):
        return item in cls.__iter__()  # pylint: disable=E1120

    def __iter__(cls):
        return iter(
            [getattr(cls, a) for a in vars(cls) if not a.startswith('_')])


"""
basic enum class
"""
Enum = MetaEnum('Enum', (object,), {'__slots__': ()})
