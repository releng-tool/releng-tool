# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.opts import RelengEngineOptions
from tests import RelengToolTestCase


class TestMisc(RelengToolTestCase):
    def test_opts_accept_profiles(self):
        # default no profiles
        opts = RelengEngineOptions()
        self.assertFalse(opts.profiles)

        # can provide a single profile
        args = MockArgs()
        args.profile = [
            'example',
        ]

        opts = RelengEngineOptions(args)
        self.assertEqual(opts.profiles, [
            'example',
        ])

        # can provide multiple profile
        args = MockArgs()
        args.profile = [
            'zulu',
            'first',
            'second',
            'third',
        ]

        opts = RelengEngineOptions(args)
        self.assertEqual(opts.profiles, [
            'zulu',
            'first',
            'second',
            'third',
        ])

        # even multiple profiles in a given profile argument
        args = MockArgs()
        args.profile = [
            'alpha,charlie',
            'bravo;delta',
        ]

        opts = RelengEngineOptions(args)
        self.assertEqual(opts.profiles, [
            'alpha',
            'charlie',
            'bravo',
            'delta',
        ])

        # profiles are normalized
        args = MockArgs()
        args.profile = [
            ' this is an--example',
        ]

        opts = RelengEngineOptions(args)
        self.assertEqual(opts.profiles, [
            'this-is-an-example',
        ])

        # only track a unique list of profiles
        args = MockArgs()
        args.profile = [
            'test1',
            'test1',
            'test1 ',
            ' test1',
        ]

        opts = RelengEngineOptions(args)
        self.assertEqual(opts.profiles, [
            'test1',
        ])

    def test_opts_accept_quirks(self):
        # default no quirks
        opts = RelengEngineOptions()
        self.assertFalse(opts.quirks)

        # can provide a single quirks
        args = MockArgs()
        args.quirk = [
            'example',
        ]

        opts = RelengEngineOptions(args)
        self.assertEqual(opts.quirks, [
            'example',
        ])

        # can provide multiple quirks
        args = MockArgs()
        args.quirk = [
            'zulu',
            'first',
            'second',
            'third',
        ]

        opts = RelengEngineOptions(args)
        self.assertEqual(opts.quirks, [
            'zulu',
            'first',
            'second',
            'third',
        ])

        # only track a unique list of quirks
        args = MockArgs()
        args.quirk = [
            'test1',
            'test1',
            'test1 ',
            ' test1',
        ]

        opts = RelengEngineOptions(args)
        self.assertEqual(opts.quirks, [
            'test1',
        ])


class MockArgs:
    def __getattr__(self, name):
        return self.name if name in self.__dict__ else None
