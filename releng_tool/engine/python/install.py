# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from pathlib import Path
from releng_tool.defs import PythonSetupType
from releng_tool.tool.python import PYTHON
from releng_tool.tool.python import PythonTool
from releng_tool.util.env import insert_env_path
from releng_tool.util.io import generate_temp_dir
from releng_tool.util.io import prepare_arguments
from releng_tool.util.io import prepare_definitions
from releng_tool.util.io_copy import path_copy
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
        python_tool = PythonTool(opts._python_interpreter)
    else:
        python_tool = PYTHON

    if not python_tool.exists():
        err('unable to install package; python is not installed')
        return False

    # default environment
    env = {}

    # if `PYTHONPATH` is already configured/setup, use it as a base
    existing_pythonpath = os.getenv('PYTHONPATH')
    if existing_pythonpath:
        env['PYTHONPATH'] = existing_pythonpath

    # include the python staging path into the set for this package's runtime
    path1 = python_tool.path(opts.staging_dir, opts.prefix)
    insert_env_path('PYTHONPATH', path1, env=env)

    # include the python target path into the set for this package's runtime
    path2 = python_tool.path(opts.target_dir, opts.prefix)
    insert_env_path('PYTHONPATH', path2, env=env)

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

    # handle package-override install
    #
    # If the package already defines a root path, use it over any other
    # configured destination directories.
    if python_root_param in python_opts:
        python_args_tmp = python_args
        if '--prefix' not in python_opts:
            python_args_tmp.extend(['--prefix', opts.prefix or '/'])

        if not python_tool.execute(python_args_tmp, env=env):
            err('failed to install python project: {}', opts.name)
            return False

        return True

    # install to target destination(s)
    #
    # We will trigger an installation into a interim folder and then copy the
    # installed content into each configured destination directory.
    #
    #  1) The `installer` module will not support installing over existing
    #     files by default (there is a `--overwrite-existing` argument; but at
    #     the time of writing, it is not a stable release and we also went to
    #     be flexible for older `installer` module versions for now). This can
    #     be a pain for users re-installing packages, forcing a requirement to
    #     clean then build the entire package set again.
    #
    #  2) We will manage the prefix path manually. For the most part, the
    #     `--prefix` argument works as expected with the `installer` module,
    #     but there are some inconsistencies for setuptools/distutils install;
    #     especially between different platform states. For example, if an
    #     "empty"/(root path) prefix is provided, a `setup.py` invoke may
    #     ignore provided `--root` value or `--prefix` value.

    with generate_temp_dir() as tmp_dir:
        python_args_tmp = python_args

        # configure to use our interim prefix; unless a package states
        # wants to do override
        tmp_prefix = python_opts.get('--prefix', 'rt-tmp-prefix')
        if '--prefix' not in python_opts:
            python_args_tmp.extend(['--prefix', tmp_prefix])

        # install the package into the interim path
        rv = python_tool.execute(
            [*python_args_tmp, python_root_param, tmp_dir], env=env)

        if not rv:
            err('failed to install python project: {}', opts.name)
            return False

        # determine the final prefix to be used in the destination directories
        if opts.prefix and opts.prefix != '/':
            install_prefix = opts.prefix.removeprefix('/')
        else:
            install_prefix = ''

        # replicate into each destination
        for cfg_dest_dir in opts.dest_dirs:
            src_dir = Path(tmp_dir) / tmp_prefix
            dest_dir = Path(cfg_dest_dir) / install_prefix

            copied = path_copy(
                f'{src_dir}{os.sep}', f'{dest_dir}', critical=False)
            if not copied:
                err('failed to install python project: {}', opts.name)
                return False

    return True
