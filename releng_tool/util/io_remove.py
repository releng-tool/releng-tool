# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from pathlib import Path
from releng_tool.util.log import debug
from releng_tool.util.log import err
import errno
import os
import stat


def path_remove(path: str | bytes | os.PathLike, quiet=False) -> bool:
    """
    remove the provided path

    .. versionchanged:: 2.2 Accepts a str, bytes or os.PathLike.

    Attempts to remove the provided path if it exists. The path value can either
    be a directory or a specific file. If the provided path does not exist, this
    method has no effect. In the event that a file or directory could not be
    removed due to an error other than unable to be found, an error message will
    be output to standard error (unless ``quiet`` is set to ``True``).

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        releng_remove('my-file')
        # (or)
        releng_remove('my-directory/')

    Args:
        path: the path to remove
        quiet (optional): whether or not to suppress output

    Returns:
        ``True`` if the path was removed or does not exist; ``False`` if the
        path could not be removed from the system
    """

    req_path = Path(os.fsdecode(path))

    if not req_path.exists() and not req_path.is_symlink():
        return True

    try:
        if req_path.is_dir() and not req_path.is_symlink():
            _path_remove_dir(req_path)
        else:
            _path_remove_file(req_path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            if not quiet:
                err('unable to remove path: {}\n'
                    '    {}', req_path, e)
            return False

    return True


def _path_remove_dir(dir_: Path) -> None:
    """
    remove the provided directory (recursive)

    Attempts to remove the provided directory. In the event that a file or
    directory could not be removed due to an error, this function will typically
    raise an OSError exception.

    In the chance that a file cannot be removed due to permission issues, this
    function can attempt to adjust permissions to specific paths to help in the
    removal processes (e.g. dealing with read-only files or other strict
    permissions setup during a build process).

    Args:
        dir_: the directory to remove

    Raises:
        OSError: if a path could not be removed
    """

    # ensure a caller has read/write access before hand to prepare for removal
    # (e.g. if marked as read-only) and ensure contents can be fetched as well
    try:
        st = dir_.stat()
        if not (st.st_mode & stat.S_IRUSR) or not (st.st_mode & stat.S_IWUSR):
            dir_.chmod(st.st_mode | stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass

    # remove directory contents (if any)
    for entry in dir_.iterdir():
        path = dir_ / entry
        if path.is_dir() and not path.is_symlink():
            _path_remove_dir(path)
        else:
            _path_remove_file(path)

    # remove directory
    debug(f'removing directory: {dir_}')
    dir_.rmdir()


def _path_remove_file(path: Path) -> None:
    """
    remove the provided file

    Attempts to remove the provided file. In the event that the file could not
    be removed due to an error, this function will typically raise an OSError
    exception.

    In the chance that a file cannot be removed due to permission issues, this
    function can attempt to adjust permissions to specific paths to help in the
    removal processes (e.g. dealing with read-only files or other strict
    permissions setup during a build process).

    Args:
        path: the file to remove

    Raises:
        OSError: if the file could not be removed
    """

    try:
        debug(f'removing file: {path}')
        path.unlink(missing_ok=True)
    except OSError as e:
        if e.errno != errno.EACCES:
            raise

        # if a file could not be removed, try adding write permissions
        # and retry removal
        try:
            st = path.stat()
            if (st.st_mode & stat.S_IWUSR):
                raise

            path.chmod(st.st_mode | stat.S_IWUSR)
            path.unlink(missing_ok=True)
        except OSError as ex2:
            raise e from ex2
