# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from releng_tool.util.file_flags import FileFlag
from releng_tool.util.file_flags import check_file_flag
from releng_tool.util.file_flags import process_file_flag
from releng_tool.util.io_mkdir import mkdir
from releng_tool.util.io_path import path_input
from releng_tool.util.log import debug
from releng_tool.util.log import warn
import inspect
import os
import re


def step(key: str, *, force: bool | None = None,
        dir_: str | bytes | os.PathLike | None = None):
    """
    invoke the scoped implementation once for a step/build

    .. versionadded:: 3.1

    The following is a helper generator that aims to act like a context manager
    for invoking a step of commands once across re-invokes. This may
    be useful for scripts which contain a large number of actions. A step
    operation accepts a name value which would typically be unique for a
    given package. Consider the following example when used in the context
    of a build script helper:

    .. code-block:: python

        for _ in releng_step('first-step'):
            # invoked only once on success

        for _ in releng_step('second-step'):
            # invoked only once on success

        for _ in releng_step('third-step'):
            # invoked only once on success

    When invoked for the first time, calls inside the for-loop scope will
    be executed as normal. Once done, the step will persist a file flag in
    the active context's package output directory (or the path defined by
    ``dir_``). In the event that the build script is re-invoked (e.g. continuing
    from a stopped/canceled state), if the step was previously completed, the
    scope will be stepped over.

    The ``force`` argument can be set depending on the stage, if desired. For
    example, when running in a build script, utilizing ``RELENG_REBUILD`` may
    be ideal:

    .. code-block:: python

        for _ in releng_step('subbuild', force=RELENG_REBUILD):
            # invoked only once on success

    Likewise with ``RELENG_RECONFIGURE`` in configuration scripts:

    .. code-block:: python

        for _ in releng_step('cfg-stage-1', force=RELENG_RECONFIGURE):
            # invoked only once on success

    If a directory cannot be detected for use of the file flag, a
    ``FailedToPrepareStepError`` exception will be thrown.

    Args:
        key: name for the file flag
        force (optional): force run the step
        dir_ (optional): the directory to store the file flag

    Raises:
        FailedToPrepareStepError: the step context could not be prepared
    """

    simple_key = re.sub(r'[^\w.-]', '-', key).strip('.')
    debug(f'running step: {simple_key}')

    # try to find the caller's globals as we will check it for releng-tool
    # defines typically injected in stage script
    current_frame = inspect.currentframe()
    if current_frame and current_frame.f_back:
        caller_globals = current_frame.f_back.f_globals
    else:
        caller_globals = globals()

    # if a directory is not explicitly provided, we rely on PKG_BUILD_OUTPUT_DIR
    # as our default path for package file flag
    if dir_ is None:
        dir_ = caller_globals.get('PKG_BUILD_OUTPUT_DIR')

        if dir_ is None:
            raise FailedToPrepareStepError('PKG_BUILD_OUTPUT_DIR not defined')

    target_dir = path_input(dir_)
    if not mkdir(target_dir):
        raise FailedToPrepareStepError(f'could not prepare {target_dir}')

    file_flag_name = f'.releng-tool-step-{simple_key}'
    file_flag = target_dir / file_flag_name

    # check if this step has already been run; if so, we stop (with exceptions)
    if not force:
        debug(f'checking for step file flag: {file_flag}')
        if check_file_flag(file_flag) == FileFlag.EXISTS:
            debug('skipping step as already ran before')
            return
    else:
        debug('forced step')

    # invoke the step scope
    debug(f'about to invoke step: {simple_key}')
    yield

    # flag at this step has been completed
    debug(f'writing step file flag: {file_flag}')
    if process_file_flag(file_flag, flag=True) != FileFlag.CONFIGURED:
        warn(f'failed to setup step file flag: {file_flag}')


class FailedToPrepareStepError(Exception):
    """
    raised when a step context could not be prepared
    """
