"""
Visualization functions for Species Boundary Evolution Analysis.

Creates publication-quality figures showing:
1. Method evolution timeline
2. Threshold changes over time
3. Technology adoption patterns
4. Family-specific evolution tracks
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import json
from pathlib import Path
from typing import Dict, List
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import pandas as pd

def create_species_boundary_evolution_figure(results: Dict) -> None:
    """Create comprehensive figure showing species boundary evolution."""
    
    # Set up the figure with subplots
    fig = plt.figure(figsize=(16, 12))
    
    # Create a grid layout
    gs = fig.add_gridspec(3, 2, height_ratios=[1.5, 1, 1], hspace=0.3, wspace=0.3)
    
    # 1. Timeline of method evolution (top panel, spanning both columns)
    ax1 = fig.add_subplot(gs[0, :])
    create_method_timeline(ax1, results)
    
    # 2. Method distribution by era (bottom left)
    ax2 = fig.add_subplot(gs[1, 0])
    create_method_distribution(ax2, results)
    
    # 3. Threshold evolution (bottom right)
    ax3 = fig.add_subplot(gs[1, 1])
    create_threshold_evolution(ax3, results)
    
    # 4. Technology adoption timeline (bottom left)
    ax4 = fig.add_subplot(gs[2, 0])
    create_technology_timeline(ax4, results)
    
    # 5. Transition flow diagram (bottom right)
    ax5 = fig.add_subplot(gs[2, 1])
    create_transition_summary(ax5, results)
    
    # Main title
    fig.suptitle("Evolution of Viral Species Demarcation Criteria (2005-2024)", 
                 fontsize=18, fontweight='bold')
    
    plt.tight_layout()
    
    # Save figure
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "species_boundary_evolution_figure.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Figure saved to: {output_file}")
    
    # Also save as PDF
    pdf_file = output_dir / "species_boundary_evolution_figure.pdf"
    plt.savefig(pdf_file, format='pdf', bbox_inches='tight')
    print(f"PDF version saved to: {pdf_file}")
    
    plt.close()

def create_method_timeline(ax, results):
    """Create timeline showing method evolution for each family."""
    
    # Extract timeline data
    timeline_data = results.get('visualization_data', {}).get('timeline_data', [])
    boundary_evolution = results.get('boundary_evolution', {})
    
    # Define method colors
    method_colors = {
        'morphological': '#8B4513',  # Brown
        'serological': '#FF6B6B',    # Light red
        'mixed': '#FFA500',          # Orange
        'genomic': '#4ECDC4',        # Teal
        'phylogenetic': '#1E90FF',   # Blue
        'DISCONTINUED': '#808080'     # Gray
    }
    
    # Create timeline for each family
    families = sorted(boundary_evolution.keys())
    y_positions = {family: i for i, family in enumerate(families)}
    
    # Plot evolution lines
    for family in families:
        history = boundary_evolution[family]
        y_pos = y_positions[family]
        
        # Plot line segments between transitions
        for i in range(len(history)):
            criteria = history[i]
            year = criteria['year']
            method = criteria['method']
            color = method_colors.get(method, '#666666')
            
            # Draw point
            ax.scatter(year, y_pos, c=color, s=100, zorder=3, edgecolors='black', linewidth=1)
            
            # Draw line to next point
            if i < len(history) - 1:
                next_year = history[i + 1]['year']
                ax.plot([year, next_year], [y_pos, y_pos], c=color, linewidth=2, alpha=0.7)
            else:
                # Extend to 2024
                ax.plot([year, 2024], [y_pos, y_pos], c=color, linewidth=2, alpha=0.7)
            
            # Add threshold annotation for significant changes
            if i > 0 and 'threshold' in criteria:
                if '%' in criteria['threshold'] and '%' in history[i-1]['threshold']:
                    try:
                        curr = int(criteria['threshold'].split('%')[0].split()[-1])
                        prev = int(history[i-1]['threshold'].split('%')[0].split()[-1])
                        if abs(curr - prev) >= 5:
                            ax.text(year, y_pos + 0.1, f"{prev}%→{curr}%", 
                                   fontsize=8, ha='center', va='bottom')
                    except:
                        pass
    
    # Customize plot
    ax.set_yticks(range(len(families)))
    ax.set_yticklabels(families)
    ax.set_xlabel("Year", fontsize=12)
    ax.set_title("Species Demarcation Method Evolution by Family", fontsize=14)
    ax.set_xlim(2004, 2025)
    ax.grid(True, axis='x', alpha=0.3)
    
    # Add vertical lines for major events
    ax.axvline(x=2019, color='red', linestyle='--', alpha=0.5, linewidth=2)
    ax.text(2019, len(families)-0.5, "Caudovirales\nDissolution", 
            ha='center', va='top', color='red', fontsize=10)
    
    ax.axvline(x=2020, color='orange', linestyle='--', alpha=0.5, linewidth=2)
    ax.text(2020, len(families)-1.5, "COVID-19", 
            ha='center', va='top', color='orange', fontsize=10)
    
    # Create legend
    legend_elements = [mpatches.Patch(color=color, label=method.capitalize()) 
                      for method, color in method_colors.items()]
    ax.legend(handles=legend_elements, loc='upper left', ncol=3, fontsize=10)

def create_method_distribution(ax, results):
    """Create stacked bar chart showing method distribution by era."""
    
    methods_by_era = results.get('methods_by_era', {})
    
    # Prepare data for stacked bar chart
    eras = list(methods_by_era.keys())
    all_methods = set()
    for methods in methods_by_era.values():
        all_methods.update(methods.keys())
    
    method_colors = {
        'morphological': '#8B4513',
        'serological': '#FF6B6B',
        'mixed': '#FFA500',
        'genomic': '#4ECDC4',
        'phylogenetic': '#1E90FF',
        'DISCONTINUED': '#808080'
    }
    
    # Create data matrix
    data = []
    for method in sorted(all_methods):
        method_counts = [methods_by_era[era].get(method, 0) for era in eras]
        data.append(method_counts)
    
    # Create stacked bar chart
    bottoms = np.zeros(len(eras))
    for i, method in enumerate(sorted(all_methods)):
        color = method_colors.get(method, '#666666')
        ax.bar(range(len(eras)), data[i], bottom=bottoms, 
               label=method.capitalize(), color=color, alpha=0.8)
        bottoms += data[i]
    
    # Customize plot
    ax.set_xticks(range(len(eras)))
    ax.set_xticklabels([era.replace('-', '-\n') for era in eras], fontsize=10)
    ax.set_ylabel("Number of Families", fontsize=12)
    ax.set_title("Classification Methods by Era", fontsize=14)
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, axis='y', alpha=0.3)

def create_threshold_evolution(ax, results):
    """Create plot showing threshold changes over time."""
    
    threshold_patterns = results.get('threshold_patterns', {})
    
    # Extract families with threshold changes
    increasing = threshold_patterns.get('increasing_stringency', [])
    stable = threshold_patterns.get('stable_thresholds', [])
    
    # Create scatter plot with annotations
    y_pos = 0
    colors = {'increasing': '#E74C3C', 'stable': '#2ECC71', 'decreasing': '#3498DB'}
    
    for pattern_type, families in [('increasing', increasing), ('stable', stable)]:
        for family_info in families:
            if 'change' in family_info:
                # Parse the change
                change_text = family_info['change']
                family = family_info['family']
                
                # Plot arrow for changes
                if '→' in change_text:
                    start, end = change_text.split('→')
                    start_val = int(start.strip().rstrip('%'))
                    end_val = int(end.strip().rstrip('%'))
                    
                    ax.annotate('', xy=(2024, end_val), xytext=(2005, start_val),
                               arrowprops=dict(arrowstyle='->', color=colors[pattern_type], 
                                             lw=2, alpha=0.7))
                    ax.text(2014.5, (start_val + end_val) / 2, family, 
                           fontsize=9, ha='center', va='bottom', rotation=15)
                
            elif 'value' in family_info:
                # Stable threshold
                value = int(family_info['value'].rstrip('%'))
                ax.plot([2005, 2024], [value, value], color=colors[pattern_type], 
                       lw=2, alpha=0.7)
                ax.text(2014.5, value + 1, family_info['family'], 
                       fontsize=9, ha='center', va='bottom')
    
    # Customize plot
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Identity Threshold (%)", fontsize=12)
    ax.set_title("Evolution of Identity Thresholds", fontsize=14)
    ax.set_xlim(2004, 2025)
    ax.set_ylim(60, 100)
    ax.grid(True, alpha=0.3)
    
    # Add legend
    legend_elements = [
        mpatches.Patch(color=colors['increasing'], label='Increasing stringency'),
        mpatches.Patch(color=colors['stable'], label='Stable threshold')
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=10)

def create_technology_timeline(ax, results):
    """Create timeline showing technology adoption."""
    
    evolution_patterns = results.get('evolution_patterns', {})
    tech_impacts = evolution_patterns.get('technology_impacts', [])
    
    # Create timeline
    y_positions = []
    for i, tech in enumerate(tech_impacts):
        y_pos = i * 0.3
        y_positions.append(y_pos)
        
        # Parse year range
        year_range = tech['adoption_year']
        if '-' in year_range:
            start, end = year_range.split('-')
            start_year = int(start)
            end_year = int(end)
        else:
            start_year = end_year = int(year_range)
        
        # Draw timeline bar
        ax.barh(y_pos, end_year - start_year, left=start_year, height=0.2, 
                alpha=0.7, color=['#3498DB', '#2ECC71', '#E74C3C'][i])
        
        # Add technology name
        ax.text(start_year - 1, y_pos, tech['technology'], 
                fontsize=10, ha='right', va='center')
        
        # Add impact description
        ax.text((start_year + end_year) / 2, y_pos - 0.15, 
                tech['impact'][:40] + '...', 
                fontsize=8, ha='center', va='top', style='italic')
    
    # Customize plot
    ax.set_xlim(2004, 2025)
    ax.set_ylim(-0.5, len(tech_impacts) * 0.3)
    ax.set_xlabel("Year", fontsize=12)
    ax.set_title("Technology Adoption Timeline", fontsize=14)
    ax.set_yticks([])
    ax.grid(True, axis='x', alpha=0.3)

def create_transition_summary(ax, results):
    """Create summary of method transitions."""
    
    transition_types = results.get('transition_types', {})
    
    # Create bar chart
    transitions = list(transition_types.keys())
    counts = list(transition_types.values())
    
    # Clean up transition names
    clean_names = {
        'phenotype_to_genotype': 'Phenotype → Genotype',
        'genotype_refinement': 'Genotype Refinement',
        'method_abandonment': 'Method Abandonment',
        'multi_marker_adoption': 'Multi-marker Adoption'
    }
    
    y_pos = np.arange(len(transitions))
    colors = ['#E74C3C', '#3498DB', '#95A5A6', '#2ECC71']
    
    bars = ax.barh(y_pos, counts, color=colors, alpha=0.8)
    
    # Add value labels
    for i, (bar, count) in enumerate(zip(bars, counts)):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                str(count), ha='left', va='center', fontsize=10)
    
    # Customize plot
    ax.set_yticks(y_pos)
    ax.set_yticklabels([clean_names.get(t, t) for t in transitions])
    ax.set_xlabel("Number of Transitions", fontsize=12)
    ax.set_title("Types of Method Transitions", fontsize=14)
    ax.grid(True, axis='x', alpha=0.3)
    ax.set_xlim(0, max(counts) * 1.2)

def create_focused_threshold_figure(results: Dict) -> None:
    """Create a focused figure on threshold evolution patterns."""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left panel: Threshold trends by virus type
    boundary_evolution = results.get('boundary_evolution', {})
    
    # Categorize families
    dna_families = ['Poxviridae', 'Herpesviridae', 'Papillomaviridae', 'Geminiviridae']
    rna_families = ['Coronaviridae', 'Picornaviridae', 'Flaviviridae', 'Retroviridae']
    phage_families = ['Siphoviridae', 'Drexlerviridae']
    
    # Extract threshold data
    for category, families, color, marker in [
        ('DNA Viruses', dna_families, '#E74C3C', 'o'),
        ('RNA Viruses', rna_families, '#3498DB', 's'),
        ('Bacteriophages', phage_families, '#2ECC71', '^')
    ]:
        for family in families:
            if family in boundary_evolution:
                history = boundary_evolution[family]
                years = []
                thresholds = []
                
                for criteria in history:
                    if '%' in criteria.get('threshold', ''):
                        try:
                            year = criteria['year']
                            # Extract percentage
                            threshold_text = criteria['threshold']
                            import re
                            match = re.search(r'(\d+)%', threshold_text)
                            if match:
                                threshold = int(match.group(1))
                                years.append(year)
                                thresholds.append(threshold)
                        except:
                            continue
                
                if years and thresholds:
                    ax1.plot(years, thresholds, color=color, marker=marker, 
                            markersize=8, alpha=0.7, linewidth=2, label=family)
    
    ax1.set_xlabel("Year", fontsize=12)
    ax1.set_ylabel("Identity Threshold (%)", fontsize=12)
    ax1.set_title("Threshold Evolution by Virus Type", fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=9)
    
    # Right panel: Method shift summary
    stats = results.get('statistics', {})
    method_2005 = stats.get('method_distribution', {}).get('2005', {})
    method_2024 = stats.get('method_distribution', {}).get('2024', {})
    
    # Create grouped bar chart
    methods = list(set(list(method_2005.keys()) + list(method_2024.keys())))
    x = np.arange(len(methods))
    width = 0.35
    
    counts_2005 = [method_2005.get(m, 0) for m in methods]
    counts_2024 = [method_2024.get(m, 0) for m in methods]
    
    bars1 = ax2.bar(x - width/2, counts_2005, width, label='2005', alpha=0.8)
    bars2 = ax2.bar(x + width/2, counts_2024, width, label='2024', alpha=0.8)
    
    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom')
    
    ax2.set_xlabel("Classification Method", fontsize=12)
    ax2.set_ylabel("Number of Families", fontsize=12)
    ax2.set_title("Shift in Classification Methods", fontsize=14)
    ax2.set_xticks(x)
    ax2.set_xticklabels([m.capitalize() for m in methods], rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    # Save figure
    output_dir = Path(__file__).parent / "results"
    output_file = output_dir / "threshold_evolution_focused.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Focused threshold figure saved to: {output_file}")
    
    plt.close()

def main():
    """Generate all visualizations."""
    # Load results
    possible_paths = [
        Path(__file__).parent / "results" / "SpeciesBoundaryAnalyzer_results.json",
        Path(__file__).parent.parent / "speciesboundaryanalyzer" / "results" / "SpeciesBoundaryAnalyzer_results.json"
    ]
    
    results_file = None
    for path in possible_paths:
        if path.exists():
            results_file = path
            break
    
    if not results_file:
        print("No results file found. Please run the analyzer first.")
        return
    
    with open(results_file, 'r') as f:
        results = json.load(f)
    
    print("Creating species boundary evolution visualizations...")
    
    # Create main comprehensive figure
    create_species_boundary_evolution_figure(results)
    
    # Create focused threshold figure
    create_focused_threshold_figure(results)
    
    print("\nAll visualizations complete!")


if __name__ == "__main__":
    main()