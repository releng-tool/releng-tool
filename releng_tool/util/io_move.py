# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import unicode_literals
from releng_tool.util.io import ensure_dir_exists
from releng_tool.util.io import path_remove
from releng_tool.util.log import err
from shutil import move
import os
import stat
import sys


def path_move(src, dst, quiet=False, critical=True, dst_dir=None, nested=False):
    """
    move a file or directory into a target file or directory

    .. versionchanged:: 0.14 Add support for ``dst_dir``.
    .. versionchanged:: 1.4 Add support for ``nested``.

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

    if src == dst:
        return True

    if nested and os.path.isdir(src):
        dst = os.path.join(dst, os.path.basename(src))

    if os.path.isfile(src) and not dst_dir:
        parent_dir = os.path.dirname(dst)
        if parent_dir and not os.path.isdir(parent_dir):
            success = ensure_dir_exists(parent_dir, quiet=quiet)
    elif not os.path.isdir(dst):
        if os.path.exists(dst):
            path_remove(dst)

        success = ensure_dir_exists(dst, quiet=quiet)
    else:
        src_dir = os.path.realpath(src)
        dst_dir = os.path.realpath(dst)
        if dst_dir.startswith(src_dir):
            if not quiet:
                err('unable to move source contents to target location\n'
                    '    attempt to move directory into a child subdirectory')
            if critical:
                sys.exit(-1)
            return False

    if success:
        try:
            if os.path.isfile(src):
                if os.path.isfile(dst):
                    path_remove(dst)

                move(src, dst)
            else:
                _path_move(src, dst)
        except Exception as e:
            success = False
            if not quiet:
                err('unable to move source contents to target location\n'
                    '    {}', e)

    if not success and critical:
        sys.exit(-1)
    return success


def path_move_into(src, dst, quiet=False, critical=True, nested=False):
    """
    move a file or directory into a target directory

    .. versionadded:: 0.14
    .. versionchanged:: 1.4 Add support for ``nested``.

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
        releng_move('my-file', 'my-file3')
        releng_move('my-directory', 'my-directory3')
        releng_move('my-file2', 'my-directory3')
        releng_move('my-directory2', 'my-directory3', nested=True)
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


def _path_move(src, dst):
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

    Raises:
        OSError: if a path could not be moved
    """

    # ensure a caller has read/write access before hand to prepare for moving
    # (e.g. if marked as read-only) and ensure contents can be fetched as well
    try:
        st = os.stat(src)
        if not (st.st_mode & stat.S_IRUSR) or not (st.st_mode & stat.S_IWUSR):
            os.chmod(src, st.st_mode | stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass

    entries = os.listdir(src)
    for entry in entries:
        src_path = os.path.join(src, entry)
        dst_path = os.path.join(dst, entry)

        if os.path.isdir(src_path) and not os.path.islink(src_path):
            if os.path.isdir(dst_path):
                _path_move(src_path, dst_path)
            else:
                if os.path.exists(dst_path):
                    path_remove(dst_path)

                move(src_path, dst_path)
        else:
            if os.path.exists(dst_path):
                path_remove(dst_path)

            move(src_path, dst_path)

    # remove directory
    os.rmdir(src)
