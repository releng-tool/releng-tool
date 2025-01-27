# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from contextlib import contextmanager
from difflib import unified_diff
from io import StringIO
from releng_tool.engine import RelengEngine
from releng_tool.opts import RelengEngineOptions
from releng_tool.util.io import generate_temp_dir
from releng_tool.util.io import interim_working_dir
from releng_tool.util.io_copy import path_copy
import os
import pprint
import sys
import unittest


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
        with open(first, encoding='utf_8') as file:
            content1 = strip_lines(file.readlines())
    except IOError:
        return 'failed to load first file: ' + first

    try:
        with open(second, encoding='utf_8') as file:
            content2 = strip_lines(file.readlines())
    except IOError:
        return 'failed to load second file: ' + second

    diff = unified_diff(content1, content2,
        fromfile=first, tofile=second, lineterm='\n')
    diff_content = ''.join(list(diff))
    if diff_content:
        return f'unexpected file differences\n{diff_content}'

    return None


def copy_template(template, target):
    """
    copy a unit testing template in to a provided target directory

    This utility method can be used to help copy the contents of a
    template (found under `tests/templates`) into a target directory.
    While this is typically managed through the various `*_testenv` calls,
    select tests may wish to manually prepare a working directory if running
    an engine multiple times.

    Args:
        template: the folder holding a template project to copy into the
                   prepared working directory
        target: the target directory
    """

    templates_dir = os.path.join(find_test_base(), 'templates')
    template_dir = os.path.join(templates_dir, template)
    if not path_copy(template_dir, target, critical=False):
        raise AssertionError('failed to setup template into directory')


@contextmanager
def mock_os_remove_permission_denied(f=None):
    """
    mock a system that emulates denying permissions to remove files/folders

    This context method provides a way to emulate failure cases when a request
    to remove a file or folder is made. This can be used to help sanity check
    implementation that attempts to cleanup paths and sanity check failure
    cases when a path cannot be cleaned up.

    Args:
        f (optional): the mock method to use; otherwise defaults to OSError
    """

    def _(path):  # noqa: ARG001
        raise OSError('Mocked permission denied')

    try:
        original_remove = os.remove
        original_rmdir = os.rmdir
        try:
            os.remove = f if f else _
            os.rmdir = f if f else _
            yield
        finally:
            os.remove = original_remove
            os.rmdir = original_rmdir
    finally:
        pass


@contextmanager
def new_test_wd():
    """
    prepare a new temporary working directory

    This utility method is used to automatically create a directory for
    testing. Once created, the working directory will be configured to
    ths directory. This method will ensure the container directory is emptied
    before returning.

    Returns:
        the container directory
    """

    with generate_temp_dir() as work_dir, interim_working_dir(work_dir):
        yield work_dir


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

    class MockArgs:
        def __getattr__(self, name):
            return self.name if name in self.__dict__ else None

    config = {} if config is None else dict(config)

    with generate_temp_dir() as work_dir, interim_working_dir(work_dir):
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
            copy_template(template, work_dir)

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
        the engine's return code
    """

    with prepare_testenv(config=config, template=template, args=args) as engine:
        return engine.run()


def find_test_base():
    """
    return the absolute path of the test base directory

    A utility call to return the absolute path of the "tests" directory for this
    implementation. This is to support interpreters (i.e. Python 2.7) which do
    not provide an absolute path via the `__file__` variable.

    Returns:
        the path
    """

    test_base = os.path.dirname(os.path.realpath(__file__))

    def templates_exist(test_base):
        return os.path.exists(os.path.join(test_base, 'templates'))

    if not templates_exist(test_base):
        test_base = os.path.dirname(os.path.abspath(sys.argv[0]))
        if not templates_exist(test_base):
            raise RuntimeError('unable to find test base directory')

    return test_base


class RelengToolTestSuite(unittest.TestSuite):
    def run(self, result, debug=False):
        """
        a releng-tool helper test suite

        Provides a `unittest.TestSuite` which will ensure stdout is flushed
        after the execution of tests. This is to help ensure all stdout content
        from the test is output to the stream before the unittest framework
        outputs a test result summary which may be output to stderr.

        See `unittest.TestSuite.run()` for more details.

        Args:
            result: the test result object to populate
            debug (optional): debug flag to ignore error collection

        Returns:
            the test result object
        """
        rv = unittest.TestSuite.run(self, result, debug)
        sys.stdout.flush()
        return rv


class RelengToolTestCase(unittest.TestCase):
    """
    a releng-tool unit test case

    Provides a `unittest.TestCase` implementation that releng-tool unit
    tests should inherit from. This test class provides the following
    capabilities:

    - Clears the running environment back to its original state after
       each test run. releng-tool events will populate the running environment
       for project scripts to use. Ensuring the environment is clean after
       each run prevents tests to conflicting with each other's state.
    """

    def run(self, result=None):
        """
        run the test

        Run the test, collecting the result into the TestResult object passed as
        result. See `unittest.TestCase.run()` for more details.

        Args:
            result (optional): the test result to populate
        """

        with self.env_wrap():
            super().run(result)

    def dumpenv(self):
        """
        dump the active environment to the standard output stream
        """

        print('-------------------------------')
        pprint.pprint(dict(os.environ))
        print('-------------------------------')

    @contextmanager
    def env_wrap(self):
        """
        wrap the context's environment

        This context method provides a way restrict environment changes to the
        context.
        """

        old_env = dict(os.environ)
        try:
            yield
        finally:
            os.environ.clear()
            os.environ.update(old_env)
