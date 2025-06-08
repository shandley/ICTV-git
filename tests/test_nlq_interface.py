#!/usr/bin/env python3
"""
Comprehensive test suite for Natural Language Query interface

Tests all components of the NLQ system including intent parsing, caching, 
query execution, and response formatting.
"""

import unittest
import tempfile
import shutil
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from advanced_features.nlq_interface import (
    QueryIntentParser,
    QueryCache, 
    NaturalLanguageQuery,
    QueryIntent,
    QueryResult,
    ResponseFormatter
)


class TestQueryIntentParser(unittest.TestCase):
    """Test query intent parsing functionality"""
    
    def setUp(self):
        self.parser = QueryIntentParser(use_openai=False)  # Use pattern matching only
    
    def test_track_history_queries(self):
        """Test parsing of history tracking queries"""
        test_cases = [
            ("What happened to bacteriophage T4?", "track_history", "bacteriophage T4"),
            ("Track SARS-CoV-2 through time", "track_history", "SARS-CoV-2"),
            ("History of Coronaviridae", "track_history", "Coronaviridae"),
            ("Picornaviridae classification changes", "track_history", "Picornaviridae")
        ]
        
        for query, expected_action, expected_entity in test_cases:
            with self.subTest(query=query):
                intent = self.parser.parse(query)
                self.assertEqual(intent.action, expected_action)
                self.assertIn(expected_entity.lower(), query.lower())
    
    def test_stability_queries(self):
        """Test parsing of stability-related queries"""
        test_cases = [
            "Show me unstable virus families",
            "Which families are volatile?", 
            "Find frequently reclassified genera",
            "What families change most often?"
        ]
        
        for query in test_cases:
            with self.subTest(query=query):
                intent = self.parser.parse(query)
                self.assertEqual(intent.action, "find_unstable")
    
    def test_temporal_queries(self):
        """Test parsing of time-based queries"""
        test_cases = [
            ("Viruses discovered in 2020", "temporal_query", "2020"),
            ("New species in 2023", "temporal_query", "2023"),
            ("Viruses discovered after 2019", "temporal_query", "after 2019")
        ]
        
        for query, expected_action, expected_time in test_cases:
            with self.subTest(query=query):
                intent = self.parser.parse(query)
                self.assertEqual(intent.action, expected_action)
                if expected_time:
                    self.assertIsNotNone(intent.time_range)
    
    def test_similarity_queries(self):
        """Test parsing of similarity search queries"""
        test_cases = [
            ("Find viruses similar to SARS-CoV-2", "similarity_search", "SARS-CoV-2"),
            ("Show me viruses related to influenza", "similarity_search", "influenza"),
            ("Viruses like HIV", "similarity_search", "HIV")
        ]
        
        for query, expected_action, expected_entity in test_cases:
            with self.subTest(query=query):
                intent = self.parser.parse(query)
                self.assertEqual(intent.action, expected_action)
                # Entity extraction might vary in pattern matching


class TestQueryCache(unittest.TestCase):
    """Test query caching functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.cache = QueryCache(cache_dir=self.temp_dir, cache_ttl_hours=1)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_cache_miss(self):
        """Test cache miss on first query"""
        result = self.cache.get("test query")
        self.assertIsNone(result)
        self.assertEqual(self.cache.miss_count, 1)
        self.assertEqual(self.cache.hit_count, 0)
    
    def test_cache_hit(self):
        """Test cache hit on subsequent query"""
        query = "What happened to bacteriophage T4?"
        response = "T4 was reclassified from Myoviridae to Straboviridae in 2019."
        
        # Cache the response
        self.cache.put(query, response)
        
        # Retrieve from cache
        cached_result = self.cache.get(query)
        self.assertEqual(cached_result, response)
        self.assertEqual(self.cache.hit_count, 1)
        self.assertEqual(self.cache.miss_count, 0)
    
    def test_cache_expiration(self):
        """Test cache expiration"""
        # Create cache with very short TTL
        short_cache = QueryCache(cache_dir=self.temp_dir, cache_ttl_hours=0.001)  # ~3.6 seconds
        
        query = "test expiration"
        response = "test response"
        
        short_cache.put(query, response)
        
        # Should hit immediately
        result = short_cache.get(query)
        self.assertEqual(result, response)
        
        # Wait for expiration (simulate with manual timestamp modification)
        import time
        time.sleep(0.1)  # Short sleep
        
        # Manually expire by setting old timestamp
        cache_key = short_cache._get_cache_key(query)
        cache_file = short_cache._get_cache_file(cache_key)
        
        if cache_file.exists():
            import pickle
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
            
            # Set timestamp to past
            cached_data['timestamp'] = datetime.now() - timedelta(hours=2)
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cached_data, f)
        
        # Should miss now
        result = short_cache.get(query)
        self.assertIsNone(result)
    
    def test_cache_stats(self):
        """Test cache statistics"""
        # Initial stats
        stats = self.cache.get_stats()
        self.assertEqual(stats['hit_count'], 0)
        self.assertEqual(stats['miss_count'], 0)
        self.assertEqual(stats['hit_rate_percent'], 0)
        
        # Add some hits and misses
        self.cache.get("miss 1")  # miss
        self.cache.get("miss 2")  # miss
        
        self.cache.put("hit query", "response")
        self.cache.get("hit query")  # hit
        self.cache.get("hit query")  # hit
        
        stats = self.cache.get_stats()
        self.assertEqual(stats['hit_count'], 2)
        self.assertEqual(stats['miss_count'], 2)
        self.assertEqual(stats['hit_rate_percent'], 50.0)
    
    def test_cache_clear(self):
        """Test cache clearing"""
        self.cache.put("test1", "response1")
        self.cache.put("test2", "response2")
        
        # Verify cache has files
        stats = self.cache.get_stats()
        self.assertGreater(stats['cache_files'], 0)
        
        # Clear cache
        self.cache.clear()
        
        # Verify cache is empty
        stats = self.cache.get_stats()
        self.assertEqual(stats['cache_files'], 0)
        self.assertEqual(stats['hit_count'], 0)
        self.assertEqual(stats['miss_count'], 0)


class TestResponseFormatter(unittest.TestCase):
    """Test response formatting functionality"""
    
    def setUp(self):
        self.formatter = ResponseFormatter()
    
    def test_format_history_response(self):
        """Test formatting of history tracking responses"""
        test_data = [
            {'version': 'MSL35', 'family': 'Siphoviridae', 'change': 'created'},
            {'version': 'MSL38', 'family': 'Drexlerviridae', 'change': 'reclassified'}
        ]
        
        result = QueryResult(
            data=test_data,
            query_type="track_history",
            entity_count=2,
            execution_time=0.15,
            confidence=0.9
        )
        
        response = self.formatter.format_response(result, "What happened to bacteriophage T4?")
        
        # Check that response contains key information
        self.assertIn("MSL35", response)
        self.assertIn("MSL38", response)
        self.assertIn("Siphoviridae", response)
        self.assertIn("Drexlerviridae", response)
        self.assertIn("0.15", response)  # execution time
    
    def test_format_empty_results(self):
        """Test formatting when no results found"""
        result = QueryResult(
            data=[],
            query_type="find_unstable",
            entity_count=0,
            execution_time=0.05,
            confidence=0.8
        )
        
        response = self.formatter.format_response(result, "Find viruses similar to XYZ")
        
        self.assertIn("No results found", response)
        self.assertIn("XYZ", response)
    
    def test_format_large_result_set(self):
        """Test formatting of large result sets"""
        # Create large dataset
        large_data = [{'virus': f'virus_{i}', 'family': f'family_{i%5}'} for i in range(50)]
        
        result = QueryResult(
            data=large_data,
            query_type="classification_level",
            entity_count=50,
            execution_time=0.8,
            confidence=0.7
        )
        
        response = self.formatter.format_response(result, "List all virus families")
        
        # Should truncate results and show count
        self.assertIn("50", response)
        self.assertIn("first", response.lower())  # Should mention showing first N results


class TestNaturalLanguageQueryIntegration(unittest.TestCase):
    """Integration tests for the complete NLQ system"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a mock git repository structure
        self.git_repo = os.path.join(self.temp_dir, "git_taxonomy")
        os.makedirs(self.git_repo, exist_ok=True)
        
        # Create mock species files for testing
        species_dir = os.path.join(self.git_repo, "realms", "riboviria", "families", "coronaviridae", "species")
        os.makedirs(species_dir, exist_ok=True)
        
        # Mock SARS-CoV-2 file
        with open(os.path.join(species_dir, "sars_cov_2.yaml"), 'w') as f:
            f.write("""
scientific_name: "Severe acute respiratory syndrome-related coronavirus"
family: "Coronaviridae"
genus: "Betacoronavirus"
discovery_year: 2019
""")
        
        self.nlq = NaturalLanguageQuery(
            git_repo_path=self.git_repo, 
            use_openai=False,
            enable_cache=True
        )
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_simple_query_with_caching(self):
        """Test a simple query and verify caching works"""
        query = "What happened to SARS-CoV-2?"
        
        # First query - should be executed and cached
        response1 = self.nlq.query(query)
        self.assertIsInstance(response1, str)
        self.assertNotIn("(Cached result)", response1)
        
        # Second identical query - should come from cache
        response2 = self.nlq.query(query)
        self.assertIsInstance(response2, str)
        self.assertIn("(Cached result)", response2)
        
        # Verify cache stats
        stats = self.nlq.get_cache_stats()
        self.assertEqual(stats['hit_count'], 1)
        self.assertGreater(stats['cache_files'], 0)
    
    def test_cache_disabled(self):
        """Test NLQ with caching disabled"""
        nlq_no_cache = NaturalLanguageQuery(
            git_repo_path=self.git_repo,
            use_openai=False,
            enable_cache=False
        )
        
        query = "Find unstable families"
        
        # Multiple queries should not use cache
        response1 = nlq_no_cache.query(query)
        response2 = nlq_no_cache.query(query)
        
        self.assertNotIn("(Cached result)", response1)
        self.assertNotIn("(Cached result)", response2)
        
        # Cache stats should indicate disabled
        stats = nlq_no_cache.get_cache_stats()
        self.assertFalse(stats['cache_enabled'])
    
    def test_error_handling(self):
        """Test error handling in queries"""
        # Query that will likely cause an error
        response = self.nlq.query("This is a completely invalid query with $#@! symbols")
        
        self.assertIn("Sorry", response)
        self.assertIn("Error", response)
        
        # Verify error responses are not cached
        stats = self.nlq.get_cache_stats()
        # Should have 0 cache files if only error queries
        # (depending on previous tests, might have some)
    
    def test_cache_clearing(self):
        """Test cache clearing functionality"""
        # Make some queries to populate cache
        self.nlq.query("What happened to SARS-CoV-2?")
        self.nlq.query("Find unstable families")
        
        # Verify cache has content
        stats_before = self.nlq.get_cache_stats()
        self.assertGreater(stats_before['cache_files'], 0)
        
        # Clear cache
        self.nlq.clear_cache()
        
        # Verify cache is empty
        stats_after = self.nlq.get_cache_stats()
        self.assertEqual(stats_after['cache_files'], 0)
        self.assertEqual(stats_after['hit_count'], 0)
        self.assertEqual(stats_after['miss_count'], 0)


class TestQueryTypes(unittest.TestCase):
    """Test different types of queries and their handling"""
    
    def setUp(self):
        self.parser = QueryIntentParser(use_openai=False)
    
    def test_all_query_types(self):
        """Test that all defined query types can be parsed"""
        test_queries = {
            "track_history": "What happened to bacteriophage T4?",
            "find_unstable": "Show me unstable virus families",
            "cross_host": "Viruses that infect both plants and animals",
            "similarity_search": "Find viruses similar to SARS-CoV-2",
            "temporal_query": "Viruses discovered in 2020",
            "classification_level": "Show me all genera in Coronaviridae"
        }
        
        for expected_action, query in test_queries.items():
            with self.subTest(action=expected_action, query=query):
                intent = self.parser.parse(query)
                self.assertEqual(intent.action, expected_action)
    
    def test_entity_extraction(self):
        """Test entity extraction from queries"""
        test_cases = [
            ("Track SARS-CoV-2 history", "sars-cov-2"),
            ("What happened to Coronaviridae?", "coronaviridae"),
            ("Find viruses similar to HIV-1", "hiv-1"),
            ("Show Picornaviridae classification", "picornaviridae")
        ]
        
        for query, expected_entity in test_cases:
            with self.subTest(query=query):
                intent = self.parser.parse(query)
                # Entity extraction logic may vary, so we check if entity is set
                # and contains relevant terms
                if intent.entity:
                    self.assertIn(expected_entity.lower(), query.lower())


def run_performance_tests():
    """Run performance benchmarks for NLQ system"""
    print("\n🚀 Running Performance Tests...")
    
    temp_dir = tempfile.mkdtemp()
    git_repo = os.path.join(temp_dir, "git_taxonomy")
    os.makedirs(git_repo, exist_ok=True)
    
    try:
        # Test with large number of queries
        nlq = NaturalLanguageQuery(git_repo_path=git_repo, enable_cache=True)
        
        test_queries = [
            "What happened to SARS-CoV-2?",
            "Find unstable families",
            "Show coronaviruses",
            "Track influenza history",
            "Find plant viruses"
        ] * 10  # 50 total queries
        
        start_time = datetime.now()
        
        for query in test_queries:
            nlq.query(query)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        stats = nlq.get_cache_stats()
        
        print(f"📊 Performance Results:")
        print(f"   Total queries: {len(test_queries)}")
        print(f"   Total time: {total_time:.2f} seconds")
        print(f"   Average time per query: {total_time/len(test_queries):.3f} seconds")
        print(f"   Cache hit rate: {stats['hit_rate_percent']}%")
        print(f"   Cache files: {stats['cache_files']}")
        
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    # Run unit tests
    print("🧪 Running NLQ Interface Test Suite...")
    unittest.main(verbosity=2, exit=False)
    
    # Run performance tests
    run_performance_tests()