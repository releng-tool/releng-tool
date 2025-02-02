# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.defs import PythonSetupType
from releng_tool.tool.python import PYTHON
from releng_tool.tool.python import PYTHON_EXTEND_ENV
from releng_tool.tool.python import PythonTool
from releng_tool.util.io import generate_temp_dir
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.io_move import path_move
from releng_tool.util.log import debug
from releng_tool.util.log import err
from releng_tool.util.string import expand
import os


def install(opts):
    """
    support installation python projects

    With provided installation options (``RelengInstallOptions``), the
    installation stage will be processed.

    Args:
        opts: installation options

    Returns:
        ``True`` if the installation stage is completed; ``False`` otherwise
    """

    if opts._python_interpreter:
        python_tool = PythonTool(opts._python_interpreter,
            env_include=PYTHON_EXTEND_ENV)
    else:
        python_tool = PYTHON

    if not python_tool.exists():
        err('unable to install package; python is not installed')
        return False

    # default environment
    path0 = python_tool.path(sysroot=opts.host_dir, prefix=opts.prefix)
    path1 = python_tool.path(sysroot=opts.staging_dir, prefix=opts.prefix)
    path2 = python_tool.path(sysroot=opts.target_dir, prefix=opts.prefix)
    env = {
        'PYTHONPATH': path0 + os.pathsep + path1 + os.pathsep + path2,
    }

    setup_type = opts._python_setup_type
    use_installer = opts._python_use_installer
    python_args = []
    python_defs = {}
    python_opts = {}

    if setup_type == PythonSetupType.PDM:
        # never attempt to perform a pdm update check
        env['PDM_CHECK_UPDATE'] = 'false'

    # parameter used to configure where the package will be installed
    python_root_param = '--root'

    # whether to install packages in an interim folder when trying to install
    # for an empty prefix that the installer does not support
    python_empty_prefix_tweak = False

    installer_types = [
        PythonSetupType.FLIT,
        PythonSetupType.HATCH,
        PythonSetupType.PDM,
        PythonSetupType.PEP517,
        PythonSetupType.POETRY,
    ]

    if setup_type in installer_types or use_installer:
        container_dir = Path('dist')
        debug('search for whl package inside "{}": {}',
            container_dir, opts.name)

        # find the built wheel package under `dist/` and append it to the
        # installer
        whl_package = None

        if container_dir.is_dir():
            for file in os.listdir(container_dir):
                if file.endswith('.whl'):
                    whl_package = file
                    debug(f'found a whl package for {opts.name}: {whl_package}')
                    break

        if not whl_package:
            err('failed to find generated wheel package: {}', opts.name)
            return False

        # https://installer.readthedocs.io/en/stable/cli/installer/
        python_args.extend([
            # installer module
            '-m', 'installer',
            # provide the package to install
            os.path.join(container_dir, whl_package),
        ])

        python_root_param = '--destdir'

        # avoid building pyc files for non-host packages
        if opts.install_type != 'host':
            python_opts['--no-compile-bytecode'] = ''
    else:
        if setup_type == PythonSetupType.SETUPTOOLS:
            # check if a project has a `setup.py` helper script; if not,
            # manually load the setuptools module and invoke the setup request
            if not os.path.exists('setup.py'):
                python_args.extend([
                    '-c',
                    'import setuptools; setuptools.setup()',
                ])

        # if not setup script override is defined, use `setup.py`
        if not python_args:
            python_args.append('setup.py')

        python_args.extend([
            # ignore user's pydistutils.cfg
            '--no-user-cfg',
            # invoke the build operation
            'install',
        ])

        # do not apply a prefix if the value is "empty"/(root path) since a
        # setup.py invoke may ignore provided `--root` value or `--prefix`
        # value; apply if it is set; otherwise flag for manipulation
        python_empty_prefix_tweak = True
        if opts.prefix and opts.prefix != os.sep:
            python_defs['--prefix'] = opts.prefix

        # avoid building pyc files for non-host packages
        if opts.install_type != 'host':
            python_opts['--no-compile'] = ''

        # configure as a single-version externally-managed package for older
        # setuptools which may not explicitly set this option with the root
        # argument
        if setup_type == PythonSetupType.SETUPTOOLS:
            python_args.append('--single-version-externally-managed')

    # apply package-specific overrides
    if opts.install_defs:
        python_defs.update(expand(opts.install_defs))

    if opts.install_env:
        env.update(expand(opts.install_env))

    if opts.install_opts:
        python_opts.update(expand(opts.install_opts))

    # argument building
    python_args.extend(prepare_definitions(python_defs))
    python_args.extend(prepare_arguments(python_opts))

    # install to target destination(s)
    #
    # If the package already defines a root path, use it over any other
    # configured destination directories.
    if python_root_param in python_opts:
        if not python_tool.execute(python_args, env=env):
            err('failed to install python project: {}', opts.name)
            return False
    else:
        # install to each destination
        for dest_dir in opts.dest_dirs:
            if python_empty_prefix_tweak and '--prefix' not in python_defs:
                # for empty prefixes, we will need to install the package into
                # an interim container folder (temporary prefix) of distutils
                # will apply a default prefix for a desired empty prefix -- we
                # set a temporary prefix, install the package in that folder,
                # then move it into the desired destination folder
                with generate_temp_dir() as tmp_dir:
                    container = 'releng-tool-container'

                    python_args_tmp = python_args
                    python_args_tmp.extend(['--prefix', container])

                    rv = python_tool.execute(
                        [*python_args_tmp, python_root_param, tmp_dir], env=env)

                    if rv:
                        src_dir = os.path.join(tmp_dir, container) + os.sep
                        path_move(src_dir, dest_dir)
            else:
                rv = python_tool.execute(
                    [*python_args, python_root_param, dest_dir], env=env)

            if not rv:
                err('failed to install python project: {}', opts.name)
                return False

    return True
