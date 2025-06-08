"""
Semantic diff tools for viral taxonomy changes.

This module provides tools to compare taxonomic changes between
MSL versions and generate meaningful diffs.
"""

import os
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
import yaml
import git
from collections import defaultdict
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class TaxonomicChange:
    """Represents a change in taxonomic classification."""
    species_name: str
    change_type: str  # 'moved', 'added', 'removed', 'renamed'
    old_classification: Optional[Dict] = None
    new_classification: Optional[Dict] = None
    old_path: Optional[str] = None
    new_path: Optional[str] = None
    details: Dict = field(default_factory=dict)


@dataclass 
class FamilyMigration:
    """Tracks migration of species between families."""
    old_family: str
    new_families: Dict[str, int]  # new_family -> count
    species_migrations: List[Tuple[str, str, str]]  # (species, old_genus, new_family)
    
    @property
    def total_species(self) -> int:
        return sum(self.new_families.values())


class TaxonomyDiff:
    """Compare taxonomy between two git commits/tags."""
    
    def __init__(self, repo_path: str):
        """Initialize with repository path."""
        self.repo_path = Path(repo_path)
        self.repo = git.Repo(repo_path)
    
    def get_species_at_version(self, version: str) -> Dict[str, Dict]:
        """Get all species and their classifications at a specific version."""
        # Checkout the version
        self.repo.git.checkout(version)
        
        species_data = {}
        
        # Walk through all YAML files
        for yaml_file in self.repo_path.rglob("*.yaml"):
            if yaml_file.parent.name == "species":
                try:
                    with open(yaml_file) as f:
                        data = yaml.safe_load(f)
                        if data and 'species_name' in data:
                            species_data[data['species_name']] = {
                                'classification': data.get('classification', {}),
                                'path': str(yaml_file.relative_to(self.repo_path)),
                                'metadata': data.get('metadata', {}),
                                'genome': data.get('genome', {})
                            }
                except Exception as e:
                    logger.error(f"Error reading {yaml_file}: {e}")
        
        # Return to master branch
        self.repo.git.checkout('master')
        
        return species_data
    
    def compare_versions(self, version1: str, version2: str) -> Dict[str, List[TaxonomicChange]]:
        """Compare two taxonomy versions and identify changes."""
        logger.info(f"Comparing {version1} to {version2}")
        
        # Get species data for both versions
        species_v1 = self.get_species_at_version(version1)
        species_v2 = self.get_species_at_version(version2)
        
        logger.info(f"{version1}: {len(species_v1)} species")
        logger.info(f"{version2}: {len(species_v2)} species")
        
        changes = {
            'added': [],
            'removed': [],
            'moved': [],
            'classification_changed': []
        }
        
        # Find removed species
        for species_name in species_v1:
            if species_name not in species_v2:
                changes['removed'].append(TaxonomicChange(
                    species_name=species_name,
                    change_type='removed',
                    old_classification=species_v1[species_name]['classification'],
                    old_path=species_v1[species_name]['path']
                ))
        
        # Find added species
        for species_name in species_v2:
            if species_name not in species_v1:
                changes['added'].append(TaxonomicChange(
                    species_name=species_name,
                    change_type='added',
                    new_classification=species_v2[species_name]['classification'],
                    new_path=species_v2[species_name]['path']
                ))
        
        # Find moved/reclassified species
        for species_name in species_v1:
            if species_name in species_v2:
                old_class = species_v1[species_name]['classification']
                new_class = species_v2[species_name]['classification']
                
                if old_class != new_class:
                    # Determine what changed
                    changed_ranks = []
                    for rank in ['realm', 'kingdom', 'phylum', 'class', 'order', 
                               'family', 'subfamily', 'genus']:
                        if old_class.get(rank) != new_class.get(rank):
                            changed_ranks.append(rank)
                    
                    change = TaxonomicChange(
                        species_name=species_name,
                        change_type='classification_changed',
                        old_classification=old_class,
                        new_classification=new_class,
                        old_path=species_v1[species_name]['path'],
                        new_path=species_v2[species_name]['path'],
                        details={'changed_ranks': changed_ranks}
                    )
                    
                    changes['classification_changed'].append(change)
        
        return changes
    
    def analyze_family_migrations(self, version1: str, version2: str, 
                                 target_families: Optional[List[str]] = None) -> Dict[str, FamilyMigration]:
        """Analyze how species moved between families."""
        changes = self.compare_versions(version1, version2)
        
        # Track migrations by old family
        family_migrations = defaultdict(lambda: defaultdict(int))
        species_details = defaultdict(list)
        
        for change in changes['classification_changed']:
            old_family = change.old_classification.get('family')
            new_family = change.new_classification.get('family')
            
            if old_family and new_family and old_family != new_family:
                if target_families is None or old_family in target_families:
                    family_migrations[old_family][new_family] += 1
                    species_details[old_family].append((
                        change.species_name,
                        change.old_classification.get('genus', 'Unknown'),
                        new_family
                    ))
        
        # Also check removed species from target families
        for change in changes['removed']:
            old_family = change.old_classification.get('family')
            if old_family and (target_families is None or old_family in target_families):
                family_migrations[old_family]['[REMOVED]'] += 1
                species_details[old_family].append((
                    change.species_name,
                    change.old_classification.get('genus', 'Unknown'),
                    '[REMOVED]'
                ))
        
        # Convert to FamilyMigration objects
        results = {}
        for old_family, migrations in family_migrations.items():
            results[old_family] = FamilyMigration(
                old_family=old_family,
                new_families=dict(migrations),
                species_migrations=species_details[old_family]
            )
        
        return results
    
    def get_order_statistics(self, version: str, target_order: str) -> Dict:
        """Get statistics for a specific order at a version."""
        species_data = self.get_species_at_version(version)
        
        stats = {
            'total_species': 0,
            'families': defaultdict(int),
            'genera': defaultdict(int),
            'species_list': []
        }
        
        for species_name, data in species_data.items():
            if data['classification'].get('order') == target_order:
                stats['total_species'] += 1
                stats['species_list'].append(species_name)
                
                family = data['classification'].get('family')
                genus = data['classification'].get('genus')
                
                if family:
                    stats['families'][family] += 1
                if genus:
                    stats['genera'][genus] += 1
        
        stats['families'] = dict(stats['families'])
        stats['genera'] = dict(stats['genera'])
        
        return stats


class CaudoviralesTracker:
    """Specialized tracker for Caudovirales reclassification."""
    
    def __init__(self, repo_path: str):
        """Initialize tracker."""
        self.diff_tool = TaxonomyDiff(repo_path)
        self.old_families = ['Myoviridae', 'Podoviridae', 'Siphoviridae']
    
    def track_dissolution(self, before_version: str = 'msl36', 
                         after_version: str = 'msl37') -> Dict:
        """Track the dissolution of Caudovirales."""
        results = {
            'before': {},
            'after': {},
            'migrations': {},
            'summary': {}
        }
        
        # Get statistics before
        results['before'] = self.diff_tool.get_order_statistics(before_version, 'Caudovirales')
        
        # Get statistics after (should be empty for Caudovirales)
        results['after'] = self.diff_tool.get_order_statistics(after_version, 'Caudovirales')
        
        # Track where the species went
        results['migrations'] = self.diff_tool.analyze_family_migrations(
            before_version, after_version, self.old_families
        )
        
        # Generate summary
        total_before = results['before']['total_species']
        total_after = results['after']['total_species']
        total_migrated = sum(m.total_species for m in results['migrations'].values())
        
        results['summary'] = {
            'order_abolished': total_after == 0,
            'species_before': total_before,
            'species_after': total_after,
            'species_migrated': total_migrated,
            'old_families_count': len([f for f in self.old_families if f in results['before']['families']]),
            'new_families_created': len(set(
                family for migration in results['migrations'].values()
                for family in migration.new_families.keys()
                if family != '[REMOVED]'
            ))
        }
        
        return results
    
    def generate_migration_report(self, results: Dict) -> str:
        """Generate a human-readable migration report."""
        report = []
        report.append("="*80)
        report.append("CAUDOVIRALES DISSOLUTION TRACKING REPORT")
        report.append("="*80)
        report.append("")
        
        # Summary
        summary = results['summary']
        report.append("SUMMARY:")
        report.append(f"  Order Caudovirales abolished: {'YES' if summary['order_abolished'] else 'NO'}")
        report.append(f"  Species before: {summary['species_before']:,}")
        report.append(f"  Species after: {summary['species_after']:,}")
        report.append(f"  Species migrated: {summary['species_migrated']:,}")
        report.append(f"  Old families dissolved: {summary['old_families_count']}")
        report.append(f"  New families created: {summary['new_families_created']}")
        report.append("")
        
        # Before statistics
        report.append("BEFORE (MSL36):")
        before = results['before']
        for family, count in sorted(before['families'].items(), key=lambda x: x[1], reverse=True):
            if family in self.old_families:
                report.append(f"  {family}: {count} species")
        report.append("")
        
        # Migration details
        report.append("MIGRATIONS:")
        for old_family in self.old_families:
            if old_family in results['migrations']:
                migration = results['migrations'][old_family]
                report.append(f"\n  From {old_family} ({migration.total_species} species):")
                
                # Sort destination families by count
                sorted_destinations = sorted(
                    migration.new_families.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                
                for new_family, count in sorted_destinations[:10]:  # Top 10
                    percentage = (count / migration.total_species) * 100
                    report.append(f"    → {new_family}: {count} species ({percentage:.1f}%)")
                
                if len(sorted_destinations) > 10:
                    report.append(f"    ... and {len(sorted_destinations) - 10} more families")
        
        report.append("")
        report.append("="*80)
        
        return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    else:
        repo_path = "output/viral-taxonomy-evolution"
    
    # Track Caudovirales dissolution
    tracker = CaudoviralesTracker(repo_path)
    results = tracker.track_dissolution()
    report = tracker.generate_migration_report(results)
    
    print(report)