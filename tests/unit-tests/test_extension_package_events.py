# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os


class TestExtensionPackageEvents(RelengToolTestCase):
    def test_extension_package_events(self):
        with prepare_testenv(template='extension-pkg-events') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            events = os.path.join(engine.opts.root_dir, 'events.json')
            self.assertTrue(os.path.exists(events))

            # list of expected events and in the expected order
            expected_events = [
                'package-bootstrap-started',
                'package-bootstrap-finished',
                'package-configure-started',
                'package-configure-finished',
                'package-build-started',
                'package-build-finished',
                'package-install-started',
                'package-install-finished',
                'package-postprocess-started',
                'package-postprocess-finished',
            ]

            with open(events) as f:
                data = json.load(f)
                last_ts = 0

                for expected_event in expected_events:
                    # verify we have seen this event
                    self.assertIn(expected_event, data)

                    # verify event in expected order
                    expect_ts = data.pop(expected_event)
                    self.assertGreater(expect_ts, last_ts)

                # ensure no extra events
                self.assertFalse(data)
