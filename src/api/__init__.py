"""
ICTV-Git API Package

RESTful API for accessing 20-year viral taxonomy history and AI-powered features.
Provides endpoints for external tools, research applications, and data integration.
"""

from .taxonomy_api import TaxonomyAPI
from .historical_api import HistoricalAPI  
from .ai_api import AIAPI
from .search_api import SearchAPI

__all__ = [
    'TaxonomyAPI',
    'HistoricalAPI', 
    'AIAPI',
    'SearchAPI'
]