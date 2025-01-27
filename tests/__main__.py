# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.log import releng_log_configuration
from releng_tool.util.runner import detect_ci_runner_debug_mode
from releng_tool.util.win32 import enable_ansi as enable_ansi_win32
from tests import RelengToolTestSuite
import argparse
import fnmatch
import os
import sys
import unittest


#: default verbosity for unit tests
DEFAULT_VERBOSITY = 2

#: directory name for the standard unit tests
UNIT_TESTS_DIRNAME = 'unit-tests'


def main():
    """
    process main for unit tests

    This method will prepare the test suite, load listed test classes and
    perform a run.
    """
    loader = unittest.TestLoader()
    suite = RelengToolTestSuite()

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--relaxed', action='store_true')
    parser.add_argument('--test-dir', default=UNIT_TESTS_DIRNAME)
    parser.add_argument('--unbuffered', '-U', action='store_true')
    parser.add_argument('--verbose', '-V', action='count', default=0)

    args, args_extra = parser.parse_known_args()

    # configure logging for unit test output
    buffered = not args.unbuffered
    verbosity = 0
    if args.verbose:
        try:
            verbosity = int(args.verbose)
            # ignore first verbose level for unbuffered mode
            if buffered:
                verbosity -= 1
        except ValueError:
            pass

        buffered = False

    if args.debug or detect_ci_runner_debug_mode():
        buffered = False
        if not verbosity:
            verbosity = 1

    nocolor = False
    werror = False
    releng_log_configuration(args.debug, nocolor, verbosity, werror)

    # disable short descriptions
    unittest.TestCase.shortDescription = lambda x: None  # noqa: ARG005

    # support character sequences (for color output on win32 cmd)
    if sys.platform == 'win32':
        enable_ansi_win32()

    # discover unit tests
    test_base = os.path.dirname(os.path.realpath(__file__))
    tests_dir = os.path.join(test_base, args.test_dir)
    unit_tests = loader.discover(tests_dir)

    # check if a unit test name was provided
    target_test_name_pattern = None
    for arg in args_extra:
        if not arg.startswith('-'):
            target_test_name_pattern = arg
            break

    # register tests
    target_unit_tests = None
    if target_test_name_pattern:
        target_unit_tests, module_load_failure = find_tests(
            unit_tests, target_test_name_pattern)
        if target_unit_tests:
            print('running specific tests:')
            for test in target_unit_tests:
                print(f'    {test.id()}')
            sys.stdout.flush()
        else:
            print('ERROR: unable to find test with pattern: '
                 f'{target_test_name_pattern}')
            if not module_load_failure:
                sys.exit(0 if args.relaxed else 1)

    if target_unit_tests:
        suite.addTests(target_unit_tests)
    else:
        suite.addTests(unit_tests)

    # invoke test suite
    runner = unittest.TextTestRunner(buffer=buffered,
        verbosity=DEFAULT_VERBOSITY)
    return 0 if runner.run(suite).wasSuccessful() else 1


def find_tests(entity, pattern):
    """
    search for a unit tests with a matching wildcard pattern

    Looks for the first 'unittest.case.TestCase' instance where its identifier
    matches the provided wildcard pattern.

    Args:
        entity: the unit test entity to search for a pattern on
        pattern: the pattern

    Returns:
        a 2-tuple (list of tests, flag if a module error is detected)
    """
    found = []
    module_load_failure = False

    if isinstance(entity, unittest.case.TestCase):
        if fnmatch.fnmatch(entity.id(), f'*{pattern}*'):
            found.append(entity)
        elif 'ModuleImportFailure' in entity.id():
            module_load_failure = True
    elif isinstance(entity, unittest.TestSuite):
        for subentity in entity:
            tests, fail = find_tests(subentity, pattern)
            if tests:
                found.extend(tests)
            if fail:
                module_load_failure = True

    return found, module_load_failure


if __name__ == '__main__':
    sys.exit(main())
