"""
Tests for MSL parsers
"""

import unittest
import tempfile
import pandas as pd
from pathlib import Path
from parsers.msl_parser import MSLParser
from parsers.incremental_parser import IncrementalMSLParser


class TestMSLParser(unittest.TestCase):
    """Test basic MSL parsing functionality."""
    
    def setUp(self):
        """Create test data."""
        self.test_data = pd.DataFrame({
            'Species': ['Tobacco mosaic virus', 'SARS-CoV-2'],
            'Genus': ['Tobamovirus', 'Betacoronavirus'],
            'Family': ['Virgaviridae', 'Coronaviridae'],
            'Order': ['Martellivirales', 'Nidovirales'],
            'Class': ['Alsuviricetes', 'Pisoniviricetes'],
            'Phylum': ['Kitrinoviricota', 'Pisuviricota'],
            'Kingdom': ['Orthornavirae', 'Orthornavirae'],
            'Realm': ['Riboviria', 'Riboviria'],
            'Genome Composition': ['ssRNA(+)', 'ssRNA(+)']
        })
        
        # Create temporary Excel file
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        self.test_data.to_excel(self.temp_file.name, sheet_name='MSL', index=False)
        
    def tearDown(self):
        """Clean up test files."""
        Path(self.temp_file.name).unlink(missing_ok=True)
        
    def test_parser_initialization(self):
        """Test parser can be initialized."""
        parser = MSLParser(self.temp_file.name)
        self.assertIsNotNone(parser)
        
    def test_parse_species(self):
        """Test parsing species data."""
        parser = MSLParser(self.temp_file.name)
        results = parser.parse_to_yaml(self.temp_file.name, version='TEST')
        
        # Should return dictionary of species
        self.assertIsInstance(results, dict)
        self.assertIn('species', results)
        self.assertEqual(len(results['species']), 2)
        
    def test_species_data_structure(self):
        """Test parsed species have correct structure."""
        parser = MSLParser(self.temp_file.name)
        results = parser.parse_to_yaml(self.temp_file.name, version='TEST')
        
        # Check first species
        species = results['species'][0]
        self.assertIn('scientific_name', species)
        self.assertIn('classification', species)
        self.assertIn('genome', species)
        
        # Check classification hierarchy
        classification = species['classification']
        self.assertIn('genus', classification)
        self.assertIn('family', classification)
        self.assertIn('realm', classification)


class TestIncrementalParser(unittest.TestCase):
    """Test incremental parsing functionality."""
    
    def test_parser_initialization(self):
        """Test incremental parser can be initialized."""
        parser = IncrementalMSLParser()
        self.assertIsNotNone(parser)
        
    def test_version_detection(self):
        """Test MSL version detection from filename."""
        parser = IncrementalMSLParser()
        
        # Test various filename formats
        test_cases = [
            ('MSL38.xlsx', 'MSL38'),
            ('ICTV_Master_Species_List_2022_MSL38.v3.xlsx', 'MSL38'),
            ('data/MSL40.xlsx', 'MSL40'),
        ]
        
        for filename, expected in test_cases:
            version = parser._extract_version(filename)
            self.assertEqual(version, expected)


if __name__ == '__main__':
    unittest.main()