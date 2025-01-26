# SPDX-License-Identifier: BSD-2-Clause
# Copyright releng-tool

# Provides an invoke testing executable, which will capture arguments and the
# working directory of a call and output it into a JSON file. Unit tests may
# use this utility file to help verify executions in certain scenarios.

import json
import os
import posixpath
import sys

data = {
    'args': sys.argv,
    'cwd': os.getcwd().replace(os.sep, posixpath.sep),
}

with open('invoke-results.json', 'w') as f:
    json.dump(data, f)
