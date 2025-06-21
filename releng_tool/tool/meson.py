# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

from releng_tool.tool import RelengTool
from releng_tool.util.log import debug
import sys


#: executable used to run meson commands
MESON_COMMAND = 'meson'

#: dictionary of environment entries append to the environment dictionary
MESON_EXTEND_ENV = {
    # meson is most likely a python script; ensure output is unbuffered
    'PYTHONUNBUFFERED': '1',
}


class MesonTool(RelengTool):
    """
    meson host tool

    Provides addition helper methods for meson-based tool interaction.
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

        # try to find meson using a standard check; if not, we will try to
        # fallback at looking for the meson module in the running interpreter
        if not super().exists():
            debug('attempting to find {} in the running interpreter', self.tool)
            self._meson_interpreter = None

            try:
                import mesonbuild  # noqa: F401, PLC0415  pylint: disable=E0401
                debug('{} tool is detected in the interpreter', self.tool)
                RelengTool.detected[self.tool] = True
                self._meson_interpreter = 'mesonbuild.mesonmain'
            except ModuleNotFoundError:
                debug('{} tool is not detected in the interpreter', self.tool)

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

        # If meson is being run using the module found inside the running
        # interpreter, invoke the meson module instead.
        module = getattr(self, '_meson_interpreter', None)
        if module:
            interpreter = sys.executable if sys.executable else 'python'
            return [interpreter, '-m', module]

        return super()._invoked_tool()

#: meson host tool helper
MESON = MesonTool(MESON_COMMAND, env_include=MESON_EXTEND_ENV)
