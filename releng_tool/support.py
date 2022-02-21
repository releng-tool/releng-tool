# -*- coding: utf-8 -*-
# Copyright 2022 releng-tool

from releng_tool import __version__ as releng_version
from releng_tool.util.log import err
import sys


def require_version(version, quiet=False, critical=True):
    """
    perform a required-version check

    Enables a caller to explicitly check for a required releng-tool version.
    Invoking this function with a dotted-separated ``version`` string, the
    string will be parsed and compared with the running releng-tool version.
    If the required version is met, this method will have no effect. In the
    event that the required version is not met, the exception ``SystemExit``
    will be raised if the critical flag is set; otherwise this call will
    return ``False``.

    An example when using in the context of script helpers is as follows:

    .. code-block:: python

        # ensure we are using releng-tool v1
        releng_require_version('1.0.0')

    Args:
        version: dotted-separated version string
        quiet (optional): whether or not to suppress output
        critical (optional): whether or not to stop execution on failure

    Returns:
        ``True`` if the version check is met; ``False`` if the version check
        has failed

    Raises:
        SystemExit: if the version check fails with ``critical=True``
    """

    rv = True

    if version:
        requested = version.split('.')
        current = releng_version.split('.')
        rv = requested <= current
        if not rv:
            if not quiet:
                args = {
                    'detected': releng_version,
                    'required': version,
                }
                err('''
required releng-tool version check has failed

This project has indicated a required minimum version of releng-tool to
be installed on this system; however, an older version has been
detected:

    (required) {required}
    (detected) {detected}

Please update to a more recent version:

 https://docs.releng.io/install/
'''.strip().format(**args))

            if critical:
                sys.exit(-1)

    return rv
