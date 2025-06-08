"""
Advanced Features for ICTV-git

This module contains the next-generation features that transform ICTV-git
from a version control system into an intelligent taxonomy platform.

Features:
1. Natural Language Query Interface
2. AI Classification Suggestions
3. Real-time Database Synchronization
"""

from .nlq_interface import NaturalLanguageQuery
from .classification_ai import ClassificationAI
from .database_sync import DatabaseSync

__all__ = [
    'NaturalLanguageQuery',
    'ClassificationAI', 
    'DatabaseSync'
]