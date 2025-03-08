# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from pathlib import Path
import os


def touch(file: str | bytes | os.PathLike,
        *args: str | bytes | os.PathLike) -> bool:
    """
    update a file's access/modifications times

    .. versionchanged:: 2.2 Accepts a str, bytes or os.PathLike.
    .. versionchanged:: 2.2 Add support for ``*args``.

    Attempts to update the access/modifications times on a file. If the file
    does not exist, it will be created. This utility call operates in the same
    fashion as the ``touch`` system command.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        if releng_touch('my-file'):
            print('file was created')
        else:
            print('file was not created')

    Args:
        file: the file
        *args (optional): additional components of the file

    Returns:
        ``True`` if the file was created/updated; ``False`` if the file could
        not be created/updated
    """

    final_file = Path(os.fsdecode(file), *map(os.fsdecode, args))

    try:
        container = final_file.parent
        container.mkdir(parents=True, exist_ok=True)

        final_file.touch(exist_ok=True)
    except OSError:
        return False
    else:
        return True
