#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2020 releng-tool

from releng_tool.util.log import warn
from releng_tool.__main__ import main
import sys

if __name__ == '__main__':
    warn('(deprecated) releng module is deprecated over releng_tool')
    sys.exit(main())
