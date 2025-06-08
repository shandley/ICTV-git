"""
Tests for git converters
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from converters.git_converter import GitConverter


class TestGitConverter(unittest.TestCase):
    """Test git conversion functionality."""
    
    def setUp(self):
        """Create test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_data = {
            'species': [
                {
                    'scientific_name': 'Tobacco mosaic virus',
                    'classification': {
                        'genus': 'Tobamovirus',
                        'family': 'Virgaviridae',
                        'order': 'Martellivirales',
                        'class': 'Alsuviricetes',
                        'phylum': 'Kitrinoviricota',
                        'kingdom': 'Orthornavirae',
                        'realm': 'Riboviria'
                    },
                    'genome': {
                        'type': 'ssRNA(+)',
                        'size': '6395 bp'
                    }
                }
            ]
        }
        
    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    def test_converter_initialization(self):
        """Test converter can be initialized."""
        converter = GitConverter(self.test_dir)
        self.assertIsNotNone(converter)
        self.assertEqual(converter.output_dir, Path(self.test_dir))
        
    def test_create_directory_structure(self):
        """Test directory structure creation."""
        converter = GitConverter(self.test_dir)
        converter.create_directory_structure()
        
        # Check main directories exist
        expected_dirs = ['realms', 'evidence', '.git']
        for dir_name in expected_dirs:
            dir_path = Path(self.test_dir) / dir_name
            self.assertTrue(dir_path.exists())
            
    def test_save_species(self):
        """Test saving species to git structure."""
        converter = GitConverter(self.test_dir)
        converter.create_directory_structure()
        
        # Save test species
        species = self.test_data['species'][0]
        file_path = converter.save_species_to_yaml(species, 'TEST')
        
        # Check file was created
        self.assertTrue(file_path.exists())
        
        # Check path structure
        path_parts = file_path.parts
        self.assertIn('realms', path_parts)
        self.assertIn('riboviria', path_parts)
        self.assertIn('tobacco_mosaic_virus.yaml', str(file_path))
        
    def test_commit_creation(self):
        """Test git commit creation."""
        converter = GitConverter(self.test_dir)
        converter.create_directory_structure()
        
        # Save species and commit
        species = self.test_data['species'][0]
        converter.save_species_to_yaml(species, 'TEST')
        
        # Create commit
        commit_hash = converter.create_version_commit('TEST', added=1, removed=0, changed=0)
        self.assertIsNotNone(commit_hash)
        
        # Check commit exists
        repo = converter.repo
        commit = repo.head.commit
        self.assertIn('TEST', commit.message)


class TestYAMLGeneration(unittest.TestCase):
    """Test YAML file generation."""
    
    def test_species_yaml_format(self):
        """Test generated YAML has correct format."""
        converter = GitConverter(tempfile.mkdtemp())
        
        species_data = {
            'scientific_name': 'Test virus',
            'classification': {'genus': 'Testvirus'},
            'genome': {'type': 'dsDNA'}
        }
        
        yaml_content = converter._generate_species_yaml(species_data)
        
        # Check key fields present
        self.assertIn('scientific_name:', yaml_content)
        self.assertIn('classification:', yaml_content)
        self.assertIn('genome:', yaml_content)
        
        # Check indentation
        lines = yaml_content.split('\n')
        for line in lines:
            if line.strip() and not line.startswith('#'):
                # Check no tabs used
                self.assertNotIn('\t', line)


if __name__ == '__main__':
    unittest.main()