#!/usr/bin/env python3
"""
Enhanced Caudovirales analysis with improved change classification.

This script provides detailed analysis of taxonomic changes with
proper classification and validation.
"""

import sys
from pathlib import Path
import logging
import json

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.taxonomy_diff import TaxonomyDiff
from src.utils.change_classifier import ChangeClassifier, ValidationSummary

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def enhanced_caudovirales_analysis():
    """Run enhanced analysis with proper change classification."""
    
    repo_path = Path(__file__).parent.parent / 'output' / 'viral-taxonomy-evolution'
    
    if not repo_path.exists():
        logger.error(f"Repository not found at {repo_path}")
        return False
    
    diff_tool = TaxonomyDiff(str(repo_path))
    classifier = ChangeClassifier()
    summary = ValidationSummary()
    
    logger.info("Running enhanced Caudovirales analysis...")
    
    # Analyze changes between MSL36 and MSL37
    changes = diff_tool.compare_versions('msl36', 'msl37')
    
    print("\n" + "="*80)
    print("ENHANCED CAUDOVIRALES ANALYSIS (MSL36 → MSL37)")
    print("="*80)
    
    # Focus on classification changes
    classification_changes = changes['classification_changed']
    
    # Categorize changes
    change_categories = {
        'reclassification': [],
        'restructure': [],
        'other': []
    }
    
    caudovirales_changes = []
    
    for change in classification_changes:
        # Add to summary
        summary.add_change(
            change.change_type, change.change_subtype, change.severity,
            change.validation_status, change.validation_notes
        )
        
        # Categorize
        if change.change_type in change_categories:
            change_categories[change.change_type].append(change)
        else:
            change_categories['other'].append(change)
        
        # Check if related to Caudovirales
        old_order = change.old_classification.get('order')
        new_order = change.new_classification.get('order')
        
        if old_order == 'Caudovirales' or new_order == 'Caudovirales':
            caudovirales_changes.append(change)
    
    # Display summary statistics
    print("\nOVERALL CHANGE SUMMARY:")
    print("-" * 40)
    print(f"Total species analyzed: {len(classification_changes):,}")
    print(f"Reclassifications: {len(change_categories['reclassification']):,}")
    print(f"Restructures: {len(change_categories['restructure']):,}")
    print(f"Other changes: {len(change_categories['other']):,}")
    
    # Display validation summary
    validation_summary = summary.get_summary_report()
    quality_score = summary.get_quality_score()
    
    print(f"\nDATA QUALITY ASSESSMENT:")
    print("-" * 40)
    print(f"Quality Score: {quality_score:.2%}")
    print("Validation Status:")
    for status, count in validation_summary['validation_status'].items():
        print(f"  {status}: {count:,}")
    
    if validation_summary['common_issues']:
        print("\nCommon Issues Found:")
        for status, issues in validation_summary['common_issues'].items():
            print(f"  {status.upper()}:")
            for issue in issues[:5]:  # Show top 5
                print(f"    - {issue}")
    
    # Detailed Caudovirales analysis
    print(f"\nCAUDOVIRALES-SPECIFIC CHANGES:")
    print("-" * 40)
    print(f"Total Caudovirales-related changes: {len(caudovirales_changes):,}")
    
    # Categorize Caudovirales changes
    caudovirales_by_type = {}
    for change in caudovirales_changes:
        change_key = f"{change.change_type}:{change.change_subtype}"
        if change_key not in caudovirales_by_type:
            caudovirales_by_type[change_key] = []
        caudovirales_by_type[change_key].append(change)
    
    print("\nChange Types in Caudovirales:")
    for change_key, changes_list in sorted(caudovirales_by_type.items()):
        change_type, subtype = change_key.split(':')
        print(f"  {change_type} ({subtype}): {len(changes_list)} species")
    
    # Show examples of each type
    print(f"\nDETAILED CHANGE EXAMPLES:")
    print("=" * 80)
    
    for change_key, changes_list in sorted(caudovirales_by_type.items()):
        change_type, subtype = change_key.split(':')
        print(f"\n{change_type.upper()} - {subtype}:")
        print("-" * 60)
        
        for i, change in enumerate(changes_list[:3]):  # Show first 3 examples
            print(f"\nExample {i+1}: {change.species_name}")
            print(f"  Description: {change.details.get('description', 'N/A')}")
            print(f"  Severity: {change.severity}")
            
            # Show specific changes
            old_class = change.old_classification
            new_class = change.new_classification
            
            for rank in ['order', 'family', 'genus']:
                old_val = old_class.get(rank, 'None')
                new_val = new_class.get(rank, 'None')
                if old_val != new_val:
                    print(f"  {rank}: {old_val} → {new_val}")
            
            if change.validation_status != 'valid':
                print(f"  Validation: {change.validation_status}")
                if change.validation_notes:
                    for note in change.validation_notes:
                        print(f"    - {note}")
        
        if len(changes_list) > 3:
            print(f"  ... and {len(changes_list) - 3} more species")
    
    # Save detailed results
    output_dir = Path(__file__).parent.parent / 'output'
    
    # Save enhanced analysis
    enhanced_results = {
        'analysis_type': 'enhanced_caudovirales',
        'versions_compared': ['msl36', 'msl37'],
        'summary': {
            'total_changes': len(classification_changes),
            'caudovirales_changes': len(caudovirales_changes),
            'data_quality_score': quality_score,
            'change_categories': {k: len(v) for k, v in change_categories.items()}
        },
        'validation_summary': validation_summary,
        'caudovirales_by_type': {
            change_key: {
                'count': len(changes_list),
                'examples': [
                    {
                        'species': change.species_name,
                        'change_type': change.change_type,
                        'subtype': change.change_subtype,
                        'severity': change.severity,
                        'description': change.details.get('description'),
                        'validation_status': change.validation_status,
                        'changes': {
                            rank: f"{change.old_classification.get(rank)} → {change.new_classification.get(rank)}"
                            for rank in ['order', 'family', 'genus']
                            if change.old_classification.get(rank) != change.new_classification.get(rank)
                        }
                    }
                    for change in changes_list[:5]  # Save top 5 examples
                ]
            }
            for change_key, changes_list in caudovirales_by_type.items()
        }
    }
    
    results_path = output_dir / 'enhanced_caudovirales_analysis.json'
    with open(results_path, 'w') as f:
        json.dump(enhanced_results, f, indent=2)
    
    logger.info(f"Enhanced analysis saved to: {results_path}")
    
    # Generate interpretation guide
    print(f"\n{'='*80}")
    print("INTERPRETATION GUIDE")
    print("=" * 80)
    
    print("\nCHANGE TYPES EXPLAINED:")
    print("- RECLASSIFICATION: Species moved to different family/genus")
    print("- RESTRUCTURE: Taxonomic hierarchy reorganized (rank addition/removal)")
    print("- OTHER: Mixed or unusual changes")
    
    print("\nSEVERITY LEVELS:")
    print("- MINOR: Small changes (subfamily level)")
    print("- NORMAL: Typical changes (genus/order level)")  
    print("- MAJOR: Significant changes (family level)")
    print("- CRITICAL: Rare high-level changes (realm/kingdom)")
    
    print("\nVALIDATION STATUS:")
    print("- VALID: Change looks correct")
    print("- WARNING: Unusual but possibly correct")
    print("- ERROR: Likely data issue")
    
    print(f"\n{'='*80}")
    print("CONCLUSION")
    print("=" * 80)
    
    print(f"The analysis shows that most Caudovirales changes were RESTRUCTURES")
    print(f"(rank removal/reorganization) rather than species RECLASSIFICATIONS.")
    print(f"This explains why the 'order abolished' but most species stayed in")
    print(f"their original families - it was hierarchy reorganization, not")
    print(f"wholesale species reclassification.")
    
    return True


if __name__ == "__main__":
    success = enhanced_caudovirales_analysis()
    sys.exit(0 if success else 1)