# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from tests import RelengToolTestCase
from tests import prepare_testenv
import json
import os


class TestNoPrefix(RelengToolTestCase):
    def test_no_prefix_global(self):
        with prepare_testenv(template='no-prefix-global') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            self.assertTrue('TEST_BUILD_OUTPUT_DIR' in os.environ)
            test_outdir = os.environ['TEST_BUILD_OUTPUT_DIR']
            results = os.path.join(test_outdir, 'invoke-env.json')
            self.assertTrue(os.path.exists(results))

            with open(results) as f:
                data = json.load(f)

            pkg_keys = [
                'HOST_BIN_DIR',
                'HOST_INCLUDE_DIR',
                'HOST_LIB_DIR',
                'HOST_SHARE_DIR',
                'PREFIXED_HOST_DIR',
                'PREFIXED_STAGING_DIR',
                'PREFIXED_TARGET_DIR',
                'STAGING_BIN_DIR',
                'STAGING_INCLUDE_DIR',
                'STAGING_LIB_DIR',
                'STAGING_SHARE_DIR',
                'TARGET_BIN_DIR',
                'TARGET_INCLUDE_DIR',
                'TARGET_LIB_DIR',
                'TARGET_SHARE_DIR',
            ]
            self.assertTrue(all(x in data for x in pkg_keys))

            # verify the package variables report expected paths with
            # a global empty prefix configured
            self.data = data
            self._verify('HOST_BIN_DIR',         'host',    'bin'    )
            self._verify('HOST_INCLUDE_DIR',     'host',    'include')
            self._verify('HOST_LIB_DIR',         'host',    'lib'    )
            self._verify('HOST_SHARE_DIR',       'host',    'share'  )
            self._verify('PREFIXED_HOST_DIR',    'host'              )
            self._verify('PREFIXED_STAGING_DIR', 'staging'           )
            self._verify('PREFIXED_TARGET_DIR',  'target'            )
            self._verify('STAGING_BIN_DIR',      'staging', 'bin'    )
            self._verify('STAGING_INCLUDE_DIR',  'staging', 'include')
            self._verify('STAGING_LIB_DIR',      'staging', 'lib'    )
            self._verify('STAGING_SHARE_DIR',    'staging', 'share'  )
            self._verify('TARGET_BIN_DIR',       'target',  'bin'    )
            self._verify('TARGET_INCLUDE_DIR',   'target',  'include')
            self._verify('TARGET_LIB_DIR',       'target',  'lib'    )
            self._verify('TARGET_SHARE_DIR',     'target',  'share'  )

    def test_no_prefix_pkg(self):
        with prepare_testenv(template='no-prefix-pkg') as engine:
            rv = engine.run()
            self.assertTrue(rv)

            self.assertTrue('TEST_BUILD_OUTPUT_DIR' in os.environ)
            test_outdir = os.environ['TEST_BUILD_OUTPUT_DIR']
            results = os.path.join(test_outdir, 'invoke-env.json')
            self.assertTrue(os.path.exists(results))

            with open(results) as f:
                data = json.load(f)

            pkg_keys = [
                'HOST_BIN_DIR',
                'HOST_INCLUDE_DIR',
                'HOST_LIB_DIR',
                'HOST_SHARE_DIR',
                'PREFIXED_HOST_DIR',
                'PREFIXED_STAGING_DIR',
                'PREFIXED_TARGET_DIR',
                'STAGING_BIN_DIR',
                'STAGING_INCLUDE_DIR',
                'STAGING_LIB_DIR',
                'STAGING_SHARE_DIR',
                'TARGET_BIN_DIR',
                'TARGET_INCLUDE_DIR',
                'TARGET_LIB_DIR',
                'TARGET_SHARE_DIR',
            ]
            self.assertTrue(all(x in data for x in pkg_keys))

            # verify the package variables report expected paths with
            # a package-specific empty prefix configured
            self.data = data
            self._verify('HOST_BIN_DIR',         'host',    'bin'    )
            self._verify('HOST_INCLUDE_DIR',     'host',    'include')
            self._verify('HOST_LIB_DIR',         'host',    'lib'    )
            self._verify('HOST_SHARE_DIR',       'host',    'share'  )
            self._verify('PREFIXED_HOST_DIR',    'host'              )
            self._verify('PREFIXED_STAGING_DIR', 'staging'           )
            self._verify('PREFIXED_TARGET_DIR',  'target'            )
            self._verify('STAGING_BIN_DIR',      'staging', 'bin'    )
            self._verify('STAGING_INCLUDE_DIR',  'staging', 'include')
            self._verify('STAGING_LIB_DIR',      'staging', 'lib'    )
            self._verify('STAGING_SHARE_DIR',    'staging', 'share'  )
            self._verify('TARGET_BIN_DIR',       'target',  'bin'    )
            self._verify('TARGET_INCLUDE_DIR',   'target',  'include')
            self._verify('TARGET_LIB_DIR',       'target',  'lib'    )
            self._verify('TARGET_SHARE_DIR',     'target',  'share'  )

    def _verify(self, key, container, leaf=None):
        entry_path = self.data[key]
        print('entry_path', entry_path)

        if leaf:
            leaf_path = os.path.basename(entry_path)
            print('leaf_path', leaf_path)
            self.assertEqual(leaf_path, leaf)
            entry_path = os.path.dirname(entry_path)
            print('entry_path2', entry_path)

        container_part = os.path.basename(entry_path)
        print('container_part', container_part)
        self.assertEqual(container_part, container)
