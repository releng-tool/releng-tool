# -*- coding: utf-8 -*-
# Copyright 2021 releng-tool

# sample extension will should load since the the required version
# number is older than the current version
def releng_setup(app):
    app.require_version('0.0')
