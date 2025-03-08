# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from pathlib import Path
import os


def path_exists(path: str | bytes | os.PathLike,
        *args: str | bytes | os.PathLike) -> bool:
    """
    return whether or not the path exists

    .. versionchanged:: 2.2 Accepts a str, bytes or os.PathLike.

    Allows a caller to verify the existence of a file on the file system. This
    call will return ``True`` if the path exists; ``False`` otherwise.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        if releng_exists('my-file'):
            print('the file exists')
        else:
            print('the file does not exist')

    Args:
        path: the path
        *args (optional): additional components of the file

    Returns:
        ``True`` if the path exists; ``False`` otherwise
    """

    return Path(os.fsdecode(path), *map(os.fsdecode, args)).exists()
