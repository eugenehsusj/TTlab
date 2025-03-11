
import os
import sys

# Ensure Sphinx can find your package
sys.path.insert(0, os.path.abspath("../../ttlab"))  # Adjust if your package is in a different location

# Project information
project = "TTLab"
author = "Eugene Hsu"
release = "0.1.0"

# Sphinx Extensions
extensions = [
    "sphinx.ext.autodoc",        # Auto-generate documentation from docstrings
    "sphinx.ext.napoleon",       # Support Google-style docstrings
    "sphinx.ext.viewcode",       # Add links to source code
]

# Theme settings
html_theme = "sphinx_rtd_theme"

# Paths
templates_path = ["_templates"]
exclude_patterns = []
