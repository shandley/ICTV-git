#!/usr/bin/env python3
"""
Convert MSL files to git-based taxonomy repository.

This script converts ICTV MSL Excel files into a git repository
with taxonomic hierarchy as directory structure.
"""

import sys
import os
from pathlib import Path
import logging
import shutil

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.converters.msl_to_git import MSLToGitConverter
from src.parsers.msl_parser import MSLParser

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def convert_msl36_demo():
    """Convert MSL36 as a demonstration."""
    
    # Paths
    data_dir = Path(__file__).parent.parent / 'data' / 'raw'
    output_dir = Path(__file__).parent.parent / 'output' / 'viral-taxonomy'
    
    # Find MSL36 file
    msl36_files = list(data_dir.glob("MSL36_*.xlsx"))
    if not msl36_files:
        logger.error("MSL36 file not found. Please run download_msl.py first.")
        return False
    
    msl_file = msl36_files[0]
    logger.info(f"Using MSL file: {msl_file.name}")
    
    # Clean output directory if it exists
    if output_dir.exists():
        logger.info(f"Cleaning existing output directory: {output_dir}")
        shutil.rmtree(output_dir)
    
    # Create converter
    logger.info(f"Creating git repository at: {output_dir}")
    converter = MSLToGitConverter(str(output_dir), initialize=True)
    
    # Convert MSL36
    logger.info("Converting MSL36 to git structure...")
    species_count = converter.convert_msl_file(str(msl_file), 'MSL36')
    
    # Get statistics
    stats = converter.get_taxonomy_stats()
    
    print("\n" + "="*60)
    print("MSL36 CONVERSION COMPLETE")
    print("="*60)
    print(f"Repository created at: {output_dir}")
    print(f"\nStatistics:")
    print(f"  Total species: {species_count}")
    print(f"  Realms: {len(stats['realms'])}")
    print(f"  Families: {len(stats['families'])}")
    print(f"  Genera: {len(stats['genera'])}")
    print(f"  Deepest taxonomy path: {stats['deepest_path']} levels")
    
    print(f"\nTop 5 Realms:")
    realm_counts = sorted(stats['realms'].items(), key=lambda x: x[1], reverse=True)
    for realm, count in realm_counts[:5]:
        print(f"  - {realm}: {count} species")
    
    print(f"\nTop 10 Families:")
    family_counts = sorted(stats['families'].items(), key=lambda x: x[1], reverse=True)
    for family, count in family_counts[:10]:
        print(f"  - {family}: {count} species")
    
    # Show example of created structure
    print(f"\nExample species files created:")
    species_files = list(output_dir.rglob("*.yaml"))[:5]
    for species_file in species_files:
        rel_path = species_file.relative_to(output_dir)
        print(f"  - {rel_path}")
    
    print(f"\nTo explore the repository:")
    print(f"  cd {output_dir}")
    print(f"  git log --oneline")
    print(f"  git show msl36")
    print(f"  find . -name '*.yaml' | head -10")
    
    return True


def convert_multiple_versions():
    """Convert multiple MSL versions to show evolution."""
    
    data_dir = Path(__file__).parent.parent / 'data' / 'raw'
    output_dir = Path(__file__).parent.parent / 'output' / 'viral-taxonomy-evolution'
    
    # Versions to convert (showing the Caudovirales change)
    versions = ['MSL35', 'MSL36', 'MSL37', 'MSL38']
    
    # Clean output directory if it exists
    if output_dir.exists():
        logger.info(f"Cleaning existing output directory: {output_dir}")
        shutil.rmtree(output_dir)
    
    # Create converter
    logger.info(f"Creating git repository at: {output_dir}")
    converter = MSLToGitConverter(str(output_dir), initialize=True)
    
    # Convert each version
    for version in versions:
        # Find file for this version
        version_files = list(data_dir.glob(f"{version}_*.xlsx"))
        if not version_files:
            logger.warning(f"No file found for {version}")
            continue
        
        msl_file = version_files[0]
        logger.info(f"\nConverting {version} from {msl_file.name}")
        
        try:
            species_count = converter.convert_msl_file(str(msl_file), version)
            logger.info(f"  Successfully converted {species_count} species")
        except Exception as e:
            logger.error(f"  Failed to convert {version}: {e}")
    
    print("\n" + "="*60)
    print("MULTI-VERSION CONVERSION COMPLETE")
    print("="*60)
    print(f"Repository created at: {output_dir}")
    print(f"\nTo explore the taxonomy evolution:")
    print(f"  cd {output_dir}")
    print(f"  git log --oneline")
    print(f"  git diff msl36 msl37 --stat  # See the Caudovirales changes")
    print(f"  git diff msl36 msl37 -- realms/*/orders/caudovirales/")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert MSL files to git repository')
    parser.add_argument('--demo', action='store_true', 
                       help='Run MSL36 demo conversion')
    parser.add_argument('--evolution', action='store_true',
                       help='Convert multiple versions to show evolution')
    parser.add_argument('--file', type=str,
                       help='Convert specific MSL file')
    parser.add_argument('--output', type=str,
                       help='Output directory for repository')
    parser.add_argument('--version', type=str,
                       help='MSL version (e.g., MSL36)')
    
    args = parser.parse_args()
    
    if args.demo:
        success = convert_msl36_demo()
    elif args.evolution:
        success = convert_multiple_versions()
    elif args.file and args.output and args.version:
        from src.converters.msl_to_git import convert_single_msl
        convert_single_msl(args.file, args.output, args.version)
        success = True
    else:
        print("Please specify --demo, --evolution, or provide --file, --output, and --version")
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()