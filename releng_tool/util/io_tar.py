# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from pathlib import Path
from releng_tool.util.io_mkdir import mkdir
import gzip
import tarfile


def tar_cachefile(src: Path, target: Path, arcname: str,
        exclude: None | str | tuple[str] = None) -> bool:
    """
    generate a tar cache file

    With a provided source directory, this call will generate a tar archive
    in a consistent manner into a provided target path. This call will
    automatically ensure the target path's directory exists.

    Args:
        src: the source directory to cache
        target: the cache file to created
        arcname: name of the archive to use
        exclude (optional): extension(s) to exclude

    Returns:
        ``True`` if the cache file was created/updated; ``False`` if the cache
        file could not be created/updated
    """

    # ensure cache file's parent directory exists
    if not mkdir(Path(target).parent):
        return False

    def tar_filter(info):
        # if an exclude filter is set, check to see if this entry should
        # be ignored
        if exclude and info.name.endswith(exclude):
            return None

        # consistent tar experience
        info.mtime = 0
        info.uid = info.gid = 0
        info.uname = info.gname = 'root'

        return info

    # build archive
    with open(target, 'wb') as f:
        with gzip.GzipFile(fileobj=f, mode='wb', mtime=0,
                filename=f'{arcname}.tar') as gz:
            with tarfile.open(fileobj=gz, mode='w|') as tar:
                tar.add(src, arcname=arcname, filter=tar_filter)

    return True
