# -*- coding: utf-8 -*-
# Copyright 2018-2020 releng-tool

from ..util.io import execute
from ..util.log import debug
from ..util.log import err
from ..util.string import is_sequence_not_string
import re
import os

class RelengTool:
    """
    a host tool

    Provides a series of host tools methods to assist in validating the
    existence of a host tool as well as the execution of a host tool.

    Attributes:
        detected: tracking whether or not a tool is available on the host system

    Args:
        tool: the file name of the tool
        exists_args (optional): argument value to check for existence (no-op)
        env_sanitize (optional): environment variables to sanitize
        env_include (optional): environment variables to always include
    """
    detected = {}

    def __init__(self, tool, exists_args=None, env_sanitize=None,
            env_include=None):
        self.include = env_include
        self.sanitize = env_sanitize

        # allow a system to override a host tool path
        override_tool_key = 'RELENG_' + re.sub(r'[^A-Z0-9]', '', tool.upper())
        if override_tool_key in os.environ:
            self.tool = os.environ[override_tool_key]
        else:
            self.tool = tool

        if exists_args is not None:
            self.exists_args = exists_args
        else:
            self.exists_args = ['--version']

    def execute(self, args=None, cwd=None, quiet=False, env=None, poll=False,
            capture=None):
        """
        execute the host tool with the provided arguments (if any)

        Runs the host tool described by ``args`` until completion.

        Args:
            args (optional): the list of arguments for the tool
            cwd (optional): working directory to use
            quiet (optional): whether or not to suppress output
            env (optional): environment variables to include
            poll (optional): force polling stdin/stdout for output data
            capture (optional): list to capture output into

        Returns:
            ``True`` if the execution has completed with no error; ``False`` if
            the execution has failed
        """
        if not self.exists():
            return False

        if args and not is_sequence_not_string(args):
            err('invalid argument type provided into execute (should be list): '
                + str(args))
            return False

        final_env = None
        if self.include or self.sanitize or env:
            final_env = os.environ.copy()
            if self.sanitize:
                for key in self.sanitize:
                    final_env.pop(key, None)
            if self.include:
                final_env.update(self.include)
            if env:
                final_env.update(env)

        final_args = [self.tool]
        if args:
            final_args.extend(args)

        return execute(final_args, cwd=cwd, env=final_env, quiet=quiet,
            critical=False, poll=poll, capture=capture)

    def exists(self):
        """
        return whether or not the host tool exists

        Returns whether or not the tool is available on the host for use.

        Returns:
            ``True``, if the tool exists; ``False`` otherwise
        """
        if self.tool in RelengTool.detected:
            return RelengTool.detected[self.tool]

        if execute([self.tool] + self.exists_args, quiet=True, critical=False):
            debug('{} tool is detected on this system'.format(self.tool))
            RelengTool.detected[self.tool] = True
        else:
            debug('{} tool is not detected on this system'.format(self.tool))
            RelengTool.detected[self.tool] = False

        return RelengTool.detected[self.tool]
