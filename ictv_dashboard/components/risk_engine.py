"""
Interactive Risk Engine for ICTV Family Assessment

Real-time risk calculation with user-configurable parameters.
Integrates with existing predictive framework.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
from pathlib import Path
import sys

# Dashboard operates independently of predictive framework
# All risk calculations are self-contained

class FamilyRiskCalculator:
    """Interactive risk calculator with real-time parameter adjustment."""
    
    def __init__(self, custom_weights: Dict[str, float] = None, 
                 custom_thresholds: Dict[str, int] = None):
        """Initialize with custom risk weights and thresholds."""
        
        # Default risk weights (can be overridden)
        self.default_weights = {
            'size_factor': 0.30,
            'growth_rate': 0.25,
            'host_breadth': 0.20,
            'genome_complexity': 0.15,
            'phylogenetic_coherence': 0.10
        }
        
        # Default intervention thresholds
        self.default_thresholds = {
            'review': 50,     # species count triggering review
            'concern': 100,   # species count indicating concern
            'crisis': 500     # species count requiring immediate action
        }
        
        self.risk_weights = custom_weights or self.default_weights
        self.thresholds = custom_thresholds or self.default_thresholds
        
        # Normalize weights to sum to 1.0
        weight_sum = sum(self.risk_weights.values())
        if weight_sum > 0:
            self.risk_weights = {k: v/weight_sum for k, v in self.risk_weights.items()}
    
    def calculate_family_risk(self, family_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate risk score for a single family with current parameters."""
        
        # Extract family characteristics
        size = family_data.get('current_size', 1)
        growth_rate = family_data.get('growth_rate', 0.0)
        host_count = family_data.get('host_breadth', 1)
        genome_diversity = family_data.get('genome_complexity', 0.5)
        phylo_coherence = family_data.get('phylogenetic_coherence', 0.8)
        
        # Calculate individual risk factors (0-10 scale)
        size_factor = min(10, size / 50)  # Risk increases with size
        growth_factor = min(10, growth_rate * 20)  # High growth = high risk
        host_factor = min(10, np.log10(max(1, host_count)) * 3)  # More hosts = more complexity
        complexity_factor = genome_diversity * 10  # Higher diversity = higher risk
        coherence_factor = (1 - phylo_coherence) * 10  # Less coherence = higher risk
        
        # Calculate weighted risk score
        risk_score = (
            size_factor * self.risk_weights['size_factor'] +
            growth_factor * self.risk_weights['growth_rate'] +
            host_factor * self.risk_weights['host_breadth'] +
            complexity_factor * self.risk_weights['genome_complexity'] +
            coherence_factor * self.risk_weights['phylogenetic_coherence']
        )
        
        # Determine risk category
        if risk_score >= 7.0:
            risk_category = "Crisis"
            intervention_type = "Emergency"
        elif risk_score >= 5.0:
            risk_category = "High Risk"
            intervention_type = "Split"
        elif risk_score >= 3.0:
            risk_category = "Medium Risk"
            intervention_type = "Review"
        else:
            risk_category = "Low Risk"
            intervention_type = "Monitor"
        
        # Calculate intervention probability (3-year forecast)
        intervention_probability = min(1.0, (risk_score / 10) ** 0.5)
        
        return {
            'family_name': family_data.get('family_name', 'Unknown'),
            'risk_score': risk_score,
            'risk_category': risk_category,
            'intervention_type': intervention_type,
            'intervention_probability': intervention_probability,
            'size_factor': size_factor,
            'growth_factor': growth_factor,
            'host_factor': host_factor,
            'complexity_factor': complexity_factor,
            'coherence_factor': coherence_factor,
            'current_size': size,
            'growth_rate': growth_rate
        }
    
    def assess_all_families(self, families_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Assess risk for all families with current parameters."""
        
        assessments = []
        for family_data in families_data:
            assessment = self.calculate_family_risk(family_data)
            assessments.append(assessment)
        
        return sorted(assessments, key=lambda x: x['risk_score'], reverse=True)
    
    def update_weights(self, new_weights: Dict[str, float]) -> None:
        """Update risk weights and renormalize."""
        self.risk_weights.update(new_weights)
        
        # Renormalize to sum to 1.0
        weight_sum = sum(self.risk_weights.values())
        if weight_sum > 0:
            self.risk_weights = {k: v/weight_sum for k, v in self.risk_weights.items()}
    
    def update_thresholds(self, new_thresholds: Dict[str, int]) -> None:
        """Update intervention thresholds."""
        self.thresholds.update(new_thresholds)
    
    def get_system_health(self, assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall system health metrics."""
        
        if not assessments:
            return {
                'total_families': 0,
                'average_risk': 0.0,
                'system_stability': 10.0,
                'families_by_category': {},
                'intervention_workload': 0
            }
        
        risk_scores = [a['risk_score'] for a in assessments]
        categories = [a['risk_category'] for a in assessments]
        
        # Count families by category
        category_counts = {}
        for category in ['Low Risk', 'Medium Risk', 'High Risk', 'Crisis']:
            category_counts[category] = categories.count(category)
        
        # Calculate system stability (inverse of average risk)
        avg_risk = np.mean(risk_scores)
        system_stability = max(0, 10 - avg_risk)
        
        # Estimate committee workload
        intervention_workload = (
            category_counts.get('Medium Risk', 0) * 1 +
            category_counts.get('High Risk', 0) * 3 +
            category_counts.get('Crisis', 0) * 5
        )
        
        return {
            'total_families': len(assessments),
            'average_risk': avg_risk,
            'system_stability': system_stability,
            'families_by_category': category_counts,
            'intervention_workload': intervention_workload,
            'high_priority_count': category_counts.get('High Risk', 0) + category_counts.get('Crisis', 0)
        }