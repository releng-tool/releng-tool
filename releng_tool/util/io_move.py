# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from pathlib import Path
from releng_tool.util.critical import raise_for_critical
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.io_remove import path_remove
from releng_tool.util.log import err
from shutil import move
import os
import stat


def path_move(src: str | bytes | os.PathLike, dst: str | bytes | os.PathLike,
    *, quiet: bool = False, critical: bool = True, dst_dir: bool | None = None,
    nested: bool = False) -> bool:
    """
    move a file or directory into a target file or directory

    .. versionchanged:: 0.14 Add support for ``dst_dir``.
    .. versionchanged:: 1.4 Add support for ``nested``.
    .. versionchanged:: 2.2 Accepts a str, bytes or os.PathLike.

    This call will attempt to move a provided file, directory's contents or
    directory itself (if ``nested`` is ``True``); defined by ``src`` into a
    destination file or directory defined by ``dst``. If ``src`` is a file,
    then ``dst`` is considered to be a file or directory; if ``src`` is a
    directory, ``dst`` is considered a target directory. If a target
    directory or target file's directory does not exist, it will be
    automatically created.

    In the event that a file or directory could not be moved, an error message
    will be output to standard error (unless ``quiet`` is set to ``True``). If
    ``critical`` is set to ``True`` and the specified file/directory could not
    be moved for any reason, this call will issue a system exit
    (``SystemExit``).

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        # (input)
        # my-directory/another-file
        # my-file
        # my-file2
        releng_move('my-file', 'my-file3')
        releng_move('my-directory/', 'my-directory2/')
        releng_move('my-file2', 'my-directory2/')
        # (output)
        # my-directory2/another-file
        # my-directory2/my-file2
        # my-file3

    Args:
        src: the source directory or file
        dst: the destination directory or file\\* (\\*if ``src`` is a file)
        quiet (optional): whether or not to suppress output
        critical (optional): whether or not to stop execution on failure
        dst_dir (optional): force hint that the destination is a directory
        nested (optional): nest a source directory into the destination

    Returns:
        ``True`` if the move has completed with no error; ``False`` if the move
        has failed

    Raises:
        SystemExit: if the copy operation fails with ``critical=True``
    """

    success = True

    src_entry = Path(os.fsdecode(src))
    dst_str = os.fsdecode(dst)
    dst_flag = dst_str.endswith(('/', '\\')) if dst_dir is None else dst_dir
    dst_entry = Path(dst_str)

    if src_entry == dst_entry:
        return True

    if nested and src_entry.is_dir():
        dst_entry = dst_entry / src_entry.name

    if src_entry.is_file() and not dst_flag:
        parent_dir = dst_entry.parent
        if not parent_dir.is_dir():
            success = bool(mkdir(parent_dir, quiet=quiet))
    elif not dst_entry.is_dir():
        if dst_entry.exists():
            path_remove(dst_entry, quiet=quiet)

        success = bool(mkdir(dst_entry, quiet=quiet))
    elif dst_entry.is_relative_to(src_entry):
        if not quiet:
            err('unable to move source contents to target location\n'
                '    attempt to move directory into a child subdirectory')
        raise_for_critical(critical)
        return False

    if success:
        try:
            if src_entry.is_file():
                if dst_entry.is_file():
                    path_remove(dst_entry, quiet=quiet)

                move(src_entry, dst_entry)
            else:
                _path_move(src_entry, dst_entry, quiet=quiet)
        except Exception as e:
            success = False
            if not quiet:
                err('unable to move source contents to target location\n'
                    '    {}', e)

    raise_for_critical(not success and critical)
    return success


def path_move_into(src: str | bytes | os.PathLike,
    dst: str | bytes | os.PathLike, *, quiet: bool = False,
    critical: bool = True, nested: bool = False) -> bool:
    """
    move a file or directory into a target directory

    .. versionadded:: 0.14
    .. versionchanged:: 1.4 Add support for ``nested``.
    .. versionchanged:: 2.2 Accepts a str, bytes or os.PathLike.

    This call will attempt to move a provided file, directory's contents or
    directory itself (if ``nested`` is ``True``); defined by ``src`` into a
    destination directory defined by ``dst``. If a target directory directory
    does not exist, it will be automatically created.

    In the event that a file or directory could not be moved, an error message
    will be output to standard error (unless ``quiet`` is set to ``True``). If
    ``critical`` is set to ``True`` and the specified file/directory could not
    be moved for any reason, this call will issue a system exit
    (``SystemExit``).

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        # (input)
        # my-directory/another-file
        # my-directory2/another-file2
        # my-file
        # my-file2
        releng_move_into('my-file', 'my-file3')
        releng_move_into('my-directory', 'my-directory3')
        releng_move_into('my-file2', 'my-directory3')
        releng_move_into('my-directory2', 'my-directory3', nested=True)
        # (output)
        # my-directory3/my-directory2/another-file2
        # my-directory3/another-file
        # my-directory3/my-file2
        # my-file3

    Args:
        src: the source directory or file
        dst: the destination directory
        quiet (optional): whether or not to suppress output
        critical (optional): whether or not to stop execution on failure
        nested (optional): nest a source directory into the destination

    Returns:
        ``True`` if the move has completed with no error; ``False`` if the move
        has failed

    Raises:
        SystemExit: if the copy operation fails with ``critical=True``
    """

    return path_move(src, dst, quiet=quiet, critical=critical, dst_dir=True,
        nested=nested)


def _path_move(src: Path, dst: Path, *, quiet: bool = False) -> None:
    """
    move the provided directory into the target directory (recursive)

    Attempts to move the provided directory into the target directory. In the
    event that a file or directory could not be moved due to an error, this
    function will typically raise an OSError exception for `pathMove` to handle.

    In the chance that a file cannot be moved due to permission issues, this
    function can attempt to adjust permissions to specific paths to help in
    the moving processes (e.g. dealing with read-only files or other strict
    permissions setup during a build process).

    Args:
        src: the source directory
        dst: the destination directory
        quiet (optional): whether to suppress output

    Raises:
        OSError: if a path could not be moved
    """

    # ensure a caller has read/write access before hand to prepare for moving
    # (e.g. if marked as read-only) and ensure contents can be fetched as well
    try:
        st = src.stat()
        if not (st.st_mode & stat.S_IRUSR) or not (st.st_mode & stat.S_IWUSR):
            src.chmod(st.st_mode | stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass

    for src_path in src.iterdir():
        dst_path = dst / src_path.name

        if src_path.is_dir() and not src_path.is_symlink():
            if dst_path.is_dir():
                _path_move(src_path, dst_path, quiet=quiet)
            else:
                if dst_path.exists():
                    path_remove(dst_path, quiet=quiet)

                move(src_path, dst_path)
        else:
            if dst_path.exists():
                path_remove(dst_path, quiet=quiet)

            move(src_path, dst_path)

    # remove directory
    src.rmdir()
