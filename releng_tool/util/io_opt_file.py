# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.log import warn
import os


# file extensions permitted for releng-tool scripts/definitions
RELENG_TOOL_EXTENSIONS = [
    '.rt',
    '.py',
]

# legacy file extensions for releng-tool scripts/definitions
RELENG_TOOL_LEGACY_EXTENSIONS = [
    '',
    '.releng',
]


def opt_file(file, *, warn_deprecated: bool = True) -> tuple[str, bool]:
    """
    return a file (and existence) to opt for based a given file path

    Various extension types are supported for user-defined configurations
    and scripts. For example, the default project configuration is named
    `releng-tool.rt`; however, select users may wish to define a
    `releng-tool.py` script instead. This utility call will return the file
    path and the existence state of the returned file. If the standard file
    does not exist but an alternative file does, this call will return the
    alternative file. Priority is given to the standard file, so if neither
    file exists, this call will return the provided/standard file path.

    Args:
        file: the file to check for
        warn_deprecated (optional): warn if a deprecated file is used

    Returns:
        a 2-tuple (file, existence flag)
    """

    for ext in RELENG_TOOL_EXTENSIONS:
        flex_file = file + ext
        if os.path.isfile(flex_file):
            return flex_file, True

    for ext in RELENG_TOOL_LEGACY_EXTENSIONS:
        flex_file = file + ext
        if os.path.isfile(flex_file):
            if warn_deprecated:
                fname = os.path.basename(file)
                warn('''\
detected use of deprecated file: {}
 (consider renaming to `{}.rt`)''', flex_file, fname)
            return flex_file, True

    return f'{file}.rt', False
