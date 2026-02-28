# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.defs import Rpk
from tests import RelengToolTestCase
from tests import prepare_testenv
from tests import setpkgcfg
import json
import os


class TestToolPatchFiltering(RelengToolTestCase):
    def test_tool_patch_filter_devmode_custom_disabled(self):
        with prepare_testenv(template='patch-file-valid') as engine:
            # force enable development mode
            with open(engine.opts.ff_devmode, 'w') as f:
                json.dump({
                    'mode': 'custom',
                }, f)

            setpkgcfg(engine, 'test', Rpk.DEVMODE_PATCHES, {
                'other': True,
            })
            setpkgcfg(engine, 'test', Rpk.DEVMODE_REVISION, 'main')

            rv = engine.run()
            self.assertTrue(rv)

            build_dir = os.path.join(engine.opts.build_dir, 'test-main')

            new_file = os.path.join(build_dir, 'new-file.txt')
            self.assertFalse(os.path.exists(new_file))

            another_file = os.path.join(build_dir, 'another-file.txt')
            self.assertFalse(os.path.exists(another_file))

    def test_tool_patch_filter_devmode_custom_enabled(self):
        with prepare_testenv(template='patch-file-valid') as engine:
            # force enable development mode
            with open(engine.opts.ff_devmode, 'w') as f:
                json.dump({
                    'mode': 'custom',
                }, f)

            setpkgcfg(engine, 'test', Rpk.DEVMODE_PATCHES, {
                'custom': True,
            })
            setpkgcfg(engine, 'test', Rpk.DEVMODE_REVISION, 'main')

            rv = engine.run()
            self.assertTrue(rv)

            build_dir = os.path.join(engine.opts.build_dir, 'test-main')

            new_file = os.path.join(build_dir, 'new-file.txt')
            self.assertTrue(os.path.exists(new_file))

            another_file = os.path.join(build_dir, 'another-file.txt')
            self.assertTrue(os.path.exists(another_file))

    def test_tool_patch_filter_devmode_custom_filter_disabled(self):
        with prepare_testenv(template='patch-file-valid') as engine:
            # force enable development mode
            with open(engine.opts.ff_devmode, 'w') as f:
                json.dump({
                    'mode': 'custom',
                }, f)

            setpkgcfg(engine, 'test', Rpk.DEVMODE_PATCHES, {
                'other': '*',
            })
            setpkgcfg(engine, 'test', Rpk.DEVMODE_REVISION, 'main')

            rv = engine.run()
            self.assertTrue(rv)

            build_dir = os.path.join(engine.opts.build_dir, 'test-main')

            new_file = os.path.join(build_dir, 'new-file.txt')
            self.assertFalse(os.path.exists(new_file))

            another_file = os.path.join(build_dir, 'another-file.txt')
            self.assertFalse(os.path.exists(another_file))

    def test_tool_patch_filter_devmode_custom_filter_enabled(self):
        with prepare_testenv(template='patch-file-valid') as engine:
            # force enable development mode
            with open(engine.opts.ff_devmode, 'w') as f:
                json.dump({
                    'mode': 'custom',
                }, f)

            setpkgcfg(engine, 'test', Rpk.DEVMODE_PATCHES, {
                'custom': '002-another-new-file.patch',
            })
            setpkgcfg(engine, 'test', Rpk.DEVMODE_REVISION, 'main')

            rv = engine.run()
            self.assertTrue(rv)

            build_dir = os.path.join(engine.opts.build_dir, 'test-main')

            new_file = os.path.join(build_dir, 'new-file.txt')
            self.assertFalse(os.path.exists(new_file))

            another_file = os.path.join(build_dir, 'another-file.txt')
            self.assertTrue(os.path.exists(another_file))

    def test_tool_patch_filter_devmode_filter(self):
        with prepare_testenv(template='patch-file-valid') as engine:
            # force enable development mode
            Path(engine.opts.ff_devmode).touch()

            setpkgcfg(engine, 'test', Rpk.DEVMODE_PATCHES, '001-*')
            setpkgcfg(engine, 'test', Rpk.DEVMODE_REVISION, 'main')

            rv = engine.run()
            self.assertTrue(rv)

            build_dir = os.path.join(engine.opts.build_dir, 'test-main')

            new_file = os.path.join(build_dir, 'new-file.txt')
            self.assertTrue(os.path.exists(new_file))

            another_file = os.path.join(build_dir, 'another-file.txt')
            self.assertFalse(os.path.exists(another_file))

    def test_tool_patch_filter_devmode_flag_disabled(self):
        with prepare_testenv(template='patch-file-valid') as engine:
            # force enable development mode
            Path(engine.opts.ff_devmode).touch()

            setpkgcfg(engine, 'test', Rpk.DEVMODE_PATCHES, value=False)
            setpkgcfg(engine, 'test', Rpk.DEVMODE_REVISION, 'main')

            rv = engine.run()
            self.assertTrue(rv)

            build_dir = os.path.join(engine.opts.build_dir, 'test-main')

            new_file = os.path.join(build_dir, 'new-file.txt')
            self.assertFalse(os.path.exists(new_file))

            another_file = os.path.join(build_dir, 'another-file.txt')
            self.assertFalse(os.path.exists(another_file))

    def test_tool_patch_filter_devmode_flag_enabled(self):
        with prepare_testenv(template='patch-file-valid') as engine:
            # force enable development mode
            Path(engine.opts.ff_devmode).touch()

            setpkgcfg(engine, 'test', Rpk.DEVMODE_PATCHES, value=True)
            setpkgcfg(engine, 'test', Rpk.DEVMODE_REVISION, 'main')

            rv = engine.run()
            self.assertTrue(rv)

            build_dir = os.path.join(engine.opts.build_dir, 'test-main')

            new_file = os.path.join(build_dir, 'new-file.txt')
            self.assertTrue(os.path.exists(new_file))

            another_file = os.path.join(build_dir, 'another-file.txt')
            self.assertTrue(os.path.exists(another_file))

    def test_tool_patch_filter_regular_filter_sanity(self):
        with prepare_testenv(template='patch-file-valid') as engine:
            setpkgcfg(engine, 'test', Rpk.IGNORE_PATCHES, 'releng')

            rv = engine.run()
            self.assertTrue(rv)

            build_dir = os.path.join(engine.opts.build_dir, 'test')

            new_file = os.path.join(build_dir, 'new-file.txt')
            self.assertTrue(os.path.exists(new_file))

            another_file = os.path.join(build_dir, 'another-file.txt')
            self.assertTrue(os.path.exists(another_file))

    def test_tool_patch_filter_regular_filter_set(self):
        with prepare_testenv(template='patch-file-valid') as engine:
            setpkgcfg(engine, 'test', Rpk.IGNORE_PATCHES, '001-*')

            rv = engine.run()
            self.assertTrue(rv)

            build_dir = os.path.join(engine.opts.build_dir, 'test')

            new_file = os.path.join(build_dir, 'new-file.txt')
            self.assertFalse(os.path.exists(new_file))

            another_file = os.path.join(build_dir, 'another-file.txt')
            self.assertTrue(os.path.exists(another_file))

    def test_tool_patch_filter_regular_flag_disabled(self):
        with prepare_testenv(template='patch-file-valid') as engine:
            setpkgcfg(engine, 'test', Rpk.IGNORE_PATCHES, value=True)

            rv = engine.run()
            self.assertTrue(rv)

            build_dir = os.path.join(engine.opts.build_dir, 'test')

            new_file = os.path.join(build_dir, 'new-file.txt')
            self.assertFalse(os.path.exists(new_file))

            another_file = os.path.join(build_dir, 'another-file.txt')
            self.assertFalse(os.path.exists(another_file))

    def test_tool_patch_filter_regular_flag_enabled(self):
        with prepare_testenv(template='patch-file-valid') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            build_dir = os.path.join(engine.opts.build_dir, 'test')

            new_file = os.path.join(build_dir, 'new-file.txt')
            self.assertTrue(os.path.exists(new_file))

            another_file = os.path.join(build_dir, 'another-file.txt')
            self.assertTrue(os.path.exists(another_file))
