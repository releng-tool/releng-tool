# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.defs import PythonSetupType
from releng_tool.tool.python import PYTHON
from releng_tool.tool.python import PythonTool
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.log import err
from releng_tool.util.log import warn
from releng_tool.util.string import expand
import os


def build(opts):
    """
    support building python projects

    With provided build options (``RelengBuildOptions``), the build stage will
    be processed.

    Args:
        opts: build options

    Returns:
        ``True`` if the building stage is completed; ``False`` otherwise
    """

    if opts._python_interpreter:
        python_tool = PythonTool(opts._python_interpreter)
    else:
        python_tool = PYTHON

    if not python_tool.exists():
        err('unable to build package; python is not installed')
        return False

    # default environment
    env = {}

    setup_type = opts._python_setup_type
    python_args = []
    python_defs = {}
    python_opts = {}

    if setup_type == PythonSetupType.FLIT:
        # https://flit.pypa.io/en/latest/bootstrap.html
        python_args.extend([
            # flit's wheel module
            '-m', 'flit_core.wheel',
        ])
    elif setup_type == PythonSetupType.HATCH:
        # https://hatch.pypa.io/
        python_args.extend([
            # hatch module
            '-m', 'hatch',
            # no interaction
            '--no-interactive',
            # build action
            'build',
            # build a wheel
            '--target', 'wheel',
        ])
    elif setup_type == PythonSetupType.PDM:
        # https://pdm.fming.dev/
        python_args.extend([
            # pdm module
            '-m', 'pdm',
            # always use releng-tool configured python
            '--ignore-python',
            # build action
            'build',
            # do not use a virtual environment
            '--no-isolation',
            # skip source package building
            '--no-sdist',
        ])

        # never attempt to perform a pdm update check
        env['PDM_CHECK_UPDATE'] = 'false'
    elif setup_type == PythonSetupType.PEP517:
        # https://pypa-build.readthedocs.io/en/latest/
        python_args.extend([
            # build module
            '-m', 'build',
            # do not use a virtual environment
            '--no-isolation',
            # build a wheel
            '--wheel',
        ])
    elif setup_type == PythonSetupType.POETRY:
        # https://python-poetry.org/docs/cli/#build
        python_args.extend([
            # poetry module
            '-m', 'poetry',
            # build action
            'build',
            # no interaction
            '--no-interaction',
        ])
    else:
        if setup_type == PythonSetupType.SETUPTOOLS:
            # check if a project has a `setup.py` helper script; if not,
            # manually load the setuptools module and invoke the setup request
            if not os.path.exists('setup.py'):
                python_args.extend([
                    '-c',
                    'import setuptools; setuptools.setup()',
                ])
        # default, use distutils; generate a warning if a Python setup type
        # has not been configured for a project
        elif setup_type != PythonSetupType.DISTUTILS:
            warn('project does not define a python setup type: {}', opts.name)

        # if not setup script override is defined, use `setup.py`
        if not python_args:
            python_args.append('setup.py')

        python_args.extend([
            # ignore user's pydistutils.cfg
            '--no-user-cfg',
            # invoke the build operation
            'bdist_wheel',
        ])

    # apply package-specific overrides
    if opts.build_defs:
        python_defs.update(expand(opts.build_defs))

    if opts.build_env:
        env.update(expand(opts.build_env))

    if opts.build_opts:
        python_opts.update(expand(opts.build_opts))

    # argument building
    python_args.extend(prepare_definitions(python_defs))
    python_args.extend(prepare_arguments(python_opts))

    if not python_tool.execute(python_args, env=env):
        err('failed to build python project: {}', opts.name)
        return False

    return True
