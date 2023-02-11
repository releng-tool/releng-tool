# -*- coding: utf-8 -*-
# Copyright 2023 releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os


class TestExtensionEventWorkingDirectories(RelengToolTestCase):
    def test_extension_event_workdirs(self):
        with prepare_testenv(template='extension-env-dirs') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            expected_workdirs = {
                'config-loaded': engine.opts.root_dir,
                'post-build-started': engine.opts.target_dir,
                'post-build-finished': engine.opts.target_dir,
            }

            for k, expected_dir in expected_workdirs.items():
                state = os.path.join(engine.opts.root_dir, k + '.json')
                self.assertTrue(os.path.exists(state))

                with open(state, 'r') as f:
                    data = json.load(f)
                    self.assertTrue('wd' in data)
                    self.assertEqual(data['wd'], expected_dir)
