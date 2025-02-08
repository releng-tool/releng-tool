# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.opts import RelengEngineOptions
from releng_tool.packages.manager import RelengPackageManager
from releng_tool.registry import RelengRegistry
from tests import RelengToolTestCase
from tests.support import fetch_unittest_assets_dir
import os


# base directory in the unit test folder which holds configurations
CONFIGS_DIR = 'configs'


class TestPkgConfigsBase(RelengToolTestCase):
    """
    package configuration unit test base

    Provides a base class for unit testing package configurations. Using this
    base allows prepares a package manager and provides a quick configuration
    loader for configurations stored in the unit test's example configuration
    directory.

    Attributes:
        configs_dir: the configuration directory
        manager: the package manager
    """

    @classmethod
    def setUpClass(cls):
        cls.opts = RelengEngineOptions()
        cls.registry = RelengRegistry()

        assets_dir = fetch_unittest_assets_dir()
        cls.configs_dir = os.path.join(assets_dir, CONFIGS_DIR)

    def setUp(self):
        self.manager = RelengPackageManager(self.opts, self.registry)

    def LOAD(self, script_name, manager=None):
        """
        attempts to load a package definition

        With a provided `script_name`, the script will be loaded and will
        populate/return package related information.

        Args:
            script_name: the script to load from the configuration directory
            manager (optional): override the package manager to use when loading

        Returns:
            returns a tuple of three (3) containing the package instance, the
            extracted environment/globals from the package script and a list of
            known package dependencies

        Raises:
            RelengToolInvalidPackageConfiguration: when an error has been
                                                    detected loading the package
        """
        if not manager:
            manager = self.manager
        script = os.path.join(self.configs_dir, script_name)
        return manager.load_package('test', script)
