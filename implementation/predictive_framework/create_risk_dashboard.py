#!/usr/bin/env python3
"""
ICTV Family Risk Assessment Dashboard
====================================

Interactive visualization dashboard for the Predictive Instability Framework.
Creates publication-quality plots showing family risk assessments, intervention
priorities, and temporal predictions for committee decision support.

Author: ICTV-git Analysis Team
Date: January 2025
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
from pathlib import Path
from family_risk_predictor import FamilyInstabilityPredictor

def load_assessment_data():
    """Load assessment data from the predictor."""
    predictor = FamilyInstabilityPredictor()
    assessments = predictor.assess_all_families()
    dashboard = predictor.generate_dashboard_summary()
    priority_list = predictor.generate_priority_list()
    
    return predictor, assessments, dashboard, priority_list

def create_risk_distribution_plot(dashboard):
    """Create risk distribution visualization."""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Risk category distribution
    categories = list(dashboard['risk_distribution'].keys())
    counts = list(dashboard['risk_distribution'].values())
    colors = {'Low': '#2E8B57', 'Medium': '#FFD700', 'High': '#FF8C00', 'Crisis': '#DC143C'}
    plot_colors = [colors[cat] for cat in categories]
    
    bars1 = ax1.bar(categories, counts, color=plot_colors, alpha=0.8, edgecolor='black', linewidth=2)
    
    # Add value labels
    for bar, count in zip(bars1, counts):
        percentage = (count / dashboard['total_families']) * 100
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{count}\n({percentage:.0f}%)', ha='center', va='bottom', 
                fontweight='bold', fontsize=11)
    
    ax1.set_ylabel('Number of Families', fontsize=12, fontweight='bold')
    ax1.set_title('Current Risk Distribution\nICTV Family Instability Assessment', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3, axis='y')
    ax1.set_ylim(0, max(counts) + 1)
    
    # Intervention type distribution
    interventions = list(dashboard['intervention_distribution'].keys())
    int_counts = list(dashboard['intervention_distribution'].values())
    int_colors = {'Monitor': '#2E8B57', 'Review': '#FFD700', 'Split': '#FF8C00', 'Emergency': '#DC143C'}
    int_plot_colors = [int_colors[inter] for inter in interventions]
    
    bars2 = ax2.bar(interventions, int_counts, color=int_plot_colors, alpha=0.8, edgecolor='black', linewidth=2)
    
    # Add value labels
    for bar, count in zip(bars2, int_counts):
        percentage = (count / dashboard['total_families']) * 100
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{count}\n({percentage:.0f}%)', ha='center', va='bottom', 
                fontweight='bold', fontsize=11)
    
    ax2.set_ylabel('Number of Families', fontsize=12, fontweight='bold')
    ax2.set_title('Recommended Interventions\nProactive Management Strategy', 
                  fontsize=14, fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_ylim(0, max(int_counts) + 1)
    
    # Add system health summary
    fig.suptitle(f'ICTV Family Stability Assessment Dashboard\n'
                f'System Stability: {dashboard["system_stability_score"]:.1f}/10 | '
                f'Average Risk: {dashboard["avg_risk_score"]:.1f}/10 | '
                f'Model Confidence: {dashboard["model_confidence"]:.0%}',
                fontsize=16, fontweight='bold', y=0.95)
    
    plt.tight_layout()
    return fig

def create_family_risk_matrix(assessments, predictor):
    """Create comprehensive risk assessment matrix."""
    
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Prepare data
    families = list(assessments.keys())
    risk_scores = [assessments[name].risk_score for name in families]
    family_sizes = [predictor.family_database[name].current_size for name in families]
    growth_rates = [predictor.family_database[name].growth_rate for name in families]
    
    # Create color map based on risk category
    colors = []
    for name in families:
        category = assessments[name].risk_category
        if category == 'Low':
            colors.append('#2E8B57')
        elif category == 'Medium':
            colors.append('#FFD700')
        elif category == 'High':
            colors.append('#FF8C00')
        else:
            colors.append('#DC143C')
    
    # Create size mapping for bubble sizes
    max_size = max(family_sizes)
    bubble_sizes = [(size / max_size) * 1000 + 100 for size in family_sizes]
    
    # Create scatter plot
    scatter = ax.scatter(family_sizes, risk_scores, c=colors, s=bubble_sizes, 
                        alpha=0.7, edgecolors='black', linewidth=2)
    
    # Add risk zones
    # Optimal zone (low risk)
    optimal_zone = patches.Rectangle((0, 0), 50, 3, linewidth=2, edgecolor='green',
                                   facecolor='green', alpha=0.1, linestyle='--')
    ax.add_patch(optimal_zone)
    ax.text(25, 1.5, 'OPTIMAL\nZONE', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='green', alpha=0.8),
            fontweight='bold', fontsize=10)
    
    # Warning zone (medium risk)
    warning_zone = patches.Rectangle((50, 3), 100, 2, linewidth=2, edgecolor='orange',
                                   facecolor='orange', alpha=0.1, linestyle='--')
    ax.add_patch(warning_zone)
    ax.text(100, 4, 'WARNING\nZONE', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='orange', alpha=0.8),
            fontweight='bold', fontsize=10)
    
    # Danger zone (high risk)
    danger_zone = patches.Rectangle((150, 5), 1000, 3, linewidth=2, edgecolor='red',
                                  facecolor='red', alpha=0.1, linestyle='--')
    ax.add_patch(danger_zone)
    ax.text(400, 6.5, 'DANGER\nZONE', ha='center', va='center',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='red', alpha=0.8),
            fontweight='bold', fontsize=10)
    
    # Annotate high-risk families
    high_risk_families = [name for name in families if assessments[name].risk_score > 5.0]
    for name in high_risk_families:
        idx = families.index(name)
        ax.annotate(name, (family_sizes[idx], risk_scores[idx]), 
                   xytext=(10, 10), textcoords='offset points',
                   fontsize=10, ha='left', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.9),
                   arrowprops=dict(arrowstyle='->', color='black', alpha=0.7))
    
    ax.set_xlabel('Family Size (Number of Species)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Risk Score (0-10)', fontsize=14, fontweight='bold')
    ax.set_title('Family Risk Assessment Matrix\nBubble Size = Growth Rate | Color = Risk Category', 
                 fontsize=16, fontweight='bold', pad=20)
    ax.set_xscale('log')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 10)
    
    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#2E8B57', 
                   markersize=10, label='Low Risk'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FFD700', 
                   markersize=10, label='Medium Risk'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#FF8C00', 
                   markersize=10, label='High Risk'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#DC143C', 
                   markersize=10, label='Crisis')
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=12)
    
    plt.tight_layout()
    return fig

def create_intervention_timeline(assessments):
    """Create intervention timeline visualization."""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    
    # Prepare timeline data
    interventions = []
    for name, assessment in assessments.items():
        if assessment.predicted_intervention_date:
            year_month = assessment.predicted_intervention_date
            year = int(year_month.split('-')[0])
            month = int(year_month.split('-')[1])
            interventions.append((year + month/12, name, assessment.intervention_type, assessment.risk_score))
    
    interventions.sort(key=lambda x: x[0])  # Sort by date
    
    if interventions:
        # Timeline plot
        dates = [x[0] for x in interventions]
        names = [x[1] for x in interventions]
        types = [x[2] for x in interventions]
        scores = [x[3] for x in interventions]
        
        # Color by intervention type
        type_colors = {'Monitor': '#2E8B57', 'Review': '#FFD700', 'Split': '#FF8C00', 'Emergency': '#DC143C'}
        colors = [type_colors[t] for t in types]
        
        # Create timeline
        ax1.scatter(dates, range(len(dates)), c=colors, s=200, alpha=0.8, edgecolors='black', linewidth=2)
        
        # Add family names
        for i, (date, name, int_type, score) in enumerate(interventions):
            ax1.text(date + 0.1, i, f'{name}\n({int_type})', va='center', fontweight='bold', fontsize=10,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Intervention Sequence', fontsize=12, fontweight='bold')
        ax1.set_title('Predicted Intervention Timeline\nProactive Management Schedule', 
                      fontsize=14, fontweight='bold', pad=20)
        ax1.grid(True, alpha=0.3, axis='x')
        ax1.set_yticks([])
        
        # Intervention workload by year
        year_workload = {}
        for date, name, int_type, score in interventions:
            year = int(date)
            if year not in year_workload:
                year_workload[year] = 0
            # Weight by intervention complexity
            weight = {'Monitor': 1, 'Review': 2, 'Split': 5, 'Emergency': 10}
            year_workload[year] += weight[int_type]
        
        years = sorted(year_workload.keys())
        workloads = [year_workload[year] for year in years]
        
        bars = ax2.bar(years, workloads, alpha=0.8, color='#1f77b4', edgecolor='black')
        
        # Add value labels
        for bar, workload in zip(bars, workloads):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    f'{workload}', ha='center', va='bottom', fontweight='bold')
        
        ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Committee Workload Score', fontsize=12, fontweight='bold')
        ax2.set_title('Projected Committee Workload\nResource Planning Guide', 
                      fontsize=14, fontweight='bold', pad=20)
        ax2.grid(True, alpha=0.3, axis='y')
    
    else:
        ax1.text(0.5, 0.5, 'No Interventions Predicted\nAll Families in Optimal Range', 
                ha='center', va='center', transform=ax1.transAxes, fontsize=16, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='green', alpha=0.7))
        ax1.set_title('Predicted Intervention Timeline', fontsize=14, fontweight='bold')
        
        ax2.text(0.5, 0.5, 'Minimal Committee Workload Expected', 
                ha='center', va='center', transform=ax2.transAxes, fontsize=16, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='green', alpha=0.7))
        ax2.set_title('Projected Committee Workload', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    return fig

def create_priority_action_summary(priority_list, assessments):
    """Create priority action summary visualization."""
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Take top 8 families for display
    top_families = priority_list[:8]
    family_names = [x[0] for x in top_families]
    risk_scores = [x[1] for x in top_families]
    action_types = [x[2] for x in top_families]
    
    # Get additional data
    probs_3yr = [assessments[name].reorganization_probability_3yr * 100 for name in family_names]
    
    # Create horizontal bar chart
    y_positions = range(len(family_names))
    
    # Color by action type
    action_colors = {'Monitor': '#2E8B57', 'Review': '#FFD700', 'Split': '#FF8C00', 'Emergency': '#DC143C'}
    colors = [action_colors[action] for action in action_types]
    
    bars = ax.barh(y_positions, risk_scores, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    
    # Add risk score labels
    for i, (bar, score, prob) in enumerate(zip(bars, risk_scores, probs_3yr)):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
               f'{score:.1f}\n({prob:.0f}%)', ha='left', va='center', fontweight='bold', fontsize=10)
    
    # Customize chart
    ax.set_yticks(y_positions)
    ax.set_yticklabels(family_names, fontsize=12, fontweight='bold')
    ax.set_xlabel('Risk Score (0-10)', fontsize=12, fontweight='bold')
    ax.set_title('Priority Action Summary\nImmediate Attention Required (Risk Score + 3-Year Probability)', 
                 fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, axis='x')
    ax.set_xlim(0, 10)
    
    # Add action type legend
    legend_elements = [
        patches.Patch(facecolor='#2E8B57', label='Monitor'),
        patches.Patch(facecolor='#FFD700', label='Review'), 
        patches.Patch(facecolor='#FF8C00', label='Split'),
        patches.Patch(facecolor='#DC143C', label='Emergency')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=12)
    
    # Add priority ranking
    for i, (name, score, action) in enumerate(top_families):
        ax.text(-0.5, i, f'#{i+1}', ha='center', va='center', fontweight='bold', 
               fontsize=12, color='red')
    
    plt.tight_layout()
    return fig

def main():
    """Generate comprehensive risk assessment dashboard."""
    
    print("📊 Creating ICTV Family Risk Assessment Dashboard...")
    
    # Load data
    predictor, assessments, dashboard, priority_list = load_assessment_data()
    
    # Create output directory
    output_dir = Path("dashboard_results")
    output_dir.mkdir(exist_ok=True)
    
    # Generate visualizations
    visualizations = [
        ("01_risk_distribution", lambda: create_risk_distribution_plot(dashboard)),
        ("02_family_risk_matrix", lambda: create_family_risk_matrix(assessments, predictor)),
        ("03_intervention_timeline", lambda: create_intervention_timeline(assessments)),
        ("04_priority_action_summary", lambda: create_priority_action_summary(priority_list, assessments))
    ]
    
    for viz_name, viz_function in visualizations:
        print(f"  Creating {viz_name}...")
        fig = viz_function()
        
        # Save PNG and PDF
        fig.savefig(output_dir / f"{viz_name}.png", dpi=300, bbox_inches='tight')
        fig.savefig(output_dir / f"{viz_name}.pdf", bbox_inches='tight')
        plt.close(fig)
    
    print("✅ Risk Assessment Dashboard created successfully!")
    print(f"📁 Saved to: {output_dir}/")
    
    # Print dashboard summary
    print(f"\n🔍 DASHBOARD SUMMARY:")
    print(f"Total families analyzed: {dashboard['total_families']}")
    print(f"System stability: {dashboard['system_stability_score']:.1f}/10")
    print(f"Families requiring attention: {len([x for x in priority_list if x[1] > 4.0])}")
    print(f"Predicted reorganizations (3yr): {dashboard['predicted_reorganizations_3yr']}")
    print(f"Model confidence: {dashboard['model_confidence']:.0%}")

if __name__ == "__main__":
    main()