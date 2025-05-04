# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.engine.script.configure import configure as configure_script
from releng_tool.tool.scons import SCONS
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.log import verbose
from releng_tool.util.string import expand


def configure(opts):
    """
    support configuration for scons projects

    With provided configuration options (``RelengConfigureOptions``), the
    configuration stage will be processed.

    Args:
        opts: configuration options

    Returns:
        ``True`` if the configuration stage is completed; ``False`` otherwise
    """

    if not SCONS.exists():
        err('unable to configure package; scons is not installed')
        return False

    # If the provided package has not provided any configuration settings,
    # assume that the scons project does not have a configuration event.
    if not opts.conf_defs and not opts._conf_env_pkg and not opts.conf_opts:
        verbose('no configuration options provided: {}', opts.name)

        # fallback to invoking a configuration script
        return configure_script(opts)

    # definitions
    scons_defs = {
    }
    if opts.conf_defs:
        scons_defs.update(expand(opts.conf_defs))

    # default options
    scons_opts = {
        # default quiet
        '-Q': '',
    }
    if opts.conf_opts:
        scons_opts.update(expand(opts.conf_opts))

    # argument building
    scons_args = [
    ]
    scons_args.extend(prepare_definitions(scons_defs))
    scons_args.extend(prepare_arguments(scons_opts))

    if not SCONS.execute(scons_args, env=expand(opts.conf_env)):
        err('failed to configure scons project: {}', opts.name)
        return False

    return True
