# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# Add the parent directory to the path so Sphinx can find the kumiho package
sys.path.insert(0, os.path.abspath(".."))

# Import kumiho to get the version dynamically
import kumiho

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Kumiho Python SDK"
copyright = "2025, Kumiho Clouds"
author = "Kumiho Clouds"

# Get version from the kumiho package (__version__)
release = kumiho.__version__  # Full version, e.g., "0.3.0"
version = ".".join(release.split(".")[:2])  # Short version, e.g., "0.3"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
    "myst_parser",
]

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Autodoc settings
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "exclude-members": "__weakref__",
    "show-inheritance": True,
}
autodoc_typehints = "description"
autodoc_class_signature = "separated"

# Suppress duplicate object warnings for re-exported symbols in __init__.py
# These occur because classes/functions are documented in both their source
# module and in the main kumiho namespace (via re-export in __init__.py)
suppress_warnings = [
    "autodoc.duplicate_object",
    "ref.python",           # Duplicate Python object references
    "py.duplicate_object",  # Python domain duplicates
]

# Autosummary settings
autosummary_generate = True

# Intersphinx mapping
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "grpc": ("https://grpc.github.io/grpc/python/", None),
}

# MyST parser settings for Markdown support
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# The suffix(es) of source filenames
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

# The master toctree document
master_doc = "index"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
# html_static_path = ["_static"]  # Uncomment when you have static files

# Theme options
html_theme_options = {
    "logo_only": False,
    # "display_version": True,  # Deprecated in sphinx-rtd-theme 3.0
    "prev_next_buttons_location": "bottom",
    "style_external_links": True,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

# Custom sidebar templates
html_sidebars = {
    "**": [
        "relations.html",
        "searchbox.html",
    ]
}

# HTML title
html_title = f"{project} v{release}"

# -- Options for LaTeX output ------------------------------------------------
latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
}

# Grouping the document tree into LaTeX files
latex_documents = [
    (master_doc, "kumiho.tex", "Kumiho Python SDK Documentation", "Kumiho Clouds", "manual"),
]

# -- Options for manual page output ------------------------------------------
man_pages = [(master_doc, "kumiho", "Kumiho Python SDK Documentation", [author], 1)]

# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    (
        master_doc,
        "kumiho",
        "Kumiho Python SDK Documentation",
        author,
        "kumiho",
        "Graph-native creative & AI asset management SDK",
        "Miscellaneous",
    ),
]
