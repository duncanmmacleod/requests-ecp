# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

from pathlib import Path

from sphinx.ext.apidoc import main as apidoc_main

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

from requests_ecp import __version__ as requests_ecp_version


# -- Project information -----------------------------------------------------

project = 'requests-ecp'
copyright = '2020, Cardiff University'
author = 'Duncan Macleod'

# The full version, including alpha/beta/rc tags
release = requests_ecp_version


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_automodapi.automodapi",
    "sphinx_tabs.tabs",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
#html_static_path = ['_static']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'monokai'

# The reST default role (used for this markup: `text`) to use for all
# documents.
default_role = 'obj'

# -- Extensions --------------------------------------------------------------

# Intersphinx directory
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "requests": ("https://requests.readthedocs.io/en/stable/", None),
}

# napoleon configuration
napoleon_use_rtype = False

# Don't inherit in automodapi
numpydoc_show_class_members = False
automodapi_inherited_members = False

# autodoc
#autodoc_mock_imports = ['cryptography', 'requests']
autodoc_default_flags = ['members', 'show-inheritance']
autosummary_generate = True
