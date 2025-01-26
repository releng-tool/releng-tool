# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.api import RelengExtractExtensionInterface
from releng_tool.api import RelengFetchExtensionInterface
from releng_tool.api import RelengInvalidSetupException
from releng_tool.api import RelengPackageExtensionInterface
from releng_tool.registry import RelengRegistry
from tests import RelengToolTestCase


class TestRegistry(RelengToolTestCase):
    def test_registry_connect_and_disconnect(self):
        registry = RelengRegistry()

        def increment_event(env):
            env['id'] += 1

        dummy_env = {
            'id': 0,
        }

        id_ = registry.connect('config-loaded', increment_event)

        registry.emit('config-loaded', env=dummy_env)
        self.assertEqual(dummy_env['id'], 1)

        registry.emit('config-loaded', env=dummy_env)
        self.assertEqual(dummy_env['id'], 2)

        registry.disconnect(id_)

        registry.emit('config-loaded', env=dummy_env)
        self.assertEqual(dummy_env['id'], 2)

    def test_registry_ignore_already_loaded_extension(self):
        registry = RelengRegistry()

        # sanity check internal seed extension is loaded
        self.assertTrue('releng_tool.ext.seed' in registry.extension)

        # attempts to reload should always work (i.e. ignored)
        loaded = registry.load('releng_tool.ext.seed')
        self.assertTrue(loaded)

    def test_registry_invalid_registration(self):
        registry = RelengRegistry()

        # sanity check extract, fetch and package type handling
        invalid_handler = False
        invalid_name = 'invalid-name'
        invalid_name_type = False
        valid_name = 'ext-valid-name'

        method_names = {
            'add_extract_type': RelengExtractExtensionInterface,
            'add_fetch_type': RelengFetchExtensionInterface,
            'add_package_type': RelengPackageExtensionInterface,
        }

        for method_name, handler_type in method_names.items():
            regcall = getattr(registry, method_name)
            valid_handler = handler_type

            # invalid name type should raise an error
            with self.assertRaises(RelengInvalidSetupException):
                regcall(invalid_name_type, valid_handler)

            # invalid name should raise an error
            with self.assertRaises(RelengInvalidSetupException):
                regcall(invalid_name, valid_handler)

            # invalid handler should raise an error
            with self.assertRaises(RelengInvalidSetupException):
                regcall(valid_name, invalid_handler)

            # valid
            regcall(valid_name, valid_handler)

            # duplicate entry should raise an error
            with self.assertRaises(RelengInvalidSetupException):
                regcall(valid_name, valid_handler)

        # sanity check event hook handling
        invalid_event = 'random-text'
        valid_event = 'config-loaded'

        def event_handler(**kwargs):
            pass

        with self.assertRaises(RelengInvalidSetupException):
            registry.connect(invalid_event, event_handler)

        with self.assertRaises(RelengInvalidSetupException):
            registry.connect(valid_event, invalid_handler)

        registry.connect(valid_event, event_handler)

    def test_registry_missing_extension(self):
        registry = RelengRegistry()

        loaded = registry.load_all_extensions([
            'some-invalid-extension-type-entry1',
        ])
        self.assertFalse(loaded)

        loaded = registry.load('some-invalid-extension-type-entry2')
        self.assertFalse(loaded)

    def test_registry_priority_fifo(self):
        registry = RelengRegistry()
        dummy_env = {}

        def first_event(env):
            env['last-event'] = 'first'

        def second_event(env):
            env['last-event'] = 'second'

        registry.connect('config-loaded', first_event)
        registry.connect('config-loaded', second_event)

        registry.emit('config-loaded', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'second')

    def test_registry_priority_scenario01(self):
        registry = RelengRegistry()
        dummy_env = {}

        def first_event(env):
            env['last-event'] = 'first'

        def second_event(env):
            env['last-event'] = 'second'

        registry.connect('config-loaded', first_event)
        registry.connect('config-loaded', second_event, priority=50)

        registry.emit('config-loaded', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'first')

    def test_registry_priority_scenario02(self):
        registry = RelengRegistry()
        dummy_env = {}

        def first_event(env):
            env['last-event'] = 'first'

        def second_event(env):
            env['last-event'] = 'second'

        def third_event(env):
            env['last-event'] = 'third'

        registry.connect('config-loaded', first_event, priority=50)
        registry.connect('config-loaded', second_event)
        registry.connect('config-loaded', third_event, priority=150)

        registry.emit('config-loaded', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'third')

    def test_registry_priority_scenario03(self):
        registry = RelengRegistry()
        dummy_env = {}

        def first_event(env):
            env['last-event'] = 'first'

        def second_event(env):
            env['last-event'] = 'second'

        def third_event(env):
            env['last-event'] = 'third'

        registry.connect('config-loaded', first_event, priority=1)
        registry.connect('config-loaded', second_event, priority=3)
        registry.connect('config-loaded', third_event, priority=2)

        registry.emit('config-loaded', env=dummy_env)
        last_event = dummy_env.get('last-event')
        self.assertEqual(last_event, 'second')
