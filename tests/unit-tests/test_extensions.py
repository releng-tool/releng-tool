# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

from releng_tool.api import RelengVersionNotSupportedException
from releng_tool.registry import RelengRegistry
import unittest


# base folder for test extensions
EXT_PREFIX = 'tests.unit-tests.assets.extensions.'


class TestExtensions(unittest.TestCase):
    def test_extension_requires_new(self):
        registry = RelengRegistry()
        with self.assertRaises(RelengVersionNotSupportedException):
            registry.load(EXT_PREFIX + 'new-requires', ignore=False)

    def test_extension_requires_old(self):
        registry = RelengRegistry()
        loaded = registry.load(EXT_PREFIX + 'old-requires')
        self.assertTrue(loaded)
