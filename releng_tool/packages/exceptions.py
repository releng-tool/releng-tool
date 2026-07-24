# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.exceptions import RelengToolException


class RelengToolInvalidPackageConfiguration(RelengToolException):
    """
    exception thrown when a package configuration has an issue
    """


class RelengToolConflictingConfiguration(RelengToolInvalidPackageConfiguration):
    """
    raised when two package configuration values conflict with each other
    """
    def __init__(self, args):
        super().__init__('''\
package has conflicting configuration values: {pkg_name}
 ({desc})
 (keys: {pkg_key1}, {pkg_key2})
'''.strip().format(**args))


class RelengToolConflictingLocalSrcsPath(RelengToolInvalidPackageConfiguration):
    """
    raised when a detected local sourced package path matches the root directory
    """
    def __init__(self, args):
        super().__init__('''\
conflicting local-sources package path and root directory: {pkg_name}
 (root: {root})
 (path: {path})
'''.strip().format(**args))


class RelengToolCyclicPackageDependency(RelengToolInvalidPackageConfiguration):
    """
    raised when a cyclic package dependency is detected
    """
    def __init__(self, args):
        super().__init__('''\
cyclic package dependency detected: {pkg_name}
'''.strip().format(**args))


class RelengToolInvalidPackageKeyValue(RelengToolInvalidPackageConfiguration):
    """
    raised when a package key is using an unsupported value
    """
    def __init__(self, args):
        super().__init__('''\
package configuration has an invalid value: {pkg_name}
 (key: {pkg_key}, expects: {expected_type})
'''.strip().format(**args))


class RelengToolMissingPackageRevision(RelengToolInvalidPackageConfiguration):
    """
    raised when a required package revision has not been defined
    """
    def __init__(self, args):
        super().__init__('''\
package defines vcs-type ({vcs_type}) but no version/revision: {pkg_name}
 (missing either key: {pkg_key1}, {pkg_key2})
'''.strip().format(**args))


class RelengToolInvalidPackageScript(RelengToolInvalidPackageConfiguration):
    """
    raised when a package script has an issue loading (e.g. syntax error)
    """
    def __init__(self, args):
        super().__init__('''\
{traceback}
unable to load package script: {script}
    {description}
'''.strip().format(**args))


class RelengToolMissingPackageScript(RelengToolInvalidPackageConfiguration):
    """
    raised when a package script cannot be found
    """
    def __init__(self, args):
        super().__init__('''\
unknown package provided: {pkg_name}
'''.strip().format(**args))


class RelengToolMissingPackageSite(RelengToolInvalidPackageConfiguration):
    """
    raised when a package site has not been defined with a vcs-type set
    """
    def __init__(self, args):
        super().__init__('''\
package defines vcs-type ({vcs_type}) but no site: {pkg_name}
 (key: {pkg_key})
'''.strip().format(**args))


class RelengToolPathPackageTraversal(RelengToolInvalidPackageConfiguration):
    """
    raised when a path traversal configuration is detected
    """
    def __init__(self, args):
        super().__init__('''\
package defines a path traversal: {pkg_name}
 (key: {pkg_key})
'''.strip().format(**args))


class RelengToolUnknownExtractType(RelengToolInvalidPackageConfiguration):
    """
    raised when a package defined an unknown extract type
    """
    def __init__(self, args):
        super().__init__('''\
unknown extract type value provided
 (package: {pkg_name}, key: {pkg_key})
'''.strip().format(**args))


class RelengToolUnknownInstallType(RelengToolInvalidPackageConfiguration):
    """
    raised when a package defined an unknown install type
    """
    def __init__(self, args):
        super().__init__('''\
unknown install type value provided
 (package: {pkg_name}, key: {pkg_key})
'''.strip().format(**args))


class RelengToolUnknownPackageType(RelengToolInvalidPackageConfiguration):
    """
    raised when a package defined an unknown package type
    """
    def __init__(self, args):
        super().__init__('''\
unknown package type value provided
 (package: {pkg_name}, key: {pkg_key})
'''.strip().format(**args))


class RelengToolUnknownPythonSetupType(RelengToolInvalidPackageConfiguration):
    """
    raised when a package defined an unknown python setup type
    """
    def __init__(self, args):
        super().__init__('''\
unknown python setup type value provided
 (package: {pkg_name}, key: {pkg_key})
'''.strip().format(**args))


class RelengToolUnknownVcsType(RelengToolInvalidPackageConfiguration):
    """
    raised when a package defined an unknown vcs type
    """
    def __init__(self, args):
        super().__init__('''\
unknown vcs type value provided
 (package: {pkg_name}, key: {pkg_key})
'''.strip().format(**args))


class RelengToolStageFailure(RelengToolException):
    """
    exception thrown when a stage event has an issue
    """


class RelengToolBootstrapStageFailure(RelengToolStageFailure):
    """
    exception thrown when a boostrap stage event has an issue
    """


class RelengToolBuildStageFailure(RelengToolStageFailure):
    """
    exception thrown when a build stage event has an issue
    """


class RelengToolConfigurationStageFailure(RelengToolStageFailure):
    """
    exception thrown when a configuration stage event has an issue
    """


class RelengToolExecStageFailure(RelengToolStageFailure):
    """
    exception thrown when an execute-request event has an issue
    """


class RelengToolExtractionStageFailure(RelengToolStageFailure):
    """
    exception thrown when an extraction stage event has an issue
    """


class RelengToolFetchPostStageFailure(RelengToolStageFailure):
    """
    exception thrown when an fetch (post) stage event has an issue
    """


class RelengToolInstallStageFailure(RelengToolStageFailure):
    """
    exception thrown when an install stage event has an issue
    """


class RelengToolLicenseStageFailure(RelengToolStageFailure):
    """
    exception thrown when a license stage event has an issue
    """


class RelengToolPatchStageFailure(RelengToolStageFailure):
    """
    exception thrown when a patch stage event has an issue
    """


class RelengToolPostStageFailure(RelengToolStageFailure):
    """
    exception thrown when a post stage event has an issue
    """
