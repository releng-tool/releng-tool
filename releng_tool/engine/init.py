# -*- coding: utf-8 -*-
# Copyright 2020-2021 releng-tool

from releng_tool.util.io import ensure_dir_exists
from releng_tool.util.log import err
from releng_tool.util.log import log
from releng_tool.util.log import verbose
from releng_tool.util.log import warn
import os


def initialize_sample(opts):
    """
    initialize a sample project

    Generates a sample provided in the root directory to help new users or new
    project get started.

    Args:
        opts: options for this run

    Returns:
        ``True`` if the sample project could be initialized; ``False`` if an
        issue has occurred generating the sample project
    """

    root_dir = opts.root_dir

    if not ensure_dir_exists(root_dir):
        return False

    if os.listdir(root_dir):
        err('unable to initialize sample project is non-empty directory')
        return False

    sample_dir = os.path.join(root_dir, 'package', 'sample')

    success = True
    if ensure_dir_exists(sample_dir):
        # sample project
        sample_defs = os.path.join(root_dir, 'package', 'sample', 'sample')
        try:
            with open(sample_defs, 'w') as f:
                f.write('''\
#!/usr/bin/env python
# -*- coding: utf-8 -*-

SAMPLE_DEPENDENCIES = []
SAMPLE_LICENSE = ['<license name>']
SAMPLE_LICENSE_FILES = ['<license file>']
SAMPLE_SITE = '<location for sources>'
SAMPLE_TYPE = '<package-type>'
SAMPLE_VERSION = '<package-version>'
''')

            verbose('written sample file')
        except IOError as e:
            err('unable to generate a sample file')
            verbose(str(e))
            success = False
    else:
        success = False

    # .gitignore
    try:
        project_gitignore = os.path.join(root_dir, '.gitignore')  # (assumption)
        with open(project_gitignore, 'w') as f:
            f.write('''\
# releng-tool
/cache/
/dl/
/output/
.releng-flag-*
''')

        verbose('written .gitignore file')
    except IOError as e:
        err('unable to generate a .gitignore file')
        verbose(str(e))
        success = False

    # releng project
    try:
        project_defs = os.path.join(root_dir, 'releng')
        with open(project_defs, 'w') as f:
            f.write('''\
#!/usr/bin/env python
# -*- coding: utf-8 -*-

packages = [
    'sample',
]
''')

        verbose('written releng file')
    except IOError as e:
        err('unable to generate a releng file')
        verbose(str(e))
        success = False

    if success:
        log('initialized empty releng-tool project')
    else:
        warn('partially initialized a releng-tool project')
    return success
