# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import Rpk
from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests import setpkgcfg
from tests import setprjcfg
from tests.support.default_engine_test import TestDefaultEngineBase
import os


class TestPrjConfigsRevisions(TestDefaultEngineBase):
    def test_prjconfig_revisions_check_ignored_revision(self):
        setprjcfg(self.engine, 'revisions', {
            'minimal': '2.3.4',
        })
        setpkgcfg(self.engine, 'minimal', Rpk.REVISION, '8.9')
        self.engine.run()

        self.assertIn('MINIMAL_REVISION', os.environ)
        self.assertEqual(os.environ['MINIMAL_REVISION'], '8.9')

    def test_prjconfig_revisions_check_ignored_version(self):
        setprjcfg(self.engine, 'revisions', {
            'minimal': '2.3.4',
        })
        setpkgcfg(self.engine, 'minimal', Rpk.VERSION, '5.6.7')
        self.engine.run()

        self.assertIn('MINIMAL_REVISION', os.environ)
        self.assertEqual(os.environ['MINIMAL_REVISION'], '5.6.7')

    def test_prjconfig_revisions_check_set(self):
        setprjcfg(self.engine, 'revisions', {
            'minimal': '1.2.3.4.5',
        })
        setpkgcfg(self.engine, 'minimal', Rpk.VERSION, None)
        self.engine.run()

        self.assertIn('MINIMAL_REVISION', os.environ)
        self.assertEqual(os.environ['MINIMAL_REVISION'], '1.2.3.4.5')

    def test_prjconfig_revisions_invalid(self):
        setprjcfg(self.engine, 'revisions', {
            'minimal': True,
        })
        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_revisions_valid(self):
        expected_revisions = {
            'minimal': '1.2.3',
        }

        setprjcfg(self.engine, 'revisions', expected_revisions)
        self.engine.run()

        opts = self.engine.opts
        self.assertEqual(opts.revisions, expected_revisions)
