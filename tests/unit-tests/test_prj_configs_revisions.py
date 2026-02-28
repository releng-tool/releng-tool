# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from functools import wraps
from pathlib import Path
from releng_tool.defs import Rpk
from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests import redirect_stdout
from tests import setpkgcfg
from tests import setprjcfg
from tests.support.default_engine_test import TestDefaultEngineBase
import json
import os


REVIGNORE_MSG = '(warn) ignoring project-defined revision'


def expect_revision_warning(*, find: bool):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            with redirect_stdout() as stream:
                func(self, *args, **kwargs)
            print(stream.getvalue())
            self.assertEqual(REVIGNORE_MSG in stream.getvalue(), find)
        return wrapper
    return decorator


class TestPrjConfigsRevisions(TestDefaultEngineBase):
    @expect_revision_warning(find=False)
    def test_prjconfig_revisions_check_devmode_na(self):
        setprjcfg(self.engine, 'revisions', {
            'minimal': '76.3',
        })
        setpkgcfg(self.engine, 'minimal', Rpk.REVISION, {
            'example': 'main',
        })
        setpkgcfg(self.engine, 'minimal', Rpk.VERSION, None)
        self.engine.run()

        self.assertIn('MINIMAL_REVISION', os.environ)
        self.assertEqual(os.environ['MINIMAL_REVISION'], '76.3')

    @expect_revision_warning(find=False)
    def test_prjconfig_revisions_check_devmode_rev1(self):
        # force enable development mode
        with open(self.engine.opts.ff_devmode, 'w') as f:
            json.dump({
                'mode': 'example',
            }, f)

        setprjcfg(self.engine, 'revisions', {
            'minimal': '1.4',
        })
        setpkgcfg(self.engine, 'minimal', Rpk.REVISION, {
            'example': '21.34',
        })
        setpkgcfg(self.engine, 'minimal', Rpk.VERSION, None)
        self.engine.run()

        self.assertIn('MINIMAL_REVISION', os.environ)
        self.assertEqual(os.environ['MINIMAL_REVISION'], '21.34')

    @expect_revision_warning(find=False)
    def test_prjconfig_revisions_check_devmode_rev2(self):
        # force enable development mode
        Path(self.engine.opts.ff_devmode).touch()

        setprjcfg(self.engine, 'revisions', {
            'minimal': '5.4',
        })
        setpkgcfg(self.engine, 'minimal', Rpk.DEVMODE_REVISION, '2.3')
        setpkgcfg(self.engine, 'minimal', Rpk.VERSION, None)
        self.engine.run()

        self.assertIn('MINIMAL_REVISION', os.environ)
        self.assertEqual(os.environ['MINIMAL_REVISION'], '2.3')

    @expect_revision_warning(find=True)
    def test_prjconfig_revisions_check_ignored_revision_asterisk(self):
        setprjcfg(self.engine, 'revisions', {
            'minimal': '1.4',
        })
        setpkgcfg(self.engine, 'minimal', Rpk.REVISION, {
            '*': '21.134',
        })
        setpkgcfg(self.engine, 'minimal', Rpk.VERSION, None)
        self.engine.run()

        self.assertIn('MINIMAL_REVISION', os.environ)
        self.assertEqual(os.environ['MINIMAL_REVISION'], '21.134')

    @expect_revision_warning(find=True)
    def test_prjconfig_revisions_check_ignored_revision_single(self):
        setprjcfg(self.engine, 'revisions', {
            'minimal': '2.3.4',
        })
        setpkgcfg(self.engine, 'minimal', Rpk.REVISION, '8.9')
        setpkgcfg(self.engine, 'minimal', Rpk.VERSION, None)
        self.engine.run()

        self.assertIn('MINIMAL_REVISION', os.environ)
        self.assertEqual(os.environ['MINIMAL_REVISION'], '8.9')

    @expect_revision_warning(find=True)
    def test_prjconfig_revisions_check_ignored_version(self):
        setprjcfg(self.engine, 'revisions', {
            'minimal': '2.3.4',
        })
        setpkgcfg(self.engine, 'minimal', Rpk.VERSION, '5.6.7')
        self.engine.run()

        self.assertIn('MINIMAL_REVISION', os.environ)
        self.assertEqual(os.environ['MINIMAL_REVISION'], '5.6.7')

    @expect_revision_warning(find=False)
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
