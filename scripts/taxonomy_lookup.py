#!/usr/bin/env python3
"""
Interactive taxonomy lookup and migration tool.

This script provides an easy way to look up taxonomic changes
for specific viruses across MSL versions.
"""

import sys
from pathlib import Path
import logging
from typing import Dict, List, Optional

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.migration_mapper import MigrationMapper
from src.utils.taxonomy_diff import TaxonomyDiff

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaxonomyLookup:
    """Interactive taxonomy lookup tool."""
    
    def __init__(self, repo_path: str):
        """Initialize lookup tool."""
        self.repo_path = Path(repo_path)
        self.mapper = MigrationMapper(str(repo_path))
        self.diff_tool = TaxonomyDiff(str(repo_path))
        
        # Get available versions
        self.versions = self._get_available_versions()
    
    def _get_available_versions(self) -> List[str]:
        """Get list of available MSL versions."""
        try:
            repo = self.diff_tool.repo
            tags = [tag.name for tag in repo.tags]
            # Sort MSL versions numerically
            msl_tags = [t for t in tags if t.startswith('msl')]
            msl_tags.sort(key=lambda x: int(x[3:]) if x[3:].isdigit() else 0)
            return msl_tags
        except Exception as e:
            logger.error(f"Error getting versions: {e}")
            return []
    
    def lookup_species(self, species_name: str, version: Optional[str] = None) -> Dict:
        """Look up a species in a specific version or all versions."""
        results = {}
        
        if version:
            # Look up in specific version
            species_data = self.diff_tool.get_species_at_version(version)
            if species_name in species_data:
                results[version] = species_data[species_name]
        else:
            # Look up in all versions
            for v in self.versions:
                try:
                    species_data = self.diff_tool.get_species_at_version(v)
                    if species_name in species_data:
                        results[v] = species_data[species_name]
                except Exception as e:
                    logger.error(f"Error checking version {v}: {e}")
        
        return results
    
    def track_species_history(self, species_name: str) -> List[Dict]:
        """Track the complete history of a species across versions."""
        history = []
        
        for i, version in enumerate(self.versions):
            try:
                species_data = self.diff_tool.get_species_at_version(version)
                
                if species_name in species_data:
                    entry = {
                        'version': version,
                        'exists': True,
                        'classification': species_data[species_name]['classification']
                    }
                    
                    # Check for changes from previous version
                    if i > 0 and history and history[-1]['exists']:
                        prev_class = history[-1]['classification']
                        curr_class = entry['classification']
                        
                        changes = []
                        for rank in ['realm', 'kingdom', 'phylum', 'class', 
                                   'order', 'family', 'genus']:
                            if prev_class.get(rank) != curr_class.get(rank):
                                changes.append(f"{rank}: {prev_class.get(rank)} → {curr_class.get(rank)}")
                        
                        if changes:
                            entry['changes'] = changes
                    
                    history.append(entry)
                else:
                    # Species doesn't exist in this version
                    if history and history[-1]['exists']:
                        # Species was removed
                        history.append({
                            'version': version,
                            'exists': False,
                            'note': 'Species removed or renamed'
                        })
                
            except Exception as e:
                logger.error(f"Error processing version {version}: {e}")
        
        return history
    
    def search_species(self, pattern: str, version: str) -> List[str]:
        """Search for species names matching a pattern."""
        matching = []
        
        try:
            species_data = self.diff_tool.get_species_at_version(version)
            pattern_lower = pattern.lower()
            
            for species_name in species_data.keys():
                if pattern_lower in species_name.lower():
                    matching.append(species_name)
            
            matching.sort()
        except Exception as e:
            logger.error(f"Error searching in version {version}: {e}")
        
        return matching


def interactive_mode():
    """Run interactive taxonomy lookup."""
    repo_path = Path(__file__).parent.parent / 'output' / 'viral-taxonomy-evolution'
    
    if not repo_path.exists():
        logger.error(f"Repository not found at {repo_path}")
        logger.info("Please run: python scripts/convert_msl.py --evolution")
        return
    
    lookup = TaxonomyLookup(str(repo_path))
    
    print("\n" + "="*60)
    print("ICTV TAXONOMY LOOKUP TOOL")
    print("="*60)
    print(f"Available versions: {', '.join(lookup.versions)}")
    print("\nCommands:")
    print("  lookup <species>          - Look up species in all versions")
    print("  lookup <species> <version> - Look up species in specific version")
    print("  history <species>         - Show complete history")
    print("  search <pattern> <version> - Search for species")
    print("  help                      - Show this help")
    print("  quit                      - Exit")
    print("")
    
    while True:
        try:
            command = input("\n> ").strip()
            
            if not command:
                continue
            
            parts = command.split()
            cmd = parts[0].lower()
            
            if cmd == 'quit' or cmd == 'exit':
                break
            
            elif cmd == 'help':
                print("\nCommands:")
                print("  lookup <species>          - Look up species in all versions")
                print("  lookup <species> <version> - Look up species in specific version")
                print("  history <species>         - Show complete history")
                print("  search <pattern> <version> - Search for species")
                print("  quit                      - Exit")
            
            elif cmd == 'lookup' and len(parts) >= 2:
                species = ' '.join(parts[1:-1] if len(parts) > 2 and parts[-1].startswith('msl') else parts[1:])
                version = parts[-1] if len(parts) > 2 and parts[-1].startswith('msl') else None
                
                print(f"\nLooking up: {species}")
                if version:
                    print(f"Version: {version}")
                
                results = lookup.lookup_species(species, version)
                
                if results:
                    for v, data in sorted(results.items()):
                        print(f"\n{v}:")
                        classification = data['classification']
                        for rank in ['realm', 'kingdom', 'phylum', 'class', 
                                   'order', 'family', 'genus']:
                            if rank in classification:
                                print(f"  {rank}: {classification[rank]}")
                else:
                    print("Species not found")
            
            elif cmd == 'history' and len(parts) >= 2:
                species = ' '.join(parts[1:])
                print(f"\nHistory for: {species}")
                
                history = lookup.track_species_history(species)
                
                if history:
                    for entry in history:
                        if entry['exists']:
                            print(f"\n{entry['version']}:")
                            if 'changes' in entry:
                                print("  Changes from previous version:")
                                for change in entry['changes']:
                                    print(f"    - {change}")
                            else:
                                print("  No changes from previous version")
                        else:
                            print(f"\n{entry['version']}: {entry['note']}")
                else:
                    print("No history found")
            
            elif cmd == 'search' and len(parts) >= 3:
                pattern = parts[1]
                version = parts[2]
                
                print(f"\nSearching for '{pattern}' in {version}")
                
                matches = lookup.search_species(pattern, version)
                
                if matches:
                    print(f"Found {len(matches)} matches:")
                    for species in matches[:20]:  # Show first 20
                        print(f"  - {species}")
                    if len(matches) > 20:
                        print(f"  ... and {len(matches) - 20} more")
                else:
                    print("No matches found")
            
            else:
                print("Invalid command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n")
            break
        except Exception as e:
            print(f"Error: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Look up viral taxonomy across MSL versions'
    )
    parser.add_argument('--interactive', '-i', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('--species', type=str,
                       help='Species name to look up')
    parser.add_argument('--version', type=str,
                       help='MSL version (e.g., msl36)')
    parser.add_argument('--history', action='store_true',
                       help='Show complete history for species')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.species:
        repo_path = Path(__file__).parent.parent / 'output' / 'viral-taxonomy-evolution'
        if not repo_path.exists():
            logger.error(f"Repository not found at {repo_path}")
            sys.exit(1)
        
        lookup = TaxonomyLookup(str(repo_path))
        
        if args.history:
            history = lookup.track_species_history(args.species)
            for entry in history:
                if entry['exists']:
                    print(f"\n{entry['version']}:")
                    classification = entry['classification']
                    print(f"  Family: {classification.get('family', 'N/A')}")
                    print(f"  Genus: {classification.get('genus', 'N/A')}")
                    if 'changes' in entry:
                        print("  Changes:", '; '.join(entry['changes']))
        else:
            results = lookup.lookup_species(args.species, args.version)
            for v, data in sorted(results.items()):
                print(f"\n{v}:")
                classification = data['classification']
                for rank in ['family', 'genus', 'order']:
                    if rank in classification:
                        print(f"  {rank}: {classification[rank]}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()