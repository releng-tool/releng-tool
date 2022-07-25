#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2018-2022 releng-tool

from sphinx.ext.autodoc import cut_lines
import os
import sys

# common
master_doc = 'index'

# meta
project = 'releng-tool'
copyright = '2022 releng-tool'
author = 'releng-tool'

# sphinx extensions
extensions = [
    'myst_parser',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_inline_tabs',
]

# add root for autodoc documentation
doc_dir = os.path.dirname(os.path.realpath(__file__))
root_dir = os.path.dirname(doc_dir)
sys.path.insert(0, root_dir)

# output - html
html_theme = 'furo'
html_theme_options = {
    'navigation_with_keys': True,
}
html_static_path = ['_static']
html_show_copyright = False
html_show_sourcelink = False
html_show_sphinx = True
html_permalinks_icon = '¶'


def setup(app):
    app.add_css_file('theme_overrides.css')

    # remove first line description docstrings in documentation
    app.connect('autodoc-process-docstring', cut_lines(1))
