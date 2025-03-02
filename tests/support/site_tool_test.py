# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import GlobalAction
from releng_tool.packages import pkg_key
from releng_tool.util.io_remove import path_remove
from releng_tool.util.io_temp_dir import temp_dir
from tests import RelengToolTestCase
from tests import prepare_testenv
import os
import unittest


PKG_NAME = 'test'
PKG_DEFDIR = os.path.join('package', PKG_NAME)
PKG_DEFINITION = os.path.join(PKG_DEFDIR, PKG_NAME + '.rt')
DEFAULT_TEMPLATE = 'site-tool'


class TestSiteToolBase(RelengToolTestCase):
    """
    site tool testing unit test base

    Provides a base class for unit testing site-specific tools supported by
    releng-tool. Using this base helps prepare an interim repository directory,
    as well as a releng-tool engine/environment with a package configuration
    configured to use the interim repository directory as a site location.

    A unit test can build/manipulate a repository's contents, modify a test
    package's configuration and invoke a prepared releng-tool engine to help
    sanity check that releng-tool handles various package options and repository
    states.
    """

    @classmethod
    def setUpClass(cls):
        # support skipping all tooling tests for a distribution build
        if os.getenv('RELENG_SKIP_TEST_TOOLING'):
            raise unittest.SkipTest('skipped due to environment flag')

        # support skipping the test for a distribution build
        test_type = cls.__qualname__.removeprefix('TestTool')
        pf = ''.join(['_' + c if c.isupper() else c for c in test_type]).upper()
        if os.getenv(f'RELENG_SKIP_TEST_TOOL{pf}'):
            raise unittest.SkipTest('skipped due to specific environment flag')


    def run(self, result=None):
        """
        run the test

        Run the test, collecting the result into the TestResult object passed as
        result. See `unittest.TestCase.run()` for more details.

        Args:
            result (optional): the test result to populate
        """

        with temp_dir(wd=True) as repo_dir:
            self.repo_dir = repo_dir
            self.prepare_repo_dir(repo_dir)

            with prepare_testenv(template=self.tool_template()) as engine:
                opts = engine.opts

                opts.gbl_action = self.prepare_global_action()

                self.build_dir_prefix = os.path.join(opts.build_dir, PKG_NAME)
                self.cache_dir = os.path.join(opts.cache_dir, PKG_NAME)
                self.def_dir = os.path.join(opts.root_dir, PKG_DEFDIR)
                self.defconfig = os.path.join(opts.root_dir, PKG_DEFINITION)
                self.engine = engine
                self.pkg_name = PKG_NAME

                self.defconfig_add('SITE', self.repo_dir)
                self.prepare_defconfig(self.defconfig)

                super().run(result)

    def prepare_global_action(self):
        """
        hook invoked to prepare a default global action for tool testing

        By default, site tool testing will default to only performing up to
        the extraction stage; however, some unit testing may wish to use an
        alternative default. This hook provides a means to override the
        default action.

        Returns:
            the global action
        """

        # by default, only perform up to the extraction stage
        return GlobalAction.EXTRACT

    def prepare_defconfig(self, defconfig):
        """
        hook invoked to prepare a package's definition

        Method invoked to allow an implementer help prepare a package's
        definition file to be used by a releng-tool engine.

        Args:
            defconfig: the definition file
        """

    def prepare_repo_dir(self, repo_dir):
        """
        hook invoked to prepare a repository

        Method invoked to allow an implementer help prepare a mocked
        repository's directory contents.

        Note that this call is invoked where the working directory is configured
        to the same path provided by `repo_dir`.

        Args:
            repo_dir: the repository directory
        """

    def tool_template(self):
        """
        the configuration template to use

        Returns the configuration template to be used when preparing a test
        environment for a unit test. This call is to be overridden by
        implementations using TestSiteToolBase.

        Returns:
            the template name; `None` if no template is to be used
        """
        return DEFAULT_TEMPLATE

    def cleanup_outdir(self):
        """
        cleanup the output directory

        Provides a unit test the ability to quickly cleanup the output directory
        of the configured output directory of a test.
        """
        path_remove(self.engine.opts.out_dir)

    def defconfig_add(self, key, value, defconfig=None, pkg_name=None):
        """
        inject a configuration into the test package's definition

        This method will inject a configuration entry named by `key` and append
        it to the running test's package definition. The representation of the
        provided value will be used as an assignment for the configuration key.

        Args:
            key: the key to use for the configuration entry
            value: the value to use for the configuration entry
            defconfig (optional): the configuration file to edit
            pkg_name (optional): the package name
        """

        if not defconfig:
            defconfig = self.defconfig

        if not pkg_name:
            pkg_name = PKG_NAME

        with open(defconfig, mode='a', encoding='utf_8') as file_def:
            file_def.write('{} = {}\n'.format(
                pkg_key(pkg_name, key), repr(value)))

    def defconfig_dump(self, defconfig=None):
        """
        dump the test package's definition contents to standard out

        When requested, the test package's definition file will be read and
        dumped to the configured standard output stream.

        Args:
            defconfig (optional): the configuration file to dump
        """

        if not defconfig:
            defconfig = self.defconfig

        with open(defconfig, encoding='utf_8') as f:
            content = f.readlines()

        print('-------------------------------')
        print(''.join(content).strip())
        print('-------------------------------')

    def dir_dump(self, dir_=None):
        """
        dump a test folders's file list to standard out

        When requested, a provide directory will be scanned for files and the
        file list will be dumped to the configured standard output stream.

        Args:
            dir_ (optional): the directory to search (defaults to
                              generated repository)
        """

        if not dir_:
            dir_ = self.repo_dir

        files = self._dir_fetch(dir_)

        print(f'DIR: {dir_}]')
        print('-------------------------------')
        for file_ in files:
            print(file_[len(dir_) + 1:])
        print('-------------------------------')

    def _dir_fetch(self, dir_):
        """
        compile a list of files in a test folder

        This call will return a list of all files found in the provided
        directory. If the provided directory contains other directories, they
        will also be searched for file entries to populate.

        Args:
            dir_: the directory to search

        Returns:
            the file list
        """

        files = []

        for f in os.scandir(dir_):
            if f.is_dir():
                files.extend(self._dir_fetch(f.path))
            elif f.is_file():
                files.append(f.path)

        return files
