#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

import fnmatch
import os
import sys
import unittest

"""
default verbosity for unit tests
"""
DEFAULT_VERBOSITY = 2

def main():
    """
    process main for unit tests

    This method will prepare the test suite, load listed test classes and
    perform a run.
    """
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # discover unit tests
    test_base = os.path.dirname(os.path.realpath(__file__))
    tests_dir = os.path.join(test_base, 'unit-tests')
    unit_tests = loader.discover(tests_dir)

    # check if a unit test name was provided
    target_test_name_pattern = None
    for arg in sys.argv[1:]:
        if not arg.startswith('-'):
            target_test_name_pattern = arg
            break

    # register tests
    target_unit_test = None
    if target_test_name_pattern:
        target_unit_test, module_load_failure = find_test(
            unit_tests, target_test_name_pattern)
        if target_unit_test:
            print('running specific test: {}'.format(target_unit_test.id()))
            sys.stdout.flush()
        else:
            print('ERROR: unable to find test with pattern: '
                '{}'.format(target_test_name_pattern))
            if not module_load_failure:
                sys.exit(1)

    if target_unit_test:
        suite.addTest(target_unit_test)
    else:
        suite.addTests(unit_tests)

    # invoke test suite
    runner = unittest.TextTestRunner(verbosity=DEFAULT_VERBOSITY)
    return 0 if runner.run(suite).wasSuccessful() else 1

def find_test(entity, pattern):
    """
    search for a unit test with a matching wildcard pattern

    Looks for the first 'unittest.case.TestCase' instance where its identifier
    matches the provided wildcard pattern.
    """
    module_load_failure = False

    if isinstance(entity, unittest.case.TestCase):
        if fnmatch.fnmatch(entity.id(), '*{}*'.format(pattern)):
            return entity, False
        elif 'ModuleImportFailure' in entity.id():
            return None, True
    elif isinstance(entity, unittest.TestSuite):
        for subentity in entity:
            found, module_load_failure = find_test(subentity, pattern)
            if found:
                return found, module_load_failure

    return None, module_load_failure

if __name__ == '__main__':
    sys.exit(main())
