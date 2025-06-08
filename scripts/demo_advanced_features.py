#!/usr/bin/env python3
"""
Comprehensive Demo for ICTV-git Advanced Features

Demonstrates all three advanced features:
1. Natural Language Query Interface
2. AI Classification Suggestions  
3. Database Synchronization

This script provides a guided tour of the capabilities.
"""

import sys
import os
import asyncio
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from advanced_features.nlq_interface import NaturalLanguageQuery
from advanced_features.classification_ai import ClassificationAI
from advanced_features.database_sync import DatabaseSync

def print_header(title: str):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(f"🦠 {title}")
    print("="*60)

def print_subheader(title: str):
    """Print a formatted subsection header"""
    print(f"\n🔬 {title}")
    print("-" * 40)

def demo_natural_language_query():
    """Demonstrate Natural Language Query interface"""
    print_header("NATURAL LANGUAGE QUERY INTERFACE")
    
    # Check if git repository exists
    repo_path = "output/git_taxonomy"
    if not os.path.exists(repo_path):
        print(f"❌ Git taxonomy repository not found at {repo_path}")
        print("Please run the MSL conversion scripts first:")
        print("  python scripts/convert_msl_to_git.py data/MSL38.xlsx")
        return False
    
    print(f"✅ Found git repository at {repo_path}")
    
    # Initialize NLQ interface
    print("\n🔧 Initializing Natural Language Query interface...")
    nlq = NaturalLanguageQuery(repo_path, use_openai=False, enable_cache=True)
    print("✅ NLQ interface ready!")
    
    # Demo queries with explanations
    demo_queries = [
        {
            "query": "What happened to bacteriophage T4?",
            "explanation": "This query tracks the classification history of a specific virus"
        },
        {
            "query": "Show me unstable virus families",
            "explanation": "This finds families with frequent reclassifications"
        },
        {
            "query": "Which viruses infect plants?",
            "explanation": "This searches for viruses by host type"
        },
        {
            "query": "List coronaviruses discovered after 2019",
            "explanation": "This combines family search with temporal filtering"
        },
        {
            "query": "Find viruses similar to SARS-CoV-2",
            "explanation": "This performs similarity-based search"
        }
    ]
    
    for i, demo in enumerate(demo_queries, 1):
        print_subheader(f"Query {i}: {demo['query']}")
        print(f"💡 Purpose: {demo['explanation']}")
        
        try:
            start_time = time.time()
            response = nlq.query(demo['query'])
            execution_time = time.time() - start_time
            
            print(f"🤖 Response:")
            print(response)
            print(f"⏱️  Execution time: {execution_time:.2f} seconds")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
    
    # Show caching performance
    print_subheader("Cache Performance Demo")
    print("Running the first query again to demonstrate caching...")
    
    cached_response = nlq.query(demo_queries[0]['query'])
    print(f"🤖 Cached Response:")
    print(cached_response)
    
    # Display cache statistics
    cache_stats = nlq.get_cache_stats()
    print(f"\n📊 Cache Statistics:")
    print(f"   Hit rate: {cache_stats['hit_rate_percent']}%")
    print(f"   Cache files: {cache_stats['cache_files']}")
    print(f"   Total hits: {cache_stats['hit_count']}")
    
    return True

def demo_ai_classification():
    """Demonstrate AI Classification Suggestions"""
    print_header("AI CLASSIFICATION SUGGESTIONS")
    
    repo_path = "output/git_taxonomy"
    print("🔧 Initializing AI Classification system...")
    
    try:
        ai_classifier = ClassificationAI(repo_path)
        print("✅ AI Classification system ready!")
    except Exception as e:
        print(f"❌ Failed to initialize AI classifier: {e}")
        return False
    
    # Demo virus examples
    test_viruses = [
        {
            "name": "SARS-CoV-2",
            "metadata": {
                'genome_composition': 'ssRNA(+)',
                'host': 'Homo sapiens',
                'genome_size': '29903 bp',
                'discovery_year': 2020
            },
            "explanation": "A well-known coronavirus - should predict Coronaviridae"
        },
        {
            "name": "Tobacco Mosaic Virus",
            "metadata": {
                'genome_composition': 'ssRNA(+)',
                'host': 'Tobacco plant',
                'genome_size': '6395 bp',
                'morphology': 'rod-shaped'
            },
            "explanation": "Classic plant virus - should predict appropriate family"
        },
        {
            "name": "Bacteriophage Lambda",
            "metadata": {
                'genome_composition': 'dsDNA',
                'host': 'Escherichia coli',
                'genome_size': '48502 bp',
                'morphology': 'icosahedral head with tail'
            },
            "explanation": "DNA bacteriophage - tests bacterial virus classification"
        },
        {
            "name": "Unknown RNA Virus",
            "metadata": {
                'genome_composition': 'ssRNA(-)',
                'host': 'Unknown mammal',
                'genome_size': '11000 bp'
            },
            "explanation": "Simulates classification of newly discovered virus"
        }
    ]
    
    for i, virus in enumerate(test_viruses, 1):
        print_subheader(f"Virus {i}: {virus['name']}")
        print(f"💡 Purpose: {virus['explanation']}")
        print(f"📋 Metadata: {virus['metadata']}")
        
        try:
            prediction = ai_classifier.suggest_classification(
                metadata=virus['metadata']
            )
            
            print(f"\n🔮 AI Prediction:")
            print(f"   Suggested family: {prediction.suggested_family}")
            print(f"   Confidence: {prediction.confidence:.2f}")
            print(f"   Stability score: {prediction.stability_score:.2f}")
            print(f"   Reasoning: {prediction.reasoning}")
            
            if prediction.alternative_families:
                print(f"   Alternatives:")
                for alt_family, alt_conf in prediction.alternative_families[:3]:
                    print(f"     - {alt_family}: {alt_conf:.2f}")
            
            if prediction.warnings:
                print(f"   ⚠️  Warnings:")
                for warning in prediction.warnings:
                    print(f"     - {warning}")
            
        except Exception as e:
            print(f"❌ Classification failed: {e}")
        
        print()
    
    # Family stability analysis
    print_subheader("Family Stability Analysis")
    print("Analyzing stability of different virus families...")
    
    test_families = ['Coronaviridae', 'Rhabdoviridae', 'Siphoviridae', 'Picornaviridae']
    
    for family in test_families:
        stability = ai_classifier.stability_analyzer.get_family_stability(family)
        warnings = ai_classifier.stability_analyzer.get_red_flags(family)
        
        print(f"📊 {family}:")
        print(f"   Stability score: {stability:.2f}")
        if warnings:
            for warning in warnings:
                print(f"   {warning}")
        else:
            print(f"   ✅ No stability concerns")
        print()
    
    return True

def demo_database_sync():
    """Demonstrate Database Synchronization"""
    print_header("DATABASE SYNCHRONIZATION")
    
    repo_path = "output/git_taxonomy"
    test_email = "demo@ictv-git.org"
    
    print("🔧 Initializing Database Synchronization system...")
    
    try:
        db_sync = DatabaseSync(repo_path, test_email)
        print("✅ Database sync system ready!")
        print(f"📡 Monitoring databases: {list(db_sync.detector.adapters.keys())}")
    except Exception as e:
        print(f"❌ Failed to initialize database sync: {e}")
        return False
    
    # Demo species for testing
    test_species = [
        "SARS-CoV-2",
        "Tobacco mosaic virus", 
        "Human immunodeficiency virus 1",
        "Influenza A virus"
    ]
    
    print_subheader("Scanning for Taxonomy Mismatches")
    print(f"🔍 Scanning {len(test_species)} test species across all databases...")
    
    async def run_sync_demo():
        try:
            # Scan for mismatches
            mismatches = await db_sync.scan_all_databases(test_species)
            
            print(f"\n📊 Scan Results:")
            print(f"   Species scanned: {len(test_species)}")
            print(f"   Mismatches found: {len(mismatches)}")
            
            if mismatches:
                print(f"\n⚠️  Detected Mismatches:")
                for mismatch in mismatches[:5]:  # Show first 5
                    print(f"   🔴 {mismatch.database}: {mismatch.species_name}")
                    print(f"      Severity: {mismatch.severity}")
                    print(f"      Entries affected: {mismatch.entries_affected}")
                    print(f"      Current: {mismatch.current_classification}")
                    print(f"      Correct: {mismatch.correct_classification}")
                    print()
                
                if len(mismatches) > 5:
                    print(f"   ... and {len(mismatches) - 5} more mismatches")
            else:
                print("   ✅ No mismatches detected (or limited database access)")
            
            # Generate correction suggestions
            if mismatches:
                print_subheader("Generating Correction Suggestions")
                corrections = await db_sync.generate_corrections(mismatches)
                
                print(f"📝 Generated {len(corrections)} correction suggestions:")
                for correction in corrections[:3]:  # Show first 3
                    print(f"   📤 {correction['database']} submission:")
                    print(f"      Species: {correction['species']}")
                    print(f"      Priority: {correction['priority']}")
                    print(f"      Type: {correction['submission_type']}")
                    print()
        
        except Exception as e:
            print(f"❌ Sync demo failed: {e}")
            import traceback
            traceback.print_exc()
    
    # Run async demo
    try:
        asyncio.run(run_sync_demo())
    except Exception as e:
        print(f"❌ Failed to run async demo: {e}")
    
    # Show dashboard data
    print_subheader("Sync Status Dashboard")
    dashboard_data = db_sync.get_sync_dashboard_data()
    
    print(f"📈 System Status:")
    for key, value in dashboard_data.items():
        print(f"   {key}: {value}")
    
    return True

def demo_integration_scenario():
    """Demonstrate integrated use of all three features"""
    print_header("INTEGRATION SCENARIO: NEW VIRUS DISCOVERY")
    
    print("""
🧬 Scenario: A researcher has discovered a new virus and wants to:
1. Use NLQ to research similar known viruses
2. Get AI classification suggestions for the new virus
3. Check for database inconsistencies in related families
""")
    
    # Simulated new virus
    new_virus = {
        "name": "Novel Coronavirus Variant X",
        "genome_sequence": "ATGAAATTGTTAGCAGTCTTC...",  # Truncated
        "metadata": {
            'genome_composition': 'ssRNA(+)',
            'host': 'Rhinolophus bat species',
            'genome_size': '29800 bp',
            'discovery_year': 2024,
            'geographic_origin': 'Southeast Asia'
        }
    }
    
    print_subheader("Step 1: Research Similar Viruses (NLQ)")
    
    repo_path = "output/git_taxonomy"
    if os.path.exists(repo_path):
        nlq = NaturalLanguageQuery(repo_path, enable_cache=True)
        
        research_queries = [
            "Find coronaviruses that infect bats",
            "What is the history of SARS-related coronaviruses?",
            "Show recent coronavirus discoveries"
        ]
        
        for query in research_queries:
            print(f"❓ Query: {query}")
            try:
                response = nlq.query(query)
                print(f"🤖 {response[:200]}...")  # Truncated
            except Exception as e:
                print(f"❌ Error: {e}")
            print()
    
    print_subheader("Step 2: AI Classification (Classification AI)")
    
    try:
        ai_classifier = ClassificationAI(repo_path)
        prediction = ai_classifier.suggest_classification(
            genome_sequence=new_virus["genome_sequence"],
            metadata=new_virus["metadata"]
        )
        
        print(f"🔮 AI Classification for {new_virus['name']}:")
        print(f"   Predicted family: {prediction.suggested_family}")
        print(f"   Confidence: {prediction.confidence:.2f}")
        print(f"   Family stability: {prediction.stability_score:.2f}")
        print(f"   Reasoning: {prediction.reasoning}")
        
        if prediction.warnings:
            print(f"   ⚠️  Warnings:")
            for warning in prediction.warnings:
                print(f"     - {warning}")
    
    except Exception as e:
        print(f"❌ AI classification failed: {e}")
    
    print_subheader("Step 3: Database Consistency Check (Database Sync)")
    
    try:
        db_sync = DatabaseSync(repo_path, "researcher@university.edu")
        
        async def check_consistency():
            # Check related coronavirus entries
            corona_species = ["SARS-CoV-2", "MERS-CoV", "SARS-CoV"]
            mismatches = await db_sync.scan_all_databases(corona_species)
            
            print(f"🔍 Checked {len(corona_species)} related coronaviruses")
            print(f"📊 Found {len(mismatches)} potential mismatches")
            
            if mismatches:
                print(f"⚠️  Recommendation: Review database consistency before submitting new sequence")
            else:
                print(f"✅ Related sequences show consistent classification")
        
        asyncio.run(check_consistency())
    
    except Exception as e:
        print(f"❌ Database sync check failed: {e}")
    
    print_subheader("Integration Summary")
    print("""
✅ Research workflow completed:
   1. NLQ provided context on related viruses
   2. AI suggested most likely classification
   3. Database sync verified consistency
   
🎯 Next steps:
   - Submit genome sequence to GenBank
   - Prepare ICTV classification proposal
   - Monitor for database updates
""")

def main():
    """Main demo function"""
    print_header("ICTV-GIT ADVANCED FEATURES DEMONSTRATION")
    
    print("""
This demonstration showcases three transformative features:

🗣️  Natural Language Query Interface
    - Ask questions in plain English
    - Get intelligent responses about viral taxonomy
    - Cached for performance

🤖 AI Classification Suggestions  
    - Predict virus family from genome/metadata
    - Assess classification stability
    - Warn about problematic families

🔄 Database Synchronization
    - Monitor GenBank, RefSeq, UniProt
    - Detect taxonomy mismatches
    - Generate correction submissions

Let's explore each feature...
""")
    
    # Run individual demos
    demos = [
        ("Natural Language Query", demo_natural_language_query),
        ("AI Classification", demo_ai_classification), 
        ("Database Synchronization", demo_database_sync),
        ("Integration Scenario", demo_integration_scenario)
    ]
    
    results = {}
    
    for demo_name, demo_func in demos:
        print(f"\n⏳ Starting {demo_name} demo...")
        try:
            success = demo_func()
            results[demo_name] = "✅ Success" if success else "⚠️  Partial"
        except Exception as e:
            print(f"❌ {demo_name} demo failed: {e}")
            results[demo_name] = "❌ Failed"
        
        input("\nPress Enter to continue to next demo...")
    
    # Final summary
    print_header("DEMONSTRATION SUMMARY")
    
    print("📊 Demo Results:")
    for demo_name, result in results.items():
        print(f"   {result} {demo_name}")
    
    print(f"""
🎉 Advanced Features Demo Complete!

These features transform ICTV-git into:

1. 🧠 **AI-Powered Platform**: Not just version control but intelligent assistance
2. 👥 **User-Friendly Interface**: Natural language accessible to all researchers  
3. 🌐 **Database Ecosystem**: Keeps entire scientific infrastructure synchronized

To explore further:
- Run individual demo scripts in scripts/ directory
- Launch interactive chat: streamlit run scripts/run_nlq_chat.py
- Read documentation in ADVANCED_FEATURES_IMPLEMENTATION_PLAN.md

Thank you for exploring ICTV-git's advanced capabilities! 🦠
""")

if __name__ == "__main__":
    main()