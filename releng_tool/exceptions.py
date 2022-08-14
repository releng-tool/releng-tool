# -*- coding: utf-8 -*-
# Copyright 2021-2022 releng-tool

"""
base exception for all custom releng-tool exceptions
"""
class RelengToolException(Exception):
    pass

"""
exception thrown when missing a project's configuration file
"""
class RelengToolMissingConfigurationError(RelengToolException):
    def __init__(self, path):
        RelengToolException.__init__(self, '''\
missing configuration file

The configuration file cannot be found. Ensure the configuration file exists
in the working directory or the provided root directory:

    {}
'''.format(path))

"""
exception thrown when a missing a command for a package's exec call
"""
class RelengToolMissingExecCommand(RelengToolException):
    def __init__(self, pkg):
        RelengToolException.__init__(self, '''\
missing package command

A request has been made to execute a command for a package; however, no command
has been provided. Ensure after specifying an exec call that the following
argument defines the command to be executed.

    releng-tool {}-exec "mycmd arg1 arg2"
'''.format(pkg))

"""
exception thrown when a project's configuration does not provide any packages
"""
class RelengToolMissingPackagesError(RelengToolException):
    def __init__(self, path, key):
        RelengToolException.__init__(self, '''\
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
