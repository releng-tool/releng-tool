# -*- coding: utf-8 -*-
# Copyright 2022 releng-tool

import pprint
import os
import unittest


class EnvironmentTestCase(unittest.TestCase):
    """
    environment-managed unit test base

    Provides a base class for unit testing which clears the running environment
    back to its original state after each test run.
    """

    def run(self, result=None):
        """
        run the test

        Run the test, collecting the result into the TestResult object passed as
        result. See `unittest.TestCase.run()` for more details.

        Args:
            result (optional): the test result to populate
        """

        old_env = dict(os.environ)
        try:
            super(EnvironmentTestCase, self).run(result)
        finally:
            os.environ.clear()
            os.environ.update(old_env)

    def dumpenv(self):
        """
        dump the active environment to the standard output stream
        """

        print('-------------------------------')
        pprint.pprint(dict(os.environ))
        print('-------------------------------')
