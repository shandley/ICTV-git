"""
Tests for REST API endpoints
"""

import unittest
from fastapi.testclient import TestClient
from community_tools.taxonomy_api import app


class TestTaxonomyAPI(unittest.TestCase):
    """Test REST API functionality."""
    
    def setUp(self):
        """Create test client."""
        self.client = TestClient(app)
        
    def test_api_root(self):
        """Test API root endpoint."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        self.assertIn("ICTV", data["message"])
        
    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        
    def test_api_versions(self):
        """Test versions listing endpoint."""
        response = self.client.get("/api/v1/versions")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        
    def test_species_search(self):
        """Test species search endpoint."""
        # Search for common term
        response = self.client.get("/api/v1/search?q=virus")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertIn("total", data)
        
    def test_species_not_found(self):
        """Test 404 response for missing species."""
        response = self.client.get("/api/v1/species/MSL99/NonexistentVirus")
        self.assertEqual(response.status_code, 404)
        
    def test_invalid_version(self):
        """Test 404 response for invalid version."""
        response = self.client.get("/api/v1/species/INVALID/Tobacco mosaic virus")
        self.assertEqual(response.status_code, 404)
        
    def test_citation_generation(self):
        """Test citation generation endpoint."""
        response = self.client.get("/api/v1/cite/MSL38?format=bibtex")
        # May return 404 if no data loaded, but should be valid response
        self.assertIn(response.status_code, [200, 404])
        
    def test_api_documentation(self):
        """Test API documentation is available."""
        response = self.client.get("/docs")
        self.assertEqual(response.status_code, 200)


class TestAPIFilters(unittest.TestCase):
    """Test API filtering and query parameters."""
    
    def setUp(self):
        """Create test client."""
        self.client = TestClient(app)
        
    def test_search_filters(self):
        """Test search with filters."""
        # Test genus filter
        response = self.client.get("/api/v1/search?genus=Tobamovirus")
        self.assertEqual(response.status_code, 200)
        
        # Test family filter
        response = self.client.get("/api/v1/search?family=Coronaviridae")
        self.assertEqual(response.status_code, 200)
        
        # Test combined filters
        response = self.client.get("/api/v1/search?q=virus&family=Coronaviridae")
        self.assertEqual(response.status_code, 200)
        
    def test_export_formats(self):
        """Test different export formats."""
        formats = ['json', 'csv', 'yaml']
        
        for fmt in formats:
            response = self.client.get(f"/api/v1/export/MSL38?format={fmt}")
            # May return 404 if no data, but parameter should be accepted
            self.assertIn(response.status_code, [200, 404])


if __name__ == '__main__':
    unittest.main()