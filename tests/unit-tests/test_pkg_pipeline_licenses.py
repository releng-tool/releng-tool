# -*- coding: utf-8 -*-
# Copyright 2021-2022 releng-tool

from releng_tool.packages.pipeline import RelengPackagePipeline
from tests import RelengToolTestCase
from tests import prepare_testenv
import os


class TestPkgPipelineLicenses(RelengToolTestCase):
    def test_pkg_pipeline_licenses_multiple(self):
        pkg_names = [
            'test-a',
            'test-b',
            'test-c',
        ]

        expected_licenses = [
            2, # mocked BSD + MIT
            None,
            1, # mocked GPL
        ]

        with prepare_testenv(template='licenses') as engine:
            pkgs = engine.pkgman.load(pkg_names)

            pipeline = RelengPackagePipeline(engine, engine.opts, {})
            for pkg in pkgs:
                if not pipeline.process(pkg):
                    break

            for pkg, expected in zip(pkg_names, expected_licenses):
                if expected is not None:
                    # a package with license information should be tracked
                    self.assertTrue(pkg in pipeline.license_files)

                    # verify we have expected license counts
                    licenses = pipeline.license_files[pkg]['files']
                    self.assertEqual(len(licenses), expected)

                    # verify that the license reference maps to a real file
                    for license_ in licenses:
                        self.assertTrue(os.path.exists(license_))
                else:
                    # packages without license data should not provide any
                    # information
                    self.assertFalse(pkg in pipeline.license_files)

    def test_pkg_pipeline_licenses_none(self):
        with prepare_testenv(template='licenses') as engine:
            pkgs = engine.pkgman.load(['test-b'])

            pipeline = RelengPackagePipeline(engine, engine.opts, {})
            for pkg in pkgs:
                if not pipeline.process(pkg):
                    break

            # verify we have no license information if packages have no license
            # information to provide
            self.assertFalse(pipeline.license_files)
