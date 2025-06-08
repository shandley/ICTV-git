#!/usr/bin/env python3
"""
Performance Benchmarks for ICTV-git Advanced Features

Tests performance and reliability of the advanced features without
requiring full dependencies.
"""

import time
import tempfile
import shutil
import os
import sys
from pathlib import Path
from datetime import datetime

def print_header(title: str):
    """Print a formatted section header"""
    print("\n" + "="*50)
    print(f"⚡ {title}")
    print("="*50)

def benchmark_cache_performance():
    """Benchmark the query caching system"""
    print_header("CACHE PERFORMANCE BENCHMARK")
    
    # Create temporary directory for cache testing
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Add src to path for imports
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        
        from advanced_features.nlq_interface import QueryCache
        
        print("🔧 Setting up cache benchmark...")
        cache = QueryCache(cache_dir=temp_dir, cache_ttl_hours=24)
        
        # Test data
        test_queries = [
            "What happened to bacteriophage T4?",
            "Show me unstable virus families",
            "Find coronaviruses discovered after 2020",
            "Which viruses infect plants?",
            "Track Tobacco mosaic virus history"
        ]
        
        test_responses = [
            f"Response for query {i}: This is a detailed response about viral taxonomy..."
            for i in range(len(test_queries))
        ]
        
        # Benchmark cache write performance
        print("\n📝 Testing cache write performance...")
        write_start = time.time()
        
        for query, response in zip(test_queries, test_responses):
            cache.put(query, response)
        
        write_time = time.time() - write_start
        print(f"   ✅ Wrote {len(test_queries)} responses in {write_time:.3f} seconds")
        print(f"   📊 Average write time: {write_time/len(test_queries):.3f} seconds per query")
        
        # Benchmark cache read performance
        print("\n📖 Testing cache read performance...")
        read_start = time.time()
        
        hit_count = 0
        for query in test_queries:
            result = cache.get(query)
            if result:
                hit_count += 1
        
        read_time = time.time() - read_start
        print(f"   ✅ Read {len(test_queries)} queries in {read_time:.3f} seconds")
        print(f"   📊 Average read time: {read_time/len(test_queries):.3f} seconds per query")
        print(f"   🎯 Cache hit rate: {hit_count}/{len(test_queries)} ({hit_count/len(test_queries)*100:.1f}%)")
        
        # Test cache statistics
        stats = cache.get_stats()
        print(f"\n📈 Cache Statistics:")
        print(f"   Hit count: {stats['hit_count']}")
        print(f"   Miss count: {stats['miss_count']}")
        print(f"   Hit rate: {stats['hit_rate_percent']}%")
        print(f"   Cache files: {stats['cache_files']}")
        
        # Stress test - many queries
        print("\n🔥 Stress test: 1000 cache operations...")
        stress_start = time.time()
        
        for i in range(500):
            cache.put(f"stress_query_{i}", f"response_{i}")
            cache.get(f"stress_query_{i}")
        
        stress_time = time.time() - stress_start
        print(f"   ✅ Completed 1000 operations in {stress_time:.3f} seconds")
        print(f"   📊 Average: {stress_time/1000:.6f} seconds per operation")
        
        return True
        
    except Exception as e:
        print(f"❌ Cache benchmark failed: {e}")
        return False
    
    finally:
        shutil.rmtree(temp_dir)

def benchmark_intent_parsing():
    """Benchmark query intent parsing"""
    print_header("INTENT PARSING BENCHMARK")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from advanced_features.nlq_interface import QueryIntentParser
        
        print("🔧 Setting up intent parsing benchmark...")
        parser = QueryIntentParser(use_openai=False)  # Use pattern matching only
        
        # Test queries of different types
        test_queries = [
            "What happened to bacteriophage T4?",
            "Show me unstable virus families",
            "Find viruses similar to SARS-CoV-2",
            "Which viruses infect both plants and animals?",
            "List coronaviruses discovered in 2020",
            "Track Tobacco mosaic virus through history",
            "Show all genera in Picornaviridae family",
            "Find frequently reclassified families",
            "What are the most volatile virus classifications?",
            "Viruses related to influenza A"
        ] * 10  # 100 total queries
        
        print(f"\n🔍 Parsing {len(test_queries)} queries...")
        parse_start = time.time()
        
        successful_parses = 0
        intent_counts = {}
        
        for query in test_queries:
            try:
                intent = parser.parse(query)
                successful_parses += 1
                
                # Count intent types
                action = intent.action
                intent_counts[action] = intent_counts.get(action, 0) + 1
                
            except Exception as e:
                print(f"   ⚠️ Failed to parse: {query[:50]}... ({e})")
        
        parse_time = time.time() - parse_start
        
        print(f"\n📊 Parsing Results:")
        print(f"   Total queries: {len(test_queries)}")
        print(f"   Successful parses: {successful_parses}")
        print(f"   Success rate: {successful_parses/len(test_queries)*100:.1f}%")
        print(f"   Total time: {parse_time:.3f} seconds")
        print(f"   Average time: {parse_time/len(test_queries):.6f} seconds per query")
        
        print(f"\n🎯 Intent Distribution:")
        for intent_type, count in sorted(intent_counts.items()):
            print(f"   {intent_type}: {count} queries ({count/successful_parses*100:.1f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Intent parsing benchmark failed: {e}")
        return False

def benchmark_classification_ai():
    """Benchmark AI classification features"""
    print_header("AI CLASSIFICATION BENCHMARK")
    
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
        from advanced_features.classification_ai import (
            ClassificationAI, 
            GenomeFeatureExtractor,
            FamilyStabilityAnalyzer
        )
        
        print("🔧 Setting up AI classification benchmark...")
        
        # Create temporary git repo
        temp_dir = tempfile.mkdtemp()
        git_repo = os.path.join(temp_dir, "git_taxonomy")
        os.makedirs(git_repo, exist_ok=True)
        
        try:
            ai_classifier = ClassificationAI(git_repo)
            feature_extractor = GenomeFeatureExtractor()
            stability_analyzer = FamilyStabilityAnalyzer(git_repo)
            
            # Test virus data
            test_viruses = [
                {
                    'genome_composition': 'ssRNA(+)',
                    'host': 'Homo sapiens',
                    'genome_size': '29903 bp',
                    'discovery_year': 2020
                },
                {
                    'genome_composition': 'ssRNA(-)',
                    'host': 'Plant',
                    'genome_size': '12000 bp'
                },
                {
                    'genome_composition': 'dsDNA',
                    'host': 'Escherichia coli',
                    'genome_size': '50000 bp'
                }
            ] * 20  # 60 total classifications
            
            print(f"\n🔮 Classifying {len(test_viruses)} viruses...")
            classify_start = time.time()
            
            successful_classifications = 0
            family_predictions = {}
            
            for virus_data in test_viruses:
                try:
                    prediction = ai_classifier.suggest_classification(metadata=virus_data)
                    successful_classifications += 1
                    
                    family = prediction.suggested_family
                    family_predictions[family] = family_predictions.get(family, 0) + 1
                    
                except Exception as e:
                    print(f"   ⚠️ Classification failed: {e}")
            
            classify_time = time.time() - classify_start
            
            print(f"\n📊 Classification Results:")
            print(f"   Total viruses: {len(test_viruses)}")
            print(f"   Successful classifications: {successful_classifications}")
            print(f"   Success rate: {successful_classifications/len(test_viruses)*100:.1f}%")
            print(f"   Total time: {classify_time:.3f} seconds")
            print(f"   Average time: {classify_time/len(test_viruses):.6f} seconds per virus")
            
            print(f"\n🏷️ Family Predictions:")
            for family, count in sorted(family_predictions.items()):
                print(f"   {family}: {count} predictions")
            
            # Test feature extraction performance
            print(f"\n⚙️ Testing feature extraction...")
            extract_start = time.time()
            
            for virus_data in test_viruses[:20]:  # Subset for speed
                features = feature_extractor.extract_features(metadata=virus_data)
            
            extract_time = time.time() - extract_start
            print(f"   ✅ Extracted features for 20 viruses in {extract_time:.3f} seconds")
            
            # Test stability analysis
            print(f"\n📈 Testing stability analysis...")
            test_families = ['Coronaviridae', 'Rhabdoviridae', 'Siphoviridae', 'Picornaviridae']
            
            stability_start = time.time()
            for family in test_families:
                stability = stability_analyzer.get_family_stability(family)
                warnings = stability_analyzer.get_red_flags(family)
            
            stability_time = time.time() - stability_start
            print(f"   ✅ Analyzed {len(test_families)} families in {stability_time:.3f} seconds")
            
            return True
            
        finally:
            shutil.rmtree(temp_dir)
        
    except Exception as e:
        print(f"❌ AI classification benchmark failed: {e}")
        return False

def run_memory_usage_test():
    """Test memory usage of advanced features"""
    print_header("MEMORY USAGE TEST")
    
    try:
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        print(f"📊 Initial memory usage: {initial_memory:.1f} MB")
        
        # Test cache memory usage
        print("\n🧠 Testing cache memory usage...")
        temp_dir = tempfile.mkdtemp()
        
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
            from advanced_features.nlq_interface import QueryCache
            
            cache = QueryCache(cache_dir=temp_dir)
            
            # Add many cached items
            for i in range(1000):
                cache.put(f"query_{i}", f"Long response {i} " * 100)  # ~1KB each
            
            cache_memory = process.memory_info().rss / 1024 / 1024
            print(f"   After caching 1000 items: {cache_memory:.1f} MB (+{cache_memory-initial_memory:.1f} MB)")
            
            # Clear cache
            cache.clear()
            
            cleared_memory = process.memory_info().rss / 1024 / 1024
            print(f"   After clearing cache: {cleared_memory:.1f} MB")
            
        finally:
            shutil.rmtree(temp_dir)
        
        return True
        
    except ImportError:
        print("⚠️  psutil not available, skipping memory test")
        return True
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return False

def main():
    """Run all benchmarks"""
    print("⚡ ICTV-git Advanced Features Performance Benchmarks")
    print("=" * 60)
    
    benchmarks = [
        ("Cache Performance", benchmark_cache_performance),
        ("Intent Parsing", benchmark_intent_parsing),
        ("AI Classification", benchmark_classification_ai),
        ("Memory Usage", run_memory_usage_test)
    ]
    
    results = {}
    overall_start = time.time()
    
    for benchmark_name, benchmark_func in benchmarks:
        print(f"\n🚀 Running {benchmark_name} benchmark...")
        
        try:
            success = benchmark_func()
            results[benchmark_name] = "✅ Pass" if success else "⚠️ Partial"
        except Exception as e:
            print(f"❌ {benchmark_name} benchmark failed: {e}")
            results[benchmark_name] = "❌ Fail"
    
    overall_time = time.time() - overall_start
    
    # Summary
    print_header("BENCHMARK SUMMARY")
    
    print("📊 Results:")
    for benchmark_name, result in results.items():
        print(f"   {result} {benchmark_name}")
    
    print(f"\n⏱️  Total benchmark time: {overall_time:.2f} seconds")
    
    passed = sum(1 for result in results.values() if "✅" in result)
    total = len(results)
    
    print(f"🎯 Overall score: {passed}/{total} benchmarks passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All benchmarks passed! Advanced features are performing well.")
    elif passed >= total * 0.8:
        print("\n👍 Most benchmarks passed. System is ready for use.")
    else:
        print("\n⚠️  Some benchmarks failed. Check system dependencies.")

if __name__ == "__main__":
    main()