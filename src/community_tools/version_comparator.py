"""
Version comparison tool for analyzing differences between taxonomy versions.
"""

import pandas as pd
from pathlib import Path
import yaml
import json
from typing import Dict, List, Tuple, Set
from dataclasses import dataclass
import difflib
from datetime import datetime

@dataclass
class TaxonomicChange:
    """Represents a change between taxonomy versions."""
    species: str
    change_type: str  # added, removed, reclassified, renamed
    old_classification: Dict = None
    new_classification: Dict = None
    details: str = ""
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'species': self.species,
            'change_type': self.change_type,
            'old_classification': self.old_classification,
            'new_classification': self.new_classification,
            'details': self.details
        }


class VersionComparator:
    """Compare taxonomy between different MSL versions."""
    
    def __init__(self, git_repo_path: str):
        self.repo_path = Path(git_repo_path)
        self.versions_data = {}
        self._load_versions()
    
    def _load_versions(self):
        """Load all available versions."""
        output_dir = self.repo_path / 'output'
        for version_dir in sorted(output_dir.glob('MSL*')):
            if version_dir.is_dir():
                version = version_dir.name
                self.versions_data[version] = self._load_version_species(version_dir)
    
    def _load_version_species(self, version_dir: Path) -> Dict[str, Dict]:
        """Load all species from a version."""
        species_dict = {}
        
        for yaml_file in version_dir.rglob('*.yaml'):
            try:
                with open(yaml_file, 'r') as f:
                    species = yaml.safe_load(f)
                    if species and 'scientific_name' in species:
                        species_dict[species['scientific_name']] = species
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")
        
        return species_dict
    
    def compare_versions(self, version1: str, version2: str) -> Dict[str, List[TaxonomicChange]]:
        """Compare two taxonomy versions comprehensively."""
        if version1 not in self.versions_data or version2 not in self.versions_data:
            raise ValueError(f"Version not found. Available: {list(self.versions_data.keys())}")
        
        v1_species = self.versions_data[version1]
        v2_species = self.versions_data[version2]
        
        changes = {
            'added': [],
            'removed': [],
            'reclassified': [],
            'renamed': [],
            'unchanged': []
        }
        
        # Find added and removed species
        v1_names = set(v1_species.keys())
        v2_names = set(v2_species.keys())
        
        added = v2_names - v1_names
        removed = v1_names - v2_names
        common = v1_names & v2_names
        
        # Process added species
        for name in added:
            changes['added'].append(TaxonomicChange(
                species=name,
                change_type='added',
                new_classification=v2_species[name].get('classification', {}),
                details=f"New species in {version2}"
            ))
        
        # Process removed species
        for name in removed:
            changes['removed'].append(TaxonomicChange(
                species=name,
                change_type='removed',
                old_classification=v1_species[name].get('classification', {}),
                details=f"Removed in {version2}"
            ))
        
        # Check for reclassifications in common species
        for name in common:
            old_class = v1_species[name].get('classification', {})
            new_class = v2_species[name].get('classification', {})
            
            if self._classification_changed(old_class, new_class):
                change_details = self._describe_classification_change(old_class, new_class)
                changes['reclassified'].append(TaxonomicChange(
                    species=name,
                    change_type='reclassified',
                    old_classification=old_class,
                    new_classification=new_class,
                    details=change_details
                ))
            else:
                changes['unchanged'].append(TaxonomicChange(
                    species=name,
                    change_type='unchanged',
                    old_classification=old_class,
                    new_classification=new_class
                ))
        
        # Detect potential renames using similarity matching
        self._detect_renames(removed, added, v1_species, v2_species, changes)
        
        return changes
    
    def _classification_changed(self, old_class: Dict, new_class: Dict) -> bool:
        """Check if classification has changed."""
        ranks = ['realm', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus']
        
        for rank in ranks:
            if old_class.get(rank) != new_class.get(rank):
                return True
        return False
    
    def _describe_classification_change(self, old_class: Dict, new_class: Dict) -> str:
        """Describe what changed in the classification."""
        changes = []
        ranks = ['realm', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus']
        
        for rank in ranks:
            old_val = old_class.get(rank, 'None')
            new_val = new_class.get(rank, 'None')
            if old_val != new_val:
                changes.append(f"{rank}: {old_val} → {new_val}")
        
        return "; ".join(changes)
    
    def _detect_renames(self, removed: Set[str], added: Set[str], 
                       v1_species: Dict, v2_species: Dict, 
                       changes: Dict[str, List]):
        """Detect potential species renames using fuzzy matching."""
        # Use string similarity to find potential renames
        for old_name in removed:
            best_match = None
            best_ratio = 0
            
            for new_name in added:
                # Compare names
                ratio = difflib.SequenceMatcher(None, old_name, new_name).ratio()
                
                # Also compare classifications
                old_class = v1_species[old_name].get('classification', {})
                new_class = v2_species[new_name].get('classification', {})
                
                # Boost ratio if genus/family match
                if old_class.get('genus') == new_class.get('genus'):
                    ratio += 0.3
                if old_class.get('family') == new_class.get('family'):
                    ratio += 0.2
                
                if ratio > best_ratio and ratio > 0.7:  # Threshold for rename
                    best_ratio = ratio
                    best_match = new_name
            
            if best_match:
                # Move from added/removed to renamed
                changes['renamed'].append(TaxonomicChange(
                    species=f"{old_name} → {best_match}",
                    change_type='renamed',
                    old_classification=v1_species[old_name].get('classification', {}),
                    new_classification=v2_species[best_match].get('classification', {}),
                    details=f"Likely renamed (similarity: {best_ratio:.2f})"
                ))
                
                # Remove from added/removed lists
                changes['added'] = [c for c in changes['added'] if c.species != best_match]
                changes['removed'] = [c for c in changes['removed'] if c.species != old_name]
    
    def generate_comparison_report(self, version1: str, version2: str, 
                                 output_path: str = None) -> Dict:
        """Generate comprehensive comparison report."""
        changes = self.compare_versions(version1, version2)
        
        # Calculate statistics
        stats = {
            'version1': version1,
            'version2': version2,
            'total_species_v1': len(self.versions_data[version1]),
            'total_species_v2': len(self.versions_data[version2]),
            'species_added': len(changes['added']),
            'species_removed': len(changes['removed']),
            'species_reclassified': len(changes['reclassified']),
            'species_renamed': len(changes['renamed']),
            'species_unchanged': len(changes['unchanged'])
        }
        
        # Analyze reclassification patterns
        reclassification_patterns = self._analyze_reclassification_patterns(
            changes['reclassified']
        )
        
        # Create report
        report = {
            'metadata': {
                'generated': datetime.now().isoformat(),
                'version1': version1,
                'version2': version2
            },
            'statistics': stats,
            'reclassification_patterns': reclassification_patterns,
            'changes': {
                key: [change.to_dict() for change in change_list]
                for key, change_list in changes.items()
            }
        }
        
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            # Also create human-readable summary
            summary_path = output_file.with_suffix('.md')
            self._write_markdown_summary(report, summary_path)
        
        return report
    
    def _analyze_reclassification_patterns(self, 
                                          reclassifications: List[TaxonomicChange]) -> Dict:
        """Analyze patterns in reclassifications."""
        patterns = {
            'rank_changes': {},
            'family_movements': {},
            'major_reorganizations': []
        }
        
        ranks = ['realm', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus']
        
        for change in reclassifications:
            old_class = change.old_classification or {}
            new_class = change.new_classification or {}
            
            # Track which ranks changed
            for rank in ranks:
                if old_class.get(rank) != new_class.get(rank):
                    key = f"{rank}_changed"
                    patterns['rank_changes'][key] = patterns['rank_changes'].get(key, 0) + 1
            
            # Track family movements
            old_family = old_class.get('family', 'Unknown')
            new_family = new_class.get('family', 'Unknown')
            
            if old_family != new_family:
                movement = f"{old_family} → {new_family}"
                patterns['family_movements'][movement] = \
                    patterns['family_movements'].get(movement, 0) + 1
        
        # Identify major reorganizations (families with many species moved)
        for movement, count in patterns['family_movements'].items():
            if count >= 10:  # Threshold for major reorganization
                patterns['major_reorganizations'].append({
                    'movement': movement,
                    'species_count': count
                })
        
        return patterns
    
    def _write_markdown_summary(self, report: Dict, output_path: Path):
        """Write human-readable markdown summary."""
        stats = report['statistics']
        patterns = report['reclassification_patterns']
        
        md_content = f"""# Taxonomy Version Comparison Report

## Versions Compared
- **Version 1**: {report['metadata']['version1']}
- **Version 2**: {report['metadata']['version2']}
- **Generated**: {report['metadata']['generated']}

## Summary Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Species (v1) | {stats['total_species_v1']:,} | - |
| Total Species (v2) | {stats['total_species_v2']:,} | - |
| Species Added | {stats['species_added']:,} | {stats['species_added']/stats['total_species_v2']*100:.1f}% |
| Species Removed | {stats['species_removed']:,} | {stats['species_removed']/stats['total_species_v1']*100:.1f}% |
| Species Reclassified | {stats['species_reclassified']:,} | {stats['species_reclassified']/stats['total_species_v1']*100:.1f}% |
| Species Renamed | {stats['species_renamed']:,} | - |
| Species Unchanged | {stats['species_unchanged']:,} | {stats['species_unchanged']/stats['total_species_v1']*100:.1f}% |

## Reclassification Analysis

### Changed Ranks
"""
        
        for rank_change, count in sorted(patterns['rank_changes'].items()):
            rank = rank_change.replace('_changed', '')
            md_content += f"- **{rank.title()}**: {count} species\n"
        
        if patterns['major_reorganizations']:
            md_content += "\n### Major Family Reorganizations\n"
            for reorg in sorted(patterns['major_reorganizations'], 
                              key=lambda x: x['species_count'], reverse=True):
                md_content += f"- {reorg['movement']}: {reorg['species_count']} species\n"
        
        # Add sample changes
        md_content += "\n## Sample Changes\n\n"
        
        if report['changes']['added']:
            md_content += "### Newly Added Species (first 10)\n"
            for change in report['changes']['added'][:10]:
                family = change['new_classification'].get('family', 'Unknown')
                md_content += f"- {change['species']} (Family: {family})\n"
        
        if report['changes']['reclassified']:
            md_content += "\n### Sample Reclassifications (first 10)\n"
            for change in report['changes']['reclassified'][:10]:
                md_content += f"- **{change['species']}**: {change['details']}\n"
        
        with open(output_path, 'w') as f:
            f.write(md_content)
    
    def compare_all_adjacent_versions(self, output_dir: str = None):
        """Compare all adjacent versions and generate reports."""
        versions = sorted(self.versions_data.keys())
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        comparison_summary = []
        
        for i in range(len(versions) - 1):
            v1 = versions[i]
            v2 = versions[i + 1]
            
            print(f"Comparing {v1} → {v2}...")
            
            if output_dir:
                report_path = output_path / f"comparison_{v1}_to_{v2}.json"
            else:
                report_path = None
            
            report = self.generate_comparison_report(v1, v2, report_path)
            
            comparison_summary.append({
                'transition': f"{v1} → {v2}",
                'species_change': report['statistics']['total_species_v2'] - 
                                report['statistics']['total_species_v1'],
                'added': report['statistics']['species_added'],
                'removed': report['statistics']['species_removed'],
                'reclassified': report['statistics']['species_reclassified']
            })
        
        # Write summary
        if output_dir:
            summary_df = pd.DataFrame(comparison_summary)
            summary_df.to_csv(output_path / "version_comparison_summary.csv", index=False)
            
            # Create visualization
            self._create_comparison_visualization(summary_df, output_path)
        
        return comparison_summary
    
    def _create_comparison_visualization(self, summary_df: pd.DataFrame, output_path: Path):
        """Create visualization of version comparisons."""
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Species change over transitions
        axes[0, 0].bar(summary_df['transition'], summary_df['species_change'])
        axes[0, 0].set_title('Net Species Change by Version Transition')
        axes[0, 0].set_xlabel('Version Transition')
        axes[0, 0].set_ylabel('Species Change')
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Added vs Removed
        x = range(len(summary_df))
        width = 0.35
        axes[0, 1].bar([i - width/2 for i in x], summary_df['added'], 
                      width, label='Added', color='green', alpha=0.7)
        axes[0, 1].bar([i + width/2 for i in x], summary_df['removed'], 
                      width, label='Removed', color='red', alpha=0.7)
        axes[0, 1].set_title('Species Added vs Removed')
        axes[0, 1].set_xlabel('Version Transition')
        axes[0, 1].set_ylabel('Number of Species')
        axes[0, 1].set_xticks(x)
        axes[0, 1].set_xticklabels(summary_df['transition'], rotation=45)
        axes[0, 1].legend()
        
        # Reclassification rate
        axes[1, 0].plot(summary_df['transition'], summary_df['reclassified'], 
                       marker='o', linewidth=2, markersize=8)
        axes[1, 0].set_title('Species Reclassified per Version')
        axes[1, 0].set_xlabel('Version Transition')
        axes[1, 0].set_ylabel('Number Reclassified')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3)
        
        # Summary statistics
        axes[1, 1].axis('off')
        summary_text = f"""Version Comparison Summary
        
Total Transitions: {len(summary_df)}
Total Species Added: {summary_df['added'].sum():,}
Total Species Removed: {summary_df['removed'].sum():,}
Total Reclassifications: {summary_df['reclassified'].sum():,}

Largest Single Addition: {summary_df['added'].max():,}
Largest Single Removal: {summary_df['removed'].max():,}
Most Reclassifications: {summary_df['reclassified'].max():,}
"""
        axes[1, 1].text(0.1, 0.5, summary_text, fontsize=12, 
                       verticalalignment='center', fontfamily='monospace')
        
        plt.tight_layout()
        plt.savefig(output_path / "version_comparison_summary.png", dpi=300, bbox_inches='tight')
        plt.close()


def main():
    """Run version comparison analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare ICTV taxonomy versions")
    parser.add_argument("git_repo", help="Path to git taxonomy repository")
    parser.add_argument("--version1", help="First version to compare")
    parser.add_argument("--version2", help="Second version to compare")
    parser.add_argument("--all", action="store_true", 
                       help="Compare all adjacent versions")
    parser.add_argument("--output", help="Output directory for reports")
    
    args = parser.parse_args()
    
    comparator = VersionComparator(args.git_repo)
    
    if args.all:
        print("Comparing all adjacent versions...")
        comparator.compare_all_adjacent_versions(args.output)
    elif args.version1 and args.version2:
        print(f"Comparing {args.version1} to {args.version2}...")
        report = comparator.generate_comparison_report(
            args.version1, args.version2, 
            args.output if args.output else None
        )
        print(f"Comparison complete. Added: {report['statistics']['species_added']}, "
              f"Removed: {report['statistics']['species_removed']}, "
              f"Reclassified: {report['statistics']['species_reclassified']}")
    else:
        print("Please specify either --all or both --version1 and --version2")


if __name__ == "__main__":
    main()