"""
Enhanced classification and validation of taxonomic changes.

This module provides detailed classification of change types and
validation to distinguish between expected patterns and system errors.
"""

from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class ChangeClassifier:
    """Classifies and validates taxonomic changes."""
    
    # Define rank hierarchy (highest to lowest)
    RANK_HIERARCHY = [
        'realm', 'subrealm', 'kingdom', 'subkingdom',
        'phylum', 'subphylum', 'class', 'subclass', 
        'order', 'suborder', 'family', 'subfamily',
        'genus', 'subgenus'
    ]
    
    # Define which ranks typically stay stable vs. change
    STABLE_RANKS = ['realm', 'kingdom', 'phylum']  # Usually don't change
    RESTRUCTURE_RANKS = ['class', 'order', 'suborder']  # Often restructured
    RECLASSIFICATION_RANKS = ['family', 'subfamily', 'genus']  # Frequent changes
    
    def classify_change(self, old_classification: Dict, new_classification: Dict) -> Tuple[str, str, str]:
        """
        Classify a taxonomic change into type, subtype, and severity.
        
        Returns:
            (change_type, change_subtype, severity)
        """
        if not old_classification or not new_classification:
            return 'invalid', 'missing_data', 'error'
        
        # Identify which ranks changed
        changed_ranks = []
        for rank in self.RANK_HIERARCHY:
            old_val = old_classification.get(rank)
            new_val = new_classification.get(rank)
            if old_val != new_val:
                changed_ranks.append(rank)
        
        if not changed_ranks:
            return 'unchanged', 'identical', 'minor'
        
        # Classify based on which ranks changed
        return self._classify_by_rank_pattern(changed_ranks, old_classification, new_classification)
    
    def _classify_by_rank_pattern(self, changed_ranks: List[str], 
                                 old_class: Dict, new_class: Dict) -> Tuple[str, str, str]:
        """Classify change based on which ranks changed."""
        
        # Check for rank removal/addition (None <-> value)
        rank_removals = []
        rank_additions = []
        rank_replacements = []
        
        for rank in changed_ranks:
            old_val = old_class.get(rank)
            new_val = new_class.get(rank)
            
            if old_val and not new_val:
                rank_removals.append(rank)
            elif not old_val and new_val:
                rank_additions.append(rank)
            elif old_val and new_val:
                rank_replacements.append(rank)
        
        # Prioritize by most significant change
        if any(rank in self.STABLE_RANKS for rank in rank_replacements):
            return 'reclassification', 'high_level_change', 'critical'
        
        if rank_removals:
            if any(rank in self.RESTRUCTURE_RANKS for rank in rank_removals):
                return 'restructure', 'rank_removal', 'normal'
            elif any(rank in self.RECLASSIFICATION_RANKS for rank in rank_removals):
                return 'reclassification', 'family_level_removal', 'major'
        
        if rank_additions:
            if any(rank in self.RESTRUCTURE_RANKS for rank in rank_additions):
                return 'restructure', 'rank_addition', 'normal'
            elif any(rank in self.RECLASSIFICATION_RANKS for rank in rank_additions):
                return 'reclassification', 'family_level_addition', 'major'
        
        if rank_replacements:
            if any(rank in self.RECLASSIFICATION_RANKS for rank in rank_replacements):
                if 'family' in rank_replacements:
                    return 'reclassification', 'family_change', 'major'
                elif 'genus' in rank_replacements:
                    return 'reclassification', 'genus_change', 'normal'
                else:
                    return 'reclassification', 'subfamily_change', 'minor'
            elif any(rank in self.RESTRUCTURE_RANKS for rank in rank_replacements):
                return 'restructure', 'order_class_change', 'normal'
        
        # Default fallback
        return 'classification_change', 'mixed_changes', 'normal'
    
    def validate_change(self, old_classification: Dict, new_classification: Dict, 
                       change_type: str, change_subtype: str) -> Tuple[str, List[str]]:
        """
        Validate a taxonomic change for potential errors.
        
        Returns:
            (validation_status, validation_notes)
        """
        notes = []
        status = 'valid'
        
        # Check for missing critical data
        if not old_classification.get('species') or not new_classification.get('species'):
            notes.append("Missing species name")
            status = 'error'
        
        # Check for impossible transitions
        old_realm = old_classification.get('realm')
        new_realm = new_classification.get('realm')
        if old_realm and new_realm and old_realm != new_realm:
            notes.append(f"Realm change is unusual: {old_realm} → {new_realm}")
            status = 'warning'
        
        # Check for orphaned classifications (genus without family, etc.)
        if new_classification.get('genus') and not new_classification.get('family'):
            notes.append("Genus exists without family")
            status = 'warning'
        
        if new_classification.get('subfamily') and not new_classification.get('family'):
            notes.append("Subfamily exists without family")
            status = 'error'
        
        # Check for skip-level changes (family changes but genus stays same)
        if (change_type == 'reclassification' and 
            old_classification.get('family') != new_classification.get('family') and
            old_classification.get('genus') == new_classification.get('genus')):
            notes.append("Family changed but genus unchanged - verify this is correct")
            status = 'warning'
        
        # Check for consistent hierarchy
        hierarchy_issues = self._check_hierarchy_consistency(new_classification)
        if hierarchy_issues:
            notes.extend(hierarchy_issues)
            status = 'warning'
        
        return status, notes
    
    def _check_hierarchy_consistency(self, classification: Dict) -> List[str]:
        """Check for hierarchy consistency issues."""
        issues = []
        
        # Check that higher ranks exist when lower ranks are present
        required_hierarchy = [
            ('subfamily', 'family'),
            ('genus', 'family'),
            ('family', 'order'),
            ('order', 'class'),
            ('class', 'phylum'),
            ('phylum', 'kingdom'),
            ('kingdom', 'realm')
        ]
        
        for lower, higher in required_hierarchy:
            if classification.get(lower) and not classification.get(higher):
                issues.append(f"{lower} present but {higher} missing")
        
        return issues
    
    def get_change_description(self, change_type: str, change_subtype: str, 
                             changed_ranks: List[str]) -> str:
        """Generate human-readable description of change."""
        
        descriptions = {
            ('reclassification', 'family_change'): "Species moved to different family",
            ('reclassification', 'genus_change'): "Species moved to different genus", 
            ('reclassification', 'subfamily_change'): "Species moved to different subfamily",
            ('reclassification', 'high_level_change'): "Major taxonomic reclassification",
            ('restructure', 'rank_removal'): "Taxonomic rank removed from hierarchy",
            ('restructure', 'rank_addition'): "New taxonomic rank added to hierarchy",
            ('restructure', 'order_class_change'): "Order/class restructuring",
            ('unchanged', 'identical'): "No taxonomic changes",
            ('classification_change', 'mixed_changes'): "Multiple taxonomic changes"
        }
        
        key = (change_type, change_subtype)
        if key in descriptions:
            return descriptions[key]
        
        # Fallback description
        if changed_ranks:
            return f"Changes in: {', '.join(changed_ranks)}"
        return "Taxonomic change"


class ValidationSummary:
    """Summarizes validation results across many changes."""
    
    def __init__(self):
        self.change_counts = defaultdict(int)
        self.subtype_counts = defaultdict(int)
        self.severity_counts = defaultdict(int)
        self.validation_counts = defaultdict(int)
        self.validation_issues = defaultdict(list)
    
    def add_change(self, change_type: str, change_subtype: str, severity: str,
                  validation_status: str, validation_notes: List[str]):
        """Add a change to the summary."""
        self.change_counts[change_type] += 1
        self.subtype_counts[change_subtype] += 1
        self.severity_counts[severity] += 1
        self.validation_counts[validation_status] += 1
        
        for note in validation_notes:
            self.validation_issues[validation_status].append(note)
    
    def get_summary_report(self) -> Dict:
        """Generate summary report."""
        return {
            'change_types': dict(self.change_counts),
            'change_subtypes': dict(self.subtype_counts),
            'severity_levels': dict(self.severity_counts),
            'validation_status': dict(self.validation_counts),
            'common_issues': {
                status: list(set(issues))  # Unique issues only
                for status, issues in self.validation_issues.items()
                if issues
            }
        }
    
    def get_quality_score(self) -> float:
        """Calculate data quality score (0-1)."""
        total_changes = sum(self.validation_counts.values())
        if total_changes == 0:
            return 1.0
        
        valid_changes = self.validation_counts.get('valid', 0)
        warning_changes = self.validation_counts.get('warning', 0)
        error_changes = self.validation_counts.get('error', 0)
        
        # Weight: valid=1.0, warning=0.5, error=0.0
        score = (valid_changes + 0.5 * warning_changes) / total_changes
        return score


if __name__ == "__main__":
    # Example usage
    classifier = ChangeClassifier()
    
    # Test classification
    old_class = {'realm': 'Duplodnaviria', 'order': 'Caudovirales', 'family': 'Myoviridae', 'genus': 'Tequatrovirus'}
    new_class = {'realm': 'Duplodnaviria', 'family': 'Straboviridae', 'genus': 'Tequatrovirus'}
    
    change_type, subtype, severity = classifier.classify_change(old_class, new_class)
    status, notes = classifier.validate_change(old_class, new_class, change_type, subtype)
    description = classifier.get_change_description(change_type, subtype, ['order', 'family'])
    
    print(f"Change: {change_type} ({subtype}) - {severity}")
    print(f"Description: {description}")
    print(f"Validation: {status}")
    if notes:
        print(f"Notes: {'; '.join(notes)}")