# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.critical import raise_for_critical
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.io_remove import path_remove
from releng_tool.util.log import err
from shutil import Error as ShutilError
from shutil import copyfile
from shutil import copystat
import os


def path_copy(src, dst, quiet=False, critical=True, dst_dir=None, nested=False):
    """
    copy a file or directory into a target file or directory

    .. versionchanged:: 0.12 Add support for ``dst_dir``.
    .. versionchanged:: 1.4 Add support for ``nested``.

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

    try:
        if os.path.isdir(src):
            if src == dst:
                errmsg = "'{!s}' and '{!s}' " \
                         "are the same folder".format(src, dst)
            elif nested:
                new_dst = os.path.join(dst, os.path.basename(src))
                if _copy_tree(src, new_dst, quiet=quiet, critical=critical):
                    success = True
            elif _copy_tree(src, dst, quiet=quiet, critical=critical):
                success = True
        elif os.path.isfile(src) or os.path.islink(src):
            attempt_copy = True

            if dst_dir:
                base_dir = dst
            else:
                base_dir = os.path.dirname(dst)

            if base_dir and not os.path.isdir(base_dir):
                attempt_copy = mkdir(base_dir, quiet=quiet)
            else:
                attempt_copy = True

            if attempt_copy:
                if os.path.isdir(dst):
                    dst = os.path.join(dst, os.path.basename(src))

                if os.path.islink(src):
                    target = os.readlink(src)
                    if os.path.islink(dst) or os.path.isfile(dst):
                        path_remove(dst, quiet=quiet)

                    os.symlink(target, dst)
                else:
                    copyfile(src, dst, follow_symlinks=False)

                # copy file statistics if both source and destination exist,
                # and if the do exist, they are not the same file (py3.5)
                if os.path.isfile(src) and os.path.isfile(dst) and (
                        not os.path.islink(src) or not os.path.islink(dst)
                        or  os.readlink(src) != os.readlink(dst)):
                    _copy_stat_compat(src, dst)

                success = True
        else:
            errmsg = f'source does not exist: {src}'
    except (OSError, ShutilError) as e:
        errmsg = str(e)

    if not quiet and errmsg:
        err('unable to copy source contents to target location\n'
            '    {}', errmsg)

    raise_for_critical(not success and critical)
    return success


def path_copy_into(src, dst, quiet=False, critical=True, nested=False):
    """
    copy a file or directory into a target directory

    .. versionadded:: 0.13
    .. versionchanged:: 1.4 Add support for ``nested``.

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


def _copy_stat_compat(src, dst):
    # do not attempt to copy if either component does not exist
    # (e.g. broken symlink)
    if not os.path.exists(src) or not os.path.exists(dst):
        return

    # do not attempt to copy if this is a symlink to itself (py3.5)
    if os.path.realpath(src) == os.path.realpath(dst):
        return

    copystat(src, dst, follow_symlinks=False)


def _copy_tree(src_folder, dst_folder, quiet=False, critical=True):
    if not mkdir(dst_folder, quiet=quiet, critical=critical):
        return False

    for entry in os.listdir(src_folder):
        src = os.path.join(src_folder, entry)
        dst = os.path.join(dst_folder, entry)

        if os.path.islink(src):
            target = os.readlink(src)
            if os.path.islink(dst) or os.path.isfile(dst):
                path_remove(dst, quiet=quiet)

            os.symlink(target, dst)
            if os.path.isfile(target) and os.path.isfile(dst):
                _copy_stat_compat(src, dst)
        elif os.path.isdir(src):
            _copy_tree(src, dst, quiet=quiet, critical=critical)
        else:
            copyfile(src, dst, follow_symlinks=False)
            _copy_stat_compat(src, dst)

    _copy_stat_compat(src_folder, dst_folder)

    return True
