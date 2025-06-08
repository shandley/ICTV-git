#!/usr/bin/env python3
"""
Analyze the Caudovirales migration between MSL versions.

This script uses the taxonomy diff tools to track how Caudovirales
species were reclassified.
"""

import sys
from pathlib import Path
import logging

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.taxonomy_diff import CaudoviralesTracker, TaxonomyDiff

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_caudovirales_migration():
    """Analyze the Caudovirales dissolution."""
    
    # Path to the evolution repository
    repo_path = Path(__file__).parent.parent / 'output' / 'viral-taxonomy-evolution'
    
    if not repo_path.exists():
        logger.error(f"Repository not found at {repo_path}")
        logger.info("Please run: python scripts/convert_msl.py --evolution")
        return False
    
    logger.info(f"Analyzing repository at: {repo_path}")
    
    # Create tracker
    tracker = CaudoviralesTracker(str(repo_path))
    
    # Track the dissolution
    logger.info("Tracking Caudovirales dissolution from MSL36 to MSL37...")
    results = tracker.track_dissolution('msl36', 'msl37')
    
    # Generate report
    report = tracker.generate_migration_report(results)
    print("\n" + report)
    
    # Save detailed report
    report_path = Path(__file__).parent.parent / 'output' / 'caudovirales_migration_report.txt'
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w') as f:
        f.write(report)
        
        # Add detailed species examples
        f.write("\n\nDETAILED SPECIES EXAMPLES:\n")
        f.write("="*80 + "\n\n")
        
        # Show examples from each old family
        for old_family in ['Myoviridae', 'Podoviridae', 'Siphoviridae']:
            if old_family in results['migrations']:
                migration = results['migrations'][old_family]
                f.write(f"\nExamples from {old_family}:\n")
                
                # Group by destination family
                by_destination = {}
                for species, genus, new_family in migration.species_migrations[:20]:
                    if new_family not in by_destination:
                        by_destination[new_family] = []
                    by_destination[new_family].append((species, genus))
                
                # Show a few examples for each destination
                for new_family, species_list in sorted(by_destination.items())[:5]:
                    f.write(f"\n  To {new_family}:\n")
                    for species, genus in species_list[:3]:
                        f.write(f"    - {species} (genus: {genus})\n")
    
    logger.info(f"Detailed report saved to: {report_path}")
    
    # Also create a summary visualization data file
    create_visualization_data(results)
    
    return True


def create_visualization_data(results):
    """Create data files for visualization."""
    import json
    
    output_dir = Path(__file__).parent.parent / 'output'
    
    # Create migration flow data (for Sankey diagram)
    flow_data = {
        'nodes': [],
        'links': []
    }
    
    # Add source nodes (old families)
    old_families = ['Myoviridae', 'Podoviridae', 'Siphoviridae']
    for i, family in enumerate(old_families):
        flow_data['nodes'].append({
            'id': i,
            'name': family,
            'type': 'old_family'
        })
    
    # Track new families and add nodes
    new_family_map = {}
    node_id = len(old_families)
    
    for old_idx, old_family in enumerate(old_families):
        if old_family in results['migrations']:
            migration = results['migrations'][old_family]
            
            for new_family, count in migration.new_families.items():
                if new_family not in new_family_map:
                    new_family_map[new_family] = node_id
                    flow_data['nodes'].append({
                        'id': node_id,
                        'name': new_family,
                        'type': 'new_family' if new_family != '[REMOVED]' else 'removed'
                    })
                    node_id += 1
                
                # Add link
                flow_data['links'].append({
                    'source': old_idx,
                    'target': new_family_map[new_family],
                    'value': count
                })
    
    # Save flow data
    flow_path = output_dir / 'caudovirales_migration_flow.json'
    with open(flow_path, 'w') as f:
        json.dump(flow_data, f, indent=2)
    
    logger.info(f"Visualization data saved to: {flow_path}")
    
    # Create summary statistics
    stats = {
        'before': {
            'total_species': results['summary']['species_before'],
            'families': {
                family: results['before']['families'].get(family, 0)
                for family in old_families
            }
        },
        'after': {
            'total_species': results['summary']['species_after'],
            'new_families_count': results['summary']['new_families_created']
        },
        'migration_summary': {
            family: {
                'total': migration.total_species,
                'top_destinations': sorted(
                    migration.new_families.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5]
            }
            for family, migration in results['migrations'].items()
        }
    }
    
    stats_path = output_dir / 'caudovirales_migration_stats.json'
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    logger.info(f"Statistics saved to: {stats_path}")


def analyze_general_changes():
    """Analyze general taxonomic changes between versions."""
    repo_path = Path(__file__).parent.parent / 'output' / 'viral-taxonomy-evolution'
    
    if not repo_path.exists():
        logger.error(f"Repository not found at {repo_path}")
        return False
    
    diff_tool = TaxonomyDiff(str(repo_path))
    
    # Compare multiple version pairs
    version_pairs = [
        ('msl35', 'msl36'),
        ('msl36', 'msl37'),
        ('msl37', 'msl38')
    ]
    
    print("\n" + "="*80)
    print("GENERAL TAXONOMY CHANGES BETWEEN VERSIONS")
    print("="*80)
    
    for v1, v2 in version_pairs:
        print(f"\n{v1.upper()} → {v2.upper()}:")
        print("-"*40)
        
        changes = diff_tool.compare_versions(v1, v2)
        
        print(f"  Added species: {len(changes['added'])}")
        print(f"  Removed species: {len(changes['removed'])}")
        print(f"  Reclassified species: {len(changes['classification_changed'])}")
        
        # Analyze reclassification patterns
        rank_changes = {}
        for change in changes['classification_changed']:
            for rank in change.details.get('changed_ranks', []):
                rank_changes[rank] = rank_changes.get(rank, 0) + 1
        
        if rank_changes:
            print(f"\n  Changes by taxonomic rank:")
            for rank, count in sorted(rank_changes.items()):
                print(f"    {rank}: {count} species")


if __name__ == "__main__":
    # Analyze Caudovirales migration
    success = analyze_caudovirales_migration()
    
    if success:
        # Also show general changes
        analyze_general_changes()
    
    sys.exit(0 if success else 1)