"""
Migration mapping tools for ICTV taxonomy versions.

This module provides tools to map taxonomic classifications between
different MSL versions, helping researchers update their datasets.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import logging
from collections import defaultdict
from dataclasses import dataclass, field, asdict

from .taxonomy_diff import TaxonomyDiff

logger = logging.getLogger(__name__)


@dataclass
class SpeciesMapping:
    """Represents a mapping for a single species between versions."""
    species_name: str
    source_version: str
    target_version: str
    source_classification: Dict[str, str]
    target_classification: Optional[Dict[str, str]] = None
    status: str = 'unchanged'  # unchanged, moved, removed, added
    changes: List[str] = field(default_factory=list)
    confidence: float = 1.0
    notes: str = ''


class MigrationMapper:
    """Maps taxonomic classifications between MSL versions."""
    
    def __init__(self, repo_path: str):
        """Initialize mapper with repository path."""
        self.repo_path = Path(repo_path)
        self.diff_tool = TaxonomyDiff(repo_path)
        self._mapping_cache = {}
    
    def create_species_mapping(self, source_version: str, target_version: str) -> Dict[str, SpeciesMapping]:
        """Create complete species mapping between two versions."""
        cache_key = f"{source_version}->{target_version}"
        if cache_key in self._mapping_cache:
            return self._mapping_cache[cache_key]
        
        logger.info(f"Creating species mapping from {source_version} to {target_version}")
        
        # Get species data for both versions
        source_species = self.diff_tool.get_species_at_version(source_version)
        target_species = self.diff_tool.get_species_at_version(target_version)
        
        mappings = {}
        
        # Map species that exist in both versions
        for species_name, source_data in source_species.items():
            if species_name in target_species:
                target_data = target_species[species_name]
                source_class = source_data['classification']
                target_class = target_data['classification']
                
                # Check what changed
                changes = []
                for rank in ['realm', 'kingdom', 'phylum', 'class', 'order', 
                           'family', 'subfamily', 'genus', 'subgenus']:
                    if source_class.get(rank) != target_class.get(rank):
                        changes.append(f"{rank}: {source_class.get(rank, 'None')} → {target_class.get(rank, 'None')}")
                
                status = 'moved' if changes else 'unchanged'
                
                mappings[species_name] = SpeciesMapping(
                    species_name=species_name,
                    source_version=source_version,
                    target_version=target_version,
                    source_classification=source_class,
                    target_classification=target_class,
                    status=status,
                    changes=changes
                )
            else:
                # Species removed in target version
                mappings[species_name] = SpeciesMapping(
                    species_name=species_name,
                    source_version=source_version,
                    target_version=target_version,
                    source_classification=source_data['classification'],
                    status='removed',
                    notes='Species not found in target version'
                )
        
        # Check for new species in target version
        for species_name in target_species:
            if species_name not in source_species:
                mappings[species_name] = SpeciesMapping(
                    species_name=species_name,
                    source_version=source_version,
                    target_version=target_version,
                    source_classification={},
                    target_classification=target_species[species_name]['classification'],
                    status='added',
                    notes='New species in target version'
                )
        
        self._mapping_cache[cache_key] = mappings
        return mappings
    
    def map_dataset(self, dataset: List[Dict], source_version: str, 
                   target_version: str, species_column: str = 'species') -> List[Dict]:
        """Map a dataset from one taxonomy version to another."""
        # Create species mapping
        mappings = self.create_species_mapping(source_version, target_version)
        
        # Map each row in dataset
        mapped_dataset = []
        for row in dataset:
            species_name = row.get(species_column)
            if not species_name:
                mapped_dataset.append(row.copy())
                continue
            
            if species_name in mappings:
                mapping = mappings[species_name]
                new_row = row.copy()
                
                # Add mapping information
                new_row['_mapping_status'] = mapping.status
                new_row['_mapping_confidence'] = mapping.confidence
                
                if mapping.target_classification:
                    # Update taxonomic fields
                    for rank, value in mapping.target_classification.items():
                        if rank in new_row or f'virus_{rank}' in new_row:
                            field_name = rank if rank in new_row else f'virus_{rank}'
                            new_row[field_name] = value
                
                if mapping.changes:
                    new_row['_mapping_changes'] = '; '.join(mapping.changes)
                
                if mapping.notes:
                    new_row['_mapping_notes'] = mapping.notes
                
                mapped_dataset.append(new_row)
            else:
                # Species not in mapping
                new_row = row.copy()
                new_row['_mapping_status'] = 'not_found'
                new_row['_mapping_notes'] = 'Species not found in mapping'
                mapped_dataset.append(new_row)
        
        return mapped_dataset
    
    def export_mapping_table(self, source_version: str, target_version: str, 
                           output_path: str, format: str = 'csv') -> None:
        """Export mapping table to file."""
        mappings = self.create_species_mapping(source_version, target_version)
        
        output_path = Path(output_path)
        
        if format == 'csv':
            self._export_csv(mappings, output_path)
        elif format == 'json':
            self._export_json(mappings, output_path)
        elif format == 'tsv':
            self._export_tsv(mappings, output_path)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Exported mapping table to {output_path}")
    
    def _export_csv(self, mappings: Dict[str, SpeciesMapping], output_path: Path) -> None:
        """Export mappings to CSV."""
        fieldnames = [
            'species_name', 'status',
            'source_realm', 'source_kingdom', 'source_phylum', 'source_class',
            'source_order', 'source_family', 'source_genus',
            'target_realm', 'target_kingdom', 'target_phylum', 'target_class',
            'target_order', 'target_family', 'target_genus',
            'changes', 'confidence', 'notes'
        ]
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for mapping in mappings.values():
                row = {
                    'species_name': mapping.species_name,
                    'status': mapping.status,
                    'confidence': mapping.confidence,
                    'notes': mapping.notes,
                    'changes': '; '.join(mapping.changes)
                }
                
                # Add source classification
                for rank in ['realm', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus']:
                    row[f'source_{rank}'] = mapping.source_classification.get(rank, '')
                
                # Add target classification
                if mapping.target_classification:
                    for rank in ['realm', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus']:
                        row[f'target_{rank}'] = mapping.target_classification.get(rank, '')
                
                writer.writerow(row)
    
    def _export_json(self, mappings: Dict[str, SpeciesMapping], output_path: Path) -> None:
        """Export mappings to JSON."""
        json_data = {}
        for species_name, mapping in mappings.items():
            json_data[species_name] = {
                'status': mapping.status,
                'source_classification': mapping.source_classification,
                'target_classification': mapping.target_classification,
                'changes': mapping.changes,
                'confidence': mapping.confidence,
                'notes': mapping.notes
            }
        
        with open(output_path, 'w') as f:
            json.dump(json_data, f, indent=2)
    
    def _export_tsv(self, mappings: Dict[str, SpeciesMapping], output_path: Path) -> None:
        """Export mappings to TSV."""
        # Similar to CSV but with tabs
        fieldnames = [
            'species_name', 'status',
            'source_family', 'source_genus',
            'target_family', 'target_genus',
            'changes'
        ]
        
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
            writer.writeheader()
            
            for mapping in mappings.values():
                row = {
                    'species_name': mapping.species_name,
                    'status': mapping.status,
                    'source_family': mapping.source_classification.get('family', ''),
                    'source_genus': mapping.source_classification.get('genus', ''),
                    'target_family': mapping.target_classification.get('family', '') if mapping.target_classification else '',
                    'target_genus': mapping.target_classification.get('genus', '') if mapping.target_classification else '',
                    'changes': '; '.join(mapping.changes)
                }
                writer.writerow(row)
    
    def generate_migration_report(self, source_version: str, target_version: str) -> Dict:
        """Generate summary report of migrations between versions."""
        mappings = self.create_species_mapping(source_version, target_version)
        
        report = {
            'source_version': source_version,
            'target_version': target_version,
            'total_species': len(mappings),
            'summary': {
                'unchanged': 0,
                'moved': 0,
                'removed': 0,
                'added': 0
            },
            'changes_by_rank': defaultdict(int),
            'family_migrations': defaultdict(lambda: defaultdict(int))
        }
        
        # Count by status
        for mapping in mappings.values():
            report['summary'][mapping.status] += 1
            
            # Count changes by rank
            for change in mapping.changes:
                if ':' in change:
                    rank = change.split(':')[0]
                    report['changes_by_rank'][rank] += 1
            
            # Track family migrations
            if mapping.status == 'moved' and mapping.target_classification:
                source_family = mapping.source_classification.get('family', 'Unknown')
                target_family = mapping.target_classification.get('family', 'Unknown')
                if source_family != target_family:
                    report['family_migrations'][source_family][target_family] += 1
        
        report['changes_by_rank'] = dict(report['changes_by_rank'])
        report['family_migrations'] = {k: dict(v) for k, v in report['family_migrations'].items()}
        
        return report


class DatasetMigrator:
    """Helper class for migrating research datasets between taxonomy versions."""
    
    def __init__(self, mapper: MigrationMapper):
        """Initialize with a migration mapper."""
        self.mapper = mapper
    
    def migrate_csv(self, input_path: str, output_path: str, 
                   source_version: str, target_version: str,
                   species_column: str = 'species') -> Dict:
        """Migrate a CSV file between taxonomy versions."""
        # Read input CSV
        dataset = []
        with open(input_path, 'r') as f:
            reader = csv.DictReader(f)
            dataset = list(reader)
        
        # Map dataset
        mapped_dataset = self.mapper.map_dataset(
            dataset, source_version, target_version, species_column
        )
        
        # Write output CSV
        if mapped_dataset:
            fieldnames = list(mapped_dataset[0].keys())
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(mapped_dataset)
        
        # Generate summary
        summary = {
            'total_rows': len(dataset),
            'mapped_rows': len(mapped_dataset),
            'status_counts': defaultdict(int)
        }
        
        for row in mapped_dataset:
            status = row.get('_mapping_status', 'unknown')
            summary['status_counts'][status] += 1
        
        summary['status_counts'] = dict(summary['status_counts'])
        
        return summary
    
    def validate_mapping(self, dataset: List[Dict], source_version: str,
                        target_version: str, species_column: str = 'species') -> List[Dict]:
        """Validate which species in a dataset can be mapped."""
        mappings = self.mapper.create_species_mapping(source_version, target_version)
        
        validation_results = []
        for row in dataset:
            species_name = row.get(species_column)
            if species_name:
                if species_name in mappings:
                    mapping = mappings[species_name]
                    validation_results.append({
                        'species': species_name,
                        'can_map': mapping.status != 'removed',
                        'status': mapping.status,
                        'changes': mapping.changes
                    })
                else:
                    validation_results.append({
                        'species': species_name,
                        'can_map': False,
                        'status': 'not_found',
                        'changes': []
                    })
        
        return validation_results


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 3:
        repo_path = sys.argv[1]
        source_version = sys.argv[2]
        target_version = sys.argv[3]
        
        mapper = MigrationMapper(repo_path)
        
        # Export mapping table
        output_path = f"mapping_{source_version}_to_{target_version}.csv"
        mapper.export_mapping_table(source_version, target_version, output_path)
        
        # Generate report
        report = mapper.generate_migration_report(source_version, target_version)
        print(f"\nMigration Report: {source_version} → {target_version}")
        print(f"Total species: {report['total_species']}")
        print(f"Unchanged: {report['summary']['unchanged']}")
        print(f"Moved: {report['summary']['moved']}")
        print(f"Removed: {report['summary']['removed']}")
        print(f"Added: {report['summary']['added']}")
    else:
        print("Usage: python migration_mapper.py <repo_path> <source_version> <target_version>")
        print("Example: python migration_mapper.py output/viral-taxonomy-evolution msl36 msl37")