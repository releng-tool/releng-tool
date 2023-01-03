# -*- coding: utf-8 -*-
# Copyright 2021-2022 releng-tool


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
        super(RelengToolMissingConfigurationError, self).__init__('''\
missing configuration file

The configuration file cannot be found. Ensure the configuration file exists
in the working directory or the provided root directory:

    {}
'''.format(path))


class RelengToolMissingExecCommand(RelengToolException):
    """
    exception thrown when a missing a command for a package's exec call
    """
    def __init__(self, pkg):
        super(RelengToolMissingExecCommand, self).__init__('''\
missing package command

A request has been made to execute a command for a package; however, no command
has been provided. Ensure after specifying an exec call that the following
argument defines the command to be executed.

    releng-tool {}-exec "mycmd arg1 arg2"
'''.format(pkg))


class RelengToolMissingPackagesError(RelengToolException):
    """
    exception thrown when a project's configuration does not provide any pkgs
    """
    def __init__(self, path, key):
        super(RelengToolMissingPackagesError, self).__init__('''\
no defined packages

The configuration file does not have any defined packages. Ensure a package
list exists with the name of packages to be part of the releng process:

    {}
        {} = ['liba', 'libb', 'libc']
'''.format(path, key))


class RelengToolWarningAsError(RelengToolException):
    """
    exception thrown for a warning being triggered as an error
    """
