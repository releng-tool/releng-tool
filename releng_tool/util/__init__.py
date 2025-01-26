# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

def nullish_coalescing(value, default):
    """
    nullish coalescing utility call

    Provides a return of the provided value unless the value is a ``None``,
    which instead the provided default value is returned instead.

    Args:
        value: the value
        default: the default value

    Returns:
        the provided value if not ``None``; otherwise, the default value
    """
    if value is None:
        return default

    return value
