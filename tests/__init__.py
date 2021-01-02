# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from contextlib import contextmanager
from releng_tool.util.io import generate_temp_dir
from difflib import unified_diff
from io import open
import sys

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

def compare_contents(first, second):
    """
    compare the contents of two files

    This utility method is used to compare the contents of two files. Both
    file's contents will be read and checked for any differences. If both
    files have the same contents, `None` will be returned; otherwise a
    string containing a unified diff string will be returned.

    Args:
        first: the first file
        second: the second file

    Returns:
        `None` if matching; otherwise a unified diff string
    """
    def strip_lines(lines):
        return [line.strip() + '\n' for line in lines]

    try:
        with open(first, mode='r', encoding='utf_8') as file:
            content1 = strip_lines(file.readlines())
    except IOError:
        return 'failed to load first file: ' + first

    try:
        with open(second, mode='r', encoding='utf_8') as file:
            content2 = strip_lines(file.readlines())
    except IOError:
        return 'failed to load second file: ' + second

    diff = unified_diff(content1, content2,
        fromfile=first, tofile=second, lineterm='\n')
    diff_content = ''.join(list(diff))
    if diff_content:
        return 'unexpected file differences\n{}'.format(diff_content)

    return None

@contextmanager
def prepare_workdir():
    """
    prepare a working directory for a test

    This utility method is used to provide a test a directory to store
    output files. This method will ensure the container directory is emptied
    before returning.

    Returns:
        the container directory
    """

    with generate_temp_dir() as work_dir:
        yield work_dir

@contextmanager
def redirect_stdout(new_target=None):
    """
    temporarily redirect stdout to another instance

    This call will temporarily redirect stdout to the provided instance
    until the end of the context, where the previous `stdout` target will be
    restored.

    Args:
        new_target (optional): the instance to map stdout to
    """

    if not new_target:
        new_target = StringIO()

    _ = sys.stdout
    try:
        sys.stdout = new_target
        yield new_target
    finally:
        sys.stdout = _
