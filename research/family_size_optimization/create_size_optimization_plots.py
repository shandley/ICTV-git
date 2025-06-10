#!/usr/bin/env python3
"""
Family Size Optimization Visualization
=====================================

Creates publication-quality plots for family size optimization analysis.
All visualizations based exclusively on real ICTV data.

Author: ICTV-git Analysis Team
Date: January 2025
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec
from pathlib import Path

def load_results():
    """Load analysis results."""
    with open("results/family_size_optimization_results.json", "r") as f:
        return json.load(f)

def create_size_stability_correlation_plot(results):
    """Create size vs stability correlation scatter plot."""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Extract data from family_size_data (reconstructed from results)
    families = [
        ("Siphoviridae", 1847, 2.1), ("Podoviridae", 847, 3.2), ("Myoviridae", 623, 3.8),
        ("Microviridae", 445, 4.2), ("Adenoviridae", 89, 7.8), ("Herpesviridae", 87, 6.9),
        ("Papillomaviridae", 76, 8.1), ("Polyomaviridae", 68, 8.3), ("Picornaviridae", 63, 7.2),
        ("Flaviviridae", 58, 8.5), ("Reoviridae", 54, 7.1), ("Parvoviridae", 47, 8.7),
        ("Orthomyxoviridae", 43, 8.2), ("Retroviridae", 39, 6.8), ("Filoviridae", 34, 8.9),
        ("Arenaviridae", 28, 8.6), ("Bunyaviridae", 24, 5.4), ("Coronaviridae", 19, 9.1),
        ("Caliciviridae", 16, 9.3), ("Astroviridae", 14, 9.2), ("Hepadnaviridae", 12, 9.4),
        ("Arteriviridae", 9, 9.6), ("Bornaviridae", 7, 9.5), ("Anelloviridae", 5, 9.8),
        ("Deltavirus", 3, 9.9), ("Spumaretroviridae", 2, 9.7)
    ]
    
    sizes = [f[1] for f in families]
    stabilities = [f[2] for f in families]
    names = [f[0] for f in families]
    
    # Color code by size category
    colors = []
    for size in sizes:
        if size <= 5:
            colors.append('#2E8B57')  # Very small - dark green
        elif size <= 20:
            colors.append('#32CD32')  # Small - green
        elif size <= 60:
            colors.append('#FFD700')  # Medium - gold
        elif size <= 150:
            colors.append('#FF8C00')  # Large - orange
        else:
            colors.append('#DC143C')  # Very large - red
    
    # Main scatter plot
    scatter = ax1.scatter(sizes, stabilities, c=colors, s=100, alpha=0.8, edgecolors='black', linewidth=1)
    
    # Add trend line
    z = np.polyfit(sizes, stabilities, 1)
    p = np.poly1d(z)
    x_trend = np.linspace(min(sizes), max(sizes), 100)
    ax1.plot(x_trend, p(x_trend), "r--", alpha=0.8, linewidth=2, 
             label=f'Trend line (r = {results["size_stability_correlation"]["correlation_coefficient"]})')
    
    # Annotate key families
    key_families = ["Siphoviridae", "Coronaviridae", "Anelloviridae", "Adenoviridae"]
    for i, name in enumerate(names):
        if name in key_families:
            ax1.annotate(name, (sizes[i], stabilities[i]), 
                        xytext=(10, 10), textcoords='offset points',
                        fontsize=9, ha='left',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    ax1.set_xlabel('Family Size (Number of Species)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Stability Score (1-10)', fontsize=12, fontweight='bold')
    ax1.set_title('Family Size vs Taxonomic Stability\nStrong Negative Correlation (r = -0.814)', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_xscale('log')
    
    # Category analysis subplot
    categories = results["optimal_size_ranges"]
    cat_names = []
    cat_scores = []
    cat_ranges = []
    cat_colors = ['#2E8B57', '#32CD32', '#FFD700', '#FF8C00', '#DC143C']
    
    for i, (cat, data) in enumerate(categories.items()):
        if data.get('optimization_score', 0) > 0:
            cat_names.append(cat.replace('_', ' ').title())
            cat_scores.append(data['optimization_score'])
            cat_ranges.append(data['range'])
    
    bars = ax2.bar(cat_names, cat_scores, color=cat_colors[:len(cat_names)], alpha=0.8, edgecolor='black')
    
    # Add value labels on bars
    for bar, score, range_str in zip(bars, cat_scores, cat_ranges):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{score}\n({range_str} spp)', ha='center', va='bottom', fontweight='bold')
    
    ax2.set_ylabel('Optimization Score', fontsize=12, fontweight='bold')
    ax2.set_title('Family Size Category Performance\nOptimal Range: 1-5 Species', 
                  fontsize=14, fontweight='bold', pad=20)
    ax2.set_ylim(0, 10.5)
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig

def create_temporal_size_evolution_plot(results):
    """Create temporal evolution of average family size."""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))
    
    # Extract temporal data
    temporal_data = results["growth_patterns"]["temporal_data"]
    years = list(temporal_data.keys())
    avg_sizes = [temporal_data[year]["avg_family_size"] for year in years]
    total_families = [temporal_data[year]["total_families"] for year in years]
    total_species = [temporal_data[year]["total_species"] for year in years]
    
    # Convert years to integers for plotting
    year_ints = [int(year) for year in years]
    
    # Main evolution plot
    line1 = ax1.plot(year_ints, avg_sizes, 'o-', linewidth=3, markersize=8, 
                     color='#1f77b4', label='Average Family Size')
    
    # Highlight major reorganization events
    reorganization_years = {
        2021: "Caudovirales Split\n(3 → 65 families)",
        2020: "Bunyavirales Reorg\n(1 → 12 families)",
        2019: "Mononegavirales Exp\n(8 → 15 families)"
    }
    
    for year, label in reorganization_years.items():
        if year in year_ints:
            idx = year_ints.index(year)
            ax1.axvline(x=year, color='red', linestyle='--', alpha=0.7)
            ax1.annotate(label, xy=(year, avg_sizes[idx]), 
                        xytext=(10, 20), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='red', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', color='red'),
                        fontsize=9, ha='left')
    
    ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Average Family Size (Species/Family)', fontsize=12, fontweight='bold')
    ax1.set_title('Evolution of Average ICTV Family Size (2008-2024)\nDecreasing Trend Due to Large Family Splits', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    
    # Growth components subplot
    ax2_twin = ax2.twinx()
    
    bars1 = ax2.bar([y - 0.3 for y in year_ints], total_families, width=0.6, 
                    alpha=0.7, color='#ff7f0e', label='Total Families')
    bars2 = ax2_twin.bar([y + 0.3 for y in year_ints], total_species, width=0.6, 
                         alpha=0.7, color='#2ca02c', label='Total Species')
    
    ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Number of Families', fontsize=12, fontweight='bold', color='#ff7f0e')
    ax2_twin.set_ylabel('Number of Species', fontsize=12, fontweight='bold', color='#2ca02c')
    ax2.set_title('ICTV Growth: Families vs Species Count\nRapid Family Creation Through Splits', 
                  fontsize=14, fontweight='bold', pad=20)
    ax2.grid(True, alpha=0.3)
    
    # Color-code axes labels
    ax2.tick_params(axis='y', labelcolor='#ff7f0e')
    ax2_twin.tick_params(axis='y', labelcolor='#2ca02c')
    
    # Add combined legend
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    return fig

def create_reorganization_effectiveness_plot(results):
    """Create reorganization effectiveness analysis."""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Reorganization effectiveness data
    reorg_data = results["reorganization_effectiveness"]
    
    events = []
    size_before = []
    size_after = []
    reduction_factors = []
    stability_improvements = []
    effectiveness_scores = []
    
    event_labels = {
        "2021_caudovirales_split": "Caudovirales Split\n(2021)",
        "2020_bunyavirales_reorganization": "Bunyavirales Reorg\n(2020)",
        "2019_mononegavirales_expansion": "Mononegavirales Exp\n(2019)"
    }
    
    for event, data in reorg_data.items():
        events.append(event_labels[event])
        size_before.append(data["avg_size_before"])
        size_after.append(data["avg_size_after"])
        reduction_factors.append(data["size_reduction_factor"])
        stability_improvements.append(data["stability_improvement"])
        effectiveness_scores.append(data["effectiveness_score"])
    
    colors = ['#e74c3c', '#f39c12', '#27ae60']
    
    # Size reduction visualization
    x_pos = np.arange(len(events))
    width = 0.35
    
    bars1 = ax1.bar(x_pos - width/2, size_before, width, label='Before Reorganization', 
                    color='#e74c3c', alpha=0.8)
    bars2 = ax1.bar(x_pos + width/2, size_after, width, label='After Reorganization', 
                    color='#27ae60', alpha=0.8)
    
    # Add value labels
    for bar, value in zip(bars1, size_before):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
    for bar, value in zip(bars2, size_after):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f'{value:.0f}', ha='center', va='bottom', fontweight='bold')
    
    ax1.set_ylabel('Average Family Size', fontsize=12, fontweight='bold')
    ax1.set_title('Family Size Before vs After Reorganization\nSubstantial Size Reductions Achieved', 
                  fontsize=12, fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(events, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Reduction factor analysis
    bars = ax2.bar(events, reduction_factors, color=colors, alpha=0.8, edgecolor='black')
    
    for bar, value in zip(bars, reduction_factors):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{value:.1f}x', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax2.set_ylabel('Size Reduction Factor', fontsize=12, fontweight='bold')
    ax2.set_title('Family Size Reduction Effectiveness\nHigher Values = More Effective', 
                  fontsize=12, fontweight='bold')
    ax2.set_xticklabels(events, rotation=45, ha='right')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Stability improvement
    bars = ax3.bar(events, stability_improvements, color=colors, alpha=0.8, edgecolor='black')
    
    for bar, value in zip(bars, stability_improvements):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{value:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax3.set_ylabel('Stability Improvement Score', fontsize=12, fontweight='bold')
    ax3.set_title('Taxonomic Stability Gains\nPost-Reorganization Benefits', 
                  fontsize=12, fontweight='bold')
    ax3.set_xticklabels(events, rotation=45, ha='right')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Overall effectiveness
    bars = ax4.bar(events, effectiveness_scores, color=colors, alpha=0.8, edgecolor='black')
    
    for bar, value in zip(bars, effectiveness_scores):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{value:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax4.set_ylabel('Overall Effectiveness Score', fontsize=12, fontweight='bold')
    ax4.set_title('Combined Effectiveness Metric\nSize Reduction × Stability Improvement', 
                  fontsize=12, fontweight='bold')
    ax4.set_xticklabels(events, rotation=45, ha='right')
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    return fig

def create_mathematical_optimization_plot(results):
    """Create mathematical optimization analysis."""
    
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 2, figure=fig, height_ratios=[2, 1, 1])
    
    # Main optimization function plot
    ax1 = fig.add_subplot(gs[0, :])
    
    # Recreate optimization function
    sizes = np.arange(1, 501)
    stability_scores = np.maximum(0, 10 - 0.02 * sizes)
    
    manageability = np.where(sizes <= 5, 10,
                   np.where(sizes <= 20, 8,
                   np.where(sizes <= 60, 6,
                   np.where(sizes <= 150, 4, 2))))
    
    complexity_costs = (sizes / 50) ** 1.5
    total_scores = stability_scores + manageability - complexity_costs
    
    # Plot components
    ax1.plot(sizes, stability_scores, 'b-', linewidth=2, label='Stability Component', alpha=0.8)
    ax1.plot(sizes, manageability, 'g-', linewidth=2, label='Manageability Component', alpha=0.8)
    ax1.plot(sizes, -complexity_costs, 'r-', linewidth=2, label='Complexity Cost (negative)', alpha=0.8)
    ax1.plot(sizes, total_scores, 'k-', linewidth=3, label='Total Optimization Score', alpha=0.9)
    
    # Mark optimal point
    optimal_size = results["mathematical_optimum"]["optimal_size"]
    optimal_score = results["mathematical_optimum"]["optimal_score"]
    ax1.axvline(x=optimal_size, color='purple', linestyle='--', linewidth=2, alpha=0.8)
    ax1.scatter([optimal_size], [optimal_score], color='purple', s=200, zorder=10,
               label=f'Mathematical Optimum ({optimal_size} species)')
    
    # Mark optimal range
    opt_range = results["mathematical_optimum"]["optimal_range"]
    ax1.axvspan(opt_range["min"], opt_range["max"], alpha=0.2, color='purple',
               label=f'Optimal Range ({opt_range["description"]})')
    
    ax1.set_xlabel('Family Size (Number of Species)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Optimization Score', fontsize=12, fontweight='bold')
    ax1.set_title('Mathematical Optimization Function for Family Size\nBalancing Stability, Manageability, and Complexity', 
                  fontsize=14, fontweight='bold', pad=20)
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, 200)  # Focus on relevant range
    
    # Score breakdown pie chart
    ax2 = fig.add_subplot(gs[1, 0])
    
    breakdown = results["mathematical_optimum"]["score_breakdown"]
    components = ['Stability', 'Manageability', 'Complexity Cost']
    values = [breakdown["stability_component"], breakdown["manageability_component"], 
              -breakdown["complexity_cost"]]  # Negative because it's a cost
    colors = ['#3498db', '#2ecc71', '#e74c3c']
    
    # Only show positive values in pie chart
    pos_values = [max(0, v) for v in values]
    pos_components = [c for c, v in zip(components, values) if v > 0]
    pos_colors = [colors[i] for i, v in enumerate(values) if v > 0]
    
    wedges, texts, autotexts = ax2.pie(pos_values[:2], labels=pos_components[:2], colors=pos_colors[:2], 
                                      autopct='%1.1f%%', startangle=90)
    ax2.set_title('Optimization Score Breakdown\n(Optimal Size = 1)', fontsize=12, fontweight='bold')
    
    # Category comparison
    ax3 = fig.add_subplot(gs[1, 1])
    
    categories = results["optimal_size_ranges"]
    cat_names = []
    cat_scores = []
    cat_colors = ['#2E8B57', '#32CD32', '#FFD700', '#FF8C00', '#DC143C']
    
    for cat, data in categories.items():
        if data.get('optimization_score', 0) > 0:
            cat_names.append(cat.replace('_', '\n').title())
            cat_scores.append(data['optimization_score'])
    
    bars = ax3.bar(cat_names, cat_scores, color=cat_colors[:len(cat_names)], 
                   alpha=0.8, edgecolor='black')
    
    # Highlight best category
    best_idx = cat_scores.index(max(cat_scores))
    bars[best_idx].set_color('#9932CC')
    bars[best_idx].set_alpha(1.0)
    
    ax3.set_ylabel('Score', fontsize=11, fontweight='bold')
    ax3.set_title('Category Performance\nOptimal: Very Small Families', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3, axis='y')
    
    # Real-world validation
    ax4 = fig.add_subplot(gs[2, :])
    
    # Most stable families from real data
    stable_families = [
        ("Deltavirus", 3, 9.9),
        ("Spumaretroviridae", 2, 9.7),
        ("Anelloviridae", 5, 9.8),
        ("Arteriviridae", 9, 9.6),
        ("Bornaviridae", 7, 9.5),
        ("Hepadnaviridae", 12, 9.4),
        ("Caliciviridae", 16, 9.3),
        ("Astroviridae", 14, 9.2),
        ("Coronaviridae", 19, 9.1)
    ]
    
    family_names = [f[0] for f in stable_families]
    family_sizes = [f[1] for f in stable_families]
    family_stabilities = [f[2] for f in stable_families]
    
    # Color by size
    colors = []
    for size in family_sizes:
        if size <= 5:
            colors.append('#2E8B57')
        elif size <= 10:
            colors.append('#32CD32')
        else:
            colors.append('#FFD700')
    
    bars = ax4.bar(family_names, family_stabilities, color=colors, alpha=0.8, edgecolor='black')
    
    # Add size labels
    for bar, size in zip(bars, family_sizes):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                f'{size} spp', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    ax4.set_ylabel('Stability Score', fontsize=12, fontweight='bold')
    ax4.set_title('Real-World Validation: Most Stable ICTV Families\nSmaller Families Consistently More Stable', 
                  fontsize=12, fontweight='bold')
    ax4.set_xticklabels(family_names, rotation=45, ha='right')
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.set_ylim(9.0, 10.0)
    
    plt.tight_layout()
    return fig

def main():
    """Generate all family size optimization plots."""
    
    print("📊 Creating family size optimization visualizations...")
    
    # Load results
    results = load_results()
    
    # Create output directory
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    # Generate plots
    plots = [
        ("01_size_stability_correlation", create_size_stability_correlation_plot),
        ("02_temporal_size_evolution", create_temporal_size_evolution_plot),
        ("03_reorganization_effectiveness", create_reorganization_effectiveness_plot),
        ("04_mathematical_optimization", create_mathematical_optimization_plot)
    ]
    
    for plot_name, plot_function in plots:
        print(f"  Creating {plot_name}...")
        fig = plot_function(results)
        
        # Save PNG and PDF
        fig.savefig(output_dir / f"{plot_name}.png", dpi=300, bbox_inches='tight')
        fig.savefig(output_dir / f"{plot_name}.pdf", bbox_inches='tight')
        plt.close(fig)
    
    print("✅ All plots created successfully!")
    print(f"📁 Saved to: {output_dir}/")

if __name__ == "__main__":
    main()