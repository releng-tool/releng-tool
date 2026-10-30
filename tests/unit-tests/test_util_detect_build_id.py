# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.util.ci_build_id import detect_build_id
from tests import RelengToolTestCase
import os


class TestUtilDetectBuildId(RelengToolTestCase):
    def setUp(self):
        os.environ.clear()

    def test_util_detect_build_id_none(self):
        raw_build_key, raw_build_id = detect_build_id()
        self.assertIsNone(raw_build_key)
        self.assertIsNone(raw_build_id)

    def test_util_detect_build_id_standard(self):
        os.environ['RELENG_BUILD_ID'] = '12345'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertEqual(raw_build_key, 'RELENG_BUILD_ID')
        self.assertEqual(raw_build_id, '12345')

    def test_util_detect_build_id_vendor_ignored(self):
        os.environ['RELENG_BUILD_ID_NO_IMPLICIT'] = '1'
        os.environ['JENKINS_URL'] = '1'
        os.environ['BUILD_NUMBER'] = '90678'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertIsNone(raw_build_key)
        self.assertIsNone(raw_build_id)

    def test_util_detect_build_id_vendor_aws_codebuild_missing(self):
        os.environ['CODEBUILD_BUILD_NUMBER'] = '23451'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertIsNone(raw_build_key)
        self.assertIsNone(raw_build_id)

    def test_util_detect_build_id_vendor_aws_codebuild_set(self):
        os.environ['CODEBUILD_BUILD_ID'] = '1'
        os.environ['CODEBUILD_BUILD_NUMBER'] = '23451'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertEqual(raw_build_key, 'CODEBUILD_BUILD_NUMBER')
        self.assertEqual(raw_build_id, '23451')

    def test_util_detect_build_id_vendor_azure_pipelines_missing(self):
        os.environ['BUILD_BUILDID'] = '34512'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertIsNone(raw_build_key)
        self.assertIsNone(raw_build_id)

    def test_util_detect_build_id_vendor_azure_pipelines_set(self):
        os.environ['TF_BUILD'] = '1'
        os.environ['BUILD_BUILDID'] = '34512'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertEqual(raw_build_key, 'BUILD_BUILDID')
        self.assertEqual(raw_build_id, '34512')

    def test_util_detect_build_id_vendor_bitbucket_pipelines_missing(self):
        os.environ['BITBUCKET_BUILD_NUMBER'] = '45123'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertIsNone(raw_build_key)
        self.assertIsNone(raw_build_id)

    def test_util_detect_build_id_vendor_bitbucket_pipelines_set(self):
        os.environ['CI'] = '1'
        os.environ['BITBUCKET_BUILD_NUMBER'] = '45123'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertEqual(raw_build_key, 'BITBUCKET_BUILD_NUMBER')
        self.assertEqual(raw_build_id, '45123')

    def test_util_detect_build_id_vendor_circleci_missing(self):
        os.environ['CIRCLE_BUILD_NUM'] = '51234'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertIsNone(raw_build_key)
        self.assertIsNone(raw_build_id)

    def test_util_detect_build_id_vendor_circleci_set(self):
        os.environ['CIRCLECI'] = '1'
        os.environ['CIRCLE_BUILD_NUM'] = '51234'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertEqual(raw_build_key, 'CIRCLE_BUILD_NUM')
        self.assertEqual(raw_build_id, '51234')

    def test_util_detect_build_id_vendor_forgejo_missing(self):
        os.environ['FORGEJO_RUN_ID'] = '67890'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertIsNone(raw_build_key)
        self.assertIsNone(raw_build_id)

    def test_util_detect_build_id_vendor_forgejo_set(self):
        os.environ['FORGEJO_ACTIONS'] = '1'
        os.environ['FORGEJO_RUN_ID'] = '67890'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertEqual(raw_build_key, 'FORGEJO_RUN_ID')
        self.assertEqual(raw_build_id, '67890')

    def test_util_detect_build_id_vendor_github_missing(self):
        os.environ['GITHUB_RUN_ID'] = '78906'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertIsNone(raw_build_key)
        self.assertIsNone(raw_build_id)

    def test_util_detect_build_id_vendor_github_set(self):
        os.environ['GITHUB_ACTIONS'] = '1'
        os.environ['GITHUB_RUN_ID'] = '78906'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertEqual(raw_build_key, 'GITHUB_RUN_ID')
        self.assertEqual(raw_build_id, '78906')

    def test_util_detect_build_id_vendor_gitlab_missing(self):
        os.environ['CI_PIPELINE_ID'] = '89067'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertIsNone(raw_build_key)
        self.assertIsNone(raw_build_id)

    def test_util_detect_build_id_vendor_gitlab_set(self):
        os.environ['GITLAB_CI'] = '1'
        os.environ['CI_PIPELINE_ID'] = '89067'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertEqual(raw_build_key, 'CI_PIPELINE_ID')
        self.assertEqual(raw_build_id, '89067')

    def test_util_detect_build_id_vendor_jenkins_missing(self):
        os.environ['BUILD_NUMBER'] = '90678'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertIsNone(raw_build_key)
        self.assertIsNone(raw_build_id)

    def test_util_detect_build_id_vendor_jenkins_set(self):
        os.environ['JENKINS_URL'] = '1'
        os.environ['BUILD_NUMBER'] = '90678'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertEqual(raw_build_key, 'BUILD_NUMBER')
        self.assertEqual(raw_build_id, '90678')

    def test_util_detect_build_id_vendor_travis_ci_missing(self):
        os.environ['TRAVIS_BUILD_ID'] = '06789'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertIsNone(raw_build_key)
        self.assertIsNone(raw_build_id)

    def test_util_detect_build_id_vendor_travis_ci_set(self):
        os.environ['TRAVIS'] = '1'
        os.environ['TRAVIS_BUILD_ID'] = '06789'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertEqual(raw_build_key, 'TRAVIS_BUILD_ID')
        self.assertEqual(raw_build_id, '06789')

    def test_util_detect_build_id_vendor_woodpecker_missing(self):
        os.environ['CI_PIPELINE_NUMBER'] = '112233'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertIsNone(raw_build_key)
        self.assertIsNone(raw_build_id)

    def test_util_detect_build_id_vendor_woodpecker_set(self):
        os.environ['CI'] = '1'
        os.environ['CI_PIPELINE_NUMBER'] = '112233'

        raw_build_key, raw_build_id = detect_build_id()
        self.assertEqual(raw_build_key, 'CI_PIPELINE_NUMBER')
        self.assertEqual(raw_build_id, '112233')
