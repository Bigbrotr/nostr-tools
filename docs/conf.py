#!/usr/bin/env python3
"""
Configuration file for the Sphinx documentation builder.
Optimized for automatic documentation generation with zero warnings.
"""

import os
from pathlib import Path
import sys

# Tell the package we're building docs
os.environ["SPHINX_BUILD"] = "1"

# -- Path setup --------------------------------------------------------------
# Import the package to get version info
import nostr_tools

# Add project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# -- Project information -----------------------------------------------------
project = "nostr-tools"
copyright = "2025, Bigbrotr"
author = "Bigbrotr"
version = nostr_tools.__version__
release = nostr_tools.__version__

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",  # Automatic documentation from docstrings
    "sphinx.ext.autosummary",  # Automatic summary generation
    "sphinx.ext.napoleon",  # Google/NumPy docstring support
    "sphinx.ext.viewcode",  # Add source code links
    "sphinx.ext.intersphinx",  # Link to other projects' docs
    "sphinx.ext.githubpages",  # GitHub Pages support
    "myst_parser",  # Markdown support
    "sphinx_rtd_theme",  # Read the Docs theme
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
master_doc = "index"

# -- Autodoc Configuration (AUTOMATIC DISCOVERY) ---------------------------
autodoc_default_options = {
    "members": True,  # Include all members
    "member-order": "bysource",  # Order by source code order
    "special-members": "__init__",  # Include __init__ methods
    "undoc-members": False,  # Don't include undocumented members
    "exclude-members": "__weakref__",  # Exclude technical attributes
    "inherited-members": True,  # Include inherited methods
    "show-inheritance": True,  # Show class inheritance
}

# Enhanced autodoc settings for better docstring handling
autodoc_class_signature = "mixed"
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented"
autodoc_typehints_format = "short"

# Include class docstrings only to avoid __init__ duplication
autoclass_content = "class"

# -- Autosummary Configuration (ZERO WARNINGS) -----------------------------
autosummary_generate = True  # Generate stub files automatically
autosummary_generate_overwrite = True  # Overwrite existing files
autosummary_imported_members = True  # Include imported members
autosummary_ignore_module_all = False  # Respect __all__ lists

# -- Napoleon Configuration (GOOGLE-STYLE DOCSTRINGS) ----------------------
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False  # Avoid duplication
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_use_keyword = True
napoleon_custom_sections = [("Returns", "params_style")]

# -- Intersphinx Configuration (EXTERNAL LINKS) ----------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
}

# -- MyST Parser Configuration (MARKDOWN SUPPORT) --------------------------
myst_enable_extensions = [
    "colon_fence",  # ::: fenced blocks
    "deflist",  # Definition lists
    "dollarmath",  # $$ math blocks
    "html_admonition",  # HTML-style admonitions
    "html_image",  # HTML image tags
    "linkify",  # Auto-detect links
    "replacements",  # Text replacements
    "smartquotes",  # Smart quotes
    "substitution",  # Variable substitutions
    "tasklist",  # Task lists
]

# -- HTML Output Configuration (APPEARANCE) --------------------------------
html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["custom.css"]

html_theme_options = {
    "canonical_url": "",
    "logo_only": False,
    "display_version": True,
    "prev_next_buttons_location": "bottom",
    "style_external_links": False,
    "style_nav_header_background": "#2980B9",
    "collapse_navigation": False,  # Keep navigation expanded
    "sticky_navigation": True,
    "navigation_depth": 4,  # Deep navigation
    "includehidden": True,
    "titles_only": False,
}

# Metadata
html_title = f"{project} v{version}"
html_short_title = project
html_last_updated_fmt = "%b %d, %Y"
html_use_smartypants = True
html_domain_indices = True
html_use_index = True
html_split_index = False
html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True

# -- Advanced Configuration for Zero Warnings ------------------------------


def skip_member(app, what, name, obj, skip, options):
    """
    Custom function to control what gets documented.
    This ensures we don't skip important members with docstrings.
    """
    # Never skip if there's a docstring
    if hasattr(obj, "__doc__") and obj.__doc__:
        return False

    # Skip private members that don't have docstrings
    if name.startswith("_") and not name.startswith("__"):
        return True

    return skip


def setup(app):
    """Custom setup for enhanced documentation generation."""
    app.connect("autodoc-skip-member", skip_member)


# Suppress specific warnings for cleaner builds (optional)
suppress_warnings = [
    # Uncomment if you want to suppress these warning types:
    # 'ref.any',          # Cross-reference warnings
    # 'toc.not_readable', # Table of contents warnings
]

# Make sure we can import everything
autodoc_mock_imports = []

# Add type hints extension if available
try:
    extensions.append("sphinx_autodoc_typehints")
    # Configure type hints extension
    typehints_fully_qualified = False
    always_document_param_types = True
    typehints_document_rtype = True
except ImportError:
    pass
