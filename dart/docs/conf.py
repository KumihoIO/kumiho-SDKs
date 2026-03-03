# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from pathlib import Path

import yaml


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Kumiho Dart SDK"
copyright = "2025, Kumiho Clouds"
author = "Kumiho Clouds"

# Get version from pubspec.yaml
_root = Path(__file__).resolve().parents[1]
package_info = yaml.safe_load((_root / "pubspec.yaml").read_text())
release = package_info.get("version", "0.0.0")  # Full version, e.g., "0.2.0"
version = ".".join(release.split(".")[:2])  # Short version, e.g., "0.2"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autosectionlabel",
    "myst_parser",
]

# Autosectionlabel settings - prefix with document name to avoid duplicates
autosectionlabel_prefix_document = True

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

# Extra static content copied verbatim into the HTML output.
# CI places generated dartdoc output under docs/_extra/dartdoc.
html_extra_path = ["_extra"]

# HTML title
html_title = f"{project} v{release}"

# -- Options for LaTeX output ------------------------------------------------
latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
}

# Grouping the document tree into LaTeX files
latex_documents = [
    (master_doc, "kumiho-dart.tex", "Kumiho Dart SDK Documentation", "Kumiho Clouds", "manual"),
]

# -- Options for manual page output ------------------------------------------
man_pages = [(master_doc, "kumiho-dart", "Kumiho Dart SDK Documentation", [author], 1)]

# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    (
        master_doc,
        "kumiho-dart",
        "Kumiho Dart SDK Documentation",
        author,
        "kumiho-dart",
        "Graph-native creative & AI asset management SDK for Dart",
        "Miscellaneous",
    ),
]
