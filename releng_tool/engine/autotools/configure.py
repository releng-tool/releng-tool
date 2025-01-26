# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.autoreconf import AUTORECONF
from releng_tool.util.io import execute
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.log import verbose
from releng_tool.util.string import expand


def configure(opts):
    """
    support configuration for autotools projects

    With provided configuration options (``RelengConfigureOptions``), the
    configuration stage will be processed.

    Args:
        opts: configuration options

    Returns:
        ``True`` if the configuration stage is completed; ``False`` otherwise
    """

    # check if autoreconf
    if opts._autotools_autoreconf:
        verbose('configured to run autoreconf')
        if not AUTORECONF.exists():
            err('unable to configure package; autoreconf is not installed')
            return False

        if not AUTORECONF.execute(['--verbose']):
            err('failed to prepare autotools project (autoreconf): {}',
                opts.name)
            return False

    # definitions
    autotools_defs = {
        '--prefix': opts.prefix,
        '--exec-prefix': opts.prefix,
    }
    if opts.conf_defs:
        autotools_defs.update(expand(opts.conf_defs))

    # default options
    autotools_opts = {
    }
    if opts.conf_opts:
        autotools_opts.update(expand(opts.conf_opts))

    # argument building
    autotools_args = [
    ]
    autotools_args.extend(prepare_definitions(autotools_defs))
    autotools_args.extend(prepare_arguments(autotools_opts))

    if not execute(['./configure', *autotools_args],
            env_update=expand(opts.conf_env), critical=False):
        err('failed to prepare autotools project (configure): {}', opts.name)
        return False

    return True
