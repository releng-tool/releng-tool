#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from .log import *
from contextlib import contextmanager
from distutils.dir_util import DistutilsFileError
from distutils.dir_util import copy_tree
from shutil import copy2
from shutil import rmtree
import errno
import os
import subprocess
import sys
import tempfile

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

class FailedToPrepareBaseDirectoryError(Exception):
    """
    raised when a base directory could not be prepared
    """
    pass

class FailedToPrepareWorkingDirectoryError(Exception):
    """
    raised when a working directory could not be prepared
    """
    pass

def ensureDirectoryExists(dir):
    """
    ensure the provided directory exists

    Attempts to create the provided directory. If the directory already exists,
    this method has no effect. If the directory does not exist and could not be
    created, this method will return ``False``.

    Args:
        dir: the directory

    Returns:
        ``True`` if the directory exists; ``False`` if the directory could not
        be created
    """
    try:
        os.makedirs(dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            err('unable to create directory: ' + dir)
            err('    {}'.format(e))
            return False
    return True

@contextmanager
def generateTempDir(dir=None):
    """
    generate a context-supported temporary directory

    Creates a temporary directory in the provided directory ``dir`` (or system
    default, is not provided). This is a context-supported call and will
    automatically remove the directory when completed. If the provided
    directory does not exist, it will created. If the directory could not be
    created, an ``FailedToPrepareBaseDirectoryError`` exception will be thrown.

    Args:
        dir (optional): the directory to create the temporary directory

    Raises:
        FailedToPrepareBaseDirectoryError: the base directory does not exist and
            could not be created
    """
    if dir and not ensureDirectoryExists(dir):
        raise FailedToPrepareBaseDirectoryError(dir)

    dir = tempfile.mkdtemp(prefix='.releng-tmp-', dir=dir)
    try:
        yield dir
    finally:
        try:
            rmtree(dir)
        except OSError as e:
            if e.errno != errno.ENOENT:
                warn('unable to cleanup temporary directory: ' + dir)
                warn('    {}'.format(e))

@contextmanager
def interimWorkingDirectory(dir):
    """
    move into a context-supported working directory

    Moves the current context into the provided working directory ``dir``. When
    returned, the original working directory will be restored. If the provided
    directory does not exist, it will created. If the directory could not be
    created, an ``FailedToPrepareWorkingDirectoryError`` exception will be
    thrown.

    Args:
        dir: the target working directory

    Raises:
        FailedToPrepareWorkingDirectoryError: the working directory does not
            exist and could not be created
    """
    owd = os.getcwd()

    if not ensureDirectoryExists(dir):
        raise FailedToPrepareWorkingDirectoryError(dir)

    os.chdir(dir)
    try:
        yield dir
    finally:
        try:
            os.chdir(owd)
        except IOError:
            warn('unable to restore original working directory: ' + owd)

def interpretStemExtension(basename):
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
        return (None, None)

    if '.' not in basename:
        return (basename, None)

    stem, ext = basename.split('.', 1)
    while '.' in ext:
        if ext.lower() in MULTIPART_EXTENSIONS:
            break

        part, ext = ext.split('.', 1)
        stem = '{}.{}'.format(stem, part)

    return (stem, ext)

def pathCopy(src, dst, quiet=False, critical=True):
    """
    copy the file or directory src into the file or directory dst

    Runs the command described by ``args`` until completion.

    Args:
        src: the source directory or file
        dst: the destination directory or file\* (\*if ``src`` is a file)
        quiet (optional): whether or not to suppress output
        critical (optional): whether or not to stop execution on failure

    Returns:
        ``True`` if the copy has completed with no error; ``False`` if the copy
        has failed
    """
    success = False

    try:
        if os.path.isfile(src):
            if not os.path.isdir(dst):
                parent_dir = os.path.dirname(dst)
                ensureDirectoryExists(parent_dir)
            copy2(src, dst)
        else:
            copy_tree(src, dst, update=True)
        success = True
    except (DistutilsFileError, IOError) as e:
        if not quiet:
            err('unable to copy source contents to target location')
            err('    {}'.format(e))

    if not success and critical:
        sys.exit(-1)
    return success

def pathExists(path, *args):
    """
    return whether or not the path exists

    Returns ``True`` if the path exists; ``False`` otherwise.

    Args:
        path: the path
        *args: additional path parts

    Returns:
        ``True`` if the path exists; ``False`` otherwise
    """
    return os.path.exists(os.path.join(path, *args))

def pathRemove(path):
    """
    quietly remove the provided path

    Attempts to remove the provided path if it exists. If the provided path does
    not exist, this method does nothing.

    Args:
        path: the path to remove

    Returns:
        ``True`` if the path was removed or does not exist; ``False`` if the
        path could not be removed from the system
    """
    try:
        if os.path.isdir(path):
            rmtree(path)
        else:
            os.remove(path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            err('unable to remove path: ' + path)
            err('    {}'.format(e))
            return False

    return True

def prependShebangInterpreter(args):
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

def execute(args, cwd=None, env=None, env_update=None, quiet=False,
        critical=True, poll=False, capture=None):
    """
    execute the provided command/arguments

    Runs the command described by ``args`` until completion.

    Args:
        args: the list of arguments to execute
        cwd (optional): working directory to use
        env (optional): environment variables to use for the process
        env_update (optional): environment variables to append for the process
        quiet (optional): whether or not to suppress output
        critical (optional): whether or not to stop execution on failure
        poll (optional): force polling stdin/stdout for output data
        capture (optional): list to capture output into

    Returns:
        ``True`` if the execution has completed with no error; ``False`` if the
        execution has failed
    """

    # append provided environment updates (if any) to the provided or existing
    # environment dictionary
    final_env = None
    if env:
        final_env = dict(env)
    if env_update:
        final_env = os.environ.copy()
        final_env.update(env_update)

    success = False
    if args:
        # attempt to always invoke using a script's interpreter (if any) to
        # help deal with long-path calls
        if sys.platform != 'win32':
            args = prependShebangInterpreter(args)

        verbose('invoking: ' + str(args).replace('{','{{').replace('}','}}'))
        try:
            proc = subprocess.Popen(args, bufsize=1,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                cwd=cwd, env=final_env)

            # check if this execution should poll (for carriage returns and new
            # lines)
            #
            # Note if quiet mode is enabled, do not attempt to poll since none
            # of the output will be printed anyways.
            if poll and not quiet:
                debug('invoked with polling option')
                line = bytearray()
                while True:
                    c = proc.stdout.read(1)
                    if not c and proc.poll() != None:
                        break
                    line += c
                    if c == b'\r' or c == b'\n':
                        decoded_line = line.decode('utf_8')
                        if c == b'\n' and capture is not None:
                            capture.append(decoded_line)
                        elif not capture is not None:
                            sys.stdout.write(decoded_line)
                            sys.stdout.flush()
                        del line[:]
            else:
                for line in iter(proc.stdout.readline, b''):
                    if capture is not None or not quiet:
                        decoded_line = line.decode('utf_8').rstrip()
                        if capture is not None:
                            capture.append(decoded_line)
                        elif not quiet:
                            print(decoded_line)
                            sys.stdout.flush()
            proc.communicate()

            success = (proc.returncode == 0)
        except OSError as e:
            if not quiet:
                err('unable to execute command: ' +
                    str(args).replace('{','{{').replace('}','}}'))
                err('    {}'.format(e))

    if not success:
        debug('failed cmd: ' + str(args).replace('{','{{').replace('}','}}'))
        if critical:
            sys.exit(-1)
    return success
