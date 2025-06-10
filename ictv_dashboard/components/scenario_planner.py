"""
Scenario Planning Component

Multi-scenario comparison and impact analysis for family interventions.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta

class ScenarioPlanner:
    """Plan and compare multiple intervention scenarios."""
    
    def __init__(self, family_data: Dict[str, Any]):
        """Initialize with current family data."""
        self.family_data = family_data
        self.current_size = family_data.get('current_size', 1)
        self.growth_rate = family_data.get('growth_rate', 0.0)
        self.host_breadth = family_data.get('host_breadth', 1)
        
    def project_no_action(self, years: int = 5) -> Dict[str, Any]:
        """Project outcomes with no intervention."""
        
        projections = []
        for year in range(years + 1):
            size = self.current_size * (1 + self.growth_rate) ** year
            
            # Risk increases with size
            risk_score = min(10, size / 50)
            
            projections.append({
                'year': year,
                'size': int(size),
                'risk_score': risk_score,
                'status': self._get_status(risk_score)
            })
        
        return {
            'scenario': 'No Action',
            'projections': projections,
            'final_size': int(projections[-1]['size']),
            'final_risk': projections[-1]['risk_score'],
            'resources_required': 0,
            'implementation_time': 0,
            'probability_of_crisis': self._calculate_crisis_probability(projections)
        }
    
    def project_gradual_split(self, num_families: int = 3, 
                            implementation_months: int = 12,
                            years: int = 5) -> Dict[str, Any]:
        """Project outcomes with gradual family split."""
        
        projections = []
        split_complete_year = implementation_months / 12.0
        
        for year in range(years + 1):
            if year < split_complete_year:
                # During implementation
                progress = year / split_complete_year
                effective_families = 1 + (num_families - 1) * progress
                size_per_family = self.current_size / effective_families
                
                # Reduced growth during transition
                growth_factor = (1 + self.growth_rate * 0.5) ** year
            else:
                # After split completion
                size_per_family = self.current_size / num_families
                years_post_split = year - split_complete_year
                
                # Growth resumes but at lower rate
                growth_factor = (1 + self.growth_rate * 0.7) ** years_post_split
            
            projected_size = size_per_family * growth_factor
            
            # Risk decreases with smaller families
            risk_score = min(10, projected_size / 50)
            
            projections.append({
                'year': year,
                'size': int(projected_size),
                'risk_score': risk_score,
                'status': self._get_status(risk_score),
                'num_families': num_families if year >= split_complete_year else 1
            })
        
        # Calculate resources
        resources = self._calculate_resources(num_families, 'gradual')
        
        return {
            'scenario': 'Gradual Split',
            'projections': projections,
            'final_size': int(projections[-1]['size']),
            'final_risk': projections[-1]['risk_score'],
            'num_families': num_families,
            'resources_required': resources,
            'implementation_time': implementation_months,
            'probability_of_crisis': self._calculate_crisis_probability(projections)
        }
    
    def project_immediate_split(self, num_families: int = 5,
                              implementation_months: int = 3,
                              years: int = 5) -> Dict[str, Any]:
        """Project outcomes with immediate family split."""
        
        projections = []
        split_complete_year = implementation_months / 12.0
        
        for year in range(years + 1):
            if year < split_complete_year:
                # Rapid implementation
                size_per_family = self.current_size
                growth_factor = 1  # No growth during rapid transition
            else:
                # After split
                size_per_family = self.current_size / num_families
                years_post_split = year - split_complete_year
                
                # Lower initial growth post-split
                growth_factor = (1 + self.growth_rate * 0.5) ** years_post_split
            
            projected_size = size_per_family * growth_factor
            
            # Risk drops quickly with immediate action
            risk_score = min(10, projected_size / 50)
            
            projections.append({
                'year': year,
                'size': int(projected_size),
                'risk_score': risk_score,
                'status': self._get_status(risk_score),
                'num_families': num_families if year >= split_complete_year else 1
            })
        
        # Calculate resources (higher for immediate action)
        resources = self._calculate_resources(num_families, 'immediate')
        
        return {
            'scenario': 'Immediate Split',
            'projections': projections,
            'final_size': int(projections[-1]['size']),
            'final_risk': projections[-1]['risk_score'],
            'num_families': num_families,
            'resources_required': resources,
            'implementation_time': implementation_months,
            'probability_of_crisis': self._calculate_crisis_probability(projections)
        }
    
    def compare_scenarios(self, scenarios: List[Dict[str, Any]]) -> pd.DataFrame:
        """Create comparison matrix of scenarios."""
        
        comparison_data = []
        
        for scenario in scenarios:
            comparison_data.append({
                'Scenario': scenario['scenario'],
                'Final Size': scenario['final_size'],
                'Final Risk': f"{scenario['final_risk']:.1f}",
                'New Families': scenario.get('num_families', 1) - 1,
                'Committee Hours': scenario['resources_required'],
                'Timeline (months)': scenario['implementation_time'],
                'Crisis Probability': f"{scenario['probability_of_crisis']:.0%}"
            })
        
        return pd.DataFrame(comparison_data)
    
    def recommend_scenario(self, scenarios: List[Dict[str, Any]]) -> Tuple[str, str]:
        """Recommend best scenario based on multiple factors."""
        
        scores = {}
        
        for scenario in scenarios:
            # Score based on multiple criteria
            risk_score = 10 - scenario['final_risk']  # Lower risk is better
            resource_score = 10 - (scenario['resources_required'] / 10)  # Fewer resources better
            crisis_score = 10 * (1 - scenario['probability_of_crisis'])  # Lower probability better
            
            # Weighted total
            total_score = (
                risk_score * 0.5 +      # Risk reduction most important
                crisis_score * 0.3 +    # Crisis prevention important
                resource_score * 0.2    # Resource efficiency
            )
            
            scores[scenario['scenario']] = total_score
        
        # Find best scenario
        best_scenario = max(scores, key=scores.get)
        
        # Generate rationale
        if best_scenario == 'No Action':
            rationale = "Family appears stable with manageable growth rate"
        elif best_scenario == 'Gradual Split':
            rationale = "Balanced approach providing risk reduction with manageable resource requirements"
        else:
            rationale = "Immediate action needed to prevent crisis situation"
        
        return best_scenario, rationale
    
    def _get_status(self, risk_score: float) -> str:
        """Get status based on risk score."""
        if risk_score < 3:
            return "Stable"
        elif risk_score < 5:
            return "Monitor"
        elif risk_score < 7:
            return "Concern"
        else:
            return "Crisis"
    
    def _calculate_resources(self, num_families: int, split_type: str) -> int:
        """Calculate committee hours required."""
        
        base_hours = {
            'gradual': 10,
            'immediate': 15
        }
        
        # More families = more work
        family_multiplier = num_families * 1.5
        
        # Larger families need more work
        size_multiplier = 1 + (self.current_size / 100)
        
        # Complex families need more work
        complexity_multiplier = 1 + (self.host_breadth / 20)
        
        total_hours = (
            base_hours.get(split_type, 10) * 
            family_multiplier * 
            size_multiplier * 
            complexity_multiplier
        )
        
        return int(total_hours)
    
    def _calculate_crisis_probability(self, projections: List[Dict[str, Any]]) -> float:
        """Calculate probability of reaching crisis level."""
        
        crisis_years = [p for p in projections if p['risk_score'] >= 7]
        
        if not crisis_years:
            return 0.0
        
        # Earlier crisis = higher probability
        first_crisis_year = crisis_years[0]['year']
        probability = 1.0 - (first_crisis_year / len(projections))
        
        return min(1.0, max(0.0, probability))
    
    def generate_implementation_plan(self, scenario: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed implementation steps."""
        
        steps = []
        
        if scenario['scenario'] == 'No Action':
            steps.append({
                'phase': 'Monitoring',
                'duration': 'Ongoing',
                'actions': [
                    'Quarterly size assessment',
                    'Annual phylogenetic review',
                    'Host range monitoring'
                ]
            })
        
        elif scenario['scenario'] == 'Gradual Split':
            steps.extend([
                {
                    'phase': 'Planning (Months 1-3)',
                    'duration': '3 months',
                    'actions': [
                        'Form working group',
                        'Phylogenetic analysis',
                        'Define new family boundaries',
                        'Community consultation'
                    ]
                },
                {
                    'phase': 'Implementation (Months 4-9)',
                    'duration': '6 months',
                    'actions': [
                        'Draft proposal documents',
                        'Species reassignment',
                        'Database updates',
                        'Stakeholder communication'
                    ]
                },
                {
                    'phase': 'Finalization (Months 10-12)',
                    'duration': '3 months',
                    'actions': [
                        'Final committee approval',
                        'Publication preparation',
                        'System updates',
                        'Monitor stability'
                    ]
                }
            ])
        
        elif scenario['scenario'] == 'Immediate Split':
            steps.extend([
                {
                    'phase': 'Emergency Planning (Month 1)',
                    'duration': '1 month',
                    'actions': [
                        'Emergency committee meeting',
                        'Rapid phylogenetic assessment',
                        'Preliminary family boundaries',
                        'Resource allocation'
                    ]
                },
                {
                    'phase': 'Rapid Implementation (Month 2)',
                    'duration': '1 month',
                    'actions': [
                        'Species reassignment',
                        'Critical database updates',
                        'Urgent communications',
                        'Temporary classifications'
                    ]
                },
                {
                    'phase': 'Stabilization (Month 3)',
                    'duration': '1 month',
                    'actions': [
                        'Refinement of boundaries',
                        'Community feedback integration',
                        'Final approvals',
                        'Post-split monitoring'
                    ]
                }
            ])
        
        return steps