# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool
#
# Note: if looking for API extension support, see the `api/` folder instead.

from releng_tool import __version__ as releng_version
import json


class ApiState(dict):
    def __init__(self):
        """
        an api state tracker

        Class which holds API state information through the lifecycle of a
        releng-tool execution.

        Attributes:
            state: the api state
        """
        self.reset()

    def __missing__(self, key):
        value = self[key] = ApiSubState()
        return value

    def reset(self):
        """
        reset the state of the api
        """
        self.clear()

        # always have a code response (assume success)
        self['code'] = 0

        # always track the active version in the state
        self['releng-tool'] = releng_version

    def __str__(self):
        return json.dumps(self, indent=4, cls=ApiStateEncoder)


class ApiSubState(dict):
    def fetch(self):
        return self

    def __missing__(self, key):
        value = self[key] = type(self)()
        return value


class ApiStateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return sorted(obj)

        return json.JSONEncoder.default(self, obj)


# global api state various components can populate into
API_STATE = ApiState()
