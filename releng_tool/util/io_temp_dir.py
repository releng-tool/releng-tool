# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.io_remove import path_remove
from releng_tool.util.io_wd import wd
from releng_tool.util.log import warn
import errno
import os
import tempfile


@contextmanager
def temp_dir(dir_: str | bytes | os.PathLike | None = None,
        *args: str | bytes | os.PathLike, **kwargs) -> Iterator[str]:
    """
    generate a context-supported temporary directory

    .. versionchanged:: 2.2 Accepts a str, bytes or os.PathLike.
    .. versionchanged:: 2.2 Add support for ``*args`` and ``**wd``.

    Creates a temporary directory in the provided directory ``dir_`` (or system
    default, is not provided). This is a context-supported call and will
    automatically remove the directory when completed. If the provided
    directory does not exist, it will created. If the directory could not be
    created, an ``FailedToPrepareBaseDirectoryError`` exception will be thrown.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        with releng_tmpdir() as dir_:
            print(dir_)

    Args:
        dir_ (optional): the directory to create the temporary directory in
        **wd (optional): whether to use the temporary directory as the
                          working directory (defaults to ``False``)

    Raises:
        FailedToPrepareBaseDirectoryError: the base directory does not exist and
            could not be created
    """

    base_dir = None
    if dir_:
        base_dir = Path(os.fsdecode(dir_), *map(os.fsdecode, args))
        if not mkdir(base_dir):
            raise FailedToPrepareBaseDirectoryError(base_dir)

    tmp_dir = tempfile.mkdtemp(prefix='.releng-tmp-', dir=base_dir)
    try:
        if kwargs.get('wd'):
            with wd(tmp_dir):
                yield tmp_dir
        else:
            yield tmp_dir
    finally:
        try:
            path_remove(tmp_dir)
        except OSError as e:
            if e.errno != errno.ENOENT:
                warn('unable to cleanup temporary directory: {}\n'
                     '    {}', tmp_dir, e)


class FailedToPrepareBaseDirectoryError(Exception):
    """
    raised when a base directory could not be prepared
    """
