# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.prerequisites import RelengPrerequisites
from releng_tool.tool.python import PYTHON
from tests import RelengToolTestCase


class TestPrerequisites(RelengToolTestCase):
    def test_prerequisites_exclude(self):
        prerequisites = RelengPrerequisites([], ['misc-command'])
        check = prerequisites.check(exclude=['misc-command'])
        self.assertTrue(check)

    def test_prerequisites_exist(self):
        # python should exist; since we rely on python
        prerequisites = RelengPrerequisites([], [PYTHON.tool])
        check = prerequisites.check()
        self.assertTrue(check)

    def test_prerequisites_missing(self):
        prerequisites = RelengPrerequisites([], ['unknown-command-releng'])
        check = prerequisites.check()
        self.assertFalse(check)
