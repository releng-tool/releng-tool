# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import os


class TestLocalNoExtraction(RelengToolTestCase):
    def test_extraction_disabled(self):
        with prepare_testenv(template='extraction-disabled') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            build_dir = os.path.join(engine.opts.build_dir, 'test-pkg')
            new_file = os.path.join(build_dir, 'metadata')
            self.assertFalse(os.path.exists(new_file))

    def test_extraction_enabled(self):
        with prepare_testenv(template='extraction-enabled') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            build_dir = os.path.join(engine.opts.build_dir, 'test-pkg')
            new_file = os.path.join(build_dir, 'metadata')
            self.assertTrue(os.path.exists(new_file))
