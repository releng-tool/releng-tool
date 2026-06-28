# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolReleaseCheckError
from tests import RelengToolTestCase
from tests import copy_template
from tests import prepare_testenv
from tests import prepare_workdir as workdir
import os


class TestReleaseChecks(RelengToolTestCase):
    def test_relchecks_development_mode(self):
        with workdir() as test_dir:
            root_dir = os.path.join(test_dir, 'root')

            config = {
                'root_dir': root_dir,
            }

            copy_template('minimal', root_dir)

            # prepare development mode
            init_config = dict(config)
            init_config.update({
                'development': True,
            })

            with prepare_testenv(config=init_config) as engine:
                rv = engine.run()
                self.assertTrue(rv)
                self.assertTrue(os.path.exists(engine.opts.ff_devmode))

            # flag release mode and verify the engine fails to run
            config['release'] = True

            with prepare_testenv(config=config) as engine:
                with self.assertRaises(RelengToolReleaseCheckError):
                    engine.run()

    def test_relchecks_force_revision(self):
        config = {
            'injected_kv': {
                'MINIMAL_FORCE_REVISION': '7.8.9',
            },
            'release': True,
        }

        with prepare_testenv(config=config, template='minimal') as engine:
            with self.assertRaises(RelengToolReleaseCheckError):
                engine.run()

    def test_relchecks_global_action(self):
        config = {
            'action': 'extract',
            'release': True,
        }

        with prepare_testenv(config=config, template='minimal') as engine:
            with self.assertRaises(RelengToolReleaseCheckError):
                engine.run()

    def test_relchecks_local_sources(self):
        with workdir() as test_dir:
            root_dir = os.path.join(test_dir, 'root')

            config = {
                'root_dir': root_dir,
            }

            copy_template('minimal', root_dir)

            # prepare local sources mode
            init_config = dict(config)
            init_config.update({
                'local_sources': [
                    # --local-sources set with no paths
                    None,
                ],
            })

            with prepare_testenv(config=init_config) as engine:
                rv = engine.run()
                self.assertTrue(rv)
                self.assertTrue(os.path.exists(engine.opts.ff_local_srcs))

            # flag release mode and verify the engine fails to run
            config['release'] = True

            with prepare_testenv(config=config) as engine:
                with self.assertRaises(RelengToolReleaseCheckError):
                    engine.run()

    def test_relchecks_package_action(self):
        config = {
            'action': 'minimal-build',
            'release': True,
        }

        with prepare_testenv(config=config, template='minimal') as engine:
            with self.assertRaises(RelengToolReleaseCheckError):
                engine.run()
