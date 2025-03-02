# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

# A flag (or option) can be driven by the existence of a file (i.e. a file
# flag). When an instance operates with file flags, two modes are approached in
# this implementation. Either the state of file flags are unknown and are
# attempted to be read. Once read, the instance can handle their process
# accordingly based off these flag states. The other path is if there is a
# request to configure file flags. If a file flag is being configured, the
# intent would be to configure the one (or multiple) file flag state and have
# the running instance shutdown.

from releng_tool.util.io_touch import touch
from releng_tool.util.log import err
from releng_tool.util.strccenum import StrCcEnum
import os


class FileFlag(StrCcEnum):
    """
    file flag result states

    Attributes:
        CONFIGURED: file flag was configured
        EXISTS: file flag exists
        NOT_CONFIGURED: unable to configure the file flag
        NO_EXIST: file flag does not exist
    """
    CONFIGURED = 'configured'
    EXISTS = 'exists'
    NOT_CONFIGURED = 'not_configured'
    NO_EXIST = 'no_exist'


def check_file_flag(file):
    """
    check a file flag

    Attempt to read a file flag state by checking for the file's existence.

    Args:
        file: the filename

    Returns:
        ``FileFlag.EXISTS`` if the flag is enabled; ``FileFlag.NO_EXIST`` if the
            flag is not enabled
    """
    return process_file_flag(file, None)


def process_file_flag(file, flag, quiet=False):
    """
    process a file flag event

    Will either write a file flag configuration event or attempt to read a file
    flag state. If the ``flag`` option is set to ``True``, this process event
    will assume that this instance is attempting to configure a file flag (on)
    state and generate the target file flag on the system. If the flag option is
    set to ``False``, the file's existence will be checked to reflect whether or
    not the flag is considered enabled.

    Args:
        file: the filename
        flag: the flag option to used; ``None`` to check flag state
        quiet: suppression of any error messages to standard out

    Returns:
        ``FileFlag.EXISTS`` if the flag is enabled; ``FileFlag.NO_EXIST`` if the
            flag is not enabled; ``FileFlag.CONFIGURED`` if the flag was
            configured as requested; ``FileFlag.NOT_CONFIGURED`` if the flag
            could not be configured as requested
    """

    if flag:
        # When checking if the file flag exists, attempt to update the access/
        # modified times. For the case where may experience issues creating the
        # file flag themselves (permission errors, etc.), fallback on just the
        # existence of the file flag to still be considered as configured.
        if touch(file):
            rv = FileFlag.CONFIGURED
        elif os.path.isfile(file):
            rv = FileFlag.CONFIGURED
        else:
            rv = FileFlag.NOT_CONFIGURED
            if not quiet:
                err('unable to configure file flag: {}', file)
    elif flag is None and os.path.isfile(file):
        rv = FileFlag.EXISTS
    else:
        rv = FileFlag.NO_EXIST

    return rv
