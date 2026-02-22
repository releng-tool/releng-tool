# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool.waf import WAF
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.string import expand


def build(opts):
    """
    support building waf projects

    With provided build options (``RelengBuildOptions``), the build stage will
    be processed.

    Args:
        opts: build options

    Returns:
        ``True`` if the building stage is completed; ``False`` otherwise
    """

    if not WAF.exists():
        err('unable to build package; waf is not installed')
        return False

    # definitions
    waf_defs = {
    }
    if opts.build_defs:
        waf_defs.update(expand(opts.build_defs))

    # default options
    waf_opts = {
    }
    if opts.build_opts:
        waf_opts.update(expand(opts.build_opts))

    # argument building
    waf_args = [
        'build',
    ]
    waf_args.extend(prepare_definitions(waf_defs))
    waf_args.extend(prepare_arguments(waf_opts))

    if opts.jobs > 1:
        waf_args.append('--jobs')
        waf_args.append(str(opts.jobs))

    if not WAF.execute(waf_args, env=expand(opts.build_env)):
        err('failed to build waf project: {}', opts.name)
        return False

    return True
