# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.opts import DEFAULT_SYSROOT_PREFIX
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
        return None  # use releng-tool default

    def python_lib(self, dir_: str,
            prefix: str = DEFAULT_SYSROOT_PREFIX) -> Path:
        """
        return the python library directory for a given path

        This call returns the default releng-tool library path for Python
        packages based on a configure target.

        Args:
            dir_: the directory to search
            prefix (optional): the prefix of the install
        """

        return Path(dir_) / prefix.strip('/') / 'lib' / 'python'

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

        for root, dirs, _ in os.walk(dir_):
            if 'site-packages' in dirs:
                return os.path.join(root, 'site-packages')

            # Workaround for Debian-based site installation paths; while
            # installing into `dist-packages` is expected for Debian-based
            # platforms, it is not desired for Python packages "installed"
            # into a staged/target sysroot. While using environment options
            # like `SETUPTOOLS_USE_DISTUTILS=stdlib` appear to force projects
            # to use `site-packages`, it does not handle when using the
            # `installer` module which provides a Debian library path. For
            # now, we leave as it so it is consistent between both
            # installation types. Users should be able to workaround by
            # manually setting a prefix. Once we figure out a way to always
            # result in a path with `site-packages`, we can remove this
            # check option below. Although, we might provide an option to
            # allow a project to override the path used, so they can point
            # to `site-packages` or `dist-packages` (outside of the explicit
            # prefix override), if it seems right.
            if 'dist-packages' in dirs:
                return os.path.join(root, 'dist-packages')

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
