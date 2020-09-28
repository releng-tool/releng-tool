# -*- coding: utf-8 -*-
# Copyright 2020 releng-tool
# flake8: noqa

from releng_tool import *

if '_RELENG_GLOBAL_NAMESPACE_DEPRECATED' not in globals():
    global _RELENG_GLOBAL_NAMESPACE_DEPRECATED
    _RELENG_GLOBAL_NAMESPACE_DEPRECATED = True
    warn('(deprecated) namespace releng has been deprecated over releng_tool')
