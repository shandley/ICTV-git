#!/usr/bin/env python3
"""
Demo script for Natural Language Query interface

This script demonstrates the NLQ capabilities with sample queries.
Run this to test the system before launching the full chat interface.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from advanced_features.nlq_interface import NaturalLanguageQuery

def main():
    """Demo the Natural Language Query interface"""
    
    print("🦠 ICTV-git Natural Language Query Demo")
    print("=" * 50)
    
    # Check if git repository exists
    repo_path = "output/git_taxonomy"
    if not os.path.exists(repo_path):
        print(f"❌ Git taxonomy repository not found at {repo_path}")
        print("Please run the MSL conversion scripts first:")
        print("  python scripts/convert_msl_to_git.py data/MSL38.xlsx")
        return
    
    print(f"✅ Found git repository at {repo_path}")
    
    # Initialize NLQ interface
    print("\n🔧 Initializing Natural Language Query interface...")
    nlq = NaturalLanguageQuery(repo_path, use_openai=False)
    print("✅ NLQ interface ready!")
    
    # Demo queries
    demo_queries = [
        "What happened to bacteriophage T4?",
        "Show me unstable virus families",
        "Which viruses infect plants?",
        "List coronaviruses discovered after 2020",
        "Find viruses similar to SARS-CoV-2",
        "What families are most stable?",
        "Track Tobacco mosaic virus through history"
    ]
    
    print(f"\n🎯 Running {len(demo_queries)} demo queries...")
    print("-" * 50)
    
    for i, query in enumerate(demo_queries, 1):
        print(f"\n[Query {i}/{len(demo_queries)}]")
        print(f"❓ {query}")
        print("🤖 Response:")
        
        try:
            response = nlq.query(query)
            print(response)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 30)
    
    print("\n🎉 Demo complete!")
    print("\nTo launch the interactive chat interface, run:")
    print("  streamlit run scripts/run_nlq_chat.py")

if __name__ == "__main__":
    main()