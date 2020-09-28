# -*- coding: utf-8 -*-
# Copyright 2020 releng-tool
# flake8: noqa

from releng_tool.api import *

if '_RELENG_GLOBAL_NAMESPACE_API_DEPRECATED' not in globals():
    global _RELENG_GLOBAL_NAMESPACE_API_DEPRECATED
    _RELENG_GLOBAL_NAMESPACE_API_DEPRECATED = True
    from releng_tool.util.log import warn as __warn
    __warn('(deprecated) namespace releng.api has been deprecated over releng_tool.api')
