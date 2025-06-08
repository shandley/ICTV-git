"""
Convert MSL data to git-based taxonomy structure.

This module creates a git repository with taxonomic hierarchy
as directory structure and species as YAML files.
"""

import os
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Set
import logging
import yaml
import git
from datetime import datetime
from collections import defaultdict

from ..parsers.msl_parser import VirusSpecies, MSLParser

# Set up logging
logger = logging.getLogger(__name__)


class MSLToGitConverter:
    """Convert MSL data to git repository structure."""
    
    # Taxonomic rank order (highest to lowest)
    RANK_ORDER = [
        'realm', 'subrealm', 'kingdom', 'subkingdom',
        'phylum', 'subphylum', 'class', 'subclass',
        'order', 'suborder', 'family', 'subfamily',
        'genus', 'subgenus'
    ]
    
    def __init__(self, repo_path: str, initialize: bool = True):
        """
        Initialize converter with repository path.
        
        Args:
            repo_path: Path where git repository will be created
            initialize: Whether to initialize a new git repo
        """
        self.repo_path = Path(repo_path)
        self.repo = None
        
        if initialize:
            self._initialize_repository()
    
    def _initialize_repository(self) -> None:
        """Initialize git repository structure."""
        # Create directory if it doesn't exist
        self.repo_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize git repo if not already initialized
        git_dir = self.repo_path / '.git'
        if not git_dir.exists():
            self.repo = git.Repo.init(self.repo_path)
            logger.info(f"Initialized git repository at {self.repo_path}")
        else:
            self.repo = git.Repo(self.repo_path)
            logger.info(f"Using existing git repository at {self.repo_path}")
        
        # Create base directories
        base_dirs = ['realms', 'evidence', 'metadata']
        for dir_name in base_dirs:
            dir_path = self.repo_path / dir_name
            dir_path.mkdir(exist_ok=True)
        
        # Create README
        readme_path = self.repo_path / 'README.md'
        if not readme_path.exists():
            readme_content = """# ICTV Viral Taxonomy Repository

This repository contains the International Committee on Taxonomy of Viruses (ICTV)
Master Species List in a git-versioned format.

## Structure

- `realms/` - Taxonomic hierarchy organized as directory structure
- `evidence/` - Supporting data (phylogenies, genomes, proposals)
- `metadata/` - Repository metadata and statistics

## Usage

Each virus species is stored as a YAML file at its taxonomic location.
Git history tracks all changes to viral taxonomy over time.
"""
            readme_path.write_text(readme_content)
    
    def _clean_name_for_path(self, name: str) -> str:
        """Clean taxonomic name for use in file paths."""
        if not name:
            return ""
        
        # Convert to lowercase and replace problematic characters
        clean = name.lower()
        clean = clean.replace(' ', '_')
        clean = clean.replace('/', '_')
        clean = clean.replace('\\', '_')
        clean = clean.replace(':', '_')
        clean = clean.replace('*', '_')
        clean = clean.replace('?', '_')
        clean = clean.replace('"', '_')
        clean = clean.replace('<', '_')
        clean = clean.replace('>', '_')
        clean = clean.replace('|', '_')
        clean = clean.replace('(', '_')
        clean = clean.replace(')', '_')
        clean = clean.replace('[', '_')
        clean = clean.replace(']', '_')
        clean = clean.replace(',', '_')
        clean = clean.replace(';', '_')
        clean = clean.replace("'", '_')
        
        # Remove multiple underscores
        while '__' in clean:
            clean = clean.replace('__', '_')
        
        # Remove leading/trailing underscores
        clean = clean.strip('_')
        
        return clean
    
    def _get_species_path(self, species: VirusSpecies) -> Path:
        """Generate file path for a species based on its taxonomy."""
        path_parts = ['realms']
        
        # Build path from taxonomic hierarchy
        for rank in self.RANK_ORDER:
            value = getattr(species, rank if rank != 'class' else 'class_')
            if value:
                # Add rank directory and specific taxon directory
                clean_name = self._clean_name_for_path(value)
                # Use singular form for rank directories
                rank_dir = rank + 's' if not rank.endswith('s') else rank + 'es'
                path_parts.extend([rank_dir, clean_name])
        
        # Add species directory and file
        path_parts.append('species')
        species_file = self._clean_name_for_path(species.species) + '.yaml'
        
        return Path(*path_parts) / species_file
    
    def _create_species_yaml(self, species: VirusSpecies) -> Dict:
        """Create YAML content for a species."""
        # Build classification hierarchy
        classification = {}
        for rank in self.RANK_ORDER:
            value = getattr(species, rank if rank != 'class' else 'class_')
            if value:
                classification[rank] = value
        
        # Core data structure
        data = {
            'species_name': species.species,
            'classification': classification,
            'metadata': {
                'sort_index': species.sort,
                'last_change': species.last_change,
                'msl_of_last_change': species.msl_of_last_change,
                'proposal': species.proposal,
                'taxon_history_url': species.taxon_history_url
            }
        }
        
        # Add genome information if available
        if species.genome_composition:
            data['genome'] = {
                'composition': species.genome_composition
            }
        
        # Remove None values from metadata
        data['metadata'] = {k: v for k, v in data['metadata'].items() if v is not None}
        
        return data
    
    def convert_msl_file(self, msl_file: str, msl_version: str, 
                        commit_message: Optional[str] = None) -> int:
        """
        Convert an MSL file to git repository structure.
        
        Args:
            msl_file: Path to MSL Excel file
            msl_version: Version string (e.g., 'MSL36')
            commit_message: Optional custom commit message
            
        Returns:
            Number of species processed
        """
        logger.info(f"Converting {msl_version} from {msl_file}")
        
        # Parse MSL file
        parser = MSLParser(msl_file)
        parser.load_file()
        parser.parse_sheet()
        species_list = parser.extract_species()
        stats = parser.get_summary_stats()
        
        logger.info(f"Processing {len(species_list)} species")
        
        # Track created files
        created_files = []
        
        # Process each species
        for species in species_list:
            # Get path for this species
            species_path = self._get_species_path(species)
            full_path = self.repo_path / species_path
            
            # Create directory structure
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create YAML content
            yaml_data = self._create_species_yaml(species)
            
            # Write YAML file
            yaml_content = yaml.dump(yaml_data, default_flow_style=False, 
                                   sort_keys=False, allow_unicode=True)
            full_path.write_text(yaml_content)
            
            created_files.append(species_path)
        
        # Create metadata file for this version
        metadata_path = self.repo_path / 'metadata' / f'{msl_version.lower()}_stats.yaml'
        metadata = {
            'version': msl_version,
            'date_processed': datetime.now().isoformat(),
            'source_file': Path(msl_file).name,
            'statistics': {
                'total_species': stats['total_species'],
                'realms': stats['realms'],
                'families': stats['families'],
                'genera': stats['genera'],
                'unique_realms': stats.get('unique_realms', []),
            },
            'species_count': len(species_list)
        }
        
        metadata_yaml = yaml.dump(metadata, default_flow_style=False, sort_keys=False)
        metadata_path.write_text(metadata_yaml)
        created_files.append(Path('metadata') / f'{msl_version.lower()}_stats.yaml')
        
        # Stage all files for commit
        if self.repo:
            # Add all created files
            self.repo.index.add([str(f) for f in created_files])
            
            # Create commit
            if not commit_message:
                commit_message = f"""Import {msl_version} taxonomy data

Imported {len(species_list)} virus species from {Path(msl_file).name}
- Realms: {stats['realms']}
- Families: {stats['families']}  
- Genera: {stats['genera']}

Source: ICTV Master Species List {msl_version}
"""
            
            self.repo.index.commit(commit_message)
            
            # Create tag for this version
            tag_name = msl_version.lower()
            self.repo.create_tag(tag_name, message=f"ICTV {msl_version} release")
            
            logger.info(f"Created commit and tag for {msl_version}")
        
        return len(species_list)
    
    def get_taxonomy_stats(self) -> Dict:
        """Get statistics about the current taxonomy structure."""
        stats = {
            'total_species': 0,
            'realms': defaultdict(int),
            'families': defaultdict(int),
            'genera': defaultdict(int),
            'deepest_path': 0
        }
        
        # Walk through species files
        species_dir = self.repo_path / 'realms'
        if species_dir.exists():
            for yaml_file in species_dir.rglob('*.yaml'):
                stats['total_species'] += 1
                
                # Track path depth
                depth = len(yaml_file.relative_to(species_dir).parts)
                stats['deepest_path'] = max(stats['deepest_path'], depth)
                
                # Read YAML to get classification
                try:
                    with open(yaml_file) as f:
                        data = yaml.safe_load(f)
                        if 'classification' in data:
                            classification = data['classification']
                            if 'realm' in classification:
                                stats['realms'][classification['realm']] += 1
                            if 'family' in classification:
                                stats['families'][classification['family']] += 1
                            if 'genus' in classification:
                                stats['genera'][classification['genus']] += 1
                except Exception as e:
                    logger.error(f"Error reading {yaml_file}: {e}")
        
        # Convert defaultdicts to regular dicts
        stats['realms'] = dict(stats['realms'])
        stats['families'] = dict(stats['families'])
        stats['genera'] = dict(stats['genera'])
        
        return stats


def convert_single_msl(msl_file: str, output_dir: str, msl_version: str) -> None:
    """
    Convenience function to convert a single MSL file.
    
    Args:
        msl_file: Path to MSL Excel file
        output_dir: Directory for git repository
        msl_version: Version string (e.g., 'MSL36')
    """
    converter = MSLToGitConverter(output_dir, initialize=True)
    species_count = converter.convert_msl_file(msl_file, msl_version)
    
    # Get and display statistics
    stats = converter.get_taxonomy_stats()
    
    print(f"\nConversion complete!")
    print(f"  Species: {species_count}")
    print(f"  Realms: {len(stats['realms'])}")
    print(f"  Families: {len(stats['families'])}")
    print(f"  Genera: {len(stats['genera'])}")
    print(f"  Repository: {output_dir}")


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: python msl_to_git.py <msl_file> <output_dir> <version>")
        print("Example: python msl_to_git.py data/raw/MSL36.xlsx output/viral-taxonomy MSL36")
        sys.exit(1)
    
    msl_file = sys.argv[1]
    output_dir = sys.argv[2]
    version = sys.argv[3]
    
    convert_single_msl(msl_file, output_dir, version)