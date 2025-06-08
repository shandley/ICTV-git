#!/usr/bin/env python3
"""
Analyze viruses with unstable classifications across ICTV MSL versions.
"""

import csv
import json
from pathlib import Path
from collections import defaultdict

def load_mapping_file(filepath):
    """Load a mapping CSV file and extract classification changes."""
    changes = []
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['status'] == 'moved':
                changes.append({
                    'species': row['species_name'],
                    'changes': row['changes'],
                    'source_family': row.get('source_family', ''),
                    'target_family': row.get('target_family', ''),
                    'source_genus': row.get('source_genus', ''),
                    'target_genus': row.get('target_genus', ''),
                    'source_order': row.get('source_order', ''),
                    'target_order': row.get('target_order', '')
                })
    return changes

def analyze_unstable_species():
    """Identify species with multiple reclassifications."""
    output_dir = Path('output')
    mapping_dir = output_dir / 'mapping_tables'
    
    # Track all changes by species
    species_history = defaultdict(list)
    
    # Load all mapping files
    transitions = [
        ('msl35_to_msl36', mapping_dir / 'mapping_msl35_to_msl36.csv'),
        ('msl36_to_msl37', mapping_dir / 'mapping_msl36_to_msl37.csv'),
        ('msl37_to_msl38', mapping_dir / 'mapping_msl37_to_msl38.csv')
    ]
    
    for transition_name, filepath in transitions:
        if filepath.exists():
            changes = load_mapping_file(filepath)
            for change in changes:
                species_history[change['species']].append({
                    'transition': transition_name,
                    **change
                })
    
    # Analyze unstable classifications
    unstable_species = {k: v for k, v in species_history.items() if len(v) >= 1}
    
    # Count by type of change
    family_changes = defaultdict(int)
    genus_changes = defaultdict(int)
    order_changes = defaultdict(int)
    
    for species, history in unstable_species.items():
        for change in history:
            changes_str = change.get('changes', '')
            if 'family:' in changes_str:
                family_changes[species] += 1
            if 'genus:' in changes_str:
                genus_changes[species] += 1
            if 'order:' in changes_str:
                order_changes[species] += 1
    
    # Find most unstable families
    family_instability = defaultdict(int)
    for species, history in unstable_species.items():
        for change in history:
            source_family = change.get('source_family', '')
            if source_family:
                family_instability[source_family] += 1
    
    # Generate report
    report = {
        'summary': {
            'total_species_with_changes': len(unstable_species),
            'species_with_family_changes': len(family_changes),
            'species_with_genus_changes': len(genus_changes),
            'species_with_order_changes': len(order_changes)
        },
        'most_unstable_families': dict(sorted(
            family_instability.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:20]),
        'example_unstable_species': {}
    }
    
    # Add examples of unstable species
    examples_count = 0
    for species, history in sorted(unstable_species.items(), key=lambda x: len(x[1]), reverse=True):
        if examples_count >= 10:
            break
        
        report['example_unstable_species'][species] = {
            'number_of_changes': len(history),
            'changes': history
        }
        examples_count += 1
    
    # Special focus on Caudovirales
    caudovirales_changes = defaultdict(list)
    for species, history in unstable_species.items():
        for change in history:
            if any(family in str(change) for family in ['Myoviridae', 'Siphoviridae', 'Podoviridae', 'Caudovirales']):
                caudovirales_changes[species].append(change)
    
    report['caudovirales_instability'] = {
        'total_affected_species': len(caudovirales_changes),
        'examples': dict(list(caudovirales_changes.items())[:10])
    }
    
    return report

def main():
    """Run the unstable classification analysis."""
    print("Analyzing unstable viral classifications...")
    
    report = analyze_unstable_species()
    
    # Save report
    output_file = Path('output/unstable_classifications_report.json')
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\nANALYSIS COMPLETE")
    print(f"================")
    print(f"Total species with classification changes: {report['summary']['total_species_with_changes']}")
    print(f"Species with family changes: {report['summary']['species_with_family_changes']}")
    print(f"Species with genus changes: {report['summary']['species_with_genus_changes']}")
    print(f"Species with order changes: {report['summary']['species_with_order_changes']}")
    
    print(f"\nMOST UNSTABLE FAMILIES:")
    for family, count in list(report['most_unstable_families'].items())[:10]:
        print(f"  {family}: {count} species reclassified")
    
    print(f"\nCAUDOVIRALES INSTABILITY:")
    print(f"  Total affected species: {report['caudovirales_instability']['total_affected_species']}")
    
    print(f"\nFull report saved to: {output_file}")

if __name__ == '__main__':
    main()