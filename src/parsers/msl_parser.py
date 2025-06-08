"""
MSL (Master Species List) parser for ICTV Excel files.

This module handles parsing of ICTV MSL Excel files and extracting
taxonomic information for conversion to git-based format.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict
import yaml
import json

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class VirusSpecies:
    """Represents a virus species with full taxonomic hierarchy."""
    
    # Core identifiers
    species: str
    sort: Optional[int] = None
    
    # Taxonomic hierarchy (15 ranks)
    realm: Optional[str] = None
    subrealm: Optional[str] = None
    kingdom: Optional[str] = None
    subkingdom: Optional[str] = None
    phylum: Optional[str] = None
    subphylum: Optional[str] = None
    class_: Optional[str] = None  # class is reserved word
    subclass: Optional[str] = None
    order: Optional[str] = None
    suborder: Optional[str] = None
    family: Optional[str] = None
    subfamily: Optional[str] = None
    genus: Optional[str] = None
    subgenus: Optional[str] = None
    
    # Additional metadata
    genome_composition: Optional[str] = None
    last_change: Optional[str] = None
    msl_of_last_change: Optional[str] = None
    proposal: Optional[str] = None
    taxon_history_url: Optional[str] = None
    
    def to_yaml(self) -> str:
        """Convert species to YAML format."""
        data = {k: v for k, v in asdict(self).items() if v is not None}
        # Fix class_ back to class for YAML
        if 'class_' in data:
            data['class'] = data.pop('class_')
        return yaml.dump(data, default_flow_style=False, sort_keys=False)
    
    def to_json(self) -> str:
        """Convert species to JSON format."""
        data = {k: v for k, v in asdict(self).items() if v is not None}
        # Fix class_ back to class for JSON
        if 'class_' in data:
            data['class'] = data.pop('class_')
        return json.dumps(data, indent=2)
    
    def get_taxonomy_path(self) -> Path:
        """Generate file system path based on taxonomic hierarchy."""
        path_parts = []
        
        # Build path from highest to lowest rank
        for rank in ['realm', 'kingdom', 'phylum', 'class_', 'order', 'family', 'genus']:
            value = getattr(self, rank)
            if value:
                # Clean name for filesystem
                clean_name = value.lower().replace(' ', '_').replace('/', '_')
                path_parts.append(f"{rank}s/{clean_name}")
        
        # Add species file
        species_name = self.species.lower().replace(' ', '_').replace('/', '_')
        path_parts.append(f"species/{species_name}.yaml")
        
        return Path(*path_parts)


class MSLParser:
    """Parser for ICTV Master Species List Excel files."""
    
    # Common column name variations across MSL versions
    COLUMN_MAPPING = {
        'Sort': ['Sort', 'sort', 'SORT'],
        'Realm': ['Realm', 'realm', 'REALM'],
        'Subrealm': ['Subrealm', 'subrealm', 'SUBREALM'],
        'Kingdom': ['Kingdom', 'kingdom', 'KINGDOM'],
        'Subkingdom': ['Subkingdom', 'subkingdom', 'SUBKINGDOM'],
        'Phylum': ['Phylum', 'phylum', 'PHYLUM'],
        'Subphylum': ['Subphylum', 'subphylum', 'SUBPHYLUM'],
        'Class': ['Class', 'class', 'CLASS'],
        'Subclass': ['Subclass', 'subclass', 'SUBCLASS'],
        'Order': ['Order', 'order', 'ORDER'],
        'Suborder': ['Suborder', 'suborder', 'SUBORDER'],
        'Family': ['Family', 'family', 'FAMILY'],
        'Subfamily': ['Subfamily', 'subfamily', 'SUBFAMILY'],
        'Genus': ['Genus', 'genus', 'GENUS'],
        'Subgenus': ['Subgenus', 'subgenus', 'SUBGENUS'],
        'Species': ['Species', 'species', 'SPECIES', 'Virus name(s)', 'Virus Name'],
        'Genome Composition': ['Genome Composition', 'Genome composition', 'Genome_composition'],
        'Last Change': ['Last Change', 'Last_Change', 'Last change'],
        'MSL of Last Change': ['MSL of Last Change', 'MSL_of_Last_Change'],
        'Proposal': ['Proposal', 'TaxoProp', 'Taxonomy proposal'],
        'Taxon History URL': ['Taxon History URL', 'Taxon_History_URL', 'History URL']
    }
    
    def __init__(self, file_path: str):
        """Initialize parser with MSL file path."""
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"MSL file not found: {file_path}")
        
        self.workbook = None
        self.main_sheet = None
        self.df = None
        
    def load_file(self) -> None:
        """Load Excel file and identify main data sheet."""
        logger.info(f"Loading MSL file: {self.file_path}")
        
        try:
            self.workbook = pd.ExcelFile(self.file_path)
        except Exception as e:
            raise ValueError(f"Failed to load Excel file: {e}")
        
        # Find main sheet (usually named MSL or Master Species List)
        sheet_names = self.workbook.sheet_names
        logger.info(f"Available sheets: {sheet_names}")
        
        # Common main sheet names (check for partial matches too)
        main_sheet_candidates = ['MSL', 'Master Species List', 'MASTER SPECIES LIST', 
                                'Sheet1', 'Data', 'Species']
        
        self.main_sheet = None
        
        # First try exact match
        for candidate in main_sheet_candidates:
            if candidate in sheet_names:
                self.main_sheet = candidate
                break
        
        # If not found, try partial match
        if not self.main_sheet:
            for sheet in sheet_names:
                # Check if sheet contains 'Master Species' or 'MSL' or 'ICTV'
                if any(keyword in sheet for keyword in ['Master Species', 'MSL', 'ICTV']):
                    self.main_sheet = sheet
                    logger.info(f"Found main sheet by partial match: {self.main_sheet}")
                    break
        
        # Skip common non-data sheets
        skip_sheets = ['Version', 'Column Definitions', 'Definitions', 'Summary', 'Info']
        if self.main_sheet in skip_sheets and len(sheet_names) > 1:
            # Try next sheet
            for sheet in sheet_names:
                if sheet not in skip_sheets:
                    self.main_sheet = sheet
                    logger.warning(f"Skipping non-data sheet, using: {self.main_sheet}")
                    break
        
        if not self.main_sheet:
            raise ValueError("Could not identify main data sheet")
        
        logger.info(f"Using main sheet: {self.main_sheet}")
        
    def parse_sheet(self) -> pd.DataFrame:
        """Parse the main data sheet."""
        if not self.workbook or not self.main_sheet:
            raise ValueError("File not loaded. Call load_file() first.")
        
        logger.info(f"Parsing sheet: {self.main_sheet}")
        
        # Read the sheet
        self.df = pd.read_excel(self.workbook, sheet_name=self.main_sheet)
        
        # Standardize column names
        self._standardize_columns()
        
        # Remove empty rows
        self.df = self.df.dropna(subset=['Species'], how='all')
        
        logger.info(f"Parsed {len(self.df)} species records")
        
        return self.df
    
    def _standardize_columns(self) -> None:
        """Standardize column names across different MSL versions."""
        if self.df is None:
            return
        
        current_columns = list(self.df.columns)
        column_mapping = {}
        
        for standard_name, variations in self.COLUMN_MAPPING.items():
            for col in current_columns:
                if col in variations:
                    column_mapping[col] = standard_name
                    break
        
        # Rename columns
        self.df = self.df.rename(columns=column_mapping)
        
        logger.info(f"Standardized columns: {list(self.df.columns)}")
    
    def extract_species(self) -> List[VirusSpecies]:
        """Extract all species as VirusSpecies objects."""
        if self.df is None:
            raise ValueError("No data parsed. Call parse_sheet() first.")
        
        species_list = []
        
        for idx, row in self.df.iterrows():
            # Skip if no species name
            if pd.isna(row.get('Species')):
                continue
            
            species = VirusSpecies(
                species=str(row['Species']),
                sort=int(row['Sort']) if pd.notna(row.get('Sort')) else None,
                realm=str(row['Realm']) if pd.notna(row.get('Realm')) else None,
                subrealm=str(row['Subrealm']) if pd.notna(row.get('Subrealm')) else None,
                kingdom=str(row['Kingdom']) if pd.notna(row.get('Kingdom')) else None,
                subkingdom=str(row['Subkingdom']) if pd.notna(row.get('Subkingdom')) else None,
                phylum=str(row['Phylum']) if pd.notna(row.get('Phylum')) else None,
                subphylum=str(row['Subphylum']) if pd.notna(row.get('Subphylum')) else None,
                class_=str(row['Class']) if pd.notna(row.get('Class')) else None,
                subclass=str(row['Subclass']) if pd.notna(row.get('Subclass')) else None,
                order=str(row['Order']) if pd.notna(row.get('Order')) else None,
                suborder=str(row['Suborder']) if pd.notna(row.get('Suborder')) else None,
                family=str(row['Family']) if pd.notna(row.get('Family')) else None,
                subfamily=str(row['Subfamily']) if pd.notna(row.get('Subfamily')) else None,
                genus=str(row['Genus']) if pd.notna(row.get('Genus')) else None,
                subgenus=str(row['Subgenus']) if pd.notna(row.get('Subgenus')) else None,
                genome_composition=str(row['Genome Composition']) if pd.notna(row.get('Genome Composition')) else None,
                last_change=str(row['Last Change']) if pd.notna(row.get('Last Change')) else None,
                msl_of_last_change=str(row['MSL of Last Change']) if pd.notna(row.get('MSL of Last Change')) else None,
                proposal=str(row['Proposal']) if pd.notna(row.get('Proposal')) else None,
                taxon_history_url=str(row['Taxon History URL']) if pd.notna(row.get('Taxon History URL')) else None,
            )
            
            species_list.append(species)
        
        logger.info(f"Extracted {len(species_list)} species records")
        
        return species_list
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics about the MSL data."""
        if self.df is None:
            raise ValueError("No data parsed. Call parse_sheet() first.")
        
        stats = {
            'total_species': len(self.df),
            'realms': self.df['Realm'].nunique() if 'Realm' in self.df else 0,
            'families': self.df['Family'].nunique() if 'Family' in self.df else 0,
            'genera': self.df['Genus'].nunique() if 'Genus' in self.df else 0,
            'unique_realms': list(self.df['Realm'].dropna().unique()) if 'Realm' in self.df else [],
            'unique_families': list(self.df['Family'].dropna().unique()) if 'Family' in self.df else [],
        }
        
        return stats


def parse_msl_file(file_path: str) -> List[VirusSpecies]:
    """Convenience function to parse an MSL file."""
    parser = MSLParser(file_path)
    parser.load_file()
    parser.parse_sheet()
    return parser.extract_species()


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        try:
            # Parse file
            parser = MSLParser(file_path)
            parser.load_file()
            parser.parse_sheet()
            
            # Get summary
            stats = parser.get_summary_stats()
            print(f"\nMSL Summary:")
            print(f"Total species: {stats['total_species']}")
            print(f"Realms: {stats['realms']}")
            print(f"Families: {stats['families']}")
            print(f"Genera: {stats['genera']}")
            
            # Extract species
            species_list = parser.extract_species()
            
            # Show first few species
            print(f"\nFirst 5 species:")
            for species in species_list[:5]:
                print(f"- {species.species} ({species.family}, {species.genus})")
                
        except Exception as e:
            logger.error(f"Error parsing MSL file: {e}")
            sys.exit(1)
    else:
        print("Usage: python msl_parser.py <path_to_msl_file.xlsx>")