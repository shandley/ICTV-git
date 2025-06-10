"""
MSL (Master Species List) Parser for ICTV taxonomy data.

This module parses real ICTV MSL Excel files to extract viral taxonomy information.
No mock or simulated data is used - all data comes from actual MSL files.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class MSLParser:
    """Parser for ICTV Master Species List Excel files."""
    
    # Common column name variations across MSL versions
    COLUMN_MAPPINGS = {
        'species': ['Species', 'Virus name', 'Virus Name', 'Species name', 'Current Species Name'],
        'genus': ['Genus', 'Current Genus', 'Genus name'],
        'subfamily': ['Subfamily', 'Current Subfamily', 'Subfamily name'],
        'family': ['Family', 'Current Family', 'Family name'],
        'order': ['Order', 'Current Order', 'Order name'],
        'class': ['Class', 'Current Class', 'Class name'],
        'phylum': ['Phylum', 'Current Phylum', 'Phylum name'],
        'kingdom': ['Kingdom', 'Current Kingdom', 'Kingdom name'],
        'realm': ['Realm', 'Current Realm', 'Realm name'],
        'genome_composition': ['Genome Composition', 'Genome composition', 'Baltimore group'],
        'host': ['Host', 'Host source', 'Host range', 'Natural host'],
        'isolate': ['Isolate', 'Type species', 'Exemplar'],
        'proposal': ['Proposal', 'TaxoProp', 'Taxonomy proposal', 'ICTV proposal']
    }
    
    def __init__(self, msl_file_path: str):
        """
        Initialize parser with MSL file path.
        
        Args:
            msl_file_path: Path to the MSL Excel file
        """
        self.file_path = Path(msl_file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"MSL file not found: {msl_file_path}")
        
        self.version = self._extract_version()
        self.data = None
        self.metadata = {}
        
    def _extract_version(self) -> str:
        """Extract MSL version from filename."""
        filename = self.file_path.name
        if 'MSL' in filename:
            # Extract version number (e.g., MSL23, MSL40)
            parts = filename.split('_')
            for part in parts:
                if part.startswith('MSL') and len(part) > 3:
                    return part
        return 'Unknown'
    
    def parse(self) -> Dict[str, Any]:
        """
        Parse the MSL file and return structured data.
        
        Returns:
            Dictionary containing parsed taxonomy data and metadata
        """
        logger.info(f"Parsing MSL file: {self.file_path.name}")
        
        try:
            # Read Excel file - MSL files typically have the main data in the first sheet
            if self.file_path.suffix == '.xls':
                self.data = pd.read_excel(self.file_path, sheet_name=0, engine='xlrd')
            else:  # .xlsx
                self.data = pd.read_excel(self.file_path, sheet_name=0, engine='openpyxl')
            
            # Clean column names
            self.data.columns = self.data.columns.str.strip()
            
            # Map columns to standard names
            self._standardize_columns()
            
            # Extract metadata
            self.metadata = self._extract_metadata()
            
            # Parse taxonomy data
            taxonomy_data = self._parse_taxonomy()
            
            return {
                'version': self.version,
                'metadata': self.metadata,
                'taxonomy': taxonomy_data,
                'statistics': self._calculate_statistics()
            }
            
        except Exception as e:
            logger.error(f"Error parsing MSL file {self.file_path.name}: {str(e)}")
            raise
    
    def _standardize_columns(self):
        """Map varying column names to standard names."""
        column_mapping = {}
        
        for standard_name, variations in self.COLUMN_MAPPINGS.items():
            for col in self.data.columns:
                if col in variations:
                    column_mapping[col] = standard_name
                    break
        
        # Rename columns
        self.data = self.data.rename(columns=column_mapping)
        
        # Log unmapped columns for debugging
        mapped_cols = set(column_mapping.values())
        all_standard_cols = set(self.COLUMN_MAPPINGS.keys())
        missing_cols = all_standard_cols - mapped_cols
        
        if missing_cols:
            logger.warning(f"Could not find columns for: {missing_cols}")
    
    def _extract_metadata(self) -> Dict[str, Any]:
        """Extract metadata about the MSL file."""
        metadata = {
            'version': self.version,
            'filename': self.file_path.name,
            'total_rows': len(self.data),
            'columns': list(self.data.columns),
            'parse_date': datetime.now().isoformat()
        }
        
        # Count non-null values for each taxonomic rank
        for rank in ['realm', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']:
            if rank in self.data.columns:
                metadata[f'{rank}_count'] = self.data[rank].notna().sum()
        
        return metadata
    
    def _parse_taxonomy(self) -> List[Dict[str, Any]]:
        """Parse taxonomy data from the DataFrame."""
        taxonomy_records = []
        
        for idx, row in self.data.iterrows():
            # Skip rows without species names
            if pd.isna(row.get('species', '')):
                continue
            
            record = {
                'index': idx,
                'species': str(row.get('species', '')).strip(),
                'classification': {}
            }
            
            # Extract classification hierarchy
            for rank in ['realm', 'kingdom', 'phylum', 'class', 'order', 'family', 'subfamily', 'genus']:
                if rank in row and pd.notna(row[rank]):
                    record['classification'][rank] = str(row[rank]).strip()
            
            # Extract additional information
            if 'genome_composition' in row and pd.notna(row['genome_composition']):
                record['genome_composition'] = str(row['genome_composition']).strip()
            
            if 'host' in row and pd.notna(row['host']):
                record['host'] = str(row['host']).strip()
            
            if 'proposal' in row and pd.notna(row['proposal']):
                record['proposal'] = str(row['proposal']).strip()
            
            taxonomy_records.append(record)
        
        return taxonomy_records
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate statistics about the taxonomy data."""
        stats = {
            'total_species': 0,
            'families': {},
            'orders': {},
            'genome_types': {}
        }
        
        if 'species' in self.data.columns:
            stats['total_species'] = self.data['species'].notna().sum()
        
        # Count species per family
        if 'family' in self.data.columns:
            family_counts = self.data[self.data['species'].notna()]['family'].value_counts()
            stats['families'] = family_counts.to_dict()
            stats['total_families'] = len(family_counts)
        
        # Count species per order
        if 'order' in self.data.columns:
            order_counts = self.data[self.data['species'].notna()]['order'].value_counts()
            stats['orders'] = order_counts.to_dict()
            stats['total_orders'] = len(order_counts)
        
        # Count by genome type
        if 'genome_composition' in self.data.columns:
            genome_counts = self.data[self.data['species'].notna()]['genome_composition'].value_counts()
            stats['genome_types'] = genome_counts.to_dict()
        
        return stats
    
    def get_families(self) -> List[str]:
        """Get list of all families in this MSL version."""
        if 'family' not in self.data.columns:
            return []
        return sorted(self.data['family'].dropna().unique().tolist())
    
    def get_species_by_family(self, family_name: str) -> List[Dict[str, Any]]:
        """Get all species belonging to a specific family."""
        if 'family' not in self.data.columns:
            return []
        
        family_data = self.data[self.data['family'] == family_name]
        species_list = []
        
        for idx, row in family_data.iterrows():
            if pd.notna(row.get('species')):
                species_list.append({
                    'species': row['species'],
                    'genus': row.get('genus', ''),
                    'host': row.get('host', ''),
                    'genome': row.get('genome_composition', '')
                })
        
        return species_list
    
    def compare_with(self, other_parser: 'MSLParser') -> Dict[str, Any]:
        """
        Compare this MSL version with another to identify changes.
        
        Args:
            other_parser: Another MSLParser instance
            
        Returns:
            Dictionary containing comparison results
        """
        comparison = {
            'version1': self.version,
            'version2': other_parser.version,
            'species_added': [],
            'species_removed': [],
            'families_added': [],
            'families_removed': [],
            'reclassifications': []
        }
        
        # Get species sets
        species1 = set(self.data['species'].dropna()) if 'species' in self.data.columns else set()
        species2 = set(other_parser.data['species'].dropna()) if 'species' in other_parser.data.columns else set()
        
        comparison['species_added'] = list(species2 - species1)
        comparison['species_removed'] = list(species1 - species2)
        
        # Get family sets
        families1 = set(self.get_families())
        families2 = set(other_parser.get_families())
        
        comparison['families_added'] = list(families2 - families1)
        comparison['families_removed'] = list(families1 - families2)
        
        # Check for reclassifications (species that exist in both but changed family)
        common_species = species1 & species2
        for species in common_species:
            family1 = self.data[self.data['species'] == species]['family'].iloc[0] if len(self.data[self.data['species'] == species]) > 0 else None
            family2 = other_parser.data[other_parser.data['species'] == species]['family'].iloc[0] if len(other_parser.data[other_parser.data['species'] == species]) > 0 else None
            
            if family1 != family2 and pd.notna(family1) and pd.notna(family2):
                comparison['reclassifications'].append({
                    'species': species,
                    'old_family': family1,
                    'new_family': family2
                })
        
        return comparison


def parse_all_msl_files(data_dir: Path) -> Dict[str, Dict[str, Any]]:
    """
    Parse all MSL files in a directory.
    
    Args:
        data_dir: Directory containing MSL files
        
    Returns:
        Dictionary mapping version names to parsed data
    """
    msl_data = {}
    msl_files = sorted(data_dir.glob("*.xls*"))
    
    for msl_file in msl_files:
        try:
            parser = MSLParser(str(msl_file))
            data = parser.parse()
            msl_data[parser.version] = data
            logger.info(f"Successfully parsed {parser.version}: {data['statistics']['total_species']} species")
        except Exception as e:
            logger.error(f"Failed to parse {msl_file.name}: {str(e)}")
    
    return msl_data


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Parse a single MSL file
    data_dir = Path(__file__).parent.parent / "data" / "raw"
    
    # Try parsing the most recent MSL file
    latest_msl = data_dir / "MSL40_ICTV_Master_Species_List_2024_MSL40.v1.xlsx"
    
    if latest_msl.exists():
        parser = MSLParser(str(latest_msl))
        data = parser.parse()
        
        print(f"\nMSL Version: {data['version']}")
        print(f"Total Species: {data['statistics']['total_species']}")
        print(f"Total Families: {data['statistics'].get('total_families', 'N/A')}")
        print(f"Total Orders: {data['statistics'].get('total_orders', 'N/A')}")
        
        # Show top 5 families by species count
        if data['statistics']['families']:
            print("\nTop 5 families by species count:")
            sorted_families = sorted(data['statistics']['families'].items(), key=lambda x: x[1], reverse=True)
            for family, count in sorted_families[:5]:
                print(f"  {family}: {count} species")