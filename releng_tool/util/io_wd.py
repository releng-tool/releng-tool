# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.log import warn
import os


@contextmanager
def wd(dir_: str | bytes | os.PathLike) -> Iterator[str]:
    """
    move into a context-supported working directory

    .. versionchanged:: 2.2 Accepts a str, bytes or os.PathLike.

    Moves the current context into the provided working directory ``dir``. When
    returned, the original working directory will be restored. If the provided
    directory does not exist, it will created. If the directory could not be
    created, an ``FailedToPrepareWorkingDirectoryError`` exception will be
    thrown.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        with releng_wd('my-directory/'):
            # invoked in 'my-directory'

        # invoked in original working directory

    Args:
        dir_: the target working directory

    Raises:
        FailedToPrepareWorkingDirectoryError: the working directory does not
            exist and could not be created
    """

    owd = Path.cwd()

    target_dir = Path(os.fsdecode(dir_))
    if not mkdir(target_dir):
        raise FailedToPrepareWorkingDirectoryError(target_dir)

    os.chdir(target_dir)
    try:
        yield str(target_dir)
    finally:
        try:
            os.chdir(owd)
        except OSError:
            warn(f'unable to restore original working directory: {owd}')


class FailedToPrepareWorkingDirectoryError(Exception):
    """
    raised when a working directory could not be prepared
    """
