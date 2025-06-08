#!/usr/bin/env python3
"""
Test the MSL parser with a downloaded file.

This script tests the MSL parser functionality and demonstrates
basic usage patterns.
"""

import sys
from pathlib import Path
import logging

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.parsers.msl_parser import MSLParser, parse_msl_file

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_msl_parser():
    """Test MSL parser with first available file."""
    
    # Find an MSL file in data/raw
    data_dir = Path(__file__).parent.parent / 'data' / 'raw'
    excel_files = list(data_dir.glob("*.xlsx"))
    
    if not excel_files:
        logger.error(f"No Excel files found in {data_dir}")
        logger.info("Please run: python scripts/download_msl.py")
        return False
    
    # Use first file for testing
    test_file = excel_files[0]
    logger.info(f"Testing with file: {test_file.name}")
    
    try:
        # Create parser
        parser = MSLParser(str(test_file))
        
        # Load and parse
        parser.load_file()
        parser.parse_sheet()
        
        # Get summary statistics
        stats = parser.get_summary_stats()
        
        print("\n" + "="*60)
        print("MSL FILE SUMMARY")
        print("="*60)
        print(f"File: {test_file.name}")
        print(f"Total species: {stats['total_species']:,}")
        print(f"Realms: {stats['realms']}")
        print(f"Families: {stats['families']}")
        print(f"Genera: {stats['genera']}")
        
        if stats['unique_realms']:
            print(f"\nRealms found:")
            for realm in sorted(stats['unique_realms']):
                print(f"  - {realm}")
        
        # Extract species
        species_list = parser.extract_species()
        
        # Show some examples
        print(f"\n{'='*60}")
        print("EXAMPLE SPECIES RECORDS")
        print("="*60)
        
        # Show first 5 species
        for i, species in enumerate(species_list[:5]):
            print(f"\nSpecies {i+1}:")
            print(f"  Name: {species.species}")
            print(f"  Genus: {species.genus}")
            print(f"  Family: {species.family}")
            print(f"  Order: {species.order}")
            print(f"  Realm: {species.realm}")
            print(f"  Genome: {species.genome_composition}")
        
        # Test YAML output
        print(f"\n{'='*60}")
        print("YAML OUTPUT EXAMPLE")
        print("="*60)
        if species_list:
            print(species_list[0].to_yaml())
        
        # Test path generation
        print(f"\n{'='*60}")
        print("FILE PATH EXAMPLES")
        print("="*60)
        for species in species_list[:3]:
            path = species.get_taxonomy_path()
            print(f"{species.species}:")
            print(f"  → {path}")
        
        # Find some interesting cases
        print(f"\n{'='*60}")
        print("INTERESTING CASES")
        print("="*60)
        
        # Find Caudovirales-related species (if any)
        caudovirales_species = [s for s in species_list if s.order == 'Caudovirales']
        if caudovirales_species:
            print(f"\nFound {len(caudovirales_species)} species in order Caudovirales")
            for species in caudovirales_species[:3]:
                print(f"  - {species.species} ({species.family})")
        
        # Find species from old families (Myoviridae, Podoviridae, Siphoviridae)
        old_families = ['Myoviridae', 'Podoviridae', 'Siphoviridae']
        for family in old_families:
            family_species = [s for s in species_list if s.family == family]
            if family_species:
                print(f"\nFound {len(family_species)} species in family {family}")
                for species in family_species[:3]:
                    print(f"  - {species.species}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing parser: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_msl_parser()
    sys.exit(0 if success else 1)