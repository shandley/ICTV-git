"""
Natural Language Query Interface

Enables users to query viral taxonomy using plain English.
Converts natural language to structured queries and formats results naturally.
"""

import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from datetime import datetime

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# Add the src directory to path for imports
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from community_tools.version_comparator import VersionComparator
from utils.git_interface import GitInterface


@dataclass
class QueryIntent:
    """Structured representation of user query intent"""
    action: str  # track_history, find_unstable, cross_host, etc.
    entity: Optional[str] = None  # species/family/genus name
    filters: Dict[str, Any] = None
    time_range: Optional[str] = None
    comparison: Optional[str] = None
    
    def __post_init__(self):
        if self.filters is None:
            self.filters = {}


@dataclass
class QueryResult:
    """Structured query result with metadata"""
    data: Any
    query_type: str
    entity_count: int
    execution_time: float
    confidence: float
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class QueryIntentParser:
    """Extract structured intent from natural language queries"""
    
    def __init__(self, use_openai: bool = False):
        self.use_openai = use_openai and HAS_OPENAI
        self.patterns = self._init_patterns()
        
        if self.use_openai and HAS_OPENAI:
            # Initialize OpenAI client (requires API key in environment)
            openai.api_key = os.getenv('OPENAI_API_KEY')
    
    def _init_patterns(self) -> Dict[str, List[str]]:
        """Initialize regex patterns for query classification"""
        return {
            'track_history': [
                r'what happened to (.+)',
                r'track (.+) through time',
                r'history of (.+)',
                r'(.+) classification changes'
            ],
            'find_unstable': [
                r'unstable (.+)',
                r'volatile (.+)',
                r'frequently reclassified (.+)',
                r'which (.+) change most'
            ],
            'cross_host': [
                r'viruses infect both (.+) and (.+)',
                r'(.+) that infect (.+)',
                r'host range (.+)'
            ],
            'similarity_search': [
                r'similar to (.+)',
                r'related to (.+)',
                r'viruses like (.+)'
            ],
            'temporal_query': [
                r'viruses discovered in (.+)',
                r'new species in (.+)',
                r'discovered after (.+)'
            ],
            'classification_level': [
                r'all (.+) in family (.+)',
                r'show me (.+) families',
                r'list (.+) genera'
            ]
        }
    
    def parse(self, query: str) -> QueryIntent:
        """Parse natural language query into structured intent"""
        query_lower = query.lower().strip()
        
        # Try OpenAI parsing first if available
        if self.use_openai:
            try:
                return self._parse_with_openai(query)
            except Exception as e:
                print(f"OpenAI parsing failed: {e}, falling back to pattern matching")
        
        # Fallback to pattern matching
        return self._parse_with_patterns(query_lower)
    
    def _parse_with_openai(self, query: str) -> QueryIntent:
        """Use OpenAI to parse query intent"""
        prompt = f"""
        Parse this viral taxonomy query into structured intent:
        
        Query: "{query}"
        
        Return a JSON object with:
        - action: one of [track_history, find_unstable, cross_host, similarity_search, temporal_query, classification_level]
        - entity: the main virus/family/genus mentioned (if any)
        - filters: any additional filters like host, year, etc.
        - time_range: time period if mentioned
        - comparison: if comparing things
        
        Example:
        Query: "What happened to bacteriophage T4 after 2018?"
        {{
            "action": "track_history",
            "entity": "bacteriophage T4",
            "filters": {{}},
            "time_range": "after 2018",
            "comparison": null
        }}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.1
        )
        
        result = json.loads(response.choices[0].message.content)
        return QueryIntent(**result)
    
    def _parse_with_patterns(self, query: str) -> QueryIntent:
        """Parse using regex patterns"""
        for action, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query)
                if match:
                    entity = match.group(1) if match.groups() else None
                    
                    # Extract additional context
                    filters = self._extract_filters(query)
                    time_range = self._extract_time_range(query)
                    
                    return QueryIntent(
                        action=action,
                        entity=entity,
                        filters=filters,
                        time_range=time_range
                    )
        
        # Default fallback
        return QueryIntent(
            action="general_search",
            entity=self._extract_likely_entity(query),
            filters=self._extract_filters(query)
        )
    
    def _extract_filters(self, query: str) -> Dict[str, Any]:
        """Extract filters from query text"""
        filters = {}
        
        # Host filters
        host_patterns = [
            r'infect (\w+)', r'host (\w+)', r'(\w+) viruses',
            r'found in (\w+)', r'isolated from (\w+)'
        ]
        for pattern in host_patterns:
            match = re.search(pattern, query)
            if match:
                filters['host'] = match.group(1)
        
        # Stability filters
        if any(word in query for word in ['unstable', 'volatile', 'change', 'reclassified']):
            filters['unstable'] = True
        
        # Genome type filters
        genome_types = ['dna', 'rna', 'positive', 'negative', 'double-stranded', 'single-stranded']
        for genome_type in genome_types:
            if genome_type in query:
                filters['genome_type'] = genome_type
        
        return filters
    
    def _extract_time_range(self, query: str) -> Optional[str]:
        """Extract time range from query"""
        time_patterns = [
            r'after (\d{4})', r'before (\d{4})', r'in (\d{4})',
            r'since (\d{4})', r'between (\d{4}) and (\d{4})'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_likely_entity(self, query: str) -> Optional[str]:
        """Extract most likely entity from query"""
        # Look for capitalized words that might be species/genus names
        words = query.split()
        capitalized = [w for w in words if w[0].isupper() and len(w) > 2]
        
        if capitalized:
            return ' '.join(capitalized[:2])  # Take first two capitalized words
        
        return None


class StructuredQueryTranslator:
    """Translate structured intent to database/git queries"""
    
    def __init__(self, git_repo_path: str):
        self.git_interface = GitInterface(git_repo_path)
        self.version_comparator = VersionComparator(git_repo_path)
    
    def translate(self, intent: QueryIntent) -> Dict[str, Any]:
        """Translate intent to executable query"""
        translator_map = {
            'track_history': self._translate_track_history,
            'find_unstable': self._translate_find_unstable,
            'cross_host': self._translate_cross_host,
            'similarity_search': self._translate_similarity_search,
            'temporal_query': self._translate_temporal_query,
            'classification_level': self._translate_classification_level,
            'general_search': self._translate_general_search
        }
        
        translator = translator_map.get(intent.action, self._translate_general_search)
        return translator(intent)
    
    def _translate_track_history(self, intent: QueryIntent) -> Dict[str, Any]:
        """Translate history tracking request"""
        return {
            'type': 'git_history',
            'entity': intent.entity,
            'command': 'git log --follow --oneline',
            'filters': intent.filters,
            'time_range': intent.time_range
        }
    
    def _translate_find_unstable(self, intent: QueryIntent) -> Dict[str, Any]:
        """Translate instability search"""
        return {
            'type': 'stability_analysis',
            'entity_type': intent.entity or 'species',
            'command': 'analyze_reclassifications',
            'filters': intent.filters,
            'threshold': 2  # Number of changes to be considered unstable
        }
    
    def _translate_cross_host(self, intent: QueryIntent) -> Dict[str, Any]:
        """Translate cross-host search"""
        return {
            'type': 'host_search',
            'hosts': [intent.entity] + list(intent.filters.values()),
            'command': 'search_by_host',
            'intersection': True
        }
    
    def _translate_similarity_search(self, intent: QueryIntent) -> Dict[str, Any]:
        """Translate similarity search"""
        return {
            'type': 'similarity_search',
            'reference': intent.entity,
            'command': 'find_similar_species',
            'similarity_threshold': 0.8
        }
    
    def _translate_temporal_query(self, intent: QueryIntent) -> Dict[str, Any]:
        """Translate temporal queries"""
        return {
            'type': 'temporal_search',
            'time_range': intent.time_range,
            'command': 'search_by_discovery_date',
            'filters': intent.filters
        }
    
    def _translate_classification_level(self, intent: QueryIntent) -> Dict[str, Any]:
        """Translate classification level queries"""
        return {
            'type': 'hierarchy_search',
            'level': self._determine_taxonomic_level(intent.entity),
            'parent': intent.filters.get('parent'),
            'command': 'search_taxonomic_level'
        }
    
    def _translate_general_search(self, intent: QueryIntent) -> Dict[str, Any]:
        """Translate general search queries"""
        return {
            'type': 'general_search',
            'query': intent.entity,
            'filters': intent.filters,
            'command': 'full_text_search'
        }
    
    def _determine_taxonomic_level(self, entity: str) -> str:
        """Determine taxonomic level from entity"""
        if not entity:
            return 'species'
        
        entity_lower = entity.lower()
        if 'family' in entity_lower or entity_lower.endswith('viridae'):
            return 'family'
        elif 'genus' in entity_lower or entity_lower.endswith('virus'):
            return 'genus'
        elif 'order' in entity_lower or entity_lower.endswith('virales'):
            return 'order'
        else:
            return 'species'


class NaturalLanguageQuery:
    """Main interface for natural language querying"""
    
    def __init__(self, git_repo_path: str, use_openai: bool = False):
        self.git_repo_path = git_repo_path
        self.parser = QueryIntentParser(use_openai=use_openai)
        self.translator = StructuredQueryTranslator(git_repo_path)
        self.executor = QueryExecutor(git_repo_path)
        self.formatter = ResponseFormatter()
        
    def query(self, natural_language_query: str) -> str:
        """Process natural language query and return natural language response"""
        start_time = datetime.now()
        
        try:
            # Step 1: Parse intent
            intent = self.parser.parse(natural_language_query)
            
            # Step 2: Translate to structured query
            structured_query = self.translator.translate(intent)
            
            # Step 3: Execute query
            raw_results = self.executor.execute(structured_query)
            
            # Step 4: Format response
            execution_time = (datetime.now() - start_time).total_seconds()
            
            result = QueryResult(
                data=raw_results,
                query_type=intent.action,
                entity_count=len(raw_results) if isinstance(raw_results, list) else 1,
                execution_time=execution_time,
                confidence=0.8  # TODO: Implement confidence scoring
            )
            
            return self.formatter.format_response(result, natural_language_query)
            
        except Exception as e:
            return f"Sorry, I couldn't process your query. Error: {str(e)}"


class QueryExecutor:
    """Execute structured queries against the git repository"""
    
    def __init__(self, git_repo_path: str):
        self.git_repo_path = Path(git_repo_path)
        self.git_interface = GitInterface(git_repo_path)
    
    def execute(self, structured_query: Dict[str, Any]) -> Any:
        """Execute structured query and return results"""
        query_type = structured_query['type']
        
        executor_map = {
            'git_history': self._execute_git_history,
            'stability_analysis': self._execute_stability_analysis,
            'host_search': self._execute_host_search,
            'similarity_search': self._execute_similarity_search,
            'temporal_search': self._execute_temporal_search,
            'hierarchy_search': self._execute_hierarchy_search,
            'general_search': self._execute_general_search
        }
        
        executor = executor_map.get(query_type, self._execute_general_search)
        return executor(structured_query)
    
    def _execute_git_history(self, query: Dict[str, Any]) -> List[Dict]:
        """Execute git history query"""
        entity = query['entity']
        if not entity:
            return []
        
        # Simplified implementation - would need to search for entity in git history
        history = []
        try:
            # This is a placeholder - real implementation would search git logs
            history = [
                {
                    'version': 'MSL38',
                    'date': '2022-03-15',
                    'change': f'{entity} classification updated',
                    'details': 'Family assignment changed'
                }
            ]
        except Exception as e:
            print(f"Error executing git history: {e}")
        
        return history
    
    def _execute_stability_analysis(self, query: Dict[str, Any]) -> List[Dict]:
        """Execute stability analysis"""
        # This would integrate with our stability analysis
        # For now, return placeholder data
        return [
            {
                'species': 'Tobacco mosaic virus',
                'family': 'Virgaviridae',
                'changes': 0,
                'stability_score': 1.0
            },
            {
                'species': 'Streptomyces virus Yaboi',
                'family': 'Stanwilliamsviridae',
                'changes': 2,
                'stability_score': 0.3
            }
        ]
    
    def _execute_host_search(self, query: Dict[str, Any]) -> List[Dict]:
        """Execute host-based search"""
        # Placeholder implementation
        return [
            {
                'species': 'Example virus',
                'hosts': ['host1', 'host2'],
                'family': 'Exampleviridae'
            }
        ]
    
    def _execute_similarity_search(self, query: Dict[str, Any]) -> List[Dict]:
        """Execute similarity search"""
        return [
            {
                'species': 'Similar virus 1',
                'similarity': 0.85,
                'family': 'Same family'
            }
        ]
    
    def _execute_temporal_search(self, query: Dict[str, Any]) -> List[Dict]:
        """Execute temporal search"""
        return [
            {
                'species': 'Recently discovered virus',
                'discovery_year': 2023,
                'family': 'Newviridae'
            }
        ]
    
    def _execute_hierarchy_search(self, query: Dict[str, Any]) -> List[Dict]:
        """Execute hierarchical search"""
        return [
            {
                'name': 'Example genus',
                'level': 'genus',
                'parent': 'Example family',
                'species_count': 42
            }
        ]
    
    def _execute_general_search(self, query: Dict[str, Any]) -> List[Dict]:
        """Execute general search"""
        return [
            {
                'species': 'Search result',
                'relevance': 0.9,
                'match_type': 'name'
            }
        ]


class ResponseFormatter:
    """Format query results into natural language responses"""
    
    def format_response(self, result: QueryResult, original_query: str) -> str:
        """Format query result into natural language"""
        
        if result.entity_count == 0:
            return "I couldn't find any results for your query. Try rephrasing or being more specific."
        
        formatter_map = {
            'track_history': self._format_history_response,
            'find_unstable': self._format_stability_response,
            'cross_host': self._format_host_response,
            'similarity_search': self._format_similarity_response,
            'temporal_query': self._format_temporal_response,
            'classification_level': self._format_hierarchy_response,
            'general_search': self._format_general_response
        }
        
        formatter = formatter_map.get(result.query_type, self._format_general_response)
        response = formatter(result)
        
        # Add metadata
        response += f"\n\n(Found {result.entity_count} results in {result.execution_time:.2f} seconds)"
        
        return response
    
    def _format_history_response(self, result: QueryResult) -> str:
        """Format history tracking response"""
        if not result.data:
            return "No classification history found for this entity."
        
        response = "Here's the classification history:\n\n"
        for item in result.data:
            response += f"• {item['date']}: {item['change']}\n"
        
        return response
    
    def _format_stability_response(self, result: QueryResult) -> str:
        """Format stability analysis response"""
        if not result.data:
            return "No instability data found."
        
        unstable = [item for item in result.data if item['changes'] > 1]
        stable = [item for item in result.data if item['changes'] <= 1]
        
        response = f"Found {len(unstable)} unstable and {len(stable)} stable classifications:\n\n"
        
        if unstable:
            response += "**Unstable classifications:**\n"
            for item in unstable[:5]:  # Show top 5
                response += f"• {item['species']}: {item['changes']} changes (stability: {item['stability_score']:.1f})\n"
        
        return response
    
    def _format_host_response(self, result: QueryResult) -> str:
        """Format host search response"""
        if not result.data:
            return "No viruses found with those host requirements."
        
        response = f"Found {len(result.data)} viruses:\n\n"
        for item in result.data[:10]:  # Show top 10
            hosts = ', '.join(item['hosts'])
            response += f"• {item['species']} (Family: {item['family']}) - Hosts: {hosts}\n"
        
        return response
    
    def _format_similarity_response(self, result: QueryResult) -> str:
        """Format similarity search response"""
        if not result.data:
            return "No similar viruses found."
        
        response = "Similar viruses:\n\n"
        for item in sorted(result.data, key=lambda x: x['similarity'], reverse=True)[:10]:
            response += f"• {item['species']} (similarity: {item['similarity']:.1%})\n"
        
        return response
    
    def _format_temporal_response(self, result: QueryResult) -> str:
        """Format temporal query response"""
        if not result.data:
            return "No viruses found in that time period."
        
        response = f"Viruses discovered in the specified period:\n\n"
        for item in result.data[:10]:
            response += f"• {item['species']} ({item['discovery_year']}) - Family: {item['family']}\n"
        
        return response
    
    def _format_hierarchy_response(self, result: QueryResult) -> str:
        """Format hierarchy search response"""
        if not result.data:
            return "No taxonomic groups found."
        
        response = "Taxonomic groups:\n\n"
        for item in result.data[:10]:
            response += f"• {item['name']} ({item['level']}) - {item.get('species_count', 'Unknown')} species\n"
        
        return response
    
    def _format_general_response(self, result: QueryResult) -> str:
        """Format general search response"""
        if not result.data:
            return "No results found."
        
        response = "Search results:\n\n"
        for item in result.data[:10]:
            response += f"• {item.get('species', item.get('name', 'Unknown'))}\n"
        
        return response


# For testing
if __name__ == "__main__":
    # Simple test
    nlq = NaturalLanguageQuery("output/git_taxonomy")
    
    test_queries = [
        "What happened to bacteriophage T4?",
        "Show me unstable coronaviruses",
        "Which viruses infect both plants and animals?",
        "Viruses discovered in 2023"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print(f"Response: {nlq.query(query)}")
        print("-" * 50)