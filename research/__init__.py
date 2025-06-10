"""
ICTV-git Research Analysis Framework

This package contains research analyses leveraging the temporal ICTV taxonomy data.
Each submodule addresses specific research questions about viral classification evolution.
"""

__version__ = "0.1.0"
__author__ = "ICTV-git Research Team"

# Research modules will be imported as they are implemented
__all__ = [
    'family_size_analysis',
    'species_boundaries', 
    'discovery_bias',
    'growth_patterns'
]