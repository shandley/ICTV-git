#!/usr/bin/env python3
"""
Create a sample dataset from full MSL data for testing and demonstration.

This script extracts a representative subset of species that includes:
- Different realms
- Various genome types
- Multiple host types
- Diverse taxonomic families
"""

import argparse
import pandas as pd
from pathlib import Path
import yaml
import json
from typing import List, Dict
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.parsers.msl_parser import MSLParser
from src.converters.msl_to_git import MSLToGitConverter


def create_sample_dataset(msl_file: str, sample_size: int = 50, 
                         output_dir: str = "data/sample") -> Dict:
    """Create a representative sample dataset from an MSL file.
    
    Args:
        msl_file: Path to MSL Excel file
        sample_size: Number of species to include
        output_dir: Directory to save sample data
        
    Returns:
        Dictionary with sample statistics
    """
    print(f"Creating sample dataset from {msl_file}")
    
    # Parse the MSL file
    parser = MSLParser(msl_file)
    all_species = parser.parse()
    print(f"Total species in file: {len(all_species)}")
    
    # Convert to DataFrame for easier sampling
    data = []
    for species in all_species:
        data.append({
            'Species': species.scientific_name,
            'Genus': species.genus or '',
            'Family': species.family or '',
            'Order': species.order or '',
            'Class': species.class_ or '',
            'Phylum': species.phylum or '',
            'Kingdom': species.kingdom or '',
            'Realm': species.realm or '',
            'Genome_Composition': species.genome_composition or '',
            'Host_Source': species.host_source or ''
        })
    
    df = pd.DataFrame(data)
    
    # Strategy: Get diverse sample
    sample_species = []
    
    # 1. Get species from each realm (if exists)
    realms = df['Realm'].unique()
    realms = [r for r in realms if r]  # Remove empty
    
    for realm in realms[:7]:  # Max 7 realms
        realm_species = df[df['Realm'] == realm].sample(
            min(5, len(df[df['Realm'] == realm]))
        )
        sample_species.append(realm_species)
    
    # 2. Get different genome types
    genome_types = df['Genome_Composition'].unique()
    genome_types = [g for g in genome_types if g][:10]  # Top 10 types
    
    for genome in genome_types:
        genome_species = df[df['Genome_Composition'] == genome].sample(
            min(2, len(df[df['Genome_Composition'] == genome]))
        )
        sample_species.append(genome_species)
    
    # 3. Get well-known viruses
    well_known = [
        'Tobacco mosaic virus',
        'Severe acute respiratory syndrome-related coronavirus',
        'Human immunodeficiency virus 1',
        'Influenza A virus',
        'Ebola virus',
        'Bacteriophage lambda',
        'Escherichia phage T4'
    ]
    
    for virus in well_known:
        matches = df[df['Species'].str.contains(virus, case=False, na=False)]
        if not matches.empty:
            sample_species.append(matches.head(1))
    
    # Combine and deduplicate
    sample_df = pd.concat(sample_species).drop_duplicates()
    
    # If we need more, randomly sample
    if len(sample_df) < sample_size:
        remaining = sample_size - len(sample_df)
        additional = df[~df['Species'].isin(sample_df['Species'])].sample(
            min(remaining, len(df) - len(sample_df))
        )
        sample_df = pd.concat([sample_df, additional])
    
    # Limit to sample size
    sample_df = sample_df.head(sample_size)
    
    # Save the sample
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save as CSV
    csv_path = output_path / 'sample_msl_data.csv'
    sample_df.to_csv(csv_path, index=False)
    print(f"Saved {len(sample_df)} species to {csv_path}")
    
    # Create sample YAML files
    yaml_dir = output_path / 'sample_species'
    yaml_dir.mkdir(exist_ok=True)
    
    for _, row in sample_df.iterrows():
        species_data = {
            'scientific_name': row['Species'],
            'classification': {
                'genus': row['Genus'],
                'family': row['Family'],
                'order': row['Order'],
                'class': row['Class'],
                'phylum': row['Phylum'],
                'kingdom': row['Kingdom'],
                'realm': row['Realm']
            },
            'genome': {
                'composition': row['Genome_Composition']
            },
            'host': row['Host_Source']
        }
        
        # Create safe filename
        safe_name = row['Species'].replace(' ', '_').replace('/', '_')
        yaml_path = yaml_dir / f"{safe_name}.yaml"
        
        with open(yaml_path, 'w') as f:
            yaml.dump(species_data, f, default_flow_style=False)
    
    print(f"Created {len(sample_df)} YAML files in {yaml_dir}")
    
    # Create statistics
    stats = {
        'total_species': len(sample_df),
        'realms': sample_df['Realm'].nunique(),
        'families': sample_df['Family'].nunique(),
        'genome_types': sample_df['Genome_Composition'].nunique(),
        'host_types': sample_df['Host_Source'].nunique(),
        'coverage': {
            'realms': list(sample_df['Realm'].unique()),
            'genome_types': list(sample_df['Genome_Composition'].unique()[:10])
        }
    }
    
    # Save statistics
    stats_path = output_path / 'sample_statistics.json'
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"\nSample statistics:")
    print(f"- Species: {stats['total_species']}")
    print(f"- Realms: {stats['realms']}")
    print(f"- Families: {stats['families']}")
    print(f"- Genome types: {stats['genome_types']}")
    
    return stats


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Create sample dataset from MSL file"
    )
    parser.add_argument(
        "msl_file",
        help="Path to MSL Excel file"
    )
    parser.add_argument(
        "--size",
        type=int,
        default=50,
        help="Number of species to include (default: 50)"
    )
    parser.add_argument(
        "--output",
        default="data/sample",
        help="Output directory (default: data/sample)"
    )
    
    args = parser.parse_args()
    
    # Check if file exists
    if not Path(args.msl_file).exists():
        print(f"Error: File {args.msl_file} not found")
        print("Please download MSL data first: python scripts/download_msl.py")
        sys.exit(1)
    
    # Create sample
    stats = create_sample_dataset(
        args.msl_file,
        sample_size=args.size,
        output_dir=args.output
    )
    
    print(f"\nSample dataset created successfully in {args.output}/")
    print("You can now use this for quick testing without the full dataset.")


if __name__ == "__main__":
    main()