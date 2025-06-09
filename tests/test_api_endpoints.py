"""
API Endpoints Test Suite

Comprehensive testing of all REST API endpoints for the ICTV-git system.
Tests taxonomy, historical, AI, and search functionality.
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from pathlib import Path
import sys
import os

# Add src to path for imports
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

# Set test repository path
os.environ['ICTV_REPO_PATH'] = str(Path(__file__).parent.parent / "output" / "ictv_complete_20_year_taxonomy")

try:
    from api.rest_server import app
    HAS_API = True
except ImportError:
    HAS_API = False
    app = None


@pytest.fixture
def client():
    """Create test client"""
    if not HAS_API:
        pytest.skip("API dependencies not available")
    return TestClient(app)


@pytest.fixture
def sample_species_name():
    """Sample species name for testing"""
    return "Tobacco Mosaic Virus"


class TestBasicEndpoints:
    """Test basic API functionality"""
    
    def test_root_endpoint(self, client):
        """Test API root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "ICTV-Git API"
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "api_components" in data


class TestTaxonomyEndpoints:
    """Test taxonomy-related endpoints"""
    
    def test_get_hierarchy(self, client):
        """Test taxonomy hierarchy endpoint"""
        response = client.get("/taxonomy/hierarchy")
        assert response.status_code == 200
        data = response.json()
        assert "families" in data
        assert "total_families" in data
        assert isinstance(data["total_families"], int)
    
    def test_list_families(self, client):
        """Test families list endpoint"""
        response = client.get("/taxonomy/families")
        assert response.status_code == 200
        data = response.json()
        assert "families" in data
        assert isinstance(data["families"], list)
    
    def test_list_genera(self, client):
        """Test genera list endpoint"""
        response = client.get("/taxonomy/genera")
        assert response.status_code == 200
        data = response.json()
        assert "genera" in data
        assert isinstance(data["genera"], list)
    
    def test_get_species_existing(self, client, sample_species_name):
        """Test getting an existing species"""
        response = client.get(f"/taxonomy/species/{sample_species_name}")
        # Should either find the species or return 404
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "scientific_name" in data
            assert data["scientific_name"] == sample_species_name
    
    def test_get_species_nonexistent(self, client):
        """Test getting a non-existent species"""
        response = client.get("/taxonomy/species/NonexistentVirusSpecies")
        assert response.status_code == 404
    
    def test_get_family_existing(self, client):
        """Test getting an existing family"""
        # First get list of families to test with
        families_response = client.get("/taxonomy/families")
        families = families_response.json()["families"]
        
        if families:
            family_name = families[0]
            response = client.get(f"/taxonomy/family/{family_name}")
            assert response.status_code == 200
            data = response.json()
            assert "name" in data
            assert "genera" in data
    
    def test_validate_classification(self, client):
        """Test classification validation"""
        valid_classification = {
            "scientific_name": "Test Virus",
            "taxonomy": {
                "family": "Virgaviridae",
                "genus": "Tobamovirus"
            }
        }
        
        response = client.post("/taxonomy/validate", json=valid_classification)
        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert isinstance(data["valid"], bool)


class TestHistoricalEndpoints:
    """Test historical data endpoints"""
    
    def test_get_releases(self, client):
        """Test MSL releases endpoint"""
        response = client.get("/historical/releases")
        assert response.status_code == 200
        data = response.json()
        assert "releases" in data
        assert isinstance(data["releases"], list)
    
    def test_get_timeline_summary(self, client):
        """Test timeline summary endpoint"""
        response = client.get("/historical/timeline")
        assert response.status_code == 200
        data = response.json()
        assert "timeline_span" in data
        assert "total_releases" in data
    
    def test_get_release_details(self, client):
        """Test specific release details"""
        # Test with MSL40 (latest)
        response = client.get("/historical/releases/MSL40")
        # Should either find the release or return 404
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "msl_version" in data
            assert data["msl_version"] == "MSL40"
    
    def test_compare_releases(self, client):
        """Test release comparison"""
        # Test comparing MSL35 to MSL40 (major versions)
        response = client.get("/historical/compare/MSL35/MSL40")
        # Should either work or return error
        assert response.status_code in [200, 400]
    
    def test_caudovirales_dissolution(self, client):
        """Test Caudovirales dissolution endpoint"""
        response = client.get("/historical/caudovirales-dissolution")
        assert response.status_code == 200
        data = response.json()
        assert "event_name" in data
        assert "msl_version" in data
    
    def test_species_history(self, client, sample_species_name):
        """Test species history tracking"""
        response = client.get(f"/historical/species/{sample_species_name}/history")
        assert response.status_code == 200
        data = response.json()
        assert "species" in data
        assert "history" in data
        assert isinstance(data["history"], list)


class TestAIEndpoints:
    """Test AI-powered endpoints"""
    
    def test_get_ai_features(self, client):
        """Test AI features listing"""
        response = client.get("/ai/features")
        assert response.status_code == 200
        data = response.json()
        assert "natural_language_query" in data
        assert "classification_ai" in data
        assert "database_sync" in data
    
    def test_ai_health_check(self, client):
        """Test AI health check"""
        response = client.get("/ai/health")
        assert response.status_code == 200
        data = response.json()
        assert "overall_status" in data
        assert "features" in data
    
    def test_natural_language_query(self, client):
        """Test natural language query"""
        query_data = {
            "query": "How many families are there?",
            "use_cache": False
        }
        
        response = client.post("/ai/query", json=query_data)
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "response" in data
    
    def test_ai_classification(self, client):
        """Test AI classification suggestions"""
        classification_data = {
            "organism_name": "Test Virus",
            "metadata": {"genome_type": "RNA", "size": "10kb"}
        }
        
        response = client.post("/ai/classify", json=classification_data)
        assert response.status_code == 200
        data = response.json()
        assert "organism_name" in data
    
    def test_family_stability(self, client):
        """Test family stability scoring"""
        response = client.get("/ai/stability/virgaviridae")
        assert response.status_code == 200
        data = response.json()
        assert "family_name" in data
    
    def test_ai_examples(self, client):
        """Test AI examples endpoint"""
        response = client.get("/ai/examples")
        assert response.status_code == 200
        data = response.json()
        assert "natural_language_query" in data
        assert "classification_suggestions" in data


class TestSearchEndpoints:
    """Test search functionality"""
    
    def test_search_species(self, client):
        """Test species search"""
        search_data = {
            "query": "virus",
            "limit": 10
        }
        
        response = client.post("/search/species", json=search_data)
        assert response.status_code == 200
        data = response.json()
        assert "query" in data
        assert "results" in data
        assert isinstance(data["results"], list)
    
    def test_get_search_facets(self, client):
        """Test search facets"""
        response = client.get("/search/facets")
        assert response.status_code == 200
        data = response.json()
        assert "families" in data
        assert "genera" in data
    
    def test_faceted_search(self, client):
        """Test faceted search"""
        facet_data = {"family": "virgaviridae"}
        
        response = client.post("/search/faceted", json=facet_data)
        assert response.status_code == 200
        data = response.json()
        assert "facet_filters" in data
        assert "results" in data
    
    def test_family_summary(self, client):
        """Test family summary"""
        response = client.get("/search/family/virgaviridae/summary")
        # Should either find family or return 404
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert "family_name" in data
            assert "statistics" in data
    
    def test_advanced_search(self, client):
        """Test advanced search"""
        search_data = {
            "query": "tobacco",
            "filters": {"family": "virgaviridae"},
            "sort_by": "alphabetical",
            "limit": 5
        }
        
        response = client.post("/search/advanced", json=search_data)
        assert response.status_code == 200
        data = response.json()
        assert "search_params" in data
        assert "results" in data
    
    def test_search_statistics(self, client):
        """Test search statistics"""
        response = client.get("/search/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "index_metadata" in data
        assert "coverage" in data


class TestDevelopmentEndpoints:
    """Test development and testing endpoints"""
    
    def test_comprehensive_test(self, client):
        """Test comprehensive functionality test"""
        response = client.get("/dev/test-all")
        assert response.status_code == 200
        data = response.json()
        assert "taxonomy" in data
        assert "historical" in data
        assert "ai" in data
        assert "search" in data
        assert "overall_status" in data


# Performance and integration tests
class TestPerformance:
    """Test API performance characteristics"""
    
    def test_multiple_concurrent_requests(self, client):
        """Test handling multiple concurrent requests"""
        # Simple test with multiple hierarchy requests
        responses = []
        for _ in range(5):
            response = client.get("/taxonomy/hierarchy")
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
    
    def test_large_search_results(self, client):
        """Test handling large search results"""
        search_data = {
            "query": "virus",
            "limit": 1000  # Large limit
        }
        
        response = client.post("/search/species", json=search_data)
        assert response.status_code == 200
        # Should handle large results gracefully


# Error handling tests
class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_msl_version(self, client):
        """Test invalid MSL version handling"""
        response = client.get("/historical/releases/MSL999")
        assert response.status_code == 404
    
    def test_malformed_search_request(self, client):
        """Test malformed search request"""
        # Missing required query field
        response = client.post("/search/species", json={})
        assert response.status_code == 422  # Validation error
    
    def test_invalid_json(self, client):
        """Test invalid JSON handling"""
        response = client.post(
            "/taxonomy/validate",
            data="invalid json",
            headers={"content-type": "application/json"}
        )
        assert response.status_code == 422


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])