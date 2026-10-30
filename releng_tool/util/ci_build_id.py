# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

import os

# map of environment variables to hint if a build identifier is provided
#
# This map defines a list of keys, which if a key is in the environment, it
# hints that there may be an applicable environment value that may suggest
# a build identifier for a run. For a given key, this map has a list of values
# per key that can be check against to if an environment variable exists
# holding a build identifier.
#
# For example, the existence of `JENKINS_URL` suggests we are running in a
# Jenkins CI context. If detected, we will then check if `BUILD_NUMBER` exists.
# If so, we will try to parse the value of `BUILD_NUMBER` as a numerical build
# identifier which can be used in a releng-tool run.
BUILD_ID_MAP = {
    'CODEBUILD_BUILD_ID': [
        'CODEBUILD_BUILD_NUMBER', # AWS CodeBuild
    ],
    'TF_BUILD': [
        'BUILD_BUILDID', # Azure Pipelines
    ],
    'CI': [
        'BITBUCKET_BUILD_NUMBER', # Bitbucket Pipelines
        'CI_PIPELINE_NUMBER', # Woodpecker
    ],
    'CIRCLECI': [
        'CIRCLE_BUILD_NUM', # CircleCI
    ],
    'FORGEJO_ACTIONS': [
        'FORGEJO_RUN_ID', # Forgejo
    ],
    'GITHUB_ACTIONS': [
        'GITHUB_RUN_ID', # GitHub
    ],
    'GITLAB_CI': [
        'CI_PIPELINE_ID', # Forgejo
    ],
    'JENKINS_URL': [
        'BUILD_NUMBER', # Jenkins
    ],
    'TRAVIS': [
        'TRAVIS_BUILD_ID', # Travis CI
    ],
}


def detect_build_id() -> tuple[str | None, str | None]:
    """
    attempt to detect a build identifier from the environment

    This call is used to detect a build identifier for a run from the
    configured environment. This is typically an integer value set via
    `RELENG_BUILD_ID`. However, if not set, populate CI environment variables
    will be checked. If a given CI vendor is detected, this call will return
    the raw identifier value set.

    Note that this call only returns a raw representation of an identifier
    that should be an integer value. However, the value must be parsed and
    validated.

    Returns:
        tuple of the environment key used and the environment value
    """

    raw_build_key = None
    raw_build_id = None

    # check for a build identifier set from our releng-tool key
    if 'RELENG_BUILD_ID' in os.environ:
        raw_build_key = 'RELENG_BUILD_ID'
        raw_build_id = os.environ['RELENG_BUILD_ID']
    elif 'RELENG_BUILD_ID_NO_IMPLICIT' in os.environ:
        # ignore any implicit checks if flagged not to check
        pass
    else:
        # otherwise, we will check against populate CI-related tools
        for ci_type, build_keys in BUILD_ID_MAP.items():
            # check if operating in a possible ci context
            if ci_type in os.environ:
                # if we believe we might be in a specific ci context,
                # check if we have a respective build identifier variable
                # set; if so, use it
                for build_key in build_keys:
                    if build_key in os.environ:
                        raw_build_key = build_key
                        raw_build_id = os.environ[build_key]
                        break

                if raw_build_id:
                    break

    return raw_build_key, raw_build_id
