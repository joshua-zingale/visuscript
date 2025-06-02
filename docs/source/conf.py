# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'visuscript'
copyright = '2025, Joshua Thomas Zingale'
author = 'Joshua Thomas Zingale'
release = '0.1.0'

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
]

templates_path = ['_templates']
exclude_patterns = []


# -- Options for autodoc ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration

autodoc_default_options = {
    'members': True,
    'undoc-members': False,
    'private-members': False,
    'special-members': '__init__',
    'show-inheritance': True,
    'inherited-members': True,
}


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
