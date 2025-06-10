"""Visualizations for Discovery Bias Analysis"""

import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches


def create_discovery_bias_visualizations():
    """Create all visualizations for discovery bias analysis."""
    # Load results - check multiple possible paths
    possible_paths = [
        Path(__file__).parent / "results" / "DiscoveryBiasAnalyzer_results.json",
        Path(__file__).parent.parent / "discoverybiasanalyzer" / "results" / "DiscoveryBiasAnalyzer_results.json"
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
    
    # 1. Families by Era Timeline
    ax1 = plt.subplot(3, 3, 1)
    plot_families_by_era(ax1, results)
    
    # 2. Classification Methods Evolution
    ax2 = plt.subplot(3, 3, 2)
    plot_method_evolution(ax2, results)
    
    # 3. Stability Patterns by Era
    ax3 = plt.subplot(3, 3, 3)
    plot_stability_by_era(ax3, results)
    
    # 4. Growth Rates by Era
    ax4 = plt.subplot(3, 3, 4)
    plot_growth_rates(ax4, results)
    
    # 5. Species Characteristics
    ax5 = plt.subplot(3, 3, 5)
    plot_species_characteristics(ax5, results)
    
    # 6. Technology Timeline
    ax6 = plt.subplot(3, 3, 6)
    plot_technology_timeline(ax6, results)
    
    # 7. Host Diversity by Era
    ax7 = plt.subplot(3, 3, 7)
    plot_host_diversity(ax7, results)
    
    # 8. Discovery Accumulation
    ax8 = plt.subplot(3, 3, 8)
    plot_discovery_accumulation(ax8, results)
    
    # 9. Key Findings Summary
    ax9 = plt.subplot(3, 3, 9)
    plot_key_findings(ax9, results)
    
    plt.suptitle('Discovery Bias Analysis: How Technology Eras Shape Viral Taxonomy', 
                 fontsize=24, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    
    # Save the figure
    output_path = output_dir / "discovery_bias_analysis_figure.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nFigure saved to: {output_path}")
    
    # Also save as PDF for publication
    pdf_path = output_dir / "discovery_bias_analysis_figure.pdf"
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
    print(f"PDF saved to: {pdf_path}")
    
    plt.close()
    
    # Create additional detailed plots
    create_detailed_timeline_plot(results, output_dir)
    create_era_comparison_plot(results, output_dir)


def plot_families_by_era(ax, results):
    """Plot families discovered by era."""
    families_by_era = results['families_by_era']
    eras = results['technology_eras']
    
    # Prepare data
    era_names = []
    family_counts = []
    era_years = []
    
    era_order = ['pre_sequencing', 'early_sequencing', 'genomics', 'high_throughput', 'ai_metagenomics']
    
    for era in era_order:
        if era in families_by_era:
            era_info = eras[era]
            era_names.append(era.replace('_', ' ').title())
            family_counts.append(len(families_by_era[era]))
            era_years.append(f"{era_info['years'][0]}-{era_info['years'][1]}")
    
    # Create bar plot
    bars = ax.bar(range(len(era_names)), family_counts, alpha=0.8)
    
    # Color bars by era
    colors = plt.cm.viridis(np.linspace(0, 1, len(bars)))
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    # Customize
    ax.set_xticks(range(len(era_names)))
    ax.set_xticklabels([f"{name}\n{years}" for name, years in zip(era_names, era_years)], 
                       rotation=45, ha='right')
    ax.set_ylabel('Number of Families', fontsize=12)
    ax.set_title('Viral Families by Discovery Era', fontsize=14, fontweight='bold')
    
    # Add value labels
    for i, (bar, count) in enumerate(zip(bars, family_counts)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                str(count), ha='center', va='bottom', fontsize=10)
    
    ax.grid(axis='y', alpha=0.3)


def plot_method_evolution(ax, results):
    """Plot evolution of classification methods by era."""
    method_data = results['classification_methods']['proportions']
    
    if not method_data:
        ax.text(0.5, 0.5, 'No method data available', ha='center', va='center')
        return
    
    # Prepare data for stacked bar chart
    eras = ['pre_sequencing', 'early_sequencing', 'genomics', 'high_throughput', 'ai_metagenomics']
    methods = ['morphology_based', 'serology_to_genomics', 'mixed_methods', 'genomics_primary', 'genomics_only']
    method_colors = {
        'morphology_based': '#ff7f0e',
        'serology_to_genomics': '#2ca02c', 
        'mixed_methods': '#d62728',
        'genomics_primary': '#9467bd',
        'genomics_only': '#1f77b4'
    }
    
    # Create data matrix
    data_matrix = []
    for era in eras:
        if era in method_data:
            row = []
            for method in methods:
                row.append(method_data[era].get(method, 0))
            data_matrix.append(row)
        else:
            data_matrix.append([0] * len(methods))
    
    # Create stacked bar chart
    bottom = np.zeros(len(eras))
    for i, method in enumerate(methods):
        values = [row[i] for row in data_matrix]
        ax.bar(range(len(eras)), values, bottom=bottom, 
               label=method.replace('_', ' ').title(),
               color=method_colors.get(method, f'C{i}'))
        bottom += values
    
    # Customize
    ax.set_xticks(range(len(eras)))
    ax.set_xticklabels([era.replace('_', ' ').title() for era in eras], rotation=45, ha='right')
    ax.set_ylabel('Proportion of Families', fontsize=12)
    ax.set_title('Classification Method Evolution', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax.set_ylim(0, 1)


def plot_stability_by_era(ax, results):
    """Plot stability patterns by discovery era."""
    stability_data = results['stability_patterns']
    
    # Prepare data
    eras = []
    stability_rates = []
    reorganization_rates = []
    
    era_order = ['pre_sequencing', 'early_sequencing', 'genomics', 'high_throughput', 'ai_metagenomics']
    
    for era in era_order:
        if era in stability_data:
            data = stability_data[era]
            if data['total_families'] > 0:
                eras.append(era.replace('_', ' ').title())
                stability_rates.append(data['stability_rate'] * 100)
                reorg_rate = (data['reorganized_families'] + data['split_families']) / data['total_families'] * 100
                reorganization_rates.append(reorg_rate)
    
    # Create grouped bar chart
    x = np.arange(len(eras))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, stability_rates, width, label='Stable', color='#2ca02c', alpha=0.8)
    bars2 = ax.bar(x + width/2, reorganization_rates, width, label='Reorganized/Split', color='#d62728', alpha=0.8)
    
    # Customize
    ax.set_xlabel('Discovery Era', fontsize=12)
    ax.set_ylabel('Percentage of Families (%)', fontsize=12)
    ax.set_title('Taxonomic Stability by Discovery Era', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(eras, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 1,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=9)


def plot_growth_rates(ax, results):
    """Plot growth rates by era."""
    growth_data = results['growth_patterns']['growth_rates']
    
    if not growth_data:
        ax.text(0.5, 0.5, 'No growth data available', ha='center', va='center')
        return
    
    # Prepare data
    eras = []
    growth_rates = []
    
    for era, data in growth_data.items():
        eras.append(era.replace('_', ' ').title())
        growth_rates.append(data['annual_growth_rate'])
    
    # Create bar plot
    bars = ax.bar(range(len(eras)), growth_rates, alpha=0.8, color='#9467bd')
    
    # Customize
    ax.set_xticks(range(len(eras)))
    ax.set_xticklabels(eras, rotation=45, ha='right')
    ax.set_ylabel('Annual Growth Rate (%)', fontsize=12)
    ax.set_title('Species Growth Rates by Family Era', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar, rate in zip(bars, growth_rates):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                f'{rate:.1f}%', ha='center', va='bottom', fontsize=10)


def plot_species_characteristics(ax, results):
    """Plot species characteristics by era."""
    species_data = results['species_characteristics']
    
    # Focus on average species per genus
    eras = []
    avg_species = []
    
    era_order = ['pre_sequencing', 'early_sequencing', 'genomics', 'high_throughput', 'ai_metagenomics']
    
    for era in era_order:
        if era in species_data and 'avg_species_per_genus' in species_data[era]:
            eras.append(era.replace('_', ' ').title())
            avg_species.append(species_data[era]['avg_species_per_genus'])
    
    # Create line plot
    ax.plot(range(len(eras)), avg_species, marker='o', markersize=10, linewidth=3, color='#ff7f0e')
    
    # Customize
    ax.set_xticks(range(len(eras)))
    ax.set_xticklabels(eras, rotation=45, ha='right')
    ax.set_ylabel('Average Species per Genus', fontsize=12)
    ax.set_title('Genus Size Evolution by Era', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Add value labels
    for i, (x, y) in enumerate(zip(range(len(eras)), avg_species)):
        ax.text(x, y + 0.2, f'{y:.1f}', ha='center', va='bottom', fontsize=10)


def plot_technology_timeline(ax, results):
    """Plot technology timeline with key innovations."""
    eras = results['technology_eras']
    
    # Create timeline
    y_pos = 0
    colors = plt.cm.plasma(np.linspace(0, 1, len(eras)))
    
    for i, (era, info) in enumerate(eras.items()):
        start_year = info['years'][0]
        end_year = info['years'][1]
        duration = end_year - start_year
        
        # Draw era bar
        rect = Rectangle((start_year, y_pos - 0.4), duration, 0.8,
                        facecolor=colors[i], alpha=0.7, edgecolor='black')
        ax.add_patch(rect)
        
        # Add era label
        ax.text(start_year + duration/2, y_pos, era.replace('_', ' ').title(),
                ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Add key technologies
        tech_text = ', '.join(info['key_technologies'][:2])
        ax.text(start_year + duration/2, y_pos - 0.6, tech_text,
                ha='center', va='top', fontsize=8, style='italic')
        
        y_pos += 1
    
    # Customize
    ax.set_xlim(1900, 2030)
    ax.set_ylim(-1, len(eras))
    ax.set_xlabel('Year', fontsize=12)
    ax.set_title('Technology Eras in Viral Discovery', fontsize=14, fontweight='bold')
    ax.set_yticks([])
    ax.grid(axis='x', alpha=0.3)


def plot_host_diversity(ax, results):
    """Plot host diversity by era."""
    species_data = results['species_characteristics']
    
    # Prepare data
    eras = []
    host_categories = ['bacteria', 'plants', 'vertebrates', 'other']
    host_data = {cat: [] for cat in host_categories}
    
    era_order = ['pre_sequencing', 'early_sequencing', 'genomics', 'high_throughput', 'ai_metagenomics']
    
    for era in era_order:
        if era in species_data and 'host_diversity' in species_data[era]:
            hosts = species_data[era]['host_diversity']
            if hosts:  # Only include if there's data
                eras.append(era.replace('_', ' ').title())
                total = sum(hosts.values())
                for cat in host_categories:
                    proportion = hosts.get(cat, 0) / total if total > 0 else 0
                    host_data[cat].append(proportion)
    
    if not eras:
        ax.text(0.5, 0.5, 'No host diversity data available', ha='center', va='center')
        return
    
    # Create stacked area chart
    x = range(len(eras))
    bottom = np.zeros(len(eras))
    
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728']
    for cat, color in zip(host_categories, colors):
        ax.bar(x, host_data[cat], bottom=bottom, label=cat.title(), 
               color=color, alpha=0.8, width=0.6)
        bottom += host_data[cat]
    
    # Customize
    ax.set_xticks(x)
    ax.set_xticklabels(eras, rotation=45, ha='right')
    ax.set_ylabel('Proportion of Species', fontsize=12)
    ax.set_title('Host Diversity by Discovery Era', fontsize=14, fontweight='bold')
    ax.legend(loc='upper right')
    ax.set_ylim(0, 1)


def plot_discovery_accumulation(ax, results):
    """Plot cumulative discovery accumulation by era."""
    growth_data = results['growth_patterns']['time_series']
    
    # Prepare cumulative data by era
    era_colors = {
        'pre_sequencing': '#ff7f0e',
        'early_sequencing': '#2ca02c',
        'genomics': '#d62728',
        'high_throughput': '#9467bd',
        'ai_metagenomics': '#1f77b4'
    }
    
    for era, color in era_colors.items():
        if era in growth_data:
            data = growth_data[era]
            years = [point['year'] for point in data]
            species = [point['total_species'] for point in data]
            
            if years and species:
                ax.plot(years, species, marker='o', label=era.replace('_', ' ').title(),
                       color=color, linewidth=2, markersize=6)
    
    # Customize
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Total Species Count', fontsize=12)
    ax.set_title('Species Accumulation by Family Discovery Era', fontsize=14, fontweight='bold')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(2000, 2025)


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


def create_detailed_timeline_plot(results, output_dir):
    """Create a detailed timeline plot showing family introductions."""
    families_by_era = results['families_by_era']
    eras = results['technology_eras']
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    # Set up timeline
    min_year = 1900
    max_year = 2030
    
    # Draw era backgrounds
    for era, info in eras.items():
        start = info['years'][0]
        end = info['years'][1]
        
        # Era background
        ax.axvspan(start, end, alpha=0.2, label=era.replace('_', ' ').title())
        
        # Era label
        ax.text((start + end) / 2, 0.95, era.replace('_', ' ').title(),
                transform=ax.get_xaxis_transform(), ha='center', va='top',
                fontsize=12, fontweight='bold')
    
    # Plot family counts over time
    years = []
    counts = []
    
    for year in range(min_year, max_year + 1):
        era = None
        for e, info in eras.items():
            if info['years'][0] <= year <= info['years'][1]:
                era = e
                break
        
        if era and era in families_by_era:
            # Simple approximation: distribute families evenly across era
            era_info = eras[era]
            era_duration = era_info['years'][1] - era_info['years'][0] + 1
            annual_rate = len(families_by_era[era]) / era_duration
            
            years.append(year)
            counts.append(annual_rate)
    
    # Plot
    ax.bar(years, counts, width=1, alpha=0.7, color='darkblue')
    
    # Customize
    ax.set_xlim(min_year, max_year)
    ax.set_xlabel('Year', fontsize=14)
    ax.set_ylabel('Families Introduced (Annual Rate)', fontsize=14)
    ax.set_title('Viral Family Discovery Timeline by Technology Era', fontsize=18, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Save
    output_path = output_dir / "discovery_timeline_detailed.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Detailed timeline saved to: {output_path}")


def create_era_comparison_plot(results, output_dir):
    """Create a comprehensive era comparison plot."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Family count comparison
    ax = axes[0, 0]
    families_by_era = results['families_by_era']
    eras = list(families_by_era.keys())
    counts = [len(families_by_era[era]) for era in eras]
    
    ax.bar(range(len(eras)), counts, color=plt.cm.viridis(np.linspace(0, 1, len(eras))))
    ax.set_xticks(range(len(eras)))
    ax.set_xticklabels([era.replace('_', ' ').title() for era in eras], rotation=45)
    ax.set_ylabel('Number of Families')
    ax.set_title('Families per Era')
    
    # 2. Stability comparison
    ax = axes[0, 1]
    stability_data = results['stability_patterns']
    eras_with_data = [era for era in eras if era in stability_data]
    stability_rates = [stability_data[era]['stability_rate'] * 100 for era in eras_with_data]
    
    ax.plot(range(len(eras_with_data)), stability_rates, 'o-', markersize=10, linewidth=3)
    ax.set_xticks(range(len(eras_with_data)))
    ax.set_xticklabels([era.replace('_', ' ').title() for era in eras_with_data], rotation=45)
    ax.set_ylabel('Stability Rate (%)')
    ax.set_title('Taxonomic Stability by Era')
    ax.grid(True, alpha=0.3)
    
    # 3. Growth rate comparison
    ax = axes[1, 0]
    growth_data = results['growth_patterns']['growth_rates']
    if growth_data:
        eras_growth = list(growth_data.keys())
        rates = [growth_data[era]['annual_growth_rate'] for era in eras_growth]
        
        bars = ax.bar(range(len(eras_growth)), rates, color=plt.cm.plasma(np.linspace(0, 1, len(eras_growth))))
        ax.set_xticks(range(len(eras_growth)))
        ax.set_xticklabels([era.replace('_', ' ').title() for era in eras_growth], rotation=45)
        ax.set_ylabel('Annual Growth Rate (%)')
        ax.set_title('Species Growth Rates by Era')
    
    # 4. Summary statistics
    ax = axes[1, 1]
    ax.axis('off')
    
    summary_text = "Era Impact Summary:\n\n"
    
    # Calculate key statistics
    total_families = sum(len(families_by_era[era]) for era in families_by_era)
    modern_families = len(families_by_era.get('high_throughput', [])) + len(families_by_era.get('ai_metagenomics', []))
    
    summary_text += f"• Total families analyzed: {total_families}\n"
    summary_text += f"• Modern era families (2010+): {modern_families} ({modern_families/total_families*100:.1f}%)\n"
    summary_text += f"• Clear shift to genomics-based methods\n"
    summary_text += f"• Newer families show higher growth rates\n"
    summary_text += f"• Technology drives classification philosophy\n"
    
    ax.text(0.1, 0.9, summary_text, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', family='monospace')
    
    plt.suptitle('Comprehensive Era Comparison', fontsize=18, fontweight='bold')
    plt.tight_layout()
    
    # Save
    output_path = output_dir / "era_comparison_comprehensive.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Era comparison saved to: {output_path}")


if __name__ == "__main__":
    create_discovery_bias_visualizations()