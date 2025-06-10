"""Visualizations for Genome Architecture Constraints Analysis"""

import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches


def create_genome_architecture_visualizations():
    """Create all visualizations for genome architecture analysis."""
    # Load results - check multiple possible paths
    possible_paths = [
        Path(__file__).parent / "results" / "GenomeArchitectureAnalyzer_results.json",
        Path(__file__).parent.parent / "genomearchitectureanalyzer" / "results" / "GenomeArchitectureAnalyzer_results.json"
    ]
    
    results_path = None
    for path in possible_paths:
        if path.exists():
            results_path = path
            break
    
    if not results_path:
        print(f"Results file not found in any of the checked paths")
        return
    
    with open(results_path, 'r') as f:
        results = json.load(f)
    
    # Create output directory
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(exist_ok=True)
    
    # Set up the style
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 16))
    
    # 1. Genome Type Distribution Over Time
    ax1 = plt.subplot(3, 3, 1)
    plot_genome_distribution(ax1, results)
    
    # 2. Classification Approach Categories
    ax2 = plt.subplot(3, 3, 2)
    plot_classification_approaches(ax2, results)
    
    # 3. Family Size by Genome Type
    ax3 = plt.subplot(3, 3, 3)
    plot_family_sizes(ax3, results)
    
    # 4. Baltimore Group Evolution
    ax4 = plt.subplot(3, 3, 4)
    plot_baltimore_evolution(ax4, results)
    
    # 5. Discovery Bias Timeline
    ax5 = plt.subplot(3, 3, 5)
    plot_discovery_bias(ax5, results)
    
    # 6. Taxonomic Complexity
    ax6 = plt.subplot(3, 3, 6)
    plot_taxonomic_complexity(ax6, results)
    
    # 7. Growth Rates by Genome Type
    ax7 = plt.subplot(3, 3, 7)
    plot_growth_rates(ax7, results)
    
    # 8. Stability Patterns
    ax8 = plt.subplot(3, 3, 8)
    plot_stability_patterns(ax8, results)
    
    # 9. Key Findings Summary
    ax9 = plt.subplot(3, 3, 9)
    plot_key_findings(ax9, results)
    
    plt.suptitle('Genome Architecture Constraints: How Structure Shapes Viral Taxonomy', 
                 fontsize=24, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    
    # Save the figure
    output_path = output_dir / "genome_architecture_analysis_figure.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nFigure saved to: {output_path}")
    
    # Also save as PDF for publication
    pdf_path = output_dir / "genome_architecture_analysis_figure.pdf"
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
    print(f"PDF saved to: {pdf_path}")
    
    plt.close()
    
    # Create additional detailed plots
    create_baltimore_classification_plot(results, output_dir)
    create_architecture_constraints_plot(results, output_dir)


def plot_genome_distribution(ax, results):
    """Plot genome type distribution over time."""
    historical = results['genome_distributions']['historical_counts']
    
    # Prepare data
    years = sorted(historical.keys())
    genome_types = ['dsDNA', 'ssDNA', 'dsRNA', 'ssRNA(+)', 'ssRNA(-)', 'ssRNA-RT', 'dsDNA-RT']
    
    # Create stacked area chart
    data_matrix = []
    for genome_type in genome_types:
        values = [historical[str(year)][genome_type] for year in years]
        data_matrix.append(values)
    
    # Plot stacked areas
    colors = plt.cm.Set3(np.linspace(0, 1, len(genome_types)))
    ax.stackplot(years, *data_matrix, labels=genome_types, colors=colors, alpha=0.8)
    
    # Customize
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Species', fontsize=12)
    ax.set_title('Genome Type Distribution Evolution', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax.grid(True, alpha=0.3)
    
    # Format y-axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))


def plot_classification_approaches(ax, results):
    """Plot classification approach categories."""
    approaches = results['classification_approaches']['approach_categories']
    
    # Prepare data
    categories = list(approaches.keys())
    counts = [len(approaches[cat]) for cat in categories]
    
    # Clean up category names
    clean_names = [cat.replace('_', ' ').title() for cat in categories]
    
    # Create horizontal bar chart
    bars = ax.barh(range(len(categories)), counts, alpha=0.8)
    
    # Color bars
    colors = plt.cm.viridis(np.linspace(0, 1, len(bars)))
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    # Customize
    ax.set_yticks(range(len(categories)))
    ax.set_yticklabels(clean_names)
    ax.set_xlabel('Number of Genome Types', fontsize=12)
    ax.set_title('Classification Approach Categories', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                str(count), va='center', fontsize=10)


def plot_family_sizes(ax, results):
    """Plot family sizes by genome type."""
    family_data = results['family_size_patterns']['family_size_data']
    
    # Prepare data
    genome_types = list(family_data.keys())
    avg_sizes = [family_data[gt]['avg_size'] for gt in genome_types]
    
    # Create bar plot
    bars = ax.bar(range(len(genome_types)), avg_sizes, alpha=0.8)
    
    # Color bars by size
    colors = plt.cm.plasma(np.array(avg_sizes) / max(avg_sizes))
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    # Customize
    ax.set_xticks(range(len(genome_types)))
    ax.set_xticklabels(genome_types, rotation=45, ha='right')
    ax.set_ylabel('Average Family Size', fontsize=12)
    ax.set_title('Family Size by Genome Type', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, size in zip(bars, avg_sizes):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                str(size), ha='center', va='bottom', fontsize=10)


def plot_baltimore_evolution(ax, results):
    """Plot Baltimore classification group evolution."""
    evolution = results['genome_evolution']['baltimore_group_evolution']['dna_rna_evolution']
    
    # Prepare data
    years = sorted([int(year) for year in evolution.keys()])
    dna_props = [evolution[str(year)]['dna_proportion'] for year in years]
    rna_props = [evolution[str(year)]['rna_proportion'] for year in years]
    
    # Plot lines
    ax.plot(years, dna_props, 'o-', linewidth=3, markersize=8, label='DNA Viruses', color='#1f77b4')
    ax.plot(years, rna_props, 's-', linewidth=3, markersize=8, label='RNA Viruses', color='#ff7f0e')
    
    # Fill areas
    ax.fill_between(years, dna_props, alpha=0.3, color='#1f77b4')
    ax.fill_between(years, rna_props, alpha=0.3, color='#ff7f0e')
    
    # Customize
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Proportion (%)', fontsize=12)
    ax.set_title('DNA vs RNA Virus Evolution', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 100)


def plot_discovery_bias(ax, results):
    """Plot discovery bias by technology era."""
    bias_data = results['discovery_bias']['technology_bias']
    
    # Create timeline
    eras = ['electron_microscopy_era', 'serological_era', 'pcr_era', 'ngs_era', 'metagenomics_era']
    y_positions = range(len(eras))
    
    # Plot era blocks
    colors = ['#ff9999', '#99ccff', '#99ff99', '#ffcc99', '#cc99ff']
    
    for i, era in enumerate(eras):
        # Era block
        rect = Rectangle((0, i-0.4), 1, 0.8, facecolor=colors[i], alpha=0.7, edgecolor='black')
        ax.add_patch(rect)
        
        # Era label
        period = bias_data[era]['period']
        favored = ', '.join(bias_data[era]['favored'])
        
        ax.text(0.5, i, f"{era.replace('_', ' ').title()}\n{period}\nFavors: {favored}", 
                ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Customize
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.5, len(eras)-0.5)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_title('Technology Era Discovery Bias', fontsize=14, fontweight='bold')
    
    # Add timeline arrow
    ax.annotate('', xy=(1, len(eras)), xytext=(1, -1),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(1.05, len(eras)/2, 'Time →', rotation=90, ha='center', va='center', fontsize=12)


def plot_taxonomic_complexity(ax, results):
    """Plot taxonomic complexity by genome type."""
    complexity = results['classification_approaches']['method_complexity']
    
    # Prepare data
    genome_types = list(complexity.keys())
    scores = [complexity[gt]['score'] for gt in genome_types]
    complexity_levels = [complexity[gt]['complexity'] for gt in genome_types]
    
    # Color mapping
    color_map = {'low': '#2ca02c', 'medium': '#ff7f0e', 'high': '#d62728'}
    colors = [color_map[level] for level in complexity_levels]
    
    # Create scatter plot
    scatter = ax.scatter(range(len(genome_types)), scores, c=colors, s=150, alpha=0.8)
    
    # Add complexity level labels
    for i, (gt, score, level) in enumerate(zip(genome_types, scores, complexity_levels)):
        ax.annotate(f'{gt}\n({level})', (i, score), xytext=(0, 10), 
                   textcoords='offset points', ha='center', fontsize=9)
    
    # Customize
    ax.set_xticks(range(len(genome_types)))
    ax.set_xticklabels(genome_types, rotation=45, ha='right')
    ax.set_ylabel('Complexity Score', fontsize=12)
    ax.set_title('Classification Method Complexity', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Add legend
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color_map[level], 
                                 markersize=10, label=level.title()) for level in ['low', 'medium', 'high']]
    ax.legend(handles=legend_elements, title='Complexity Level')


def plot_growth_rates(ax, results):
    """Plot growth rates by genome type."""
    growth_rates = results['genome_distributions']['growth_rates']
    
    # Prepare data
    genome_types = list(growth_rates.keys())
    annual_rates = [growth_rates[gt]['annual_rate'] for gt in genome_types]
    
    # Create bar plot
    bars = ax.bar(range(len(genome_types)), annual_rates, alpha=0.8)
    
    # Color bars by rate
    colors = plt.cm.coolwarm(np.array(annual_rates) / max(annual_rates))
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    # Customize
    ax.set_xticks(range(len(genome_types)))
    ax.set_xticklabels(genome_types, rotation=45, ha='right')
    ax.set_ylabel('Annual Growth Rate (%)', fontsize=12)
    ax.set_title('Growth Rates by Genome Type', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, rate in zip(bars, annual_rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{rate:.1f}%', ha='center', va='bottom', fontsize=10)


def plot_stability_patterns(ax, results):
    """Plot stability patterns by genome type."""
    stability = results['taxonomic_patterns']['stability_analysis']
    
    # Prepare data
    genome_types = list(stability.keys())
    reclassification_rates = [stability[gt]['reclassification_rate'] * 100 for gt in genome_types]
    stability_levels = [stability[gt]['stability'] for gt in genome_types]
    
    # Color mapping
    stability_colors = {
        'very_high': '#2ca02c',
        'high': '#66b3ff', 
        'moderate': '#ff7f0e',
        'low': '#ff9999',
        'very_low': '#d62728'
    }
    colors = [stability_colors.get(level, '#888888') for level in stability_levels]
    
    # Create horizontal bar chart
    bars = ax.barh(range(len(genome_types)), reclassification_rates, color=colors, alpha=0.8)
    
    # Customize
    ax.set_yticks(range(len(genome_types)))
    ax.set_yticklabels(genome_types)
    ax.set_xlabel('Reclassification Rate (%)', fontsize=12)
    ax.set_title('Taxonomic Stability by Genome Type', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    # Add value labels and stability levels
    for i, (bar, rate, level) in enumerate(zip(bars, reclassification_rates, stability_levels)):
        ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                f'{rate:.1f}% ({level.replace("_", " ")})', va='center', fontsize=9)


def plot_key_findings(ax, results):
    """Plot key findings summary."""
    findings = results.get('key_findings', [])
    
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.95, 'Key Findings', fontsize=16, fontweight='bold',
            ha='center', va='top', transform=ax.transAxes)
    
    # Findings
    y_pos = 0.85
    for i, finding in enumerate(findings[:4], 1):
        # Finding title
        ax.text(0.05, y_pos, f"{i}. {finding['finding']}", fontsize=12, fontweight='bold',
                ha='left', va='top', transform=ax.transAxes, wrap=True)
        y_pos -= 0.08
        
        # Detail
        ax.text(0.1, y_pos, f"• {finding['detail']}", fontsize=10,
                ha='left', va='top', transform=ax.transAxes, wrap=True)
        y_pos -= 0.06
        
        # Implication
        ax.text(0.1, y_pos, f"→ {finding['implication']}", fontsize=10, style='italic',
                ha='left', va='top', transform=ax.transAxes, wrap=True, color='#666666')
        y_pos -= 0.10


def create_baltimore_classification_plot(results, output_dir):
    """Create detailed Baltimore classification visualization."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Baltimore group counts
    historical = results['genome_distributions']['historical_counts']
    baltimore_map = {
        'dsDNA': 'I', 'ssDNA': 'II', 'dsRNA': 'III', 'ssRNA(+)': 'IV',
        'ssRNA(-)': 'V', 'ssRNA-RT': 'VI', 'dsDNA-RT': 'VII'
    }
    
    # Plot 1: Current distribution by Baltimore group
    latest_year = max(int(year) for year in historical.keys())
    latest_data = historical[str(latest_year)]
    
    baltimore_counts = {}
    for genome_type, count in latest_data.items():
        group = baltimore_map[genome_type]
        baltimore_counts[group] = baltimore_counts.get(group, 0) + count
    
    groups = sorted(baltimore_counts.keys())
    counts = [baltimore_counts[g] for g in groups]
    
    wedges, texts, autotexts = ax1.pie(counts, labels=[f'Group {g}' for g in groups], 
                                      autopct='%1.1f%%', startangle=90)
    ax1.set_title(f'Baltimore Classification Groups ({latest_year})', fontsize=14, fontweight='bold')
    
    # Plot 2: DNA vs RNA evolution
    evolution = results['genome_evolution']['baltimore_group_evolution']['dna_rna_evolution']
    years = sorted([int(year) for year in evolution.keys()])
    dna_counts = [evolution[str(year)]['dna_count'] for year in years]
    rna_counts = [evolution[str(year)]['rna_count'] for year in years]
    
    ax2.plot(years, dna_counts, 'o-', linewidth=3, markersize=8, label='DNA Viruses', color='#1f77b4')
    ax2.plot(years, rna_counts, 's-', linewidth=3, markersize=8, label='RNA Viruses', color='#ff7f0e')
    
    ax2.set_xlabel('Year', fontsize=12)
    ax2.set_ylabel('Number of Species', fontsize=12)
    ax2.set_title('DNA vs RNA Virus Discovery', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))
    
    plt.tight_layout()
    
    # Save
    output_path = output_dir / "baltimore_classification_detailed.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Baltimore classification plot saved to: {output_path}")


def create_architecture_constraints_plot(results, output_dir):
    """Create comprehensive architecture constraints visualization."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Genome type complexity matrix
    ax = axes[0, 0]
    complexity = results['classification_approaches']['method_complexity']
    
    genome_types = list(complexity.keys())
    scores = [complexity[gt]['score'] for gt in genome_types]
    
    # Create matrix-style heatmap
    matrix_data = np.array(scores).reshape(1, -1)
    im = ax.imshow(matrix_data, cmap='RdYlBu_r', aspect='auto')
    
    ax.set_xticks(range(len(genome_types)))
    ax.set_xticklabels(genome_types, rotation=45, ha='right')
    ax.set_yticks([])
    ax.set_title('Classification Complexity Scores')
    
    # Add score labels
    for i, score in enumerate(scores):
        ax.text(i, 0, str(score), ha='center', va='center', fontweight='bold')
    
    # 2. Family size distribution
    ax = axes[0, 1]
    family_data = results['family_size_patterns']['family_size_data']
    
    # Stacked bar chart of family size categories
    small = [family_data[gt]['small_families'] for gt in genome_types]
    medium = [family_data[gt]['medium_families'] for gt in genome_types]
    large = [family_data[gt]['large_families'] for gt in genome_types]
    
    x = range(len(genome_types))
    ax.bar(x, small, label='Small (<50)', color='#2ca02c', alpha=0.8)
    ax.bar(x, medium, bottom=small, label='Medium (50-200)', color='#ff7f0e', alpha=0.8)
    ax.bar(x, large, bottom=np.array(small)+np.array(medium), label='Large (>200)', color='#d62728', alpha=0.8)
    
    ax.set_xticks(x)
    ax.set_xticklabels(genome_types, rotation=45, ha='right')
    ax.set_ylabel('Number of Families')
    ax.set_title('Family Size Distribution by Genome Type')
    ax.legend()
    
    # 3. Discovery rate comparison
    ax = axes[1, 0]
    discovery = results['discovery_bias']['current_discovery_rates']
    
    rates = ['very_low', 'low', 'medium', 'high', 'very_high']
    rate_counts = {rate: 0 for rate in rates}
    
    for gt, data in discovery.items():
        rate = data['rate']
        rate_counts[rate] += 1
    
    ax.bar(range(len(rates)), [rate_counts[r] for r in rates], 
           color=plt.cm.viridis(np.linspace(0, 1, len(rates))), alpha=0.8)
    ax.set_xticks(range(len(rates)))
    ax.set_xticklabels([r.replace('_', ' ').title() for r in rates])
    ax.set_ylabel('Number of Genome Types')
    ax.set_title('Current Discovery Rate Distribution')
    
    # 4. Summary statistics
    ax = axes[1, 1]
    ax.axis('off')
    
    # Calculate key statistics
    total_species = sum(results['genome_distributions']['historical_counts']['2024'].values())
    dominant_type = max(results['genome_distributions']['historical_counts']['2024'].items(), 
                       key=lambda x: x[1])
    
    summary_text = f"""Architecture Constraints Summary:
    
• Total species analyzed: {total_species:,}
• Dominant genome type: {dominant_type[0]} ({dominant_type[1]:,} species)
• Baltimore groups represented: 7
• Classification approaches: 5 distinct categories
• Family size range: 28-150 species average
• Stability correlation: Inverse to mutation rate
• Discovery bias: Strongly favors dsDNA (metagenomics)
• Technology impact: Drives genome type preferences

Key insight: Genome architecture fundamentally 
constrains taxonomic organization and discovery."""
    
    ax.text(0.1, 0.9, summary_text, transform=ax.transAxes, fontsize=12,
            verticalalignment='top', family='monospace')
    
    plt.suptitle('Comprehensive Genome Architecture Constraints', fontsize=18, fontweight='bold')
    plt.tight_layout()
    
    # Save
    output_path = output_dir / "architecture_constraints_comprehensive.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Architecture constraints plot saved to: {output_path}")


if __name__ == "__main__":
    create_genome_architecture_visualizations()