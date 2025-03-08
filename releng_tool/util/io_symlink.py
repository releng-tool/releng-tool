# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from pathlib import Path
from releng_tool.util.critical import raise_for_critical
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.io_remove import path_remove
from releng_tool.util.log import err
import os


def symlink(target: str | bytes | os.PathLike,
        link_path: str | bytes | os.PathLike, *,
        quiet: bool = False, critical: bool = True,
        lpd: bool = False, relative: bool = True) -> bool:
    """
    create a symbolic link to a target at a provided link path

    .. note::

        this call may not work in Windows environments if the user invoking
        releng-tool does not have permission to create symbolic links.

    .. versionadded:: 1.4
    .. versionchanged:: 2.2 Accepts a str, bytes or os.PathLike.

    This call will attempt to create a symbolic link to a ``target`` path.
    A provided ``link_path`` determines where the symbolic link will be
    created. By default, the ``link_path`` identifies the symbolic link file
    to be created. However, if ``lpd`` is set to ``True``, it will consider
    the ``link_path`` as a directory to create a symbolic link in. For this
    case, the resulting symbolic link's filename will match the basename of
    the provided ``target`` path.

    If a symbolic link already exists at the provided link path, the
    symbolic link will be replaced with the new ``target``. If the resolved
    link path already exists and is not a symbolic link, this operation will
    not attempt to create a symbolic link.

    If the directory structure of a provided ``link_path`` does not exist,
    it will be automatically created. In the event that a symbolic link or
    directory could not be created, an error message will be output to
    standard error (unless ``quiet`` is set to ``True``). If ``critical`` is
    set to ``True`` and the symbolic link could not be created for any
    reason, this call will issue a system exit (``SystemExit``).

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        # my-link -> my-file
        releng_symlink('my-file', 'my-link')

        # my-link -> container/my-file
        releng_symlink('container/my-file', 'my-link')

        # some/folder/my-link -> ../../my-file
        releng_symlink('my-file', 'some/folder/my-link')

        # my-file -> container/my-file
        releng_symlink('my-file', 'container', ldp=True)

        # some-path/my-link -> <workdir>/folder/my-file
        releng_symlink('folder/my-file', 'some-path/my-link', relative=False)

    Args:
        target: the source path to link to
        link_path: the symbolic link path
        quiet (optional): whether to suppress output
        critical (optional): whether to stop execution on failure
        lpd (optional): hint that the link is a directory to create in
        relative (optional): whether to build a relative link

    Returns:
        ``True`` if the symbolic link has been created; ``False`` if the
        symbolic link could not be created

    Raises:
        SystemExit: if the symbolic link operation fails with ``critical=True``
    """

    def symlink_failure(msg):
        if not quiet:
            err('unable to create symbolic link\n'
                '    {}', msg)

        raise_for_critical(critical)
        return False

    link_path_entry = Path(os.fsdecode(link_path))
    target_entry = Path(os.fsdecode(target))

    if lpd:
        base_dir = link_path_entry
        dst_file = link_path_entry / target_entry.name
    else:
        base_dir = link_path_entry.parent
        dst_file = link_path_entry

    if dst_file.exists() and not dst_file.is_symlink():
        return symlink_failure(f'link path already exist: {dst_file}')

    if dst_file.is_symlink():
        if not path_remove(dst_file, quiet=quiet):
            return symlink_failure(f'failed to remove symlink: {dst_file}')
    elif base_dir and not mkdir(base_dir, quiet=quiet, critical=critical):
        return False

    if relative:
        final_target = Path(os.path.relpath(target_entry, start=base_dir))
    else:
        final_target = target_entry.absolute()

    try:
        dst_file.symlink_to(final_target)
    except OSError as e:
        return symlink_failure(str(e))

    return True
