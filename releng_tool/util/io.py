# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from __future__ import annotations
from releng_tool.support import releng_script_envs
from releng_tool.util.critical import raise_for_critical
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import is_debug
from releng_tool.util.log import is_verbose
from releng_tool.util.log import verbose
from releng_tool.util.string import expand as expand_util
from runpy import run_path
from shlex import quote
import os
import subprocess
import sys
import traceback


#: list of (lower-cased) extension with "multiple parts"
#: (see ``interpretStemExtension``)
MULTIPART_EXTENSIONS = [
    'tar.bz',
    'tar.bz2',
    'tar.gz',
    'tar.lzma',
    'tar.xz',
    'tar.z',
]


def execute(args, cwd=None, env=None, env_update=None, quiet=None,
        critical=True, poll=False, capture=None, expand=True,
        args_str=False, ignore_stderr=False):
    """
    execute the provided command/arguments

    .. versionchanged:: 1.13 Add support for ``expand``.
    .. versionchanged:: 1.14 Add support for ``args_str``.
    .. versionchanged:: 2.0 Add support for ``ignore_stderr``.

    Runs the command described by ``args`` until completion. A caller can adjust
    the working directory of the executed command by explicitly setting the
    directory in ``cwd``. The execution request will return ``True`` on a
    successful execution; ``False`` if an issue has been detected (e.g. bad
    options or called process returns a non-zero value). In the event that the
    execution fails, an error message will be output to standard error unless
    ``quiet`` is set to ``True``.

    The environment variables used on execution can be manipulated in two ways.
    First, the environment can be explicitly controlled by applying a new
    environment content using the ``env`` dictionary. Key of the dictionary will
    be used as environment variable names, whereas the respective values will be
    the respective environment variable's value. If ``env`` is not provided, the
    existing environment of the executing context will be used. Second, a caller
    can instead update the existing environment by using the ``env_update``
    option. Like ``env``, the key-value pairs match to respective environment
    key-value pairs. The difference with this option is that the call will use
    the original environment values and update select values which match in the
    updated environment request. When ``env`` and ``env_update`` are both
    provided, ``env_update`` will be updated the options based off of ``env``
    instead of the original environment of the caller.

    If ``critical`` is set to ``True`` and the execution fails for any reason,
    this call will issue a system exit (``SystemExit``). By default, the
    critical flag is enabled (i.e. ``critical=True``).

    In special cases, an executing process may not provide carriage returns/new
    lines to simple output processing. This can lead the output of a process to
    be undesirably buffered. To workaround this issue, the execution call can
    instead poll for output results by using the ``poll`` option with a value
    of ``True``. By default, polling is disabled with a value of ``False``.

    A caller may wish to capture the provided output from a process for
    examination. If a list is provided in the call argument ``capture``, the
    list will be populated with the output provided from an invoked process.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        releng_execute(['echo', '$TEST'], env={'TEST': 'this is a test'})

    Args:
        args: the list of arguments to execute
        cwd (optional): working directory to use
        env (optional): environment variables to use for the process
        env_update (optional): environment variables to append for the process
        quiet (optional): whether or not to suppress output (defaults to
            ``False``)
        critical (optional): whether or not to stop execution on failure
            (defaults to ``True``)
        poll (optional): force polling stdin/stdout for output data (defaults to
            ``False``)
        capture (optional): list to capture output into
        expand (optional): perform variable expansion on arguments
        args_str (optional): invoke arguments as a single string
        ignore_stderr (optional): ignore any stderr output

    Returns:
        ``True`` if the execution has completed with no error; ``False`` if the
        execution has failed

    Raises:
        SystemExit: if the execution operation fails with ``critical=True``
    """

    rv = _execute(
        args,
        capture=capture,
        critical=critical,
        cwd=cwd,
        env=env,
        env_update=env_update,
        expand=expand,
        poll=poll,
        quiet=quiet,
        args_str=args_str,
        ignore_stderr=ignore_stderr,
    )
    return rv == 0


def execute_rv(command, *args, **kwargs):
    """
    execute the provided command/arguments

    .. versionadded:: 0.8
    .. versionchanged:: 1.13 Add support for ``expand``.
    .. versionchanged:: 1.14 Add support for ``args_str``.
    .. versionchanged:: 2.0 Add support for ``ignore_stderr``.

    Runs the command ``command`` with provided ``args`` until completion. A
    caller can adjust the working directory of the executed command by
    explicitly setting the directory in ``cwd``. The execution request will
    return the command's return code as well as any captured output.

    The environment variables used on execution can be manipulated in two ways.
    First, the environment can be explicitly controlled by applying a new
    environment content using the ``env`` dictionary. Key of the dictionary will
    be used as environment variable names, whereas the respective values will be
    the respective environment variable's value. If ``env`` is not provided, the
    existing environment of the executing context will be used. Second, a caller
    can instead update the existing environment by using the ``env_update``
    option. Like ``env``, the key-value pairs match to respective environment
    key-value pairs. The difference with this option is that the call will use
    the original environment values and update select values which match in the
    updated environment request. When ``env`` and ``env_update`` are both
    provided, ``env_update`` will be updated the options based off of ``env``
    instead of the original environment of the caller.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        rv, out = releng_execute_rv('echo', '$TEST', env={'TEST': 'env-test'})

    Args:
        command: the command to invoke
        *args (optional): arguments to add to the command
        **cwd: working directory to use
        **env: environment variables to use for the process
        **env_update: environment variables to append for the process
        **expand: perform variable expansion on arguments
        **args_str: invoke arguments as a single string
        **ignore_stderr: ignore any stderr output

    Returns:
        the return code and output of the execution request
    """

    out = []
    rv = _execute(
        [command, *list(args)],
        capture=out,
        critical=False,
        cwd=kwargs.get('cwd'),
        env=kwargs.get('env'),
        env_update=kwargs.get('env_update'),
        expand=kwargs.get('expand'),
        args_str=kwargs.get('args_str'),
        ignore_stderr=kwargs.get('ignore_stderr'),
        quiet=True,
    )
    return rv, '\n'.join(out)


def _execute(args, cwd=None, env=None, env_update=None, quiet=None,
        critical=True, poll=False, capture=None, expand=True,
        args_str=False, ignore_stderr=False):
    """
    execute the provided command/arguments

    Runs the command described by ``args`` until completion. A caller can adjust
    the working directory of the executed command by explicitly setting the
    directory in ``cwd``. The execution request will return the command's return
    code as well as any captured output.

    The environment variables used on execution can be manipulated in two ways.
    First, the environment can be explicitly controlled by applying a new
    environment content using the ``env`` dictionary. Key of the dictionary will
    be used as environment variable names, whereas the respective values will be
    the respective environment variable's value. If ``env`` is not provided, the
    existing environment of the executing context will be used. Second, a caller
    can instead update the existing environment by using the ``env_update``
    option. Like ``env``, the key-value pairs match to respective environment
    key-value pairs. The difference with this option is that the call will use
    the original environment values and update select values which match in the
    updated environment request. When ``env`` and ``env_update`` are both
    provided, ``env_update`` will be updated the options based off of ``env``
    instead of the original environment of the caller.

    If ``critical`` is set to ``True`` and the execution fails for any reason,
    this call will issue a system exit (``SystemExit``). By default, the
    critical flag is enabled (i.e. ``critical=True``).

    In special cases, an executing process may not provide carriage returns/new
    lines to simple output processing. This can lead the output of a process to
    be undesirably buffered. To workaround this issue, the execution call can
    instead poll for output results by using the ``poll`` option with a value
    of ``True``. By default, polling is disabled with a value of ``False``.

    A caller may wish to capture the provided output from a process for
    examination. If a list is provided in the call argument ``capture``, the
    list will be populated with the output provided from an invoked process.

    Args:
        args: the list of arguments to execute
        cwd (optional): working directory to use
        env (optional): environment variables to use for the process
        env_update (optional): environment variables to append for the process
        quiet (optional): whether or not to suppress output (defaults to
            ``False``)
        critical (optional): whether or not to stop execution on failure
            (defaults to ``True``)
        poll (optional): force polling stdin/stdout for output data (defaults to
            ``False``)
        capture (optional): list to capture output into
        expand (optional): perform variable expansion on arguments
        args_str (optional): invoke arguments as a single string
        ignore_stderr (optional): ignore any stderr output

    Returns:
        the return code of the execution request

    Raises:
        SystemExit: if the execution operation fails with ``critical=True``
    """

    # flexbile execute request
    if isinstance(args, str):
        args = [args]

    # append provided environment updates (if any) to the provided or existing
    # environment dictionary
    final_env = None
    if env:
        final_env = dict(env)
    if env_update:
        if not final_env:
            final_env = os.environ.copy()
        final_env.update(env_update)

    # if quiet is undefined, default its state based on whether or not the
    # caller wishes to capture output to a list
    if quiet is None:
        quiet = capture is not None

    cmd_str = None
    rv = 1
    if args:
        # force any `None` arguments to empty strings, as a subprocess request
        # will not accept it; ideally, a call should not be passing a `None`
        # entry, but providing flexibility when it has been done
        args = [str(arg) if arg is not None else '' for arg in args]

        # expand any variables
        if expand:
            args = expand_util(args, kv=final_env)

        # attempt to always invoke using a script's interpreter (if any) to
        # help deal with long-path calls
        if sys.platform != 'win32':
            args = prepend_shebang_interpreter(args)

        if is_verbose():
            debug('(wd) {}', cwd if cwd else os.getcwd())
            cmd_str = cmd_args_to_str(args)
            verbose('invoking: ' + cmd_str)
            AT_LEAST_THREE_ARGS = 3
            if len(args) >= AT_LEAST_THREE_ARGS and is_debug('execute-args'):
                arg_str = '\n ' + args[0]
                for arg in args[1:]:
                    arg_str += f'\n  {arg}'
                debug(arg_str)
            if final_env and is_debug('execute-env'):
                env_str = '(env)'
                for k, v in sorted(final_env.items()):
                    env_str += f'\n  {k}: {v}'
                debug(env_str)

        try:
            # check if this execution should poll (for carriage returns and new
            # lines); note if quiet mode is enabled, do not attempt to poll
            # since none of the output will be printed anyways.
            if poll and not quiet:
                debug('will poll process for output')
                bufsize = 0
                universal_newlines = False
            else:
                bufsize = 1
                universal_newlines = True

            run_args = ' '.join(args) if args_str else args

            # allow a caller to ignore the stderr output, if they are only
            # interested in the stdout stream
            stderr = subprocess.DEVNULL if ignore_stderr else subprocess.STDOUT

            proc = subprocess.Popen(
                run_args,
                bufsize=bufsize,
                cwd=cwd,
                env=final_env,
                stderr=stderr,
                stdout=subprocess.PIPE,
                universal_newlines=universal_newlines,
            )

            if bufsize == 0:
                line = bytearray()
                while True:
                    c = proc.stdout.read(1)
                    if not c and proc.poll() is not None:
                        break
                    line += c
                    if c in (b'\r', b'\n'):
                        decoded_line = line.decode('utf_8')
                        if c == b'\n' and capture is not None:
                            capture.append(decoded_line)
                        if not quiet:
                            sys.stdout.write(decoded_line)
                            sys.stdout.flush()
                        del line[:]
            else:
                for line in iter(proc.stdout.readline, ''):
                    if capture is not None or not quiet:
                        line = line.rstrip()
                        if capture is not None:
                            capture.append(line)
                        if not quiet:
                            print(line)
                            sys.stdout.flush()
            proc.communicate()

            rv = proc.returncode
        except OSError as e:
            if not quiet:
                if not cmd_str:
                    cmd_str = cmd_args_to_str(args)

                err('unable to execute command: {}\n'
                    '    {}', cmd_str, e)

    if rv != 0:
        if critical:
            cmd_str = cmd_args_to_str(args) if args else '<empty>'
            err('failed to issue command ({}): {}', rv, cmd_str)

            # trigger a hard stop
            raise_for_critical()
        elif args:
            debug('failed to issue last command ({})', rv)
        else:
            debug('failed to issue an empty command ({})', rv)

    return rv


def cmd_args_to_str(args):
    """
    convert an argument list to a platform escaped string

    This call attempts to convert a list of arguments (to be passed into a
    `subprocess.Popen` request) into a string value. This is primarily to help
    support logging commands for a user in error/verbose scenarios to minimize
    the effort needed to manually re-invoke a command in a shell.

    Args:
        args: the argument list

    Returns:
        the argument(s) represented as a single string
    """
    if sys.platform == 'win32':
        cmd_str = subprocess.list2cmdline(args)
    else:
        cmd_str = ''
        for arg in args:
            if isinstance(arg, bytes):
                arg = arg.decode('utf_8')
            cmd_str += ' ' + quote(arg)
        cmd_str = cmd_str.strip()

    return cmd_str


def interpret_stem_extension(basename):
    """
    interpret the stem and extension from a provided basename

    Attempts to return the stem value and the an assumed "complete" extension
    value from a provided ``basename``. While a file extension is more
    "commonly" the last dot part of a path's base name, this does not apply to
    resources where they may have multiple extension parts (e.g. my-file.tar.gz)
    or have no extension (my-file).

    Examples for some basenames are as follows:

     - my-file.txt -> (my-file, txt)
     - my-file.tar.gz -> (my-file, tar.gz)
     - my.file.name.dat -> (my.file.name, dat)
     - my-file -> (my-file, None)
     - None -> (None, None)

    Args:
        basename: the basename to interpret

    Returns:
        a 2-tuple (stem, extension)
    """
    if not basename:
        return None, None

    if '.' not in basename:
        return basename, None

    stem, ext = basename.split('.', 1)
    while '.' in ext:
        if ext.lower() in MULTIPART_EXTENSIONS:
            break

        part, ext = ext.split('.', 1)
        stem = f'{stem}.{part}'

    return stem, ext


def prepare_arguments(args):
    """
    prepares arguments from a dictionary

    With a provided dictionary of arguments in key-value pairs and builds them
    into an argument list. For example, if a dictionary contains a key ``foo``
    with a value ``bar``, the returns arguments will be a list with the values
    ``['foo', 'bar']``. If a key contains a value of ``None``, the key will be
    ignored and will not be part of the final argument list.

    Args:
        args: the arguments to process

    Returns:
        list of arguments
    """
    final = []

    if args:
        for key, val in args.items():
            if val is None:
                continue

            final.append(key)
            if val:
                final.append(val)

    return final


def prepare_definitions(defs, prefix=None):
    """
    prepares definitions from a dictionary

    With a provided dictionary of definitions in key-value pairs and builds them
    into an definition list. For example, if a dictionary contains a key ``foo``
    with a value ``bar``, the returns definitions will be a list with the values
    ``['foo=bar']``. If a key contains a value of ``None``, the key will be
    ignored and will not be part of the final definition list. If a ``prefix``
    value is provided, each definition entry will be prefixed with the provided
    value.

    Args:
        defs: the arguments to process
        prefix (optional): prefix value to prefix each definition

    Returns:
        list of arguments
    """
    final = []

    if defs:
        for key, val in defs.items():
            if val is None:
                continue

            if prefix:
                key = prefix + key

            final.append(f'{key}={val}')

    return final


def prepend_shebang_interpreter(args):
    """
    prepend interpreter program (if any) to argument list

    When invoking an executable defines an interpreter beyond system limits,
    the system may be unable to handle the request. Instead of relying on the
    system to extract the interpreter directive from a script, extract the value
    and prepend the program (and possibly argument) to the returned argument
    list. In the event that no interpreter directive exists (or is unsupported),
    this method will return the same ``args`` value.

    Args:
        args: the argument list

    Returns:
        the final argument list
    """
    try:
        with open(args[0], 'rb') as f:
            if f.read(1) == b'#' and f.read(1) == b'!':
                MAXINTERP = 2048
                interp = f.readline(MAXINTERP + 1).rstrip()
                if len(interp) > MAXINTERP:
                    return args
                interp_args = interp.split(None, 1)[:2]
                return interp_args + [arg.encode() for arg in args]
    except (OSError, UnicodeError):
        pass
    return args


def run_script(script, globals_, subject=None, catch=True):
    """
    execute the provided script and provide the resulting globals module

    With the provided ``script`` file, execute the code and return the resulting
    global module based on the execution results. This invoke is just a wrapper
    call for ``run_path`` but with improved formatting for user feedback when
    invoked in various stages of a releng-tool run. The provided ``globals``
    will be passed into the ``run_path`` call.

    When an issue occurs invoking the provided script, an error messaged is
    output to standard error. This includes an error message (tailored, if
    provided, by a ``subject`` value), the captured exception message and a
    stack trace. This call will return ``None`` when an error is detected.

    Args:
        script: the script
        globals_: dictionary to pre-populate script's globals
        subject (optional): subject value to enhance a final error message
        catch (optional): whether or not to catch any exceptions

    Returns:
        resulting globals module; ``None`` if an execution error occurs
    """

    with releng_script_envs(script, globals_) as script_env:
        if not catch:
            result = run_path(script, init_globals=script_env)
        else:
            try:
                result = run_path(script, init_globals=script_env)
            except Exception as e:
                err('{}\n'
                    'error running {}{}script: {}\n'
                    '    {}',
                    traceback.format_exc(),
                    subject, subject and ' ', script,
                    e)
                return None

    return result
