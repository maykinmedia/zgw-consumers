# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys
from pathlib import Path

import django

_root_dir = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(_root_dir))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testapp.settings")

django.setup()

# -- Project information -----------------------------------------------------

project = "ZGW Consumers"
copyright = "2022, Maykin Media"
author = "Maykin Media"

# The full version, including alpha/beta/rc tags
release = "1.0.0"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "django_setup_configuration.documentation.setup_config_example",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

# -- Intersphinx configuration -----------------------------------------------

intersphinx_mapping = {
    "requests": ("https://requests.readthedocs.io/en/latest/", None),
    "ape-pie": ("https://ape-pie.readthedocs.io/en/latest/", None),
}
