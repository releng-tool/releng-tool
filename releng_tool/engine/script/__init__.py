# -*- coding: utf-8 -*-
# Copyright releng-tool
# SPDX-License-Identifier: BSD-2-Clause

from releng_tool.util.io import opt_file
from releng_tool.util.log import warn
import os


def resolve_remote_script(build_dir, script_name):
    script_filename = '{}-{}'.format('releng-tool', script_name)
    script_base = os.path.join(build_dir, script_filename)
    remote_script, script_exists = opt_file(script_base)

    if not script_exists:
        deprecated_names = [
            'releng',
        ]

        for deprecated_name in deprecated_names:
            alt_script_filename = '{}-{}'.format(deprecated_name, script_name)
            script_base = os.path.join(build_dir, alt_script_filename)
            remote_script, script_exists = opt_file(script_base)
            if os.path.isfile(remote_script):
                warn('using deprecated script {} -- switch '
                     'to {}.rt when possible', os.path.basename(remote_script),
                     script_filename)
                break

    return remote_script, script_exists
