#!/usr/bin/env python3
"""
Analyze the Caudovirales reclassification across MSL versions.

This script demonstrates the breaking changes in viral taxonomy
by tracking how Caudovirales species were reclassified.
"""

import sys
from pathlib import Path
import pandas as pd
from collections import defaultdict
import logging
from typing import Dict, List, Set

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.parsers.msl_parser import MSLParser

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CaudoviralesAnalyzer:
    """Analyze changes in Caudovirales classification across MSL versions."""
    
    # The three morphology-based families that were abolished
    OLD_FAMILIES = ['Myoviridae', 'Podoviridae', 'Siphoviridae']
    
    def __init__(self, data_dir: str):
        """Initialize analyzer with data directory."""
        self.data_dir = Path(data_dir)
        self.msl_data = {}
        self.caudovirales_tracking = defaultdict(dict)
    
    def load_msl_versions(self, versions: List[str]) -> None:
        """Load specified MSL versions."""
        for version in versions:
            # Find file for this version
            pattern = f"{version}_*.xlsx"
            files = list(self.data_dir.glob(pattern))
            
            if not files:
                logger.warning(f"No file found for {version}")
                continue
            
            file_path = files[0]
            logger.info(f"Loading {version} from {file_path.name}")
            
            try:
                parser = MSLParser(str(file_path))
                parser.load_file()
                parser.parse_sheet()
                species_list = parser.extract_species()
                
                self.msl_data[version] = {
                    'file': file_path.name,
                    'species': species_list,
                    'stats': parser.get_summary_stats()
                }
                
                logger.info(f"  Loaded {len(species_list)} species from {version}")
                
            except Exception as e:
                logger.error(f"Failed to load {version}: {e}")
    
    def analyze_caudovirales_changes(self) -> Dict:
        """Analyze how Caudovirales changed across versions."""
        results = {
            'summary': {},
            'family_changes': {},
            'species_tracking': {},
            'new_families': set()
        }
        
        for version, data in sorted(self.msl_data.items()):
            version_stats = {
                'total_species': len(data['species']),
                'caudovirales_count': 0,
                'old_families': {},
                'new_families': set()
            }
            
            # Count Caudovirales and track families
            caudovirales_species = []
            family_counts = defaultdict(int)
            
            for species in data['species']:
                if species.order == 'Caudovirales':
                    caudovirales_species.append(species)
                    version_stats['caudovirales_count'] += 1
                    if species.family:
                        family_counts[species.family] += 1
                
                # Also check if species is in old families regardless of order
                if species.family in self.OLD_FAMILIES:
                    if species.family not in version_stats['old_families']:
                        version_stats['old_families'][species.family] = 0
                    version_stats['old_families'][species.family] += 1
            
            # Identify new families (not in old families list)
            for family in family_counts:
                if family not in self.OLD_FAMILIES:
                    version_stats['new_families'].add(family)
                    results['new_families'].add(family)
            
            version_stats['caudovirales_families'] = dict(family_counts)
            results['summary'][version] = version_stats
            
            # Track individual species changes
            if version == 'MSL36':  # Before the big change
                for species in caudovirales_species:
                    if species.family in self.OLD_FAMILIES:
                        self.caudovirales_tracking[species.species] = {
                            'original_family': species.family,
                            'original_genus': species.genus,
                            'versions': {version: {
                                'family': species.family,
                                'genus': species.genus
                            }}
                        }
        
        # Now track what happened to these species in later versions
        for species_name, tracking in self.caudovirales_tracking.items():
            for version, data in self.msl_data.items():
                if version <= 'MSL36':
                    continue
                
                # Find this species in the newer version
                found = False
                for species in data['species']:
                    if species.species == species_name:
                        tracking['versions'][version] = {
                            'family': species.family,
                            'genus': species.genus,
                            'order': species.order
                        }
                        found = True
                        break
                
                if not found:
                    tracking['versions'][version] = {'status': 'not_found'}
        
        results['species_tracking'] = self.caudovirales_tracking
        
        return results
    
    def generate_report(self, results: Dict) -> str:
        """Generate a human-readable report of the analysis."""
        report = []
        report.append("="*80)
        report.append("CAUDOVIRALES RECLASSIFICATION ANALYSIS")
        report.append("="*80)
        report.append("")
        
        # Summary by version
        report.append("SUMMARY BY MSL VERSION:")
        report.append("-"*80)
        
        for version in sorted(results['summary'].keys()):
            stats = results['summary'][version]
            report.append(f"\n{version}:")
            report.append(f"  Total species: {stats['total_species']:,}")
            report.append(f"  Caudovirales species: {stats['caudovirales_count']:,}")
            
            if stats['old_families']:
                report.append(f"  Old morphology-based families:")
                for family, count in sorted(stats['old_families'].items()):
                    report.append(f"    - {family}: {count} species")
            
            if stats['new_families']:
                report.append(f"  New genomics-based families: {len(stats['new_families'])}")
        
        # The big change analysis
        report.append("\n" + "="*80)
        report.append("THE BIG CHANGE: MSL36 → MSL37")
        report.append("="*80)
        
        if 'MSL36' in results['summary'] and 'MSL37' in results['summary']:
            msl36 = results['summary']['MSL36']
            msl37 = results['summary']['MSL37']
            
            report.append("\nBEFORE (MSL36):")
            total_old_families = sum(msl36['old_families'].values())
            report.append(f"  Total species in old families: {total_old_families}")
            for family, count in sorted(msl36['old_families'].items()):
                report.append(f"    - {family}: {count} species")
            
            report.append("\nAFTER (MSL37):")
            if msl37['old_families']:
                report.append("  Old families still present:")
                for family, count in sorted(msl37['old_families'].items()):
                    report.append(f"    - {family}: {count} species")
            else:
                report.append("  Old morphology-based families: COMPLETELY ABOLISHED")
            
            if msl37['new_families']:
                report.append(f"\n  New families created: {len(msl37['new_families'])}")
                for family in sorted(list(msl37['new_families']))[:10]:  # Show first 10
                    count = msl37['caudovirales_families'].get(family, 0)
                    report.append(f"    - {family}: {count} species")
                if len(msl37['new_families']) > 10:
                    report.append(f"    ... and {len(msl37['new_families']) - 10} more families")
        
        # Example species tracking
        report.append("\n" + "="*80)
        report.append("EXAMPLE SPECIES RECLASSIFICATIONS")
        report.append("="*80)
        
        examples_shown = 0
        for species_name, tracking in results['species_tracking'].items():
            if examples_shown >= 5:  # Show first 5 examples
                break
            
            if 'MSL36' in tracking['versions'] and 'MSL37' in tracking['versions']:
                v36 = tracking['versions']['MSL36']
                v37 = tracking['versions']['MSL37']
                
                if v37.get('status') != 'not_found' and v36['family'] != v37.get('family'):
                    report.append(f"\n{species_name}:")
                    report.append(f"  MSL36: {v36['family']} → MSL37: {v37.get('family', 'Unknown')}")
                    report.append(f"  Genus: {v36['genus']} → {v37.get('genus', 'Unknown')}")
                    examples_shown += 1
        
        return "\n".join(report)


def main():
    """Run Caudovirales analysis."""
    data_dir = Path(__file__).parent.parent / 'data' / 'raw'
    
    # Analyze key versions: before and after the big change
    analyzer = CaudoviralesAnalyzer(str(data_dir))
    
    # Load MSL versions around the Caudovirales reclassification
    versions = ['MSL35', 'MSL36', 'MSL37', 'MSL38']
    analyzer.load_msl_versions(versions)
    
    # Analyze changes
    results = analyzer.analyze_caudovirales_changes()
    
    # Generate report
    report = analyzer.generate_report(results)
    print(report)
    
    # Save report
    report_path = Path(__file__).parent.parent / 'data' / 'caudovirales_analysis.txt'
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"\n\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()