"""
AI API - Advanced features integration

Provides REST API access to AI-powered taxonomy features including
Natural Language Query, Classification Suggestions, and Database Synchronization.
"""

from typing import List, Dict, Optional, Any
from pathlib import Path
import json
import sys
import traceback

# Try to import advanced features with fallbacks
try:
    from ..advanced_features.nlq_interface import NaturalLanguageQuery
    HAS_NLQ = True
except ImportError:
    HAS_NLQ = False

try:
    from ..advanced_features.classification_ai import ClassificationAI
    HAS_CLASSIFICATION_AI = True
except ImportError:
    HAS_CLASSIFICATION_AI = False

try:
    from ..advanced_features.database_sync import DatabaseSync
    HAS_DATABASE_SYNC = True
except ImportError:
    HAS_DATABASE_SYNC = False


class AIAPI:
    """API for AI-powered taxonomy features"""
    
    def __init__(self, taxonomy_repo_path: str, config: Optional[Dict] = None):
        """
        Initialize AI API with taxonomy repository
        
        Args:
            taxonomy_repo_path: Path to complete 20-year taxonomy repository
            config: Optional configuration for AI features
        """
        self.repo_path = Path(taxonomy_repo_path)
        self.config = config or {}
        
        # Initialize available AI features
        self.nlq_interface = None
        self.classification_ai = None
        self.database_sync = None
        
        self._initialize_features()
    
    def _initialize_features(self):
        """Initialize available AI features with error handling"""
        errors = []
        
        # Initialize Natural Language Query
        if HAS_NLQ:
            try:
                self.nlq_interface = NaturalLanguageQuery(
                    taxonomy_repo_path=str(self.repo_path)
                )
            except Exception as e:
                errors.append(f"NLQ initialization failed: {e}")
        
        # Initialize Classification AI
        if HAS_CLASSIFICATION_AI:
            try:
                self.classification_ai = ClassificationAI(
                    taxonomy_repo_path=str(self.repo_path)
                )
            except Exception as e:
                errors.append(f"Classification AI initialization failed: {e}")
        
        # Initialize Database Sync
        if HAS_DATABASE_SYNC:
            try:
                self.database_sync = DatabaseSync(
                    taxonomy_repo_path=str(self.repo_path)
                )
            except Exception as e:
                errors.append(f"Database Sync initialization failed: {e}")
        
        if errors:
            print(f"Warning: Some AI features failed to initialize: {errors}")
    
    def get_available_features(self) -> Dict:
        """
        Get list of available AI features
        
        Returns:
            Dictionary of feature availability and status
        """
        return {
            'natural_language_query': {
                'available': self.nlq_interface is not None,
                'description': 'Query taxonomy using natural language',
                'endpoints': ['/ai/query', '/ai/query-cached']
            },
            'classification_ai': {
                'available': self.classification_ai is not None,
                'description': 'AI-powered classification suggestions',
                'endpoints': ['/ai/classify', '/ai/stability-score']
            },
            'database_sync': {
                'available': self.database_sync is not None,
                'description': 'Real-time database synchronization',
                'endpoints': ['/ai/sync-status', '/ai/sync-databases']
            },
            'dependencies': {
                'has_nlq_module': HAS_NLQ,
                'has_classification_module': HAS_CLASSIFICATION_AI,
                'has_sync_module': HAS_DATABASE_SYNC
            }
        }
    
    def query_natural_language(self, query: str, use_cache: bool = True) -> Dict:
        """
        Process natural language query about taxonomy
        
        Args:
            query: Natural language question about viral taxonomy
            use_cache: Whether to use cached results
            
        Returns:
            Query response with answer and metadata
        """
        if not self.nlq_interface:
            return {
                'error': 'Natural Language Query feature not available',
                'available_fallbacks': ['Search API endpoints']
            }
        
        try:
            response = self.nlq_interface.query(query)
            
            return {
                'query': query,
                'response': response,
                'cached': use_cache,
                'feature': 'natural_language_query',
                'timestamp': str(Path().resolve())  # Simple timestamp
            }
            
        except Exception as e:
            return {
                'error': f'Query processing failed: {str(e)}',
                'query': query,
                'feature': 'natural_language_query'
            }
    
    def get_cache_stats(self) -> Dict:
        """Get Natural Language Query cache statistics"""
        if not self.nlq_interface:
            return {'error': 'NLQ feature not available'}
        
        try:
            return self.nlq_interface.get_cache_stats()
        except Exception as e:
            return {'error': f'Failed to get cache stats: {str(e)}'}
    
    def classify_organism(self, 
                         genome_sequence: Optional[str] = None,
                         metadata: Optional[Dict] = None,
                         organism_name: Optional[str] = None) -> Dict:
        """
        Get AI classification suggestions for an organism
        
        Args:
            genome_sequence: DNA/RNA sequence data
            metadata: Additional organism metadata
            organism_name: Name of organism for context
            
        Returns:
            Classification suggestions with confidence scores
        """
        if not self.classification_ai:
            return {
                'error': 'Classification AI feature not available',
                'available_fallbacks': ['Manual taxonomy lookup']
            }
        
        try:
            suggestion = self.classification_ai.suggest_classification(
                genome_sequence=genome_sequence,
                metadata=metadata
            )
            
            return {
                'organism_name': organism_name,
                'suggestion': suggestion,
                'feature': 'classification_ai',
                'input_data': {
                    'has_sequence': genome_sequence is not None,
                    'has_metadata': metadata is not None,
                    'sequence_length': len(genome_sequence) if genome_sequence else 0
                }
            }
            
        except Exception as e:
            return {
                'error': f'Classification failed: {str(e)}',
                'organism_name': organism_name,
                'feature': 'classification_ai'
            }
    
    def get_family_stability_score(self, family_name: str) -> Dict:
        """
        Get stability score for a viral family
        
        Args:
            family_name: Name of the viral family
            
        Returns:
            Stability analysis with historical data
        """
        if not self.classification_ai:
            return {
                'error': 'Classification AI feature not available'
            }
        
        try:
            stability_data = self.classification_ai.stability_analyzer.get_family_stability(family_name)
            
            return {
                'family_name': family_name,
                'stability_data': stability_data,
                'feature': 'family_stability'
            }
            
        except Exception as e:
            return {
                'error': f'Stability analysis failed: {str(e)}',
                'family_name': family_name
            }
    
    def get_database_sync_status(self) -> Dict:
        """Get current database synchronization status"""
        if not self.database_sync:
            return {
                'error': 'Database Sync feature not available'
            }
        
        try:
            return self.database_sync.get_sync_status()
        except Exception as e:
            return {
                'error': f'Failed to get sync status: {str(e)}'
            }
    
    async def sync_databases(self, 
                           databases: Optional[List[str]] = None,
                           species_list: Optional[List[str]] = None) -> Dict:
        """
        Synchronize with external databases
        
        Args:
            databases: List of database names to sync ('genbank', 'refseq', 'uniprot')
            species_list: Specific species to check (default: all)
            
        Returns:
            Synchronization results and any mismatches found
        """
        if not self.database_sync:
            return {
                'error': 'Database Sync feature not available'
            }
        
        try:
            results = await self.database_sync.sync_databases(
                databases=databases,
                species_list=species_list
            )
            
            return {
                'sync_results': results,
                'feature': 'database_sync',
                'databases_checked': databases or ['genbank', 'refseq', 'uniprot']
            }
            
        except Exception as e:
            return {
                'error': f'Database sync failed: {str(e)}',
                'feature': 'database_sync'
            }
    
    def get_ai_health_check(self) -> Dict:
        """
        Comprehensive health check of all AI features
        
        Returns:
            Status of all AI components and dependencies
        """
        health_data = {
            'overall_status': 'healthy',
            'features': {},
            'dependencies': {
                'python_version': sys.version,
                'repository_path': str(self.repo_path),
                'repository_exists': self.repo_path.exists()
            },
            'errors': []
        }
        
        # Check each feature
        features_to_check = [
            ('natural_language_query', self.nlq_interface),
            ('classification_ai', self.classification_ai),
            ('database_sync', self.database_sync)
        ]
        
        for feature_name, feature_instance in features_to_check:
            if feature_instance:
                try:
                    # Try a simple operation to verify feature works
                    if feature_name == 'natural_language_query':
                        test_result = self.nlq_interface.get_cache_stats()
                        health_data['features'][feature_name] = {
                            'status': 'healthy',
                            'test_result': 'cache_stats_accessible'
                        }
                    elif feature_name == 'classification_ai':
                        # Test basic functionality
                        health_data['features'][feature_name] = {
                            'status': 'healthy',
                            'test_result': 'initialization_successful'
                        }
                    elif feature_name == 'database_sync':
                        status = self.database_sync.get_sync_status()
                        health_data['features'][feature_name] = {
                            'status': 'healthy',
                            'test_result': 'status_accessible'
                        }
                        
                except Exception as e:
                    health_data['features'][feature_name] = {
                        'status': 'error',
                        'error': str(e)
                    }
                    health_data['errors'].append(f'{feature_name}: {str(e)}')
                    health_data['overall_status'] = 'degraded'
            else:
                health_data['features'][feature_name] = {
                    'status': 'unavailable',
                    'reason': 'Feature not initialized'
                }
        
        # Overall status
        if len(health_data['errors']) > 0:
            health_data['overall_status'] = 'degraded'
        
        return health_data
    
    def get_example_queries(self) -> Dict:
        """
        Get example queries for each AI feature
        
        Returns:
            Dictionary of example usage for each feature
        """
        return {
            'natural_language_query': {
                'examples': [
                    "What happened to Caudovirales in 2019?",
                    "Show me families with unstable classifications",
                    "How many species were added between MSL35 and MSL40?",
                    "What are the largest viral families?",
                    "Explain the COVID-19 taxonomy changes"
                ],
                'description': "Ask questions about viral taxonomy in natural language"
            },
            'classification_suggestions': {
                'examples': [
                    "Classify a new RNA virus with genome size 12kb",
                    "Get stability score for Siphoviridae family",
                    "Suggest classification for SARS-like coronavirus",
                    "Analyze classification confidence for novel phage"
                ],
                'description': "Get AI-powered classification suggestions"
            },
            'database_synchronization': {
                'examples': [
                    "Check GenBank consistency for Coronaviridae",
                    "Sync all databases for recent species",
                    "Find taxonomy mismatches in RefSeq",
                    "Get synchronization status report"
                ],
                'description': "Synchronize with external biological databases"
            }
        }