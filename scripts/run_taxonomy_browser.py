#!/usr/bin/env python3
"""
Run the interactive taxonomy browser web application.

Usage:
    python scripts/run_taxonomy_browser.py [git_repo_path]
    
    Or with streamlit directly:
    streamlit run scripts/run_taxonomy_browser.py -- output/git_taxonomy
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.community_tools.taxonomy_browser import TaxonomyBrowser

def main():
    """Run the taxonomy browser."""
    # Default to the git taxonomy output
    if len(sys.argv) > 1:
        git_repo = sys.argv[1]
    else:
        git_repo = Path(__file__).parent.parent / "output" / "git_taxonomy"
    
    print(f"Starting taxonomy browser with repository: {git_repo}")
    
    # Create and run browser
    browser = TaxonomyBrowser(str(git_repo))
    browser.render_web_interface()

if __name__ == "__main__":
    main()