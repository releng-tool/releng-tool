# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

class RelengToolException(Exception):
    """
    base exception for all custom releng-tool exceptions
    """


class RelengToolSilentException(RelengToolException):
    """
    exception to trigger a stop with an error message already printed
    """


class RelengToolInvalidConfigurationScript(RelengToolSilentException):
    """
    exception thrown when a project's configuration file could not be loaded
    """


class RelengToolInvalidConfigurationSettings(RelengToolSilentException):
    """
    exception thrown when a project's configuration file has invalid settings
    """


class RelengToolInvalidOverrideConfigurationScript(RelengToolSilentException):
    """
    exception thrown when a project's override configuration file could
    not be loaded
    """


class RelengToolMissingConfigurationError(RelengToolException):
    """
    exception thrown when missing a project's configuration file
    """
    def __init__(self, path):
        super().__init__(f'''\
missing configuration file

The configuration file cannot be found. Ensure the configuration file exists
in the working directory or the provided root directory:

    {path}
'''.strip())


class RelengToolMissingExecCommand(RelengToolException):
    """
    exception thrown when a missing a command for a package's exec call
    """
    def __init__(self, pkg):
        super().__init__(f'''\
missing package command

A request has been made to execute a command for a package; however, no command
has been provided. Ensure after specifying an exec call that the following
argument defines the command to be executed.

    releng-tool {pkg}-exec "mycmd arg1 arg2"
     (or)
    releng-tool {pkg}-exec -- mycmd arg1 arg2
'''.strip())


class RelengToolMissingPackagesError(RelengToolException):
    """
    exception thrown when a project's configuration does not provide any pkgs
    """
    def __init__(self, path, key):
        super().__init__(f'''\
no defined packages

The configuration file does not have any defined packages. Ensure a package
list exists with the name of packages to be part of the releng process:

    {path}
        {key} = ['liba', 'libb', 'libc']
'''.strip())


class RelengToolMissingVsDevCmdError(RelengToolException):
    """
    exception thrown when a project uses VsDevCmd.bat and it cannot be found
    """
    def __init__(self, status, output):
        super().__init__(f'''\
{status}

The project configuration indicates a requirement for VsDevCmd.bat but the
environment could not be prepared.

    {output}
'''.strip())


class RelengToolOutsidePathError(RelengToolException):
    """
    exception thrown when unexpectedly interacting outside of a path
    """


class RelengToolUnknownAction(RelengToolException):
    """
    raised when an unknown action or package is provided
    """
    def __init__(self, args):
        super().__init__('''\
unknown action or package: {action}{extra}
'''.strip().format(**args))


class RelengToolWarningAsError(RelengToolException):
    """
    exception thrown for a warning being triggered as an error
    """
