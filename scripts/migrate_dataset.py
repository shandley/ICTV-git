#!/usr/bin/env python3
"""
Migrate research datasets between ICTV taxonomy versions.

This script helps researchers update their datasets when ICTV
releases new taxonomy versions.
"""

import sys
import csv
from pathlib import Path
import logging
import json

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.migration_mapper import MigrationMapper, DatasetMigrator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_example_dataset():
    """Create an example dataset for demonstration."""
    example_data = [
        {
            'sample_id': 'SAMPLE001',
            'species': 'Escherichia virus T4',
            'family': 'Myoviridae',
            'genus': 'Tequatrovirus',
            'host': 'Escherichia coli',
            'isolation_date': '2020-01-15',
            'genome_length': '168903'
        },
        {
            'sample_id': 'SAMPLE002',
            'species': 'Salmonella virus Chi',
            'family': 'Siphoviridae',
            'genus': 'Chivirus',
            'host': 'Salmonella enterica',
            'isolation_date': '2020-02-20',
            'genome_length': '59407'
        },
        {
            'sample_id': 'SAMPLE003',
            'species': 'Bacillus virus G',
            'family': 'Myoviridae',
            'genus': 'Gbacillus',
            'host': 'Bacillus megaterium',
            'isolation_date': '2020-03-10',
            'genome_length': '497513'
        },
        {
            'sample_id': 'SAMPLE004',
            'species': 'Pseudomonas virus gh1',
            'family': 'Podoviridae',
            'genus': 'Ghvirus',
            'host': 'Pseudomonas putida',
            'isolation_date': '2020-04-05',
            'genome_length': '37368'
        },
        {
            'sample_id': 'SAMPLE005',
            'species': 'Lactococcus virus bIL67',
            'family': 'Siphoviridae',
            'genus': 'Bilsevenvirus',
            'host': 'Lactococcus lactis',
            'isolation_date': '2020-05-12',
            'genome_length': '23823'
        }
    ]
    
    # Save example dataset
    example_path = Path(__file__).parent.parent / 'data' / 'example_dataset.csv'
    example_path.parent.mkdir(exist_ok=True)
    
    with open(example_path, 'w', newline='') as f:
        fieldnames = ['sample_id', 'species', 'family', 'genus', 'host', 
                     'isolation_date', 'genome_length']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(example_data)
    
    logger.info(f"Created example dataset: {example_path}")
    return example_path


def migrate_dataset(input_path: str, source_version: str, target_version: str,
                   species_column: str = 'species'):
    """Migrate a dataset between taxonomy versions."""
    
    # Setup paths
    repo_path = Path(__file__).parent.parent / 'output' / 'viral-taxonomy-evolution'
    
    if not repo_path.exists():
        logger.error(f"Repository not found at {repo_path}")
        logger.info("Please run: python scripts/convert_msl.py --evolution")
        return False
    
    # Create output path
    input_path = Path(input_path)
    output_path = input_path.parent / f"{input_path.stem}_migrated_{target_version}{input_path.suffix}"
    
    logger.info(f"Migrating dataset from {source_version} to {target_version}")
    logger.info(f"Input: {input_path}")
    logger.info(f"Output: {output_path}")
    
    # Create mapper and migrator
    mapper = MigrationMapper(str(repo_path))
    migrator = DatasetMigrator(mapper)
    
    # Migrate the dataset
    summary = migrator.migrate_csv(
        str(input_path), str(output_path),
        source_version, target_version,
        species_column
    )
    
    # Display summary
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    print(f"Total rows: {summary['total_rows']}")
    print(f"Mapped rows: {summary['mapped_rows']}")
    print("\nStatus breakdown:")
    for status, count in summary['status_counts'].items():
        print(f"  {status}: {count}")
    
    # Create detailed mapping report
    mapping_report_path = output_path.parent / f"{input_path.stem}_mapping_report_{source_version}_to_{target_version}.json"
    report = mapper.generate_migration_report(source_version, target_version)
    
    with open(mapping_report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nOutput file: {output_path}")
    print(f"Mapping report: {mapping_report_path}")
    
    # Show some examples of changes
    print("\n" + "="*60)
    print("EXAMPLE CHANGES")
    print("="*60)
    
    # Read the migrated file to show examples
    with open(output_path, 'r') as f:
        reader = csv.DictReader(f)
        examples_shown = 0
        for row in reader:
            if row.get('_mapping_status') == 'moved' and examples_shown < 3:
                print(f"\n{row['species']}:")
                if '_mapping_changes' in row:
                    changes = row['_mapping_changes'].split('; ')
                    for change in changes:
                        print(f"  - {change}")
                examples_shown += 1
    
    return True


def export_mapping_tables():
    """Export mapping tables for common version transitions."""
    repo_path = Path(__file__).parent.parent / 'output' / 'viral-taxonomy-evolution'
    
    if not repo_path.exists():
        logger.error(f"Repository not found at {repo_path}")
        return False
    
    mapper = MigrationMapper(str(repo_path))
    
    # Common version transitions
    transitions = [
        ('msl35', 'msl36'),
        ('msl36', 'msl37'),
        ('msl37', 'msl38')
    ]
    
    output_dir = Path(__file__).parent.parent / 'output' / 'mapping_tables'
    output_dir.mkdir(exist_ok=True)
    
    print("\n" + "="*60)
    print("EXPORTING MAPPING TABLES")
    print("="*60)
    
    for source, target in transitions:
        # Export CSV
        csv_path = output_dir / f"mapping_{source}_to_{target}.csv"
        mapper.export_mapping_table(source, target, str(csv_path), format='csv')
        print(f"\nExported: {csv_path}")
        
        # Generate report
        report = mapper.generate_migration_report(source, target)
        print(f"  Total species: {report['total_species']}")
        print(f"  Changed: {report['summary']['moved']}")
        print(f"  Removed: {report['summary']['removed']}")
        print(f"  Added: {report['summary']['added']}")
    
    return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrate datasets between ICTV taxonomy versions'
    )
    parser.add_argument('--example', action='store_true',
                       help='Create and migrate example dataset')
    parser.add_argument('--export-tables', action='store_true',
                       help='Export mapping tables for all version transitions')
    parser.add_argument('--input', type=str,
                       help='Input dataset CSV file')
    parser.add_argument('--source', type=str,
                       help='Source MSL version (e.g., msl36)')
    parser.add_argument('--target', type=str,
                       help='Target MSL version (e.g., msl37)')
    parser.add_argument('--species-column', type=str, default='species',
                       help='Column name containing species names (default: species)')
    
    args = parser.parse_args()
    
    if args.example:
        # Create and migrate example dataset
        example_path = create_example_dataset()
        success = migrate_dataset(str(example_path), 'msl36', 'msl37')
    elif args.export_tables:
        # Export all mapping tables
        success = export_mapping_tables()
    elif args.input and args.source and args.target:
        # Migrate user dataset
        success = migrate_dataset(args.input, args.source, args.target, 
                                args.species_column)
    else:
        parser.print_help()
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()