"""
Search API - Advanced search and filtering

Provides comprehensive search capabilities across the 20-year taxonomy dataset
with support for complex queries, faceted search, and performance optimization.
"""

from typing import List, Dict, Optional, Set, Union
from pathlib import Path
import yaml
import json
import re
from collections import defaultdict, Counter


class SearchAPI:
    """Advanced search and filtering API"""
    
    def __init__(self, taxonomy_repo_path: str):
        """Initialize with path to complete 20-year taxonomy repository"""
        self.repo_path = Path(taxonomy_repo_path)
        self.families_path = self.repo_path / "families"
        self._search_index = None
        self._metadata_cache = None
    
    def build_search_index(self, force_rebuild: bool = False) -> Dict:
        """
        Build search index for faster queries
        
        Args:
            force_rebuild: Force rebuild even if index exists
            
        Returns:
            Index building statistics
        """
        if self._search_index and not force_rebuild:
            return {'status': 'index_already_exists', 'entries': len(self._search_index)}
        
        index = {
            'species': {},          # scientific_name -> full_data
            'families': {},         # family_name -> species_list
            'genera': {},           # genus_name -> species_list
            'keywords': defaultdict(set),  # keyword -> species_set
            'metadata': {}          # Additional metadata
        }
        
        species_count = 0
        family_count = 0
        genus_count = 0
        
        for family_path in self.families_path.glob("*"):
            if not family_path.is_dir():
                continue
            
            family_name = family_path.name
            family_count += 1
            index['families'][family_name] = []
            
            genera_path = family_path / "genera"
            if not genera_path.exists():
                continue
            
            for genus_path in genera_path.glob("*"):
                if not genus_path.is_dir():
                    continue
                
                genus_name = genus_path.name
                genus_count += 1
                if genus_name not in index['genera']:
                    index['genera'][genus_name] = []
                
                species_path = genus_path / "species"
                if not species_path.exists():
                    continue
                
                for species_file in species_path.glob("*.yaml"):
                    try:
                        with open(species_file) as f:
                            species_data = yaml.safe_load(f)
                        
                        scientific_name = species_data.get('scientific_name', '')
                        if not scientific_name:
                            continue
                        
                        # Add taxonomic context
                        species_data['_search_metadata'] = {
                            'family': family_name,
                            'genus': genus_name,
                            'file_path': str(species_file.relative_to(self.repo_path))
                        }
                        
                        # Index by scientific name
                        index['species'][scientific_name] = species_data
                        
                        # Add to family and genus lists
                        index['families'][family_name].append(scientific_name)
                        index['genera'][genus_name].append(scientific_name)
                        
                        # Index keywords from scientific name
                        words = re.findall(r'\w+', scientific_name.lower())
                        for word in words:
                            if len(word) > 2:  # Skip very short words
                                index['keywords'][word].add(scientific_name)
                        
                        # Index from other text fields
                        for field in ['genus', 'family']:
                            if field in species_data.get('taxonomy', {}):
                                value = species_data['taxonomy'][field].lower()
                                index['keywords'][value].add(scientific_name)
                        
                        species_count += 1
                        
                    except Exception as e:
                        print(f"Warning: Failed to index {species_file}: {e}")
                        continue
        
        # Convert sets to lists for JSON serialization
        for keyword in index['keywords']:
            index['keywords'][keyword] = list(index['keywords'][keyword])
        
        # Store metadata
        index['metadata'] = {
            'total_species': species_count,
            'total_families': family_count,
            'total_genera': genus_count,
            'keywords_count': len(index['keywords']),
            'build_timestamp': str(Path().resolve())  # Simple timestamp
        }
        
        self._search_index = index
        return {
            'status': 'index_built',
            'statistics': index['metadata']
        }
    
    def search_species(self, 
                      query: str,
                      family_filter: Optional[str] = None,
                      genus_filter: Optional[str] = None,
                      exact_match: bool = False,
                      limit: int = 100) -> Dict:
        """
        Search species with advanced filtering
        
        Args:
            query: Search query
            family_filter: Filter by family name
            genus_filter: Filter by genus name
            exact_match: Require exact name match
            limit: Maximum results
            
        Returns:
            Search results with metadata
        """
        if not self._search_index:
            self.build_search_index()
        
        results = []
        query_lower = query.lower()
        
        # Get candidate species from index
        candidates = set()
        
        if exact_match:
            # Exact match search
            for species_name in self._search_index['species']:
                if query_lower == species_name.lower():
                    candidates.add(species_name)
        else:
            # Keyword-based search
            query_words = re.findall(r'\w+', query_lower)
            
            if query_words:
                # Find species matching any keyword
                for word in query_words:
                    if word in self._search_index['keywords']:
                        candidates.update(self._search_index['keywords'][word])
                
                # Also do substring search on species names
                for species_name in self._search_index['species']:
                    if query_lower in species_name.lower():
                        candidates.add(species_name)
        
        # Apply filters
        filtered_candidates = []
        for species_name in candidates:
            species_data = self._search_index['species'][species_name]
            metadata = species_data['_search_metadata']
            
            # Apply family filter
            if family_filter and metadata['family'].lower() != family_filter.lower():
                continue
            
            # Apply genus filter
            if genus_filter and metadata['genus'].lower() != genus_filter.lower():
                continue
            
            filtered_candidates.append(species_name)
        
        # Sort by relevance (simple scoring)
        def relevance_score(species_name):
            score = 0
            name_lower = species_name.lower()
            
            # Exact match gets highest score
            if query_lower == name_lower:
                score += 100
            
            # Starting with query gets high score
            if name_lower.startswith(query_lower):
                score += 50
            
            # Contains query gets medium score
            if query_lower in name_lower:
                score += 25
            
            # Word matches get lower scores
            query_words = query_lower.split()
            name_words = name_lower.split()
            for qword in query_words:
                for nword in name_words:
                    if qword in nword:
                        score += 10
            
            return score
        
        # Sort and limit results
        filtered_candidates.sort(key=relevance_score, reverse=True)
        limited_candidates = filtered_candidates[:limit]
        
        # Build result objects
        for species_name in limited_candidates:
            species_data = self._search_index['species'][species_name].copy()
            species_data['_relevance_score'] = relevance_score(species_name)
            results.append(species_data)
        
        return {
            'query': query,
            'total_matches': len(filtered_candidates),
            'returned_count': len(results),
            'results': results,
            'filters_applied': {
                'family': family_filter,
                'genus': genus_filter,
                'exact_match': exact_match
            },
            'search_metadata': {
                'index_size': self._search_index['metadata']['total_species'],
                'candidates_found': len(candidates),
                'after_filtering': len(filtered_candidates)
            }
        }
    
    def get_facets(self) -> Dict:
        """
        Get search facets for filtering options
        
        Returns:
            Available facets with counts
        """
        if not self._search_index:
            self.build_search_index()
        
        facets = {
            'families': {},
            'genera': {},
            'msl_versions': Counter(),
            'eras': Counter()
        }
        
        # Count families
        for family_name, species_list in self._search_index['families'].items():
            facets['families'][family_name] = len(species_list)
        
        # Count genera
        for genus_name, species_list in self._search_index['genera'].items():
            facets['genera'][genus_name] = len(species_list)
        
        # Count MSL versions and eras from species data
        for species_data in self._search_index['species'].values():
            classification = species_data.get('classification', {})
            historical = species_data.get('historical_context', {})
            
            msl_version = classification.get('msl_version', 'unknown')
            facets['msl_versions'][msl_version] += 1
            
            era = historical.get('era', 'unknown')
            facets['eras'][era] += 1
        
        # Convert counters to sorted dictionaries
        facets['msl_versions'] = dict(facets['msl_versions'].most_common())
        facets['eras'] = dict(facets['eras'].most_common())
        
        return facets
    
    def search_by_facets(self, facet_filters: Dict, limit: int = 100) -> Dict:
        """
        Search using faceted filters
        
        Args:
            facet_filters: Dictionary of facet filters
            limit: Maximum results
            
        Returns:
            Filtered results
        """
        if not self._search_index:
            self.build_search_index()
        
        results = []
        
        for species_name, species_data in self._search_index['species'].items():
            include = True
            metadata = species_data['_search_metadata']
            classification = species_data.get('classification', {})
            historical = species_data.get('historical_context', {})
            
            # Apply filters
            if 'family' in facet_filters:
                if metadata['family'].lower() != facet_filters['family'].lower():
                    include = False
            
            if 'genus' in facet_filters:
                if metadata['genus'].lower() != facet_filters['genus'].lower():
                    include = False
            
            if 'msl_version' in facet_filters:
                if classification.get('msl_version') != facet_filters['msl_version']:
                    include = False
            
            if 'era' in facet_filters:
                if historical.get('era') != facet_filters['era']:
                    include = False
            
            if include:
                results.append(species_data)
                
                if len(results) >= limit:
                    break
        
        return {
            'facet_filters': facet_filters,
            'total_matches': len(results),
            'results': results
        }
    
    def get_family_summary(self, family_name: str) -> Dict:
        """
        Get comprehensive summary of a viral family
        
        Args:
            family_name: Name of the viral family
            
        Returns:
            Family summary with statistics and species list
        """
        if not self._search_index:
            self.build_search_index()
        
        family_lower = family_name.lower()
        
        if family_lower not in self._search_index['families']:
            return {'error': f'Family {family_name} not found'}
        
        species_names = self._search_index['families'][family_lower]
        
        # Collect detailed statistics
        genera = set()
        msl_versions = Counter()
        eras = Counter()
        species_details = []
        
        for species_name in species_names:
            species_data = self._search_index['species'][species_name]
            metadata = species_data['_search_metadata']
            classification = species_data.get('classification', {})
            historical = species_data.get('historical_context', {})
            
            genera.add(metadata['genus'])
            msl_versions[classification.get('msl_version', 'unknown')] += 1
            eras[historical.get('era', 'unknown')] += 1
            
            species_details.append({
                'scientific_name': species_name,
                'genus': metadata['genus'],
                'msl_version': classification.get('msl_version'),
                'era': historical.get('era')
            })
        
        return {
            'family_name': family_name,
            'statistics': {
                'total_species': len(species_names),
                'total_genera': len(genera),
                'genera_list': sorted(list(genera)),
                'msl_distribution': dict(msl_versions.most_common()),
                'era_distribution': dict(eras.most_common())
            },
            'species': species_details
        }
    
    def advanced_search(self, search_params: Dict) -> Dict:
        """
        Advanced search with multiple parameters
        
        Args:
            search_params: Complex search parameters
            
        Returns:
            Advanced search results
        """
        # Extract parameters
        text_query = search_params.get('query', '')
        filters = search_params.get('filters', {})
        sort_by = search_params.get('sort_by', 'relevance')
        limit = search_params.get('limit', 100)
        
        # Start with text search if provided
        if text_query:
            results = self.search_species(
                query=text_query,
                family_filter=filters.get('family'),
                genus_filter=filters.get('genus'),
                limit=limit * 2  # Get more for post-filtering
            )
            candidates = results['results']
        else:
            # Use all species as candidates
            if not self._search_index:
                self.build_search_index()
            candidates = list(self._search_index['species'].values())
        
        # Apply additional filters
        filtered_results = []
        for species_data in candidates:
            include = True
            classification = species_data.get('classification', {})
            historical = species_data.get('historical_context', {})
            
            # MSL version filter
            if 'msl_version' in filters:
                if classification.get('msl_version') != filters['msl_version']:
                    include = False
            
            # Era filter
            if 'era' in filters:
                if historical.get('era') != filters['era']:
                    include = False
            
            # Year range filter
            if 'year_range' in filters:
                year_range = filters['year_range']
                species_year = classification.get('msl_year', 0)
                if species_year < year_range.get('start', 0) or species_year > year_range.get('end', 9999):
                    include = False
            
            if include:
                filtered_results.append(species_data)
        
        # Sort results
        if sort_by == 'alphabetical':
            filtered_results.sort(key=lambda x: x.get('scientific_name', ''))
        elif sort_by == 'year':
            filtered_results.sort(key=lambda x: x.get('classification', {}).get('msl_year', 0))
        elif sort_by == 'family':
            filtered_results.sort(key=lambda x: x.get('_search_metadata', {}).get('family', ''))
        # Default: relevance (already sorted from text search)
        
        # Apply limit
        final_results = filtered_results[:limit]
        
        return {
            'search_params': search_params,
            'total_matches': len(filtered_results),
            'returned_count': len(final_results),
            'results': final_results,
            'applied_filters': filters,
            'sort_order': sort_by
        }
    
    def get_search_statistics(self) -> Dict:
        """Get comprehensive search index statistics"""
        if not self._search_index:
            self.build_search_index()
        
        return {
            'index_metadata': self._search_index['metadata'],
            'coverage': {
                'families_indexed': len(self._search_index['families']),
                'genera_indexed': len(self._search_index['genera']),
                'species_indexed': len(self._search_index['species']),
                'keywords_indexed': len(self._search_index['keywords'])
            },
            'top_families': dict(Counter({
                family: len(species_list) 
                for family, species_list in self._search_index['families'].items()
            }).most_common(10)),
            'repository_path': str(self.repo_path)
        }