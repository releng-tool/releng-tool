# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from __future__ import unicode_literals
from contextlib import contextmanager
from releng_tool.support import releng_script_envs
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.log import is_verbose
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
from releng_tool.util.string import expand as expand_util
from runpy import run_path
from shutil import copyfileobj
import errno
import os
import stat
import subprocess
import sys
import tempfile
import traceback

try:
    from shlex import quote
except ImportError:
    from pipes import quote

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

# file extensions permitted for releng-tool scripts/definitions
RELENG_TOOL_EXTENSIONS = [
    '.releng',
    '.py',
]


class FailedToPrepareBaseDirectoryError(Exception):
    """
    raised when a base directory could not be prepared
    """


class FailedToPrepareWorkingDirectoryError(Exception):
    """
    raised when a working directory could not be prepared
    """


def cat(file, *args):
    """
    concatenate files and print on the standard output

    Attempts to read one or more files provided to this call. For each file, it
    will be read and printed out to the standard output.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        releng_cat('my-file')

    Args:
        file: the file
        *args (optional): additional files to include

    Returns:
        ``True`` if all the files exists and were printed to the standard
        output; ``False`` if one or more files could not be read
    """

    files = []
    files.append(file)
    files.extend(args)

    for f in files:
        if not os.path.isfile(f):
            return False

    try:
        for filename in files:
            with open(filename, 'r') as f:
                copyfileobj(f, sys.stdout)
    except OSError:
        return False
    else:
        return True


def ensure_dir_exists(dir_, *args, **kwargs):
    """
    ensure the provided directory exists

    Attempts to create the provided directory. If the directory already exists,
    this method has no effect. If the directory does not exist and could not be
    created, this method will return ``None``. Also, if an error has been
    detected, an error message will be output to standard error (unless
    ``quiet`` is set to ``True``).

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        if releng_mkdir('my-directory'):
            print('directory was created')
        else:
            print('directory was not created')

        target_dir = releng_mkdir(TARGET_DIR, 'sub-folder')
        if target_dir:
            # output] target directory: <target>/sub-folder
            print('target directory:', target_dir)
        else:
            print('directory was not created')

    Args:
        dir_: the directory
        *args (optional): additional components of the directory
        **quiet (optional): whether or not to suppress output (defaults
            to ``False``)
        **critical (optional): whether or not to stop execution on
            failure (defaults to ``False``)

    Returns:
        the directory that exists; ``None`` if the directory could not
        be created
    """
    quiet = kwargs.get('quiet')
    critical = kwargs.get('critical')

    final_dir = os.path.join(dir_, *args)
    try:
        os.makedirs(final_dir)
    except OSError as e:
        if e.errno != errno.EEXIST or not os.path.isdir(final_dir):
            if not quiet:
                err('unable to create directory: {}\n'
                    '    {}', final_dir, e)
            if critical:
                sys.exit(-1)
            return None
    return final_dir


def execute(args, cwd=None, env=None, env_update=None, quiet=None,
        critical=True, poll=False, capture=None, expand=True):
    """
    execute the provided command/arguments

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
    )
    return rv == 0


def execute_rv(command, *args, **kwargs):
    """
    execute the provided command/arguments

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

    Returns:
        the return code and output of the execution request
    """

    out = []
    rv = _execute(
        [command] + list(args),
        capture=out,
        critical=False,
        cwd=kwargs.get('cwd'),
        env=kwargs.get('env'),
        env_update=kwargs.get('env_update'),
        expand=kwargs.get('expand'),
        quiet=True,
    )
    return rv, '\n'.join(out)


def _execute(args, cwd=None, env=None, env_update=None, quiet=None,
        critical=True, poll=False, capture=None, expand=True):
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

    Returns:
        the return code of the execution request

    Raises:
        SystemExit: if the execution operation fails with ``critical=True``
    """

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
        args = [arg if arg is not None else '' for arg in args]

        # expand any variables
        if expand:
            args = expand_util(args, kv=final_env)

        # attempt to always invoke using a script's interpreter (if any) to
        # help deal with long-path calls
        if sys.platform != 'win32':
            args = prepend_shebang_interpreter(args)

        # python 2.7 can have trouble with unicode environment variables;
        # forcing all values to an ascii type
        if final_env and sys.version_info[0] < 3:  # noqa: PLR2004
            debug('detected python 2.7; sanity checking environment variables')
            for k, v in final_env.items():
                if isinstance(v, unicode):  # pylint: disable=E0602 # noqa: F821
                    final_env[k] = v.encode('ascii', 'replace')

        if is_verbose():
            debug('(wd) {}', cwd if cwd else os.getcwd())
            cmd_str = _cmd_args_to_str(args)
            verbose('invoking: ' + cmd_str)
            sys.stdout.flush()

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

            proc = subprocess.Popen(
                args,
                bufsize=bufsize,
                cwd=cwd,
                env=final_env,
                stderr=subprocess.STDOUT,
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
                    cmd_str = _cmd_args_to_str(args)

                err('unable to execute command: {}\n'
                    '    {}', cmd_str, e)

    if rv != 0:
        if critical:
            cmd_str = _cmd_args_to_str(args) if args else '<empty>'
            err('failed to issue command: ' + cmd_str)

            # trigger a hard stop
            sys.exit(-1)
        elif args:
            debug('failed to issue last command')
        else:
            debug('failed to issue an empty command')

    return rv


def _cmd_args_to_str(args):
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


@contextmanager
def generate_temp_dir(dir_=None):
    """
    generate a context-supported temporary directory

    Creates a temporary directory in the provided directory ``dir_`` (or system
    default, is not provided). This is a context-supported call and will
    automatically remove the directory when completed. If the provided
    directory does not exist, it will created. If the directory could not be
    created, an ``FailedToPrepareBaseDirectoryError`` exception will be thrown.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        with releng_tmpdir() as dir_:
            print(dir_)

    Args:
        dir_ (optional): the directory to create the temporary directory in

    Raises:
        FailedToPrepareBaseDirectoryError: the base directory does not exist and
            could not be created
    """
    if dir_ and not ensure_dir_exists(dir_):
        raise FailedToPrepareBaseDirectoryError(dir_)

    dir_ = tempfile.mkdtemp(prefix='.releng-tmp-', dir=dir_)
    try:
        yield dir_
    finally:
        try:
            path_remove(dir_)
        except OSError as e:
            if e.errno != errno.ENOENT:
                warn('unable to cleanup temporary directory: {}\n'
                     '    {}', dir_, e)


@contextmanager
def interim_working_dir(dir_):
    """
    move into a context-supported working directory

    Moves the current context into the provided working directory ``dir``. When
    returned, the original working directory will be restored. If the provided
    directory does not exist, it will created. If the directory could not be
    created, an ``FailedToPrepareWorkingDirectoryError`` exception will be
    thrown.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        with releng_wd('my-directory/'):
            # invoked in 'my-directory'

        # invoked in original working directory

    Args:
        dir_: the target working directory

    Raises:
        FailedToPrepareWorkingDirectoryError: the working directory does not
            exist and could not be created
    """
    owd = os.getcwd()

    if not ensure_dir_exists(dir_):
        raise FailedToPrepareWorkingDirectoryError(dir_)

    os.chdir(dir_)
    try:
        yield dir_
    finally:
        try:
            os.chdir(owd)
        except IOError:
            warn('unable to restore original working directory: ' + owd)


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
        stem = '{}.{}'.format(stem, part)

    return stem, ext


def ls(dir_):
    """
    list a directory's contents

    Attempts to read a directory for its contents and prints this information
    to the configured standard output stream.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        releng_ls('my-dir/')

    Args:
        dir_: the directory

    Returns:
        ``True`` if the directory could be read and its contents have been
        printed to the standard output; ``False`` if the directory could not
        be read
    """

    if not os.path.isdir(dir_):
        return False

    try:
        for entry in os.listdir(dir_):
            if os.path.isdir(os.path.join(dir_, entry)):
                print(entry + '/')
            else:
                print(entry)
    except OSError:
        return False
    else:
        return True


def opt_file(file):
    """
    return a file (and existence) to opt for based a given file path

    Various user-defined scripts by default do not have an extension. For
    example, a project's releng-tool script is defined by a file named `releng`;
    however, select users may wish to define a `releng.releng` or `releng.py`
    script instead. Consider, with the previous example, the file `releng` is
    the "standard" file and the `releng.releng` or `releng.py` script is the
    "alternative" file. This utility call will return the file path and the
    existence state of the returned file. If the standard file does not exist
    but the alternative file does, this call will return the alternative file.
    Priority is given to the standard file, so if neither file exists, this
    call will return the provided/standard file path.

    Args:
        file: the file to check for

    Returns:
        a 2-tuple (file, existence flag)
    """

    exists = os.path.isfile(file)
    if not exists:
        for ext in RELENG_TOOL_EXTENSIONS:
            flex_file = file + ext
            if os.path.isfile(flex_file):
                return flex_file, True

    return file, exists


def path_exists(path, *args):
    """
    return whether or not the path exists

    Allows a caller to verify the existence of a file on the file system. This
    call will return ``True`` if the path exists; ``False`` otherwise.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        if releng_exists('my-file'):
            print('the file exists')
        else:
            print('the file does not exist')

    Args:
        path: the path
        *args: additional path parts

    Returns:
        ``True`` if the path exists; ``False`` otherwise
    """
    return os.path.exists(os.path.join(path, *args))


def path_remove(path, quiet=False):
    """
    remove the provided path

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

    if not os.path.exists(path):
        return True

    try:
        if os.path.isdir(path) and not os.path.islink(path):
            _path_remove_dir(path)
        else:
            _path_remove_file(path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            if not quiet:
                err('unable to remove path: {}\n'
                    '    {}', path, e)
            return False

    return True


def _path_remove_dir(dir_):
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
        st = os.stat(dir_)
        if not (st.st_mode & stat.S_IRUSR) or not (st.st_mode & stat.S_IWUSR):
            os.chmod(dir_, st.st_mode | stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass

    # remove directory contents (if any)
    entries = os.listdir(dir_)
    for entry in entries:
        path = os.path.join(dir_, entry)
        if os.path.isdir(path) and not os.path.islink(path):
            _path_remove_dir(path)
        else:
            _path_remove_file(path)

    # remove directory
    os.rmdir(dir_)


def _path_remove_file(path):
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
        os.remove(path)
    except OSError as e:
        if e.errno != errno.EACCES:
            raise

        # if a file could not be removed, try adding write permissions
        # and retry removal
        try:
            st = os.stat(path)
            if (st.st_mode & stat.S_IWUSR):
                raise

            os.chmod(path, st.st_mode | stat.S_IWUSR)
            os.remove(path)
        except OSError:
            raise e


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

            final.append('{}={}'.format(key, val))

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
    except (IOError, UnicodeError):
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


def touch(file):
    """
    update a file's access/modifications times

    Attempts to update the access/modifications times on a file. If the file
    does not exist, it will be created. This utility call operates in the same
    fashion as the ``touch`` system command.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        if releng_touch('my-file'):
            print('file was created')
        else:
            print('file was not created')

    Args:
        file: the file

    Returns:
        ``True`` if the file was created/updated; ``False`` if the file could
        not be created/updated
    """
    try:
        parent_dir = os.path.dirname(file)
        if parent_dir and not os.path.isdir(parent_dir):
            ensure_dir_exists(parent_dir)

        with open(file, 'ab'):
            os.utime(file, None)
    except OSError:
        return False
    else:
        return True
