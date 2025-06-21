# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool
from releng_tool.util.log import debug
import os
import site
import sys


#: executable used to run scons commands
SCONS_COMMAND = 'scons'

#: list of environment keys to filter from a environment dictionary
SCONS_SANITIZE_ENV_KEYS = [
    'SCONSFLAGS',
    'SCONS_LIB_DIR',
]


class SconsTool(RelengTool):
    """
    scons host tool

    Provides addition helper methods for scons-based tool interaction.
    """

    def exists(self):
        """
        return whether or not the host tool exists

        Returns whether or not the tool is available on the host for use.

        Returns:
            ``True``, if the tool exists; ``False`` otherwise
        """
        if self.tool in RelengTool.detected:
            return RelengTool.detected[self.tool]

        # try to find scons using a standard check; if not, we will try to
        # fallback at looking for the SCons module in the running interpreter
        if not super().exists():
            debug('attempting to find {} in the running interpreter', self.tool)
            self._scons_interpreter = None

            try:
                import SCons  # noqa: PLC0415  pylint: disable=E0401
                debug('{} tool is detected in the interpreter', self.tool)
                RelengTool.detected[self.tool] = True
                self._scons_interpreter = 'SCons'
            except ModuleNotFoundError:
                debug('{} tool is not detected in the interpreter', self.tool)

            # older versions of SCons will have its module found inside
            # a `scons` directory; append this folder into the system path,
            # import it and invoke the module's mainline script
            if not self._scons_interpreter:
                for site_base in site.getsitepackages():
                    scons_container = os.path.join(site_base, 'scons')
                    if not os.path.exists(scons_container):
                        continue

                    debug('searching for {} tool inside container: {}',
                        self.tool, scons_container)
                    sys.path.append(str(scons_container))

                    try:
                        # pylint: disable=E0401
                        import SCons  # noqa: F401, PLC0415
                        debug('{} tool is detected in container', self.tool)
                        RelengTool.detected[self.tool] = True
                        self._scons_interpreter = 'releng_tool.tool.scons_proxy'
                        break
                    except ModuleNotFoundError:
                        debug('{} tool is not detected in container', self.tool)

        return RelengTool.detected[self.tool]

    def _invoked_tool(self):
        """
        returns the tool arguments to be invoked

        Provides the arguments used to invoke the tool for an execution
        request. This is typically the executable's name/path; however,
        in some scenarios, a tool may override how a tool is invoked.

        Returns:
            tool arguments to invoke
        """

        # If scons is being run using the module found inside the running
        # interpreter, invoke the SCons module instead.
        module = getattr(self, '_scons_interpreter', None)
        if module:
            interpreter = sys.executable if sys.executable else 'python'
            return [interpreter, '-m', module]

        return super()._invoked_tool()

#: scons host tool helper
SCONS = SconsTool(SCONS_COMMAND, env_sanitize=SCONS_SANITIZE_ENV_KEYS)
