# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from collections import defaultdict
from pathlib import Path
from releng_tool import __version__ as releng_version
from releng_tool.defs import PackageInstallType
from releng_tool.exceptions import RelengToolException
from releng_tool.tool.python import PYTHON
from releng_tool.tool.python import PythonTool
from releng_tool.util.io_copy import path_copy
from releng_tool.util.io_temp_dir import temp_dir
from releng_tool.util.log import debug
from releng_tool.util.log import err
import os
import sys
import sysconfig
import traceback

try:
    from installer import install as installer_install
    from installer.destinations import SchemeDictionaryDestination
    from installer.sources import WheelFile
    from installer.utils import get_launcher_kind
    has_installer = True
except ImportError:
    has_installer = False


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

    if not has_installer:
        err('unable to install package; installer module is not installed')
        return False

    # find the built wheel package under `dist/` and append it to the
    # installer
    whl_pkg = None
    pkg_dist_path = opts._python_dist_path
    container_dir = Path(pkg_dist_path if pkg_dist_path else 'dist')
    debug('search for whl package inside "{}": {}', container_dir, opts.name)

    if container_dir.is_dir():
        for file in os.listdir(container_dir):
            if file.endswith('.whl'):
                whl_pkg = container_dir / file
                debug(f'found a whl package for {opts.name}: {whl_pkg.name}')
                break
    else:
        debug(f'no dist folder ({container_dir}) found: {opts.name}')

    if not whl_pkg:
        err('failed to find generated wheel package: {}', opts.name)
        return False

    # determine the prefix to be used in the destination directories
    install_prefix = opts.prefix.strip('/')

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

    pkg_installer_interpreter = opts._python_installer_interpreter
    pkg_installer_launcher_kind = opts._python_installer_launcher_kind
    pkg_installer_scheme = opts._python_installer_scheme
    scheme_paths = {}
    scheme_template = None

    if isinstance(pkg_installer_scheme, dict):
        scheme_paths = pkg_installer_scheme
    else:
        scheme_template = pkg_installer_scheme

    if scheme_template:
        # if a user defines a "default" (a releng-tool hint), this is an
        # indication to use the interpreter's default scheme, which is
        # selected by having no scheme argument provided
        if scheme_template == 'native':
            cfg_scheme = sysconfig.get_paths()
        else:
            try:
                cfg_scheme = sysconfig.get_paths(scheme_template)
            except KeyError:
                err('unsupported scheme type: {}', scheme_template)
                return False

        debug(f'installing with scheme template: {scheme_template}')
    elif scheme_paths:
        debug('using custom scheme paths')
        cfg_scheme = defaultdict(lambda: f'{install_prefix}/undefined')
        cfg_scheme.update(scheme_paths)
    else:
        debug('using releng-tool scheme paths')
        cfg_scheme = python_tool.scheme(install_prefix)

    if pkg_installer_launcher_kind:
        script_kind = pkg_installer_launcher_kind
    else:
        script_kind = get_launcher_kind()

    # configure the interpreter to to use
    #
    # If a host build, use the same interpreter used by releng-tool since
    # we want to ensure any host build's utilities can run. For non-host
    # environments, use the package-defined interpreter. If none are
    # configured, default to common platform interpreter (just in case
    # releng-tool is operating in a custom interpreter; e.g. pipx).
    if opts.install_type == PackageInstallType.HOST:
        installer_interpreter = sys.executable
    elif pkg_installer_interpreter:
        installer_interpreter = pkg_installer_interpreter
    elif sys.platform == 'win32':
        installer_interpreter = 'python.exe'
    else:
        installer_interpreter = '/usr/bin/python'

    # avoid building pyc files for non-host packages
    if opts.install_type != 'host':
        optimization = []  # --no-compile-bytecode
    else:
        optimization = [0, 1]  # default

    with temp_dir() as tmp_dir:
        # prepare the destination for the installation request
        dst = SchemeDictionaryDestination(
            cfg_scheme,
            interpreter=installer_interpreter,
            script_kind=script_kind,
            bytecode_optimization_levels=optimization,
            destdir=tmp_dir,  # --destdir
        )

        # install the wheel file into the interim path
        try:
            installer_str = f'releng-tool {releng_version}'

            debug('opening wheel file...')
            with WheelFile.open(whl_pkg) as src:
                debug('performing installation...')
                installer_install(
                    source=src,
                    destination=dst,
                    additional_metadata={
                        'INSTALLER': installer_str.encode('utf-8'),
                    },
                )
        except Exception as ex:
            raise RelengToolPythonInstallError({
                'description': str(ex),
                'name': opts.name,
                'traceback': traceback.format_exc(),
            }) from ex

        # replicate into each destination
        for dest_dir in opts.dest_dirs:
            debug(f'copying install to destination: {dest_dir}')

            copied = path_copy(f'{tmp_dir}/', f'{dest_dir}', critical=False)
            if not copied:
                err('failed to install python project: {}', opts.name)
                return False

    return True


class RelengToolPythonInstallError(RelengToolException):
    """
    raised when a python package fails to install
    """
    def __init__(self, args):
        super().__init__('''\
{traceback}
failed to install python project: {name}
    {description}
'''.strip().format(**args))
