#!/usr/bin/env python3
"""
ICTV Automated Intervention Recommendation System
================================================

Generates detailed, actionable recommendations for ICTV committee interventions
based on predictive risk assessment. Provides specific guidance on timing,
resource allocation, and implementation strategies for family reorganizations.

Author: ICTV-git Analysis Team
Date: January 2025
"""

import json
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from family_risk_predictor import FamilyInstabilityPredictor, RiskAssessment

@dataclass
class InterventionPlan:
    """Detailed intervention plan for a family."""
    family_name: str
    priority_level: int  # 1 (highest) to 5 (lowest)
    intervention_type: str
    timeline: str  # e.g., "Q2 2025", "Within 6 months"
    resource_requirements: Dict[str, str]
    implementation_steps: List[str]
    success_criteria: List[str]
    risk_mitigation: List[str]
    expected_outcomes: Dict[str, str]
    committee_recommendations: List[str]

class InterventionRecommender:
    """
    Automated system for generating detailed intervention recommendations
    based on family risk assessments and evidence-based best practices.
    """
    
    def __init__(self):
        """Initialize with predictor and intervention templates."""
        self.predictor = FamilyInstabilityPredictor()
        
        # Resource requirement templates
        self.resource_templates = {
            'Monitor': {
                'committee_time': '1-2 hours/quarter',
                'expert_taxonomists': '1 monitoring specialist',
                'administrative_support': 'Minimal',
                'timeline': '6-12 months between reviews',
                'budget_estimate': '$2,000-5,000/year'
            },
            'Review': {
                'committee_time': '8-12 hours over 3-6 months',
                'expert_taxonomists': '3-4 committee members + 2 external experts',
                'administrative_support': 'Moderate (documentation, coordination)',
                'timeline': '3-6 months for complete review',
                'budget_estimate': '$15,000-25,000'
            },
            'Split': {
                'committee_time': '20-40 hours over 12-18 months',
                'expert_taxonomists': '5-8 committee members + 3-5 external experts',
                'administrative_support': 'High (proposal preparation, stakeholder coordination)',
                'timeline': '12-18 months for complete reorganization',
                'budget_estimate': '$50,000-100,000'
            },
            'Emergency': {
                'committee_time': '40-80 hours over 6-12 months',
                'expert_taxonomists': 'Full committee + 5-10 external experts',
                'administrative_support': 'Maximum (priority coordination, rapid implementation)',
                'timeline': '6-12 months emergency timeline',
                'budget_estimate': '$100,000-200,000'
            }
        }
        
        # Success criteria templates
        self.success_criteria_templates = {
            'Monitor': [
                'Family growth rate remains below 10% annually',
                'No phylogenetic coherence degradation',
                'Committee workload stays manageable',
                'No user complaints about family size'
            ],
            'Review': [
                'Complete phylogenetic analysis completed',
                'Natural subdivision points identified',
                'Stakeholder consensus on family boundaries',
                'Clear recommendations for future action'
            ],
            'Split': [
                'All new families achieve >8.0 stability scores',
                'Phylogenetic monophyly maintained in all daughter families',
                'User community acceptance >80%',
                'Database integration completed without errors',
                'No species misclassifications in transition'
            ],
            'Emergency': [
                'Crisis resolved within timeline',
                'System instability eliminated',
                'All affected species properly reassigned',
                'International database synchronization achieved',
                'Community confidence restored'
            ]
        }
    
    def generate_intervention_plan(self, family_name: str) -> InterventionPlan:
        """Generate comprehensive intervention plan for a specific family."""
        
        # Get risk assessment
        assessment = self.predictor.predict_family_risk(family_name)
        family_data = self.predictor.family_database[family_name]
        
        # Determine priority level (1-5, where 1 is highest)
        if assessment.risk_score >= 8.0:
            priority_level = 1
        elif assessment.risk_score >= 6.0:
            priority_level = 2
        elif assessment.risk_score >= 4.0:
            priority_level = 3
        elif assessment.risk_score >= 2.0:
            priority_level = 4
        else:
            priority_level = 5
        
        # Get timeline recommendation
        timeline = self._generate_timeline(assessment)
        
        # Generate implementation steps
        implementation_steps = self._generate_implementation_steps(assessment, family_data)
        
        # Generate risk mitigation strategies
        risk_mitigation = self._generate_risk_mitigation(assessment, family_data)
        
        # Generate expected outcomes
        expected_outcomes = self._generate_expected_outcomes(assessment, family_data)
        
        # Generate committee-specific recommendations
        committee_recommendations = self._generate_committee_recommendations(assessment, family_data)
        
        return InterventionPlan(
            family_name=family_name,
            priority_level=priority_level,
            intervention_type=assessment.intervention_type,
            timeline=timeline,
            resource_requirements=self.resource_templates[assessment.intervention_type],
            implementation_steps=implementation_steps,
            success_criteria=self.success_criteria_templates[assessment.intervention_type],
            risk_mitigation=risk_mitigation,
            expected_outcomes=expected_outcomes,
            committee_recommendations=committee_recommendations
        )
    
    def _generate_timeline(self, assessment: RiskAssessment) -> str:
        """Generate specific timeline recommendations."""
        
        if assessment.intervention_type == 'Emergency':
            return "IMMEDIATE ACTION REQUIRED - Begin within 30 days"
        elif assessment.intervention_type == 'Split':
            if assessment.risk_score > 7.0:
                return "Q2 2025 - High priority, begin planning immediately"
            else:
                return "Q3-Q4 2025 - Begin planning within 6 months"
        elif assessment.intervention_type == 'Review':
            if assessment.risk_score > 5.0:
                return "Q2 2025 - Schedule review within 3 months"
            else:
                return "Q4 2025 - Schedule review within 9 months"
        else:  # Monitor
            return "Ongoing - Quarterly monitoring with annual assessment"
    
    def _generate_implementation_steps(self, assessment: RiskAssessment, family_data) -> List[str]:
        """Generate detailed implementation steps."""
        
        steps = []
        
        if assessment.intervention_type == 'Monitor':
            steps = [
                "Establish quarterly monitoring schedule",
                "Assign monitoring specialist to track family metrics",
                "Set up automated alerts for growth rate >10%",
                "Schedule annual comprehensive review",
                "Maintain documentation of family evolution"
            ]
        
        elif assessment.intervention_type == 'Review':
            steps = [
                "Form review committee (3-4 members + external experts)",
                "Conduct comprehensive phylogenetic analysis",
                "Analyze host range patterns and geographic distribution",
                "Identify potential natural subdivision criteria",
                "Prepare preliminary recommendations report",
                "Conduct stakeholder consultation (30-day period)",
                "Finalize review report with action recommendations",
                "Present findings to full ICTV committee"
            ]
        
        elif assessment.intervention_type == 'Split':
            steps = [
                "Establish reorganization working group (5-8 experts)",
                "Allocate dedicated committee resources and timeline",
                "Conduct comprehensive molecular phylogenetic analysis",
                "Perform host range and biogeographic analysis",
                "Identify optimal splitting criteria and boundaries",
                "Draft formal reorganization proposal",
                "Prepare new family definitions and descriptions",
                "Create species assignment mapping for all taxa",
                "Submit proposal for ICTV Executive Committee review",
                "Conduct international stakeholder consultation (60-day period)",
                "Address feedback and revise proposal if needed",
                "Submit for formal ICTV ratification vote",
                "Coordinate implementation across international databases",
                "Monitor post-reorganization stability and user adoption"
            ]
            
            # Add size-specific steps
            if family_data.current_size > 300:
                steps.insert(4, "Consider multiple daughter families (6-12) rather than binary split")
                steps.insert(5, "Model different splitting scenarios for optimal family sizes")
        
        elif assessment.intervention_type == 'Emergency':
            steps = [
                "IMMEDIATE: Convene emergency ICTV session within 30 days",
                "Assign maximum priority and resource allocation",
                "Form crisis response team with full committee + external experts",
                "Conduct rapid but comprehensive analysis (6-8 weeks)",
                "Develop emergency reorganization proposal",
                "Fast-track proposal through abbreviated review process",
                "Coordinate immediate implementation with major databases",
                "Establish post-crisis monitoring and support systems",
                "Conduct post-implementation review and lessons learned"
            ]
        
        return steps
    
    def _generate_risk_mitigation(self, assessment: RiskAssessment, family_data) -> List[str]:
        """Generate risk mitigation strategies."""
        
        mitigation = []
        
        # Size-related risks
        if family_data.current_size > 200:
            mitigation.append("Phased implementation to minimize disruption to user community")
            mitigation.append("Prepare comprehensive species mapping to prevent misassignments")
        
        # Growth rate risks
        if family_data.growth_rate > 0.12:
            mitigation.append("Accelerated timeline to prevent further size increases")
            mitigation.append("Temporary moratorium on new species assignments until reorganization")
        
        # Host range risks
        if family_data.host_breadth > 5:
            mitigation.append("Use host boundaries as primary splitting criteria to maintain biological coherence")
            mitigation.append("Ensure each daughter family has coherent host range profile")
        
        # Committee process risks
        if assessment.intervention_type in ['Split', 'Emergency']:
            mitigation.extend([
                "Establish clear decision-making timeline to prevent delays",
                "Prepare backup committee members in case of unavailability",
                "Create communication plan to manage stakeholder expectations",
                "Develop contingency plans for common implementation challenges"
            ])
        
        # Technical implementation risks
        mitigation.extend([
            "Coordinate with major databases (NCBI, EMBL-EBI) before implementation",
            "Prepare database migration scripts and validation procedures",
            "Establish rollback procedures in case of implementation problems",
            "Create user communication and support plan for transition period"
        ])
        
        return mitigation
    
    def _generate_expected_outcomes(self, assessment: RiskAssessment, family_data) -> Dict[str, str]:
        """Generate expected outcomes from intervention."""
        
        outcomes = {}
        
        if assessment.intervention_type == 'Monitor':
            outcomes = {
                'stability_improvement': '10-20% improvement in family coherence metrics',
                'growth_management': 'Maintained manageable growth rate <10%/year',
                'resource_efficiency': 'Minimal resource investment with proactive oversight',
                'user_satisfaction': 'Maintained high user satisfaction with family structure'
            }
        
        elif assessment.intervention_type == 'Review':
            outcomes = {
                'information_clarity': 'Complete understanding of family structure and boundaries',
                'decision_readiness': 'Clear recommendations for future intervention needs',
                'stakeholder_alignment': 'Community consensus on family status and needs',
                'proactive_planning': 'Early identification of optimization opportunities'
            }
        
        elif assessment.intervention_type == 'Split':
            # Calculate expected outcomes based on current family size
            expected_families = min(8, max(3, family_data.current_size // 50))
            avg_size_after = family_data.current_size // expected_families
            
            outcomes = {
                'family_creation': f'{expected_families-1} new families created',
                'average_family_size': f'Reduced to {avg_size_after} species per family',
                'stability_improvement': f'Expected stability increase to >8.0 for all daughter families',
                'phylogenetic_coherence': 'Achievement of monophyly in all resulting families',
                'management_efficiency': '60-80% reduction in family management complexity',
                'user_satisfaction': '>85% user approval for improved family structure'
            }
        
        elif assessment.intervention_type == 'Emergency':
            outcomes = {
                'crisis_resolution': 'Complete elimination of system instability within 6-12 months',
                'stability_restoration': 'Return to normal operational stability across all families',
                'confidence_recovery': 'Restored community confidence in ICTV classification system',
                'future_prevention': 'Implementation of early warning systems to prevent future crises'
            }
        
        return outcomes
    
    def _generate_committee_recommendations(self, assessment: RiskAssessment, family_data) -> List[str]:
        """Generate specific recommendations for ICTV committee action."""
        
        recommendations = []
        
        # Priority and urgency recommendations
        if assessment.risk_score > 7.0:
            recommendations.append("URGENT: Assign highest committee priority to this family")
            recommendations.append("Allocate dedicated committee member as family liaison")
        elif assessment.risk_score > 5.0:
            recommendations.append("HIGH PRIORITY: Include in next quarterly committee meeting agenda")
        else:
            recommendations.append("ROUTINE: Include in annual family review cycle")
        
        # Resource allocation recommendations
        if assessment.intervention_type in ['Split', 'Emergency']:
            recommendations.extend([
                "Approve dedicated budget allocation for reorganization project",
                "Assign project manager for reorganization coordination",
                "Establish dedicated communication channel for stakeholder updates"
            ])
        
        # Expertise recommendations
        if family_data.host_breadth > 5:
            recommendations.append("Recruit additional experts in host-pathogen interactions")
        if family_data.genome_complexity > 6:
            recommendations.append("Include experts in complex genome architectures (RT viruses)")
        if family_data.geographic_distribution > 6:
            recommendations.append("Ensure international expert representation on committee")
        
        # Process recommendations
        recommendations.extend([
            "Document all decisions and rationale for future reference",
            "Maintain regular communication with affected research communities",
            "Coordinate timing with major virology conferences for maximum input",
            "Plan implementation to minimize disruption to ongoing research projects"
        ])
        
        # Post-implementation recommendations
        if assessment.intervention_type in ['Split', 'Emergency']:
            recommendations.extend([
                "Schedule 6-month post-implementation review",
                "Monitor user adoption and satisfaction metrics",
                "Prepare lessons learned document for future reorganizations",
                "Update ICTV procedures based on implementation experience"
            ])
        
        return recommendations
    
    def generate_quarterly_report(self) -> Dict:
        """Generate comprehensive quarterly intervention report."""
        
        # Get all assessments
        assessments = self.predictor.assess_all_families()
        
        # Generate plans for all families requiring intervention
        intervention_plans = {}
        for family_name, assessment in assessments.items():
            if assessment.risk_score > 2.0:  # Only families needing attention
                intervention_plans[family_name] = self.generate_intervention_plan(family_name)
        
        # Prioritize by urgency
        priority_order = sorted(intervention_plans.items(), 
                              key=lambda x: (x[1].priority_level, -assessments[x[0]].risk_score))
        
        # Calculate resource requirements
        total_budget = 0
        total_committee_hours = 0
        for _, plan in intervention_plans.items():
            budget_str = plan.resource_requirements['budget_estimate']
            # Extract budget range and use midpoint
            budget_range = budget_str.replace('$', '').replace(',', '').split('-')
            if len(budget_range) == 2:
                budget_midpoint = (int(budget_range[0]) + int(budget_range[1])) / 2
                total_budget += budget_midpoint
            
            # Extract committee hours
            hours_str = plan.resource_requirements['committee_time']
            if '-' in hours_str:
                hours_range = hours_str.split('-')
                hours_midpoint = (int(hours_range[0]) + int(hours_range[1].split()[0])) / 2
                total_committee_hours += hours_midpoint
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(assessments, intervention_plans)
        
        return {
            'report_date': datetime.now().strftime("%Y-%m-%d"),
            'reporting_period': 'Q1 2025',
            'executive_summary': executive_summary,
            'priority_interventions': [
                {
                    'family': family_name,
                    'priority_level': plan.priority_level,
                    'intervention_type': plan.intervention_type,
                    'timeline': plan.timeline,
                    'risk_score': assessments[family_name].risk_score,
                    'key_recommendations': plan.committee_recommendations[:3]
                }
                for family_name, plan in priority_order[:10]
            ],
            'resource_summary': {
                'total_budget_estimate': f"${total_budget:,.0f}",
                'total_committee_hours': f"{total_committee_hours:.0f} hours",
                'families_requiring_action': len(intervention_plans),
                'emergency_interventions': len([p for p in intervention_plans.values() if p.intervention_type == 'Emergency']),
                'planned_splits': len([p for p in intervention_plans.values() if p.intervention_type == 'Split'])
            },
            'detailed_plans': {name: self._plan_to_dict(plan) for name, plan in intervention_plans.items()},
            'recommendations_for_committee': self._generate_committee_recommendations_summary(intervention_plans)
        }
    
    def _generate_executive_summary(self, assessments, intervention_plans) -> List[str]:
        """Generate executive summary for quarterly report."""
        
        total_families = len(assessments)
        high_risk_count = len([a for a in assessments.values() if a.risk_score > 6.0])
        intervention_count = len(intervention_plans)
        
        summary = [
            f"Assessment of {total_families} ICTV families reveals {intervention_count} requiring intervention",
            f"{high_risk_count} families assessed as high risk requiring immediate attention",
            f"System stability score: {self.predictor.generate_dashboard_summary()['system_stability_score']:.1f}/10"
        ]
        
        # Add specific family highlights
        if high_risk_count > 0:
            high_risk_families = [name for name, a in assessments.items() if a.risk_score > 6.0]
            summary.append(f"Immediate attention required for: {', '.join(high_risk_families)}")
        
        # Add resource summary
        split_count = len([p for p in intervention_plans.values() if p.intervention_type == 'Split'])
        if split_count > 0:
            summary.append(f"{split_count} families recommended for reorganization within 12-18 months")
        
        summary.append("Proactive intervention strategy recommended to prevent crisis-driven reorganizations")
        
        return summary
    
    def _generate_committee_recommendations_summary(self, intervention_plans) -> List[str]:
        """Generate high-level committee recommendations."""
        
        recommendations = [
            "Adopt quarterly family monitoring schedule to identify issues early",
            "Allocate resources for proactive interventions to prevent crisis situations",
            "Establish dedicated reorganization project management capabilities"
        ]
        
        # Add specific recommendations based on current needs
        emergency_count = len([p for p in intervention_plans.values() if p.intervention_type == 'Emergency'])
        split_count = len([p for p in intervention_plans.values() if p.intervention_type == 'Split'])
        
        if emergency_count > 0:
            recommendations.append("URGENT: Convene emergency session for crisis-level families")
        
        if split_count > 2:
            recommendations.append("Consider staggered reorganization timeline to manage committee workload")
            recommendations.append("Recruit additional expert committee members for reorganization support")
        
        recommendations.extend([
            "Implement automated monitoring system for real-time family risk assessment",
            "Develop standardized reorganization procedures based on evidence-based practices",
            "Coordinate with international databases for seamless implementation of changes"
        ])
        
        return recommendations
    
    def _plan_to_dict(self, plan: InterventionPlan) -> Dict:
        """Convert intervention plan to dictionary for JSON serialization."""
        
        return {
            'priority_level': plan.priority_level,
            'intervention_type': plan.intervention_type,
            'timeline': plan.timeline,
            'resource_requirements': plan.resource_requirements,
            'implementation_steps': plan.implementation_steps,
            'success_criteria': plan.success_criteria,
            'risk_mitigation': plan.risk_mitigation,
            'expected_outcomes': plan.expected_outcomes,
            'committee_recommendations': plan.committee_recommendations
        }
    
    def save_quarterly_report(self, filename: str = "quarterly_intervention_report.json") -> str:
        """Save quarterly report to file."""
        
        report = self.generate_quarterly_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filename

def main():
    """Generate automated intervention recommendations."""
    
    print("🤖 ICTV Automated Intervention Recommendation System")
    print("=" * 60)
    print("Evidence-based recommendations for proactive family management")
    print()
    
    # Initialize recommender
    recommender = InterventionRecommender()
    
    # Generate quarterly report
    print("📊 GENERATING QUARTERLY INTERVENTION REPORT")
    print("-" * 50)
    report = recommender.generate_quarterly_report()
    
    # Display executive summary
    print("🔍 EXECUTIVE SUMMARY:")
    for item in report['executive_summary']:
        print(f"  • {item}")
    print()
    
    # Display priority interventions
    print("🚨 PRIORITY INTERVENTIONS:")
    for i, intervention in enumerate(report['priority_interventions'][:5]):
        print(f"{i+1}. {intervention['family']} (Priority {intervention['priority_level']})")
        print(f"   Action: {intervention['intervention_type']}")
        print(f"   Timeline: {intervention['timeline']}")
        print(f"   Risk Score: {intervention['risk_score']:.1f}/10")
        print(f"   Key Recommendation: {intervention['key_recommendations'][0]}")
        print()
    
    # Display resource summary
    print("💰 RESOURCE REQUIREMENTS:")
    resources = report['resource_summary']
    print(f"  Total Budget Estimate: {resources['total_budget_estimate']}")
    print(f"  Committee Hours Required: {resources['total_committee_hours']}")
    print(f"  Families Requiring Action: {resources['families_requiring_action']}")
    print(f"  Emergency Interventions: {resources['emergency_interventions']}")
    print(f"  Planned Reorganizations: {resources['planned_splits']}")
    print()
    
    # Display committee recommendations
    print("📋 COMMITTEE RECOMMENDATIONS:")
    for i, rec in enumerate(report['recommendations_for_committee'][:5]):
        print(f"  {i+1}. {rec}")
    print()
    
    # Generate detailed example for highest priority family
    if report['priority_interventions']:
        top_family = report['priority_interventions'][0]['family']
        print(f"📋 DETAILED PLAN EXAMPLE: {top_family}")
        print("-" * 40)
        
        plan = recommender.generate_intervention_plan(top_family)
        
        print(f"Intervention Type: {plan.intervention_type}")
        print(f"Timeline: {plan.timeline}")
        print(f"Priority Level: {plan.priority_level}/5")
        print()
        
        print("Implementation Steps:")
        for i, step in enumerate(plan.implementation_steps[:5]):
            print(f"  {i+1}. {step}")
        if len(plan.implementation_steps) > 5:
            print(f"  ... and {len(plan.implementation_steps) - 5} additional steps")
        print()
        
        print("Expected Outcomes:")
        for key, value in plan.expected_outcomes.items():
            print(f"  • {key.replace('_', ' ').title()}: {value}")
        print()
        
        print("Key Risk Mitigation:")
        for mitigation in plan.risk_mitigation[:3]:
            print(f"  • {mitigation}")
    
    # Save report
    print("\n💾 SAVING COMPREHENSIVE REPORT")
    print("-" * 35)
    filename = recommender.save_quarterly_report()
    print(f"Report saved to: {filename}")
    
    print("\n✅ Automated Intervention Recommendation System operational!")
    print("📈 Ready for committee decision support and proactive management")
    
    return recommender

if __name__ == "__main__":
    recommender = main()