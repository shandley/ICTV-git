#!/usr/bin/env python3
"""
Run the ICTV Taxonomy API server.

Usage:
    python scripts/run_taxonomy_api.py [git_repo_path] [--host HOST] [--port PORT]
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.community_tools.taxonomy_api import TaxonomyAPI, run_api

def main():
    """Run the API server."""
    parser = argparse.ArgumentParser(description="Run ICTV Taxonomy API server")
    parser.add_argument("git_repo", nargs="?", 
                       default="output/git_taxonomy",
                       help="Path to git taxonomy repository")
    parser.add_argument("--host", default="0.0.0.0", 
                       help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000,
                       help="Port to bind to (default: 8000)")
    
    args = parser.parse_args()
    
    # Convert to absolute path
    repo_path = Path(args.git_repo)
    if not repo_path.is_absolute():
        repo_path = Path(__file__).parent.parent / repo_path
    
    print(f"Starting ICTV Taxonomy API server...")
    print(f"Repository: {repo_path}")
    print(f"API will be available at: http://{args.host}:{args.port}")
    print(f"Documentation at: http://{args.host}:{args.port}/docs")
    print()
    
    run_api(str(repo_path), host=args.host, port=args.port)

if __name__ == "__main__":
    main()