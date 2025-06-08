#!/usr/bin/env python3
"""
Convert complete MSL history (MSL23-40) to git-based taxonomy repository.

This script converts all available ICTV MSL files into a single git repository
showing the complete 20-year evolution of viral taxonomy from 2005-2024.
"""

import sys
import os
from pathlib import Path
import logging
import shutil
import re

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


def get_available_msl_files(data_dir: Path) -> list:
    """Get all available MSL files sorted by version number."""
    
    # Find all MSL files (.xls and .xlsx)
    msl_files = []
    msl_files.extend(data_dir.glob("MSL*_*.xls"))
    msl_files.extend(data_dir.glob("MSL*_*.xlsx"))
    
    # Extract version numbers and sort
    version_files = []
    for file_path in msl_files:
        # Extract MSL version number (e.g., MSL23, MSL36)
        match = re.search(r'MSL(\d+)', file_path.name)
        if match:
            version_num = int(match.group(1))
            # Extract year from filename
            year_match = re.search(r'(\d{4})', file_path.name)
            year = int(year_match.group(1)) if year_match else None
            
            version_files.append({
                'version_num': version_num,
                'version_name': f'MSL{version_num}',
                'year': year,
                'file_path': file_path,
                'filename': file_path.name
            })
    
    # Sort by version number
    version_files.sort(key=lambda x: x['version_num'])
    
    return version_files


def convert_complete_history():
    """Convert all available MSL files to show complete taxonomy evolution."""
    
    data_dir = Path(__file__).parent.parent / 'data' / 'raw'
    output_dir = Path(__file__).parent.parent / 'output' / 'viral-taxonomy-complete-history'
    
    logger.info("Scanning for available MSL files...")
    msl_files = get_available_msl_files(data_dir)
    
    if not msl_files:
        logger.error("No MSL files found. Please run download_msl.py first.")
        return False
    
    print("\n" + "="*80)
    print("COMPLETE ICTV TAXONOMY HISTORY CONVERSION")
    print("="*80)
    print(f"Found {len(msl_files)} MSL files:")
    for msl_info in msl_files:
        file_size = msl_info['file_path'].stat().st_size / 1024  # KB
        print(f"  - {msl_info['version_name']} ({msl_info['year']}): {msl_info['filename']} ({file_size:.0f} KB)")
    
    # Clean output directory if it exists
    if output_dir.exists():
        logger.info(f"Cleaning existing output directory: {output_dir}")
        shutil.rmtree(output_dir)
    
    # Create converter
    logger.info(f"Creating git repository at: {output_dir}")
    converter = MSLToGitConverter(str(output_dir), initialize=True)
    
    # Track conversion statistics
    conversion_stats = []
    
    # Convert each version in chronological order
    for i, msl_info in enumerate(msl_files):
        version_name = msl_info['version_name']
        file_path = msl_info['file_path']
        year = msl_info['year']
        
        print(f"\n{'-'*60}")
        print(f"Converting {version_name} ({year}): {file_path.name}")
        print(f"Progress: {i+1}/{len(msl_files)}")
        print(f"{'-'*60}")
        
        try:
            # Parse file first to get basic stats
            parser = MSLParser(str(file_path))
            parser.load_file()
            parser.parse_sheet()
            species_list = parser.extract_species()
            
            # Convert to git
            species_count = converter.convert_msl_file(str(file_path), version_name.lower())
            
            # Get taxonomy stats
            stats = converter.get_taxonomy_stats()
            
            conversion_info = {
                'version': version_name,
                'year': year,
                'filename': file_path.name,
                'species_count': species_count,
                'families': len(stats['families']),
                'genera': len(stats['genera']),
                'success': True
            }
            
            print(f"  ✓ Successfully converted {species_count:,} species")
            print(f"    - Families: {len(stats['families']):,}")
            print(f"    - Genera: {len(stats['genera']):,}")
            
            # Show growth compared to previous version
            if conversion_stats:
                prev_stats = conversion_stats[-1]
                species_growth = species_count - prev_stats['species_count']
                families_growth = len(stats['families']) - prev_stats['families']
                print(f"    - Growth: +{species_growth:,} species, +{families_growth:,} families")
            
            conversion_stats.append(conversion_info)
            
        except Exception as e:
            logger.error(f"  ✗ Failed to convert {version_name}: {e}")
            conversion_stats.append({
                'version': version_name,
                'year': year,
                'filename': file_path.name,
                'error': str(e),
                'success': False
            })
    
    # Final summary
    print("\n" + "="*80)
    print("COMPLETE HISTORY CONVERSION SUMMARY")
    print("="*80)
    
    successful = [s for s in conversion_stats if s.get('success', False)]
    failed = [s for s in conversion_stats if not s.get('success', False)]
    
    print(f"Repository created at: {output_dir}")
    print(f"Total conversions: {len(conversion_stats)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        print(f"\n20-Year Taxonomy Evolution ({successful[0]['year']}-{successful[-1]['year']}):")
        print(f"  First version: {successful[0]['version']} ({successful[0]['species_count']:,} species)")
        print(f"  Latest version: {successful[-1]['version']} ({successful[-1]['species_count']:,} species)")
        
        total_growth = successful[-1]['species_count'] - successful[0]['species_count']
        years_span = successful[-1]['year'] - successful[0]['year']
        avg_annual_growth = total_growth / years_span if years_span > 0 else 0
        
        print(f"  Total growth: +{total_growth:,} species over {years_span} years")
        print(f"  Average annual growth: {avg_annual_growth:.0f} species/year")
    
    if failed:
        print(f"\nFailed conversions:")
        for failure in failed:
            print(f"  - {failure['version']}: {failure['error']}")
    
    # Usage instructions
    print(f"\nExplore the complete taxonomy evolution:")
    print(f"  cd {output_dir}")
    print(f"  git log --oneline  # See all MSL versions")
    print(f"  git log --graph --oneline  # Visual timeline")
    print(f"  git diff msl23 msl40 --stat  # Overall 20-year changes")
    print(f"  git diff msl36 msl37 --stat  # Caudovirales reorganization")
    
    # Create summary report
    report_path = output_dir / 'CONVERSION_REPORT.md'
    with open(report_path, 'w') as f:
        f.write("# Complete ICTV Taxonomy History Conversion Report\n\n")
        f.write(f"Generated: {Path(__file__).name}\n\n")
        f.write("## Conversion Summary\n\n")
        f.write(f"- Total MSL versions processed: {len(conversion_stats)}\n")
        f.write(f"- Successful conversions: {len(successful)}\n")
        f.write(f"- Failed conversions: {len(failed)}\n")
        f.write(f"- Time span: {successful[0]['year']}-{successful[-1]['year']} ({years_span} years)\n")
        f.write(f"- Species growth: {successful[0]['species_count']:,} → {successful[-1]['species_count']:,} (+{total_growth:,})\n\n")
        
        f.write("## Version Details\n\n")
        f.write("| Version | Year | Species | Families | Genera | Status |\n")
        f.write("|---------|------|---------|----------|--------|--------|\n")
        for stats in conversion_stats:
            if stats.get('success', False):
                f.write(f"| {stats['version']} | {stats['year']} | {stats['species_count']:,} | {stats['families']:,} | {stats['genera']:,} | ✓ |\n")
            else:
                f.write(f"| {stats['version']} | {stats['year']} | - | - | - | ✗ |\n")
        
        f.write(f"\n## Git Repository Usage\n\n")
        f.write(f"```bash\n")
        f.write(f"cd {output_dir}\n")
        f.write(f"git log --oneline  # See chronological changes\n")
        f.write(f"git diff msl23 msl40 --stat  # 20-year overview\n")
        f.write(f"git show msl36  # Examine specific version\n")
        f.write(f"```\n")
    
    logger.info(f"Conversion report saved to: {report_path}")
    
    return len(failed) == 0


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert complete MSL history to git repository')
    parser.add_argument('--output', type=str,
                       help='Output directory for repository (default: output/viral-taxonomy-complete-history)')
    
    args = parser.parse_args()
    
    success = convert_complete_history()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()