# -*- coding: utf-8 -*-
# Copyright 2018-2021 releng-tool

from contextlib import contextmanager
from difflib import unified_diff
from io import open
from releng_tool.engine import RelengEngine
from releng_tool.opts import RelengEngineOptions
from releng_tool.util.io import generate_temp_dir
from releng_tool.util.io import path_copy
import os
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
def prepare_testenv(config=None, template=None, args=None):
    """
    prepare an engine-ready environment for a test

    This utility method is used to provide an `RelengEngine` instance ready for
    execution on an interim working directory.

    Args:
        config (optional): dictionary of options to mock for arguments
        template (optional): the folder holding a template project to copy into
                              the prepared working directory
        args (optional): additional arguments to add to the "forwarded options"

    Yields:
        the engine
    """

    class MockArgs(object):
        def __getattr__(self, name):
            return self.name if name in self.__dict__ else None

    if config is None:
        config = {}

    with generate_temp_dir() as work_dir:
        # force root directory to temporary directory; or configure all working
        # content based off the generated temporary directory
        if 'root_dir' not in config:
            config['root_dir'] = work_dir
        else:
            if 'cache_dir' not in config:
                config['cache_dir'] = os.path.join(work_dir, 'cache')
            if 'dl_dir' not in config:
                config['dl_dir'] = os.path.join(work_dir, 'dl')
            if 'out_dir' not in config:
                config['out_dir'] = os.path.join(work_dir, 'out')

        if template:
            test_base = os.path.dirname(os.path.realpath(__file__))
            templates_dir = os.path.join(test_base, 'templates')
            template_dir = os.path.join(templates_dir, template)
            path_copy(template_dir, work_dir)

        # build arguments instance
        test_args = MockArgs()
        for k, v in config.items():
            setattr(test_args, k, v)

        # prepare engine options and build an engine instance
        opts = RelengEngineOptions(args=test_args, forward_args=args)
        engine = RelengEngine(opts)

        yield engine

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

def run_testenv(config=None, template=None, args=None):
    """
    execute an engine instance with provide environment options for a test

    This utility method is used to invoke an `RelengEngine` instance which is
    prepared based off the provided configuration options and base template (if
    any) to copy.

    Args:
        config (optional): dictionary of options to mock for arguments
        template (optional): the folder holding a template project to copy into
                              the prepared working directory
        args (optional): additional arguments to add to the "forwarded options"

    Returns:
        the engine
    """

    with prepare_testenv(config=config, template=template, args=args) as engine:
        engine.run()
    return engine
