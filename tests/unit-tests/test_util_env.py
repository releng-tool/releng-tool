# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from releng_tool.util.env import extend_script_env
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
