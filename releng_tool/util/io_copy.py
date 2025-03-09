# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from pathlib import Path
from releng_tool.util.critical import raise_for_critical
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.io_remove import path_remove
from releng_tool.util.log import err
from shutil import Error as ShutilError
from shutil import copyfile
from shutil import copystat
import os


def path_copy(src: str | bytes | os.PathLike, dst: str | bytes | os.PathLike,
    *, quiet: bool = False, critical: bool = True, dst_dir: bool | None = None,
    nested: bool = False) -> bool:
    """
    copy a file or directory into a target file or directory

    .. versionchanged:: 0.12 Add support for ``dst_dir``.
    .. versionchanged:: 1.4 Add support for ``nested``.
    .. versionchanged:: 2.2 Accepts a str, bytes or os.PathLike.

    This call will attempt to copy a provided file, directory's contents or
    directory itself (if ``nested`` is ``True``); defined by ``src`` into a
    destination file or directory defined by ``dst``. If ``src`` is a file,
    then ``dst`` is considered to be a file or directory; if ``src`` is a
    directory, ``dst`` is considered a target directory. If a target
    directory or target file's directory does not exist, it will be
    automatically created. In the event that a file or directory could not be
    copied, an error message will be output to standard error (unless ``quiet``
    is set to ``True``). If ``critical`` is set to ``True`` and the specified
    file/directory could not be copied for any reason, this call will issue a
    system exit (``SystemExit``).

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        # (stage)
        # my-file
        releng_copy('my-file', 'my-file2')
        # (stage)
        # my-file
        # my-file2
        releng_copy('my-file', 'my-directory/')
        # (stage)
        # my-directory/my-file
        # my-file
        # my-file2
        releng_copy('my-directory/', 'my-directory2/')
        # (stage)
        # my-directory/my-file
        # my-directory2/my-file
        # my-file
        # my-file2

    Args:
        src: the source directory or file
        dst: the destination directory or file\\* (\\*if ``src`` is a file)
        quiet (optional): whether or not to suppress output
        critical (optional): whether or not to stop execution on failure
        dst_dir (optional): force hint that the destination is a directory
        nested (optional): nest a source directory into the destination

    Returns:
        ``True`` if the copy has completed with no error; ``False`` if the copy
        has failed

    Raises:
        SystemExit: if the copy operation fails with ``critical=True``
    """
    success = False
    errmsg = None

    src_entry = Path(os.fsdecode(src))
    dst_str = os.fsdecode(dst)
    dst_flag = dst_str.endswith(('/', '\\')) if dst_dir is None else dst_dir
    dst_entry = Path(dst_str)

    try:
        if src_entry.is_dir() and not src_entry.is_symlink():
            if src_entry == dst_entry:
                errmsg = "'{!s}' and '{!s}' " \
                         "are the same folder".format(src_entry, dst_entry)
            elif nested:
                new_dst = dst_entry / src_entry.name
                if _copy_tree(src_entry, new_dst, quiet=quiet, critical=critical):
                    success = True
            elif _copy_tree(src_entry, dst_entry, quiet=quiet, critical=critical):
                success = True
        elif src_entry.is_file() or src_entry.is_symlink():
            attempt_copy = True

            if dst_flag:
                base_dir = dst_entry
            else:
                base_dir = dst_entry.parent

            if base_dir and not base_dir.is_dir():
                attempt_copy = bool(mkdir(base_dir, quiet=quiet))
            else:
                attempt_copy = True

            if attempt_copy:
                if dst_entry.is_dir():
                    dst_entry = dst_entry / src_entry.name

                if src_entry.is_symlink():
                    target = src_entry.readlink()
                    if dst_entry.is_symlink() or dst_entry.is_file():
                        path_remove(dst_entry, quiet=quiet)

                    dst_entry.symlink_to(target)
                else:
                    copyfile(src_entry, dst_entry, follow_symlinks=False)

                # copy file statistics if both source and destination exist
                if src_entry.is_file() and dst_entry.is_file():
                    copystat(src_entry, dst_entry)

                success = True
        else:
            errmsg = f'source does not exist: {src_entry}'
    except (OSError, ShutilError) as e:
        errmsg = str(e)

    if not quiet and errmsg:
        err('unable to copy source contents to target location\n'
            '    {}', errmsg)

    raise_for_critical(not success and critical)
    return success


def path_copy_into(src: str | bytes | os.PathLike,
    dst: str | bytes | os.PathLike, *, quiet: bool = False,
    critical: bool = True, nested: bool = False) -> bool:
    """
    copy a file or directory into a target directory

    .. versionadded:: 0.13
    .. versionchanged:: 1.4 Add support for ``nested``.
    .. versionchanged:: 2.2 Accepts a str, bytes or os.PathLike.

    This call will attempt to copy a provided file, directory's contents or
    directory itself (if ``nested`` is ``True``); defined by ``src`` into a
    destination directory defined by ``dst``. If a target directory does not
    exist, it will be automatically created. In the event that a file or
    directory could not be copied, an error message will be output to
    standard error (unless ``quiet`` is set to ``True``). If ``critical``
    is set to ``True`` and the specified file/directory could not be copied
    for any reason, this call will issue a system exit (``SystemExit``).

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        # (stage)
        # my-file
        releng_copy_into('my-file', 'my-directory')
        # (stage)
        # my-directory/my-file
        # my-file
        releng_copy_into('my-directory', 'my-directory2')
        # (stage)
        # my-directory/my-file
        # my-directory2/my-file
        # my-file
        releng_copy_into('my-directory', 'my-directory3', nested=True)
        # (stage)
        # my-directory/my-file
        # my-directory2/my-file
        # my-directory3/directory/my-file
        # my-file

    Args:
        src: the source directory or file
        dst: the destination directory
        quiet (optional): whether or not to suppress output
        critical (optional): whether or not to stop execution on failure
        nested (optional): nest a source directory into the destination

    Returns:
        ``True`` if the copy has completed with no error; ``False`` if the copy
        has failed

    Raises:
        SystemExit: if the copy operation fails with ``critical=True``
    """

    return path_copy(src, dst, quiet=quiet, critical=critical, dst_dir=True,
        nested=nested)


def _copy_tree(src_folder: Path, dst_folder: Path, *,
        quiet: bool = False, critical: bool = True) -> bool:
    """
    copy a source tree into a destination tree

    Attempt to copy the contents of a source folder into a target destination
    folder.

    Args:
        src_folder: the source directory or file
        dst_folder: the destination directory
        quiet (optional): whether to suppress output
        critical (optional): whether to stop execution on failure

    Returns:
        ``True`` if the copy has completed with no error; ``False`` if the copy
        has failed

    Raises:
        SystemExit: if the tree copy fails with ``critical=True``
    """

    if not mkdir(dst_folder, quiet=quiet, critical=critical):
        return False

    for src in src_folder.iterdir():
        dst = dst_folder / src.name

        if src.is_symlink():
            target = src.readlink()
            if dst.is_symlink() or dst.is_file():
                path_remove(dst, quiet=quiet)

            dst.symlink_to(target)
            if target.is_file() and dst.is_file():
                copystat(src, dst)
        elif src.is_dir():
            _copy_tree(src, dst, quiet=quiet, critical=critical)
        else:
            copyfile(src, dst, follow_symlinks=False)
            copystat(src, dst)

    copystat(src_folder, dst_folder)

    return True
