"""
Simple MSL Parser using only built-in libraries.
Parses CSV exports of ICTV MSL files.
"""

import csv
import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict, Counter


class SimpleMSLParser:
    """Simple parser for ICTV MSL CSV files using only built-in libraries."""
    
    def __init__(self, csv_file_path: str):
        """Initialize parser with CSV file path."""
        self.file_path = Path(csv_file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        
        self.version = self._extract_version()
        self.data = []
        self.headers = []
        
    def _extract_version(self) -> str:
        """Extract MSL version from filename."""
        filename = self.file_path.name
        if 'MSL' in filename:
            parts = filename.split('_')
            for part in parts:
                if part.startswith('MSL') and len(part) > 3:
                    return part[:5]  # e.g., MSL23, MSL40
        return 'Unknown'
    
    def parse(self) -> Dict[str, Any]:
        """Parse the CSV file and return structured data."""
        with open(self.file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            self.headers = reader.fieldnames or []
            self.data = list(reader)
        
        # Process and return data
        return {
            'version': self.version,
            'metadata': self._extract_metadata(),
            'statistics': self._calculate_statistics(),
            'sample_data': self.data[:5] if self.data else []  # First 5 records as sample
        }
    
    def _extract_metadata(self) -> Dict[str, Any]:
        """Extract metadata about the MSL file."""
        return {
            'version': self.version,
            'filename': self.file_path.name,
            'total_rows': len(self.data),
            'columns': self.headers
        }
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate statistics from the data."""
        stats = {
            'total_species': 0,
            'families': Counter(),
            'orders': Counter(),
            'genome_types': Counter()
        }
        
        # Find relevant columns (case-insensitive)
        species_col = self._find_column(['Species', 'Virus name', 'Current Species Name'])
        family_col = self._find_column(['Family', 'Current Family'])
        order_col = self._find_column(['Order', 'Current Order'])
        genome_col = self._find_column(['Genome Composition', 'Baltimore group'])
        
        for row in self.data:
            # Count species
            if species_col and row.get(species_col):
                stats['total_species'] += 1
                
                # Count families
                if family_col and row.get(family_col):
                    stats['families'][row[family_col]] += 1
                
                # Count orders  
                if order_col and row.get(order_col):
                    stats['orders'][row[order_col]] += 1
                
                # Count genome types
                if genome_col and row.get(genome_col):
                    stats['genome_types'][row[genome_col]] += 1
        
        # Convert Counters to regular dicts for JSON serialization
        stats['families'] = dict(stats['families'].most_common())
        stats['orders'] = dict(stats['orders'].most_common())
        stats['genome_types'] = dict(stats['genome_types'].most_common())
        stats['total_families'] = len(stats['families'])
        stats['total_orders'] = len(stats['orders'])
        
        return stats
    
    def _find_column(self, possible_names: List[str]) -> str:
        """Find column name from list of possibilities (case-insensitive)."""
        headers_lower = {h.lower(): h for h in self.headers}
        for name in possible_names:
            if name.lower() in headers_lower:
                return headers_lower[name.lower()]
        return ''
    
    def get_families(self) -> List[str]:
        """Get list of all families."""
        family_col = self._find_column(['Family', 'Current Family'])
        if not family_col:
            return []
        
        families = set()
        for row in self.data:
            if row.get(family_col):
                families.add(row[family_col])
        
        return sorted(families)
    
    def analyze_family_sizes_over_time(self, all_versions_data: Dict[str, 'SimpleMSLParser']) -> Dict[str, Any]:
        """Analyze how family sizes change over MSL versions."""
        family_evolution = defaultdict(dict)
        
        # Get all families across all versions
        all_families = set()
        for version, parser in all_versions_data.items():
            all_families.update(parser.get_families())
        
        # Track family sizes across versions
        for family in all_families:
            for version, parser in sorted(all_versions_data.items()):
                family_col = parser._find_column(['Family', 'Current Family'])
                species_col = parser._find_column(['Species', 'Virus name', 'Current Species Name'])
                
                if family_col and species_col:
                    count = sum(1 for row in parser.data 
                              if row.get(family_col) == family and row.get(species_col))
                    if count > 0:
                        family_evolution[family][version] = count
        
        # Find families that split or were created
        split_families = []
        new_families = []
        
        for family, history in family_evolution.items():
            versions = sorted(history.keys())
            if len(versions) > 1:
                # Check if family disappeared (potential split)
                if versions[-1] != sorted(all_versions_data.keys())[-1]:
                    split_families.append({
                        'family': family,
                        'last_seen': versions[-1],
                        'peak_size': max(history.values())
                    })
                # Check if family appeared later (new family)
                if versions[0] != sorted(all_versions_data.keys())[0]:
                    new_families.append({
                        'family': family,
                        'first_seen': versions[0],
                        'initial_size': history[versions[0]]
                    })
        
        return {
            'family_evolution': dict(family_evolution),
            'split_families': split_families,
            'new_families': new_families,
            'total_families_tracked': len(family_evolution)
        }


def demo_real_data_analysis():
    """Demonstrate analysis using real ICTV data."""
    print("ICTV MSL Real Data Analysis Demo")
    print("=" * 50)
    print("\nNOTE: This analysis uses ONLY real ICTV MSL data.")
    print("To run this demo, you need to export MSL Excel files to CSV format.")
    print("\nSteps to prepare data:")
    print("1. Open MSL Excel files in Excel/LibreOffice")
    print("2. Export the main sheet as CSV")
    print("3. Save in data/csv/ directory")
    print("\nExample: MSL40_ICTV_Master_Species_List_2024_MSL40.csv")
    
    # Check for CSV files
    csv_dir = Path(__file__).parent.parent / "data" / "csv"
    if not csv_dir.exists():
        print(f"\nCreating directory: {csv_dir}")
        csv_dir.mkdir(parents=True, exist_ok=True)
        return
    
    csv_files = list(csv_dir.glob("*.csv"))
    if not csv_files:
        print(f"\nNo CSV files found in {csv_dir}")
        print("Please export MSL Excel files to CSV format first.")
        return
    
    print(f"\nFound {len(csv_files)} CSV file(s)")
    
    # Parse all available CSV files
    all_parsers = {}
    for csv_file in sorted(csv_files):
        try:
            parser = SimpleMSLParser(str(csv_file))
            data = parser.parse()
            all_parsers[parser.version] = parser
            
            print(f"\n{parser.version}:")
            print(f"  Total species: {data['statistics']['total_species']}")
            print(f"  Total families: {data['statistics']['total_families']}")
            print(f"  Total orders: {data['statistics']['total_orders']}")
            
            # Show top 3 families
            if data['statistics']['families']:
                print("  Top 3 families by species count:")
                families = list(data['statistics']['families'].items())
                for family, count in families[:3]:
                    print(f"    {family}: {count} species")
        
        except Exception as e:
            print(f"\nError parsing {csv_file.name}: {str(e)}")
    
    # If we have multiple versions, analyze evolution
    if len(all_parsers) > 1:
        print("\n" + "=" * 50)
        print("FAMILY SIZE EVOLUTION ANALYSIS")
        print("=" * 50)
        
        # Use the most recent parser for analysis
        latest_version = sorted(all_parsers.keys())[-1]
        latest_parser = all_parsers[latest_version]
        
        analysis = latest_parser.analyze_family_sizes_over_time(all_parsers)
        
        print(f"\nTotal families tracked: {analysis['total_families_tracked']}")
        print(f"Families that disappeared: {len(analysis['split_families'])}")
        print(f"New families created: {len(analysis['new_families'])}")
        
        # Show some examples
        if analysis['split_families']:
            print("\nExample families that disappeared (potential splits):")
            for fam in analysis['split_families'][:3]:
                print(f"  {fam['family']}: last seen in {fam['last_seen']} with {fam['peak_size']} species")
        
        if analysis['new_families']:
            print("\nExample new families:")
            for fam in analysis['new_families'][:3]:
                print(f"  {fam['family']}: first seen in {fam['first_seen']} with {fam['initial_size']} species")
        
        # Save detailed results
        results_file = csv_dir.parent / "family_evolution_analysis.json"
        with open(results_file, 'w') as f:
            json.dump(analysis, f, indent=2)
        print(f"\nDetailed results saved to: {results_file}")


if __name__ == "__main__":
    demo_real_data_analysis()