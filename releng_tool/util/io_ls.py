# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from pathlib import Path
import os


def ls(dir_: str | bytes | os.PathLike, *, recursive: bool = False) -> bool:
    """
    list a directory's contents

    .. versionadded:: 0.11
    .. versionchanged:: 2.0 Add support for ``recursive``.

    Attempts to read a directory for its contents and prints this information
    to the configured standard output stream.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        releng_ls('my-dir/')

    Args:
        dir_: the directory
        recursive (optional): recursive search of entries

    Returns:
        ``True`` if the directory could be read and its contents have been
        printed to the standard output; ``False`` if the directory could not
        be read
    """

    path = Path(os.fsdecode(dir_))
    if not path.is_dir():
        return False

    if recursive:
        for p in sorted(path.rglob('*')):
            pf = os.sep if p.is_dir() else ''
            print(f'{p.relative_to(path)}{pf}')
    else:
        for p in sorted(path.iterdir()):
            pf = os.sep if p.is_dir() else ''
            print(f'{p.relative_to(path)}{pf}')

    return True
