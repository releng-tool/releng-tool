# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from io import open  # noqa: A004
from releng_tool.tool import RelengTool
import sys

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

#: executable used to run git commands
GIT_COMMAND = 'git'

#: list of environment keys to filter from a environment dictionary
GIT_SANITIZE_ENV_KEYS = [
    # disable repository location overrides
    'GIT_ALTERNATE_OBJECT_DIRECTORIES',
    'GIT_DIR',
    'GIT_INDEX_FILE',
    'GIT_OBJECT_DIRECTORY',
    'GIT_WORK_TREE',
    # remove the possibility for authenticated prompts
    'GIT_ASKPASS',
    'SSH_ASKPASS',
    # misc
    'GIT_FLUSH',
    # perforce-related options
    'P4AUDIT',
    'P4CLIENT',
    'P4CLIENTPATH',
    'P4CONFIG',
    'P4PORT',
    'P4PASSWD',
]

#: dictionary of environment entries append to the environment dictionary
GIT_EXTEND_ENV = {
    # disable all advice messages
    'GIT_ADVICE': '0',
    # prevent the terminal prompt for ssh clones from being shown
    'GIT_SSH_COMMAND': 'ssh -oBatchMode=yes',
    # prevent the terminal prompt from being shown
    'GIT_TERMINAL_PROMPT': '0',
}


class GitTool(RelengTool):
    """
    git host tool

    Provides addition helper methods for git-based tool interaction.
    """

    def parse_cfg_file(self, target):
        """
        return a configuration parser for a provided git configuration file

        Returns a prepared configuration parser based of a Git configuration
        file provided. In the event that the file cannot be parsed, this call
        will return a ``None`` value.

        Args:
            target: the file to parse

        Returns:
            the parser; ``None`` when a parsing error is detected
        """

        with open(target, mode='r', encoding='utf_8') as f:
            data = '\n'.join(f.readlines())

        return self.parse_cfg_str(data)

    def parse_cfg_str(self, value):
        """
        return a configuration parser for a provided git configuration string

        Returns a prepared configuration parser based of a Git configuration
        value provided. In the event that the value cannot be parsed, this call
        will return a ``None`` value.

        Args:
            value: the value to parse

        Returns:
            the parser; ``None`` when a parsing error is detected
        """

        cfg = configparser.ConfigParser(allow_no_value=True)
        try:
            if sys.version_info >= (3, 0):
                cfg.read_string(value)
            else:
                # strip whitespaces from lines for python 2.7
                value = '\n'.join([line.strip() for line in value.splitlines()])

                fp = StringIO(value)
                cfg.readfp(fp)  # pylint: disable=E1101
        except configparser.Error:
            return None

        return cfg

#: git host tool helper
GIT = GitTool(GIT_COMMAND,
    env_sanitize=GIT_SANITIZE_ENV_KEYS, env_include=GIT_EXTEND_ENV)
