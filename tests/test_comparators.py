"""
Tests for version comparison tools
"""

import unittest
from community_tools.version_comparator import VersionComparator


class TestVersionComparator(unittest.TestCase):
    """Test version comparison functionality."""
    
    def setUp(self):
        """Create test data."""
        self.v1_species = {
            'Tobacco mosaic virus': {
                'genus': 'Tobamovirus',
                'family': 'Virgaviridae'
            },
            'SARS-CoV': {
                'genus': 'Betacoronavirus',
                'family': 'Coronaviridae'
            },
            'Phage Lambda': {
                'genus': 'Lambdavirus',
                'family': 'Siphoviridae'
            }
        }
        
        self.v2_species = {
            'Tobacco mosaic virus': {
                'genus': 'Tobamovirus',
                'family': 'Virgaviridae'
            },
            'SARS-CoV-2': {  # New species
                'genus': 'Betacoronavirus',
                'family': 'Coronaviridae'
            },
            'Phage Lambda': {
                'genus': 'Lambdavirus',
                'family': 'Drexlerviridae'  # Reclassified
            }
        }
        
    def test_comparator_initialization(self):
        """Test comparator can be initialized."""
        comparator = VersionComparator(None)  # Don't need real repo for tests
        self.assertIsNotNone(comparator)
        
    def test_detect_added_species(self):
        """Test detection of newly added species."""
        comparator = VersionComparator(None)
        changes = comparator._analyze_changes(self.v1_species, self.v2_species)
        
        self.assertIn('added', changes)
        self.assertIn('SARS-CoV-2', changes['added'])
        
    def test_detect_removed_species(self):
        """Test detection of removed species."""
        comparator = VersionComparator(None)
        changes = comparator._analyze_changes(self.v1_species, self.v2_species)
        
        self.assertIn('removed', changes)
        self.assertIn('SARS-CoV', changes['removed'])
        
    def test_detect_reclassification(self):
        """Test detection of reclassified species."""
        comparator = VersionComparator(None)
        changes = comparator._analyze_changes(self.v1_species, self.v2_species)
        
        self.assertIn('reclassified', changes)
        self.assertEqual(len(changes['reclassified']), 1)
        
        # Check reclassification details
        reclassified = changes['reclassified'][0]
        self.assertEqual(reclassified['species'], 'Phage Lambda')
        self.assertEqual(reclassified['changes']['family']['from'], 'Siphoviridae')
        self.assertEqual(reclassified['changes']['family']['to'], 'Drexlerviridae')
        
    def test_fuzzy_rename_detection(self):
        """Test fuzzy matching for renamed species."""
        comparator = VersionComparator(None)
        
        # Test similar names
        removed = {'SARS-CoV', 'Bacteriophage T4'}
        added = {'SARS-CoV-2', 'Tequatrovirus T4'}
        
        v1_data = {
            'SARS-CoV': {'genus': 'Betacoronavirus'},
            'Bacteriophage T4': {'genus': 'Tequatrovirus'}
        }
        v2_data = {
            'SARS-CoV-2': {'genus': 'Betacoronavirus'},
            'Tequatrovirus T4': {'genus': 'Tequatrovirus'}
        }
        
        changes = {'renamed': []}
        comparator._detect_renames(removed, added, v1_data, v2_data, changes)
        
        # Should detect both renames
        self.assertEqual(len(changes['renamed']), 2)
        
        # Check rename mappings
        rename_map = {r['from']: r['to'] for r in changes['renamed']}
        self.assertEqual(rename_map['SARS-CoV'], 'SARS-CoV-2')
        self.assertEqual(rename_map['Bacteriophage T4'], 'Tequatrovirus T4')


class TestChangeClassification(unittest.TestCase):
    """Test classification of change types."""
    
    def test_restructure_vs_reclassification(self):
        """Test distinguishing restructures from reclassifications."""
        comparator = VersionComparator(None)
        
        # Caudovirales case - order split, not removed
        changes = {
            'removed': [],
            'added': ['Crassvirales', 'Kirjokansivirales', 'Methanobavirales'],
            'reclassified': [
                {
                    'species': 'Phage Lambda',
                    'changes': {
                        'order': {'from': 'Caudovirales', 'to': 'Crassvirales'},
                        'family': {'from': 'Siphoviridae', 'to': 'Drexlerviridae'}
                    }
                }
            ] * 100  # Many reclassifications
        }
        
        analysis = comparator._classify_changes(changes)
        self.assertIn('restructures', analysis)
        self.assertIn('Caudovirales', analysis['restructures'])


if __name__ == '__main__':
    unittest.main()