# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolInvalidConfigurationSettings
from tests import setprjcfg
from tests import writeprjcfg
from tests.support.default_engine_test import TestDefaultEngineBase


class TestPrjConfigsUrlopenContext(TestDefaultEngineBase):
    def test_prjconfig_urlopen_context_invalid(self):
        setprjcfg(self.engine, 'urlopen_context', 1)

        with self.assertRaises(RelengToolInvalidConfigurationSettings):
            self.engine.run()

    def test_prjconfig_urlopen_context_valid(self):
        writeprjcfg(self.engine, '''\
import ssl

urlopen_context = ssl.create_default_context()
''')
        self.engine.run()

        opts = self.engine.opts
        self.assertIsNotNone(opts.urlopen_context)
