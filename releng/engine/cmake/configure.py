#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018 releng-tool

from ...defs import PackageInstallType
from ...tool.cmake import *
from ...util.log import *
from ...util.string import expand as EXP
from os.path import join

def configure(opts):
    """
    support configuration for cmake projects

    With provided configuration options (``RelengConfigureOptions``), the
    configuration stage will be processed.

    Args:
        opts: configuration options

    Returns:
        ``True`` if the configuration stage is completed; ``False`` otherwise
    """

    if not CMAKE.exists():
        err('unable to configure package; cmake is not installed')
        return False

    prefix = opts.prefix
    if opts._install_type == PackageInstallType.HOST:
        include_loc = join(opts.host_dir, prefix, 'include')
        library_loc = join(opts.host_dir, prefix, 'lib')
        prefix_loc = join(opts.host_dir, prefix)
    else:
        include_loc = ('"' +
            join(opts.staging_dir, prefix, 'include') + ';' +
            join(opts.target_dir, prefix, 'include') + '"')
        library_loc = ('"' +
            join(opts.staging_dir, prefix, 'lib') + ';' +
            join(opts.target_dir, prefix, 'lib') + '"')
        prefix_loc = ('"' +
            join(opts.staging_dir, prefix) + ';' +
            join(opts.target_dir, prefix) + '"')

    # default options
    cmakeOpts = {
        # build RelWithDebInfo (when using single configuration projects
        '-DCMAKE_BUILD_TYPE': 'RelWithDebInfo',
        '-DCMAKE_INCLUDE_PATH': include_loc,
        '-DCMAKE_INSTALL_PREFIX': prefix,
        '-DCMAKE_LIBRARY_PATH': library_loc,
        '-DCMAKE_PREFIX_PATH': prefix_loc,
    }

    # apply package-specific options
    if opts._cmake_conf_opts:
        cmakeOpts.update(EXP(opts._cmake_conf_opts))

    # argument building
    cmakeArgs = [
        '--no-warn-unused-cli', # suppress common options if not used in project
    ]

    for key, val in cmakeOpts.items():
        if val:
            cmakeArgs.append('{}={}'.format(key, val))
        else:
            cmakeArgs.append(key)

    # output directory
    cmakeArgs.append(opts.build_output_dir)

    if not CMAKE.execute(cmakeArgs, env=EXP(opts._cmake_conf_env)):
        err('failed to prepare cmake project: {}', opts.name)
        return False

    return True
