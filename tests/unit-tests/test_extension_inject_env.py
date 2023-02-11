# -*- coding: utf-8 -*-
# Copyright 2023 releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os


class TestExtensionInjectEnvironment(RelengToolTestCase):
    def test_extension_inject_env(self):
        with prepare_testenv(template='extension-env-inject') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            sts = os.path.join(engine.opts.target_dir, 'status.json')
            self.assertTrue(os.path.exists(sts))

            with open(sts, 'r') as f:
                data = json.load(f)
                self.assertTrue('custom-invoke' in data)
                self.assertEqual(data['custom-invoke'], 42)
