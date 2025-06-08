#!/usr/bin/env python3
"""
Getting Started with ICTV-git

This example demonstrates basic usage of the ICTV-git system for:
1. Loading taxonomy data
2. Searching for species
3. Tracking classification changes
4. Generating citations
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.parsers.msl_parser import MSLParser
from src.community_tools.citation_generator import CitationGenerator
from src.community_tools.version_comparator import VersionComparator


def example_1_parse_msl():
    """Example 1: Parse an MSL file and explore the data."""
    print("=" * 60)
    print("Example 1: Parsing MSL Files")
    print("=" * 60)
    
    # Path to MSL file
    msl_file = Path(__file__).parent.parent / "data" / "MSL38.xlsx"
    
    if not msl_file.exists():
        print(f"MSL file not found at {msl_file}")
        print("Please run: python scripts/download_msl.py")
        return
    
    # Parse the file
    parser = MSLParser(str(msl_file))
    species_list = parser.parse()
    
    print(f"\nParsed {len(species_list)} species from MSL38")
    
    # Show first 5 species
    print("\nFirst 5 species:")
    for i, species in enumerate(species_list[:5]):
        print(f"{i+1}. {species.scientific_name}")
        print(f"   Family: {species.family}, Genus: {species.genus}")
        print(f"   Genome: {species.genome_composition}")
    
    # Search for coronavirus
    print("\n\nSearching for 'coronavirus'...")
    coronaviruses = [s for s in species_list 
                     if 'coronavirus' in s.scientific_name.lower()]
    print(f"Found {len(coronaviruses)} coronavirus species")
    
    for virus in coronaviruses[:3]:
        print(f"- {virus.scientific_name}")


def example_2_compare_versions():
    """Example 2: Compare two taxonomy versions."""
    print("\n" + "=" * 60)
    print("Example 2: Comparing Taxonomy Versions")
    print("=" * 60)
    
    git_repo = Path(__file__).parent.parent / "output" / "git_taxonomy"
    
    if not git_repo.exists():
        print(f"Git taxonomy not found at {git_repo}")
        print("Please run: python scripts/convert_full_history.py")
        return
    
    # Initialize comparator
    comparator = VersionComparator(str(git_repo))
    
    # Compare MSL37 to MSL38
    print("\nComparing MSL37 to MSL38...")
    changes = comparator.compare_versions("MSL37", "MSL38")
    
    print(f"\nSummary of changes:")
    print(f"- Species added: {len(changes['added'])}")
    print(f"- Species removed: {len(changes['removed'])}")
    print(f"- Species reclassified: {len(changes['reclassified'])}")
    print(f"- Species renamed: {len(changes['renamed'])}")
    
    # Show some examples
    if changes['added']:
        print(f"\nExample newly added species:")
        for change in changes['added'][:3]:
            print(f"- {change.species}")
    
    if changes['reclassified']:
        print(f"\nExample reclassified species:")
        for change in changes['reclassified'][:3]:
            print(f"- {change.species}")
            print(f"  {change.details}")


def example_3_generate_citations():
    """Example 3: Generate citations for species."""
    print("\n" + "=" * 60)
    print("Example 3: Generating Citations")
    print("=" * 60)
    
    git_repo = Path(__file__).parent.parent / "output" / "git_taxonomy"
    
    if not git_repo.exists():
        print(f"Git taxonomy not found at {git_repo}")
        return
    
    # Initialize citation generator
    generator = CitationGenerator(str(git_repo))
    
    # Generate citation for SARS-CoV-2
    species = "Severe acute respiratory syndrome-related coronavirus"
    version = "MSL38"
    
    print(f"\nGenerating citations for: {species}")
    print(f"Version: {version}\n")
    
    # Standard citation
    print("Standard format:")
    print(generator.cite_species(species, version, format="standard"))
    
    # BibTeX citation
    print("\n\nBibTeX format:")
    print(generator.cite_species(species, version, format="bibtex"))
    
    # Git citation (with commit info)
    print("\n\nGit format (for reproducibility):")
    print(generator.cite_species(species, version, format="git"))


def example_4_practical_workflow():
    """Example 4: A practical research workflow."""
    print("\n" + "=" * 60)
    print("Example 4: Practical Research Workflow")
    print("=" * 60)
    
    print("\nScenario: You have a dataset from 2018 (MSL34) that needs updating to 2023 (MSL38)")
    
    # Your old data
    old_classifications = [
        ("Escherichia phage T4", "Myoviridae"),
        ("Tobacco mosaic virus", "Virgaviridae"),
        ("Human immunodeficiency virus 1", "Retroviridae")
    ]
    
    print("\nYour 2018 dataset:")
    for virus, family in old_classifications:
        print(f"- {virus}: Family {family}")
    
    # Check current classifications
    git_repo = Path(__file__).parent.parent / "output" / "git_taxonomy"
    if git_repo.exists():
        comparator = VersionComparator(str(git_repo))
        
        print("\n\nChecking current (MSL38) classifications:")
        # In a real implementation, you would look up each species
        # This is a simplified example
        print("- Escherichia phage T4: Family changed (see migration tools)")
        print("- Tobacco mosaic virus: Family unchanged")
        print("- Human immunodeficiency virus 1: Family unchanged")
        
        print("\n\nTo update your dataset:")
        print("1. Use migration tools to map old families to new")
        print("2. Validate species names haven't changed")
        print("3. Generate citation for the specific versions used")


def main():
    """Run all examples."""
    print("ICTV-git: Getting Started Examples")
    print("==================================\n")
    
    # Run examples
    example_1_parse_msl()
    example_2_compare_versions()
    example_3_generate_citations()
    example_4_practical_workflow()
    
    print("\n\nNext steps:")
    print("- Try the interactive browser: streamlit run scripts/run_taxonomy_browser.py")
    print("- Explore the API: python scripts/run_taxonomy_api.py")
    print("- Read the documentation: docs/")


if __name__ == "__main__":
    main()