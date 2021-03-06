# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

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
        RelengToolInvalidPackageConfiguration.__init__(self,
'''
package has conflicting configuration values: {pkg_name}
 ({desc})
 (keys: {pkg_key1}, {pkg_key2})
'''.strip().format(**args))

class RelengToolConflictingLocalSrcsPath(RelengToolInvalidPackageConfiguration):
    """
    raised when a detected local sourced package path matches the root directory
    """
    def __init__(self, args):
        RelengToolInvalidPackageConfiguration.__init__(self,
'''
conflicting local-sources package path and root directory: {pkg_name}
 (root: {root})
 (path: {path})
'''.strip().format(**args))

class RelengToolCyclicPackageDependency(RelengToolInvalidPackageConfiguration):
    """
    raised when a cyclic package dependency is detected
    """
    def __init__(self, args):
        RelengToolInvalidPackageConfiguration.__init__(self,
'''
cyclic package dependency detected: {pkg_name}
'''.strip().format(**args))

class RelengToolInvalidPackageKeyValue(RelengToolInvalidPackageConfiguration):
    """
    raised when a package key is using an unsupported value
    """
    def __init__(self, args):
        RelengToolInvalidPackageConfiguration.__init__(self,
'''
package configuration has an invalid value: {pkg_name}
 (key: {pkg_key}, expects: {expected_type})
'''.strip().format(**args))

class RelengToolInvalidPackageScript(RelengToolInvalidPackageConfiguration):
    """
    raised when a package script has an issue loading (e.g. syntax error)
    """
    def __init__(self, args):
        RelengToolInvalidPackageConfiguration.__init__(self,
'''
{traceback}
unable to load package script: {script}
    {description}
'''.strip().format(**args))

class RelengToolMissingPackageScript(RelengToolInvalidPackageConfiguration):
    """
    raised when a package script cannot be found
    """
    def __init__(self, args):
        RelengToolInvalidPackageConfiguration.__init__(self,
'''
unknown package provided: {pkg_name}
 (script) {script}
'''.strip().format(**args))

class RelengToolMissingPackageSite(RelengToolInvalidPackageConfiguration):
    """
    raised when a package site has not been defined with a vcs-type set
    """
    def __init__(self, args):
        RelengToolInvalidPackageConfiguration.__init__(self,
'''
package defines vcs-type ({vcs_type}) but no site: {pkg_name}
 (key: {pkg_key})
'''.strip().format(**args))

class RelengToolMissingPackageVersion(RelengToolInvalidPackageConfiguration):
    """
    raised when a package version has not been defined
    """
    def __init__(self, args):
        RelengToolInvalidPackageConfiguration.__init__(self,
'''
package has no version defined: {pkg_name}
 (missing key: {pkg_key})
'''.strip().format(**args))

class RelengToolUnknownExtractType(RelengToolInvalidPackageConfiguration):
    """
    raised when a package defined an unknown extract type
    """
    def __init__(self, args):
        RelengToolInvalidPackageConfiguration.__init__(self,
'''
unknown extract type value provided
 (package: {pkg_name}, key: {pkg_key})
'''.strip().format(**args))

class RelengToolUnknownInstallType(RelengToolInvalidPackageConfiguration):
    """
    raised when a package defined an unknown install type
    """
    def __init__(self, args):
        RelengToolInvalidPackageConfiguration.__init__(self,
'''
unknown install type value provided
 (package: {pkg_name}, key: {pkg_key})
'''.strip().format(**args))

class RelengToolUnknownPackageType(RelengToolInvalidPackageConfiguration):
    """
    raised when a package defined an unknown package type
    """
    def __init__(self, args):
        RelengToolInvalidPackageConfiguration.__init__(self,
'''
unknown package type value provided
 (package: {pkg_name}, key: {pkg_key})
'''.strip().format(**args))

class RelengToolUnknownVcsType(RelengToolInvalidPackageConfiguration):
    """
    raised when a package defined an unknown vcs type
    """
    def __init__(self, args):
        RelengToolInvalidPackageConfiguration.__init__(self,
'''
unknown vcs type value provided
 (package: {pkg_name}, key: {pkg_key})
'''.strip().format(**args))
