# Configuration file for the Sphinx documentation builder.
# For the full list of built-in configuration values, see:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# Add project source to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# -- Project information -----------------------------------------------------

project = "nostr-tools"
copyright = "2024, Bigbrotr"
author = "Bigbrotr"

# The version info from setuptools-scm
try:
    from nostr_tools import __version__

    version = __version__
    release = __version__
except ImportError:
    version = "development"
    release = "development"

# -- General configuration ---------------------------------------------------

extensions = [
    # Sphinx built-in extensions
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
    # Third-party extensions
    "myst_parser",  # For Markdown support
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"
html_title = f"{project} v{version}"
html_short_title = project

html_static_path = ["_static"]
html_css_files = ["custom.css"]

# Theme options
html_theme_options = {
    "canonical_url": "https://bigbrotr.github.io/nostr-tools/",
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": True,
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
}

# -- Extension configuration -------------------------------------------------

# Napoleon settings (for Google/NumPy docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
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
autodoc_typehints_description_target = "documented"
autodoc_preserve_defaults = True

# Autosummary settings
autosummary_generate = True
autosummary_imported_members = False

# MyST settings (Markdown parser)
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

# Intersphinx settings (links to other docs)
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
    "websockets": ("https://websockets.readthedocs.io/en/stable/", None),
}

# -- Options for LaTeX output ------------------------------------------------
latex_engine = "pdflatex"
latex_elements = {
    "papersize": "letterpaper",
    "pointsize": "10pt",
    "preamble": "",
    "fncychap": "\\usepackage[Bjornstrup]{fncychap}",
    "printindex": "\\footnotesize\\raggedright\\printindex",
}

latex_documents = [
    (
        "index",
        "nostr-tools.tex",
        f"{project} Documentation",
        author,
        "manual",
    ),
]

# -- Options for manual page output ------------------------------------------
man_pages = [("index", "nostr-tools", f"{project} Documentation", [author], 1)]

# -- Options for Texinfo output ----------------------------------------------
texinfo_documents = [
    (
        "index",
        "nostr-tools",
        f"{project} Documentation",
        author,
        "nostr-tools",
        "A comprehensive Python library for Nostr protocol interactions",
        "Miscellaneous",
    ),
]

# -- Options for Epub output -------------------------------------------------
epub_title = project
epub_author = author
epub_publisher = author
epub_copyright = copyright

# -- Custom configuration ----------------------------------------------------

# Add any paths that contain custom static files (such as style sheets)
if not os.path.exists("_static"):
    os.makedirs("_static")

# Create custom CSS if it doesn't exist
custom_css_path = Path("_static/custom.css")
if not custom_css_path.exists():
    custom_css_content = """
/* Custom CSS for nostr-tools documentation */

.wy-nav-content {
    max-width: 1200px;
}

/* Better code block styling */
.highlight pre {
    font-size: 14px;
    line-height: 1.4;
}

/* Improve table styling */
.wy-table-responsive table td, .wy-table-responsive table th {
    white-space: normal;
}

/* Better admonition styling */
.admonition {
    margin: 1em 0;
    padding: 0.5em 1em;
}

/* Code inline styling */
code.literal {
    background: #f8f8f8;
    border: 1px solid #e1e4e5;
    padding: 2px 5px;
    border-radius: 3px;
}
"""
    with open(custom_css_path, "w") as f:
        f.write(custom_css_content)


def setup(app):
    """Custom Sphinx setup function."""
    app.add_css_file("custom.css")
