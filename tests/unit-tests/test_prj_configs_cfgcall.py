# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from functools import wraps
from releng_tool.exceptions import RelengToolInvalidConfigurationOption
from tests import redirect_stdout
from tests.support.default_engine_test import TestDefaultEngineBase
from unittest.mock import MagicMock


CFGIGNORE_MSG = 'ignored since this project uses `releng_config`'


def expect_prjcfg_warning(*, find: bool):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            with redirect_stdout() as stream:
                func(self, *args, **kwargs)
            self.assertEqual(
                CFGIGNORE_MSG in stream.getvalue(), find, stream.getvalue())
        return wrapper
    return decorator


class TestPrjConfigsCfgCall(TestDefaultEngineBase):
    @expect_prjcfg_warning(find=False)
    def test_prjconfig_cfgcall_accept_option(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    default_internal=True,
)
''')

        self.engine.pkgman = MagicMock()
        self.engine.run()

        opts = self.engine.opts
        self.assertTrue(opts.default_internal_pkgs)
        self.engine.pkgman.load.assert_called_with([
            'minimal',
        ])

    @expect_prjcfg_warning(find=True)
    def test_prjconfig_cfgcall_global_ignored_packages(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'use-this',
    ],
    default_internal=True,
)

packages = [
    'not-this',
]
''')

        self.engine.pkgman = MagicMock()
        self.engine.run()

        opts = self.engine.opts
        self.assertTrue(opts.default_internal_pkgs)
        self.engine.pkgman.load.assert_called_with([
            'use-this',
        ])

    @expect_prjcfg_warning(find=True)
    def test_prjconfig_cfgcall_global_ignored_option_check1(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    default_internal=False,
)

default_internal=True
''')

        self.engine.run()

        opts = self.engine.opts
        self.assertFalse(opts.default_internal_pkgs)

    @expect_prjcfg_warning(find=True)
    def test_prjconfig_cfgcall_global_ignored_option_check2(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    default_internal=True,
)

default_internal=False
''')

        self.engine.run()

        opts = self.engine.opts
        self.assertTrue(opts.default_internal_pkgs)

    def test_prjconfig_cfgcall_invalid_argument(self):
        self.newprjcfg('''\
releng_config(
    packages = [
        'minimal',
    ],
    some_uknown_argument='value',
)
''')

        with self.assertRaises(RelengToolInvalidConfigurationOption):
            self.engine.run()
