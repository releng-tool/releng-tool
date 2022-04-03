# -*- coding: utf-8 -*-
# Copyright 2022 releng-tool

from releng_tool.packages.pipeline import RelengPackagePipeline
from tests import prepare_testenv
import json
import os
import unittest

class TestPkgPipelineContainedEnvironment(unittest.TestCase):
    def test_pkg_pipeline_containedenv(self):
        pkg_names = [
            'test1',
            'test2',
        ]

        with prepare_testenv(template='contained-env') as engine:
            pkgs = engine.pkgman.load(pkg_names)

            pipeline = RelengPackagePipeline(engine, engine.opts, {})
            for pkg in pkgs:
                if not pipeline.process(pkg):
                    break

            # verify package-specific environment variables were set
            self.assertTrue('TEST1_BUILD_OUTPUT_DIR' in os.environ)
            test1_outdir = os.environ['TEST1_BUILD_OUTPUT_DIR']
            results1 = os.path.join(test1_outdir, 'invoke-env.json')
            self.assertTrue(os.path.exists(results1))

            with open(results1, 'r') as f:
                data = json.load(f)

            pkg_keys = [
                'NJOBS',
                'NJOBSCONF',
                'PREFIX',
            ]
            self.assertTrue(all(x in data for x in pkg_keys))
            self.assertEqual(data['NJOBS'], '42')
            self.assertEqual(data['NJOBSCONF'], '42')
            self.assertEqual(data['PREFIX'], '/my-custom-prefix')

            # verify package-specific environment variables were properly
            # restored to original counts (leak check)
            self.assertTrue('TEST2_BUILD_OUTPUT_DIR' in os.environ)
            test2_outdir = os.environ['TEST2_BUILD_OUTPUT_DIR']
            results2 = os.path.join(test2_outdir, 'invoke-env.json')
            self.assertTrue(os.path.exists(results2))

            with open(results2, 'r') as f:
                data = json.load(f)

            if 'NJOBS' in data:
                self.assertNotEqual(data['NJOBS'], '42')
            if 'NJOBSCONF' in data:
                self.assertNotEqual(data['NJOBSCONF'], '42')
            if 'PREFIX' in data:
                self.assertNotEqual(data['PREFIX'], '/my-custom-prefix')
