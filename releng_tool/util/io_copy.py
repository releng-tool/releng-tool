# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import unicode_literals
from functools import partial
from releng_tool.util.io import ensure_dir_exists
from releng_tool.util.io import path_remove
from releng_tool.util.log import err
from shutil import Error as ShutilError
from shutil import copyfile as shutil_copyfile
from shutil import copystat as shutil_copystat
import os
import sys

if sys.version_info[0] >= 3:  # noqa: PLR2004
    _copyfile = partial(shutil_copyfile, follow_symlinks=False)
    _copystat = partial(shutil_copystat, follow_symlinks=False)
else:
    _copyfile = shutil_copyfile
    _copystat = shutil_copystat


def path_copy(src, dst, quiet=False, critical=True, dst_dir=None):
    """
    copy a file or directory into a target file or directory

    This call will attempt to copy a provided file or directory, defined by
    ``src`` into a destination file or directory defined by ``dst``. If ``src``
    is a file, then ``dst`` is considered to be a file or directory; if ``src``
    is a directory, ``dst`` is considered a target directory. If a target
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

    Returns:
        ``True`` if the copy has completed with no error; ``False`` if the copy
        has failed

    Raises:
        SystemExit: if the copy operation fails with ``critical=True``
    """
    success = False
    errmsg = None

    try:
        if os.path.isfile(src):
            attempt_copy = True

            if dst_dir:
                base_dir = dst
            else:
                base_dir = os.path.dirname(dst)

            if base_dir and not os.path.isdir(base_dir):
                attempt_copy = ensure_dir_exists(base_dir, quiet=quiet)
            else:
                attempt_copy = True

            if attempt_copy:
                if os.path.isdir(dst):
                    dst = os.path.join(dst, os.path.basename(src))

                if os.path.islink(src):
                    target = os.readlink(src)
                    if os.path.islink(dst) or os.path.isfile(dst):
                        path_remove(dst)

                    os.symlink(target, dst)
                else:
                    _copyfile(src, dst)

                _copystat(src, dst)
                success = True
        elif os.path.exists(src):
            if src == dst:
                errmsg = "'{!s}' and '{!s}' " \
                         "are the same folder".format(src, dst)
            elif _copy_tree(src, dst, quiet=quiet, critical=critical):
                success = True
        else:
            errmsg = 'source does not exist: {}'.format(src)
    except (IOError, ShutilError) as e:
        errmsg = str(e)

    if not quiet and errmsg:
        err('unable to copy source contents to target location\n'
            '    {}', errmsg)

    if not success and critical:
        sys.exit(-1)
    return success


def path_copy_into(src, dst, quiet=False, critical=True):
    """
    copy a file or directory into a target directory

    This call will attempt to copy a provided file or directory, defined by
    ``src`` into a destination directory defined by ``dst``. If a target
    directory does not exist, it will be automatically created. In the event
    that a file or directory could not be copied, an error message will be
    output to standard error (unless ``quiet`` is set to ``True``). If
    ``critical`` is set to ``True`` and the specified file/directory could
    not be copied for any reason, this call will issue a system exit
    (``SystemExit``).

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

    Args:
        src: the source directory or file
        dst: the destination directory
        quiet (optional): whether or not to suppress output
        critical (optional): whether or not to stop execution on failure

    Returns:
        ``True`` if the copy has completed with no error; ``False`` if the copy
        has failed

    Raises:
        SystemExit: if the copy operation fails with ``critical=True``
    """

    return path_copy(src, dst, quiet=quiet, critical=critical, dst_dir=True)


def _copy_tree(src_folder, dst_folder, quiet=False, critical=True):
    if not ensure_dir_exists(dst_folder, quiet=quiet, critical=critical):
        return False

    for entry in os.listdir(src_folder):
        src = os.path.join(src_folder, entry)
        dst = os.path.join(dst_folder, entry)

        if os.path.islink(src):
            target = os.readlink(src)
            if os.path.islink(dst) or os.path.isfile(dst):
                path_remove(dst)

            os.symlink(target, dst)
            _copystat(src, dst)
        elif os.path.isdir(src):
            _copy_tree(src, dst, quiet=quiet, critical=critical)
        else:
            _copyfile(src, dst)
            _copystat(src, dst)

    _copystat(src_folder, dst_folder)

    return True
