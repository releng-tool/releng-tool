# -*- coding: utf-8 -*-
# Copyright 2022 releng-tool

from tests.support.site_tool_test import TestSiteToolBase
import os


class PythonSiteToolBase(TestSiteToolBase):
    """
    python site tool testing unit test base

    Provides an extension of the TestSiteToolBase base class for
    Python-specific unit testing. This base class provides additional
    helpers that are specific to Python-related builds/installs.
    """

    def prepare_global_action(self):
        return None # use releng-tool default

    def find_site_packages(self, dir_):
        """
        find a Python site-package folder inside a provided directory

        The following call will accept a directory argument and will perform
        a nested search to find a `site-packages` folder. This is to help
        perform checks on a generated site-package folder, without having to
        worry about various platform-specific prefixes.

        Args:
            dir_: the directory to search
        """

        for root, dirs, files in os.walk(dir_):
            if 'site-packages' in dirs:
                return os.path.join(root, 'site-packages')

        return None

    def assertPythonModuleExists(self, site_packages, module):
        """
        verify that a provided module exists in a site-package folder

        This assertion helper allows a test to verify that a specific Python
        module can be found in a site-package folder.

        Args:
            site_packages: the site-packages location
            module: the module to check for
        """

        module = os.path.join(site_packages, module, '__init__.py')
        self.assertTrue(os.path.exists(module))
