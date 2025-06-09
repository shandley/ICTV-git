"""
Taxonomy API - Core taxonomic data access endpoints

Provides REST API access to viral taxonomy classification data
across all 20 years of ICTV Master Species Lists.
"""

from typing import List, Dict, Optional, Union
from pathlib import Path
import yaml
import json
from datetime import datetime
import re


class TaxonomyAPI:
    """Core taxonomy data access API"""
    
    def __init__(self, taxonomy_repo_path: str):
        """Initialize with path to complete 20-year taxonomy repository"""
        self.repo_path = Path(taxonomy_repo_path)
        self.families_path = self.repo_path / "families"
        self._load_metadata()
    
    def _load_metadata(self):
        """Load repository metadata"""
        try:
            metadata_path = self.repo_path / "release_metadata.json"
            if metadata_path.exists():
                with open(metadata_path) as f:
                    self.metadata = json.load(f)
            else:
                self.metadata = {"msl_version": "unknown", "species_count": 0}
        except Exception:
            self.metadata = {"msl_version": "unknown", "species_count": 0}
    
    def get_species(self, scientific_name: str, msl_version: Optional[str] = None) -> Optional[Dict]:
        """
        Get species data by scientific name
        
        Args:
            scientific_name: Scientific name of the species
            msl_version: Specific MSL version (defaults to current)
            
        Returns:
            Species data dictionary or None if not found
        """
        # Search through families/genera structure
        for family_path in self.families_path.glob("*"):
            if not family_path.is_dir():
                continue
                
            for genus_path in (family_path / "genera").glob("*"):
                if not genus_path.is_dir():
                    continue
                    
                for species_file in (genus_path / "species").glob("*.yaml"):
                    try:
                        with open(species_file) as f:
                            species_data = yaml.safe_load(f)
                            
                        if species_data.get('scientific_name') == scientific_name:
                            # Add path information
                            species_data['_api_metadata'] = {
                                'family': family_path.name,
                                'genus': genus_path.name,
                                'file_path': str(species_file.relative_to(self.repo_path))
                            }
                            return species_data
                    except Exception:
                        continue
        
        return None
    
    def get_family(self, family_name: str) -> Optional[Dict]:
        """
        Get complete family data including all genera and species
        
        Args:
            family_name: Name of the viral family
            
        Returns:
            Family data with nested genera and species
        """
        family_path = self.families_path / family_name.lower()
        if not family_path.exists():
            return None
        
        family_data = {
            'name': family_name,
            'genera': {},
            'species_count': 0
        }
        
        genera_path = family_path / "genera"
        if not genera_path.exists():
            return family_data
        
        for genus_path in genera_path.glob("*"):
            if not genus_path.is_dir():
                continue
                
            genus_name = genus_path.name
            genus_data = {
                'name': genus_name,
                'species': []
            }
            
            species_path = genus_path / "species"
            if species_path.exists():
                for species_file in species_path.glob("*.yaml"):
                    try:
                        with open(species_file) as f:
                            species_data = yaml.safe_load(f)
                        genus_data['species'].append(species_data)
                        family_data['species_count'] += 1
                    except Exception:
                        continue
            
            family_data['genera'][genus_name] = genus_data
        
        return family_data
    
    def search_species(self, 
                      query: str,
                      family: Optional[str] = None,
                      genus: Optional[str] = None,
                      limit: int = 100) -> List[Dict]:
        """
        Search species by name pattern
        
        Args:
            query: Search query (supports partial matching)
            family: Filter by family name
            genus: Filter by genus name  
            limit: Maximum results to return
            
        Returns:
            List of matching species
        """
        results = []
        query_lower = query.lower()
        
        # Determine search scope
        family_paths = []
        if family:
            family_path = self.families_path / family.lower()
            if family_path.exists():
                family_paths.append(family_path)
        else:
            family_paths = [p for p in self.families_path.glob("*") if p.is_dir()]
        
        for family_path in family_paths:
            genera_path = family_path / "genera"
            if not genera_path.exists():
                continue
            
            # Determine genus scope
            genus_paths = []
            if genus:
                genus_path = genera_path / genus.lower()
                if genus_path.exists():
                    genus_paths.append(genus_path)
            else:
                genus_paths = [p for p in genera_path.glob("*") if p.is_dir()]
            
            for genus_path in genus_paths:
                species_path = genus_path / "species"
                if not species_path.exists():
                    continue
                
                for species_file in species_path.glob("*.yaml"):
                    try:
                        with open(species_file) as f:
                            species_data = yaml.safe_load(f)
                        
                        # Check if query matches scientific name
                        scientific_name = species_data.get('scientific_name', '')
                        if query_lower in scientific_name.lower():
                            species_data['_api_metadata'] = {
                                'family': family_path.name,
                                'genus': genus_path.name,
                                'file_path': str(species_file.relative_to(self.repo_path))
                            }
                            results.append(species_data)
                            
                            if len(results) >= limit:
                                return results
                    except Exception:
                        continue
        
        return results
    
    def get_taxonomy_hierarchy(self) -> Dict:
        """
        Get complete taxonomy hierarchy structure
        
        Returns:
            Nested hierarchy of all families, genera, and species counts
        """
        hierarchy = {
            'families': {},
            'total_families': 0,
            'total_genera': 0,
            'total_species': 0,
            'repository_metadata': self.metadata
        }
        
        for family_path in self.families_path.glob("*"):
            if not family_path.is_dir():
                continue
            
            family_name = family_path.name
            family_data = {
                'genera': {},
                'genera_count': 0,
                'species_count': 0
            }
            
            genera_path = family_path / "genera"
            if genera_path.exists():
                for genus_path in genera_path.glob("*"):
                    if not genus_path.is_dir():
                        continue
                    
                    genus_name = genus_path.name
                    species_count = 0
                    
                    species_path = genus_path / "species"
                    if species_path.exists():
                        species_count = len(list(species_path.glob("*.yaml")))
                    
                    family_data['genera'][genus_name] = {
                        'species_count': species_count
                    }
                    family_data['genera_count'] += 1
                    family_data['species_count'] += species_count
                    hierarchy['total_species'] += species_count
                
                hierarchy['total_genera'] += family_data['genera_count']
            
            hierarchy['families'][family_name] = family_data
            hierarchy['total_families'] += 1
        
        return hierarchy
    
    def get_families_list(self) -> List[str]:
        """Get list of all family names"""
        families = []
        for family_path in self.families_path.glob("*"):
            if family_path.is_dir():
                families.append(family_path.name)
        return sorted(families)
    
    def get_genera_list(self, family: Optional[str] = None) -> List[str]:
        """Get list of genera, optionally filtered by family"""
        genera = []
        
        if family:
            family_path = self.families_path / family.lower()
            genera_path = family_path / "genera"
            if genera_path.exists():
                for genus_path in genera_path.glob("*"):
                    if genus_path.is_dir():
                        genera.append(genus_path.name)
        else:
            for family_path in self.families_path.glob("*"):
                if not family_path.is_dir():
                    continue
                genera_path = family_path / "genera"
                if genera_path.exists():
                    for genus_path in genera_path.glob("*"):
                        if genus_path.is_dir():
                            genera.append(genus_path.name)
        
        return sorted(genera)
    
    def validate_classification(self, classification_data: Dict) -> Dict:
        """
        Validate a taxonomic classification
        
        Args:
            classification_data: Dictionary with taxonomic ranks
            
        Returns:
            Validation result with status and details
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }
        
        # Check required fields
        required_fields = ['scientific_name']
        for field in required_fields:
            if field not in classification_data:
                result['valid'] = False
                result['errors'].append(f"Missing required field: {field}")
        
        # Validate taxonomy hierarchy if provided
        if 'taxonomy' in classification_data:
            taxonomy = classification_data['taxonomy']
            
            # Check family exists
            if 'family' in taxonomy:
                family_name = taxonomy['family'].lower()
                if not (self.families_path / family_name).exists():
                    result['warnings'].append(f"Family '{taxonomy['family']}' not found in current taxonomy")
            
            # Check genus exists within family
            if 'family' in taxonomy and 'genus' in taxonomy:
                family_path = self.families_path / taxonomy['family'].lower()
                genus_path = family_path / "genera" / taxonomy['genus'].lower()
                if not genus_path.exists():
                    result['warnings'].append(f"Genus '{taxonomy['genus']}' not found in family '{taxonomy['family']}'")
        
        return result