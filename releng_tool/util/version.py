# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

def str_to_version(val: str, *, relaxed: bool = False) -> list[int]:
    """
    convert a string into a comparable version value

    This call accepts a dotted-version string and converts in into an
    integer list. In turn, can be used to compare two version values with
    each other. For example:

        ver1 = str_to_version('1.1')
        ver2 = str_to_version('1.2')
        if ver2 > ver1:
            <do something>

    Args:
        val: the version string to parse
        **relaxed (optional): convert non-integer values to zero

    Returns:
        the list of integer version parts

    Raises:
        ValueError: if a non-integer value is detected
    """

    # convert the base version to a list of integers; any string special
    # suffix will just be assumed a zero value in a relaxed more, or throw
    # an exception to handle
    def cast_int(s: str) -> int:
        try:
            return int(s)
        except ValueError:
            # if operating in a strict mode, re-raise
            if not relaxed:
                raise

            return 0

    ver_list = list(map(cast_int, val.split('.')))

    # remove trailing zero values (e.g. allow 1.0.0 to equal 1.0)
    while ver_list and ver_list[-1] == 0:
        ver_list.pop()

    return ver_list or [0]
