# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.util.env import env_value
from releng_tool.util.env import extend_script_env
import os
import unittest


class TestUtilEnv(unittest.TestCase):
    def test_utilenv_extendscriptenv(self):
        env = {'a': 1}

        # can append new entries
        extend_script_env(env, {'b': 2})
        self.assertEqual(len(env.keys()), 2)
        self.assertIn('a', env)
        self.assertIn('b', env)
        self.assertEqual(env['a'], 1)
        self.assertEqual(env['b'], 2)

        # will override existing entries
        extend_script_env(env, {'b': 3})
        self.assertEqual(len(env.keys()), 2)
        self.assertIn('a', env)
        self.assertIn('b', env)
        self.assertEqual(env['a'], 1)
        self.assertEqual(env['b'], 3)

        # magic values are ignored
        extend_script_env(env, {'__magic__': 4})
        self.assertEqual(len(env.keys()), 2)

        # imported built-in functions are ignored
        extend_script_env(env,
            {'test': globals()['__builtins__']['hash']})
        self.assertEqual(len(env.keys()), 2)

        # imported functions are ignored
        extend_script_env(env,
            {'test': globals()['extend_script_env']})
        self.assertEqual(len(env.keys()), 2)

        # imported modules are ignored
        extend_script_env(env, {'test': globals()['unittest']})
        self.assertEqual(len(env.keys()), 2)

    def test_utilenv_env_value(self):
        test_env_key = 'RELENG_TOOL_UNIT_TEST_KEY'
        test_env_val = 'NEW_VALUE'

        # check a (should be) empty/unset environment variable
        value = os.environ.get(test_env_key)
        self.assertIsNone(value)

        value = env_value(test_env_key)
        self.assertIsNone(value)

        # configure an environment variable
        value = env_value(test_env_key, test_env_val)
        self.assertEqual(value, test_env_val)

        value = env_value(test_env_key)
        self.assertEqual(value, test_env_val)

        value = os.environ.get(test_env_key)
        self.assertEqual(value, test_env_val)

        # configure an empty environment variable
        value = env_value(test_env_key, '')
        self.assertEqual(value, '')

        value = env_value(test_env_key)
        self.assertEqual(value, '')

        value = os.environ.get(test_env_key)
        self.assertEqual(value, '')

        # remove the environment variable
        value = env_value(test_env_key, None)
        self.assertIsNone(value)

        value = env_value(test_env_key)
        self.assertIsNone(value)

        value = os.environ.get(test_env_key)
        self.assertIsNone(value)

        # retry removing the environment variable (no-op)
        value = env_value(test_env_key, None)
        self.assertIsNone(value)
