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
    .. versionchanged:: 2.2 Accepts a str, bytes or os.PathLike.

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
        path_obs = path.rglob('*')
    else:
        path_obs = path.iterdir()

    for p in sorted(path_obs):
        print(f'{p.relative_to(path)}{_desc(p)}')

    return True


def _desc(path: Path) -> str:
    """
    provide a description of a path entry

    Args:
        path: the path

    Returns:
        a path description
    """

    desc = ''

    if path.is_dir():
        desc += os.sep

    if path.is_symlink():
        desc += f' -> {path.readlink()}'

    return desc
