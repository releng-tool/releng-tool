# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.api import RelengVersionNotSupportedException
from releng_tool.registry import RelengRegistry
from tests import RelengToolTestCase


# base folder for test extensions
EXT_PREFIX = 'tests.unit-tests.assets.extensions.'


class TestExtensions(RelengToolTestCase):
    def test_extension_events(self):
        registry = RelengRegistry()
        loaded = registry.load(EXT_PREFIX + 'events')
        self.assertTrue(loaded)

        dummy_env = {}

        registry.emit('config-loaded', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'config-loaded')

        registry.emit('post-build-started', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'post-build-started')

        registry.emit('post-build-finished', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'post-build-finished')

        registry.emit('package-bootstrap-started', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'package-bootstrap-started')

        registry.emit('package-bootstrap-finished', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'package-bootstrap-finished')

        registry.emit('package-configure-started', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'package-configure-started')

        registry.emit('package-configure-finished', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'package-configure-finished')

        registry.emit('package-build-started', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'package-build-started')

        registry.emit('package-build-finished', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'package-build-finished')

        registry.emit('package-install-started', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'package-install-started')

        registry.emit('package-install-finished', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'package-install-finished')

        registry.emit('package-postprocess-started', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'package-postprocess-started')

        registry.emit('package-postprocess-finished', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'package-postprocess-finished')

    def test_extension_requires_new(self):
        registry = RelengRegistry()
        with self.assertRaises(RelengVersionNotSupportedException):
            registry.load(EXT_PREFIX + 'new-requires', ignore=False)

    def test_extension_requires_old(self):
        registry = RelengRegistry()
        loaded = registry.load(EXT_PREFIX + 'old-requires')
        self.assertTrue(loaded)
