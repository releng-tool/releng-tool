# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.engine.suggest import suggest
from releng_tool.opts import RelengEngineOptions
from releng_tool.defs import PkgAction
from tests import RelengToolTestCase


class TestEngineSuggest(RelengToolTestCase):
    def setUp(self):
        self.opts = RelengEngineOptions()

    def test_engine_suggest_action_multiple(self):
        def pkg_finder(opts):  # noqa: ARG001
            return []

        suggested = self._suggest('clea', pkg_finder)
        self.assertIn('distclean', suggested)
        self.assertIn('clean', suggested)

    def test_engine_suggest_action_single(self):
        def pkg_finder(opts):  # noqa: ARG001
            return []

        suggested = self._suggest('fecth', pkg_finder)
        self.assertIn('fetch', suggested)

    def test_engine_suggest_valid_action_unknown_pkg(self):
        def pkg_finder(opts):  # noqa: ARG001
            return ['example']

        self.opts.pkg_action = PkgAction.PATCH
        suggested = self._suggest('exanple-patch', pkg_finder)
        self.assertIn('example-patch', suggested)

    def test_engine_suggest_valid_pkg_unknown_action(self):
        def pkg_finder(opts):  # noqa: ARG001
            return ['example']

        suggested = self._suggest('example-instll', pkg_finder)
        self.assertIn('example-install', suggested)

    def test_engine_suggest_unknown_all(self):
        def pkg_finder(opts):  # noqa: ARG001
            return ['a-long-pkg-name']

        suggested = self._suggest('long-pkg', pkg_finder)
        self.assertIn('a-long-pkg-name', suggested)

    def test_engine_suggest_unknown_package(self):
        def pkg_finder(opts):  # noqa: ARG001
            return ['example']

        suggested = self._suggest('exmaple', pkg_finder)
        self.assertIn('example', suggested)

    def _suggest(self, value, pkg_finder):
        self.opts.target_action = value
        return suggest(self.opts, value, pkg_finder=pkg_finder)
