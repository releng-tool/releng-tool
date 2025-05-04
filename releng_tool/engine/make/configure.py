# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.engine.script.configure import configure as configure_script
from releng_tool.tool.make import MAKE
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.log import verbose
from releng_tool.util.string import expand


def configure(opts):
    """
    support configuration for make projects

    With provided configuration options (``RelengConfigureOptions``), the
    configuration stage will be processed.

    Args:
        opts: configuration options

    Returns:
        ``True`` if the configuration stage is completed; ``False`` otherwise
    """

    if not MAKE.exists():
        err('unable to configure package; make is not installed')
        return False

    # If the provided package has not provided any configuration settings,
    # assume that the Make project does not have a configuration event.
    if not opts.conf_defs and not opts._conf_env_pkg and not opts.conf_opts:
        verbose('no configuration settings provided: {}', opts.name)

        # fallback to invoking a configuration script
        return configure_script(opts)

    # definitions
    make_defs = {
    }
    if opts.conf_defs:
        make_defs.update(expand(opts.conf_defs))

    # default options
    make_opts = {
    }
    if opts.conf_opts:
        make_opts.update(expand(opts.conf_opts))

    # argument building
    make_args = [
    ]
    make_args.extend(prepare_definitions(make_defs))
    make_args.extend(prepare_arguments(make_opts))

    if not MAKE.execute(make_args, env=expand(opts.conf_env)):
        err('failed to configure make project: {}', opts.name)
        return False

    return True
