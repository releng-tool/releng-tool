# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from io import open
from releng_tool.tool import RelengTool
from releng_tool.util.log import err
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
    # prevent the terminal prompt from being shown
    'GIT_TERMINAL_PROMPT': '0',
}


class GitTool(RelengTool):
    """
    git host tool

    Provides addition helper methods for git-based tool interaction.
    """

    def extract_submodule_revision(self, git_dir):
        """
        extract a submodule revision

        Attempts to extract the HEAD reference of a submodule based off a
        provided git Git repository. This is to help support processing Git
        submodules which do not have a branch/version explicitly set for module,
        which is required for (at least) recursive submodule processing.

        Args:
            git_dir: the git repository

        Returns:
            the revision; ``None`` when a revision cannot be extracted
        """

        rv, ref = self.execute_rv('--git-dir=' + git_dir, 'show-ref', '--head')
        if rv != 0:
            err('failed to extract a submodule revision')
            return None

        # a `--head` fetch may fetch more than one reference; extract the first
        # entry and remove any known ref prefix from it
        revision = ref.split(None, 2)[1]
        if revision.startswith('refs/heads/'):
            revision = revision[len('refs/heads/'):]
        elif revision.startswith('refs/remotes/origin/'):
            revision = revision[len('refs/remotes/origin/'):]
        return revision

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
