"""Visualizations for Growth Pattern Analysis"""

import json
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches
from scipy.optimize import curve_fit


def create_growth_pattern_visualizations():
    """Create all visualizations for growth pattern analysis."""
    # Load results - check multiple possible paths
    possible_paths = [
        Path(__file__).parent / "results" / "GrowthPatternAnalyzer_results.json",
        Path(__file__).parent.parent / "growthpatternanalyzer" / "results" / "GrowthPatternAnalyzer_results.json"
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
    
    # 1. Growth Trajectory with Phases
    ax1 = plt.subplot(3, 3, 1)
    plot_growth_trajectory(ax1, results)
    
    # 2. Growth Phases Comparison
    ax2 = plt.subplot(3, 3, 2)
    plot_growth_phases(ax2, results)
    
    # 3. Technology Correlation
    ax3 = plt.subplot(3, 3, 3)
    plot_technology_correlation(ax3, results)
    
    # 4. Growth Models Comparison
    ax4 = plt.subplot(3, 3, 4)
    plot_growth_models(ax4, results)
    
    # 5. Annual Additions Pattern
    ax5 = plt.subplot(3, 3, 5)
    plot_annual_additions(ax5, results)
    
    # 6. Future Projections
    ax6 = plt.subplot(3, 3, 6)
    plot_future_projections(ax6, results)
    
    # 7. Family Growth Patterns
    ax7 = plt.subplot(3, 3, 7)
    plot_family_patterns(ax7, results)
    
    # 8. Breakthrough Years
    ax8 = plt.subplot(3, 3, 8)
    plot_breakthrough_years(ax8, results)
    
    # 9. Key Findings Summary
    ax9 = plt.subplot(3, 3, 9)
    plot_key_findings(ax9, results)
    
    plt.suptitle('Growth Pattern Analysis: Exponential Expansion in Viral Discovery', 
                 fontsize=24, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    
    # Save the figure
    output_path = output_dir / "growth_pattern_analysis_figure.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\nFigure saved to: {output_path}")
    
    # Also save as PDF for publication
    pdf_path = output_dir / "growth_pattern_analysis_figure.pdf"
    plt.savefig(pdf_path, format='pdf', bbox_inches='tight')
    print(f"PDF saved to: {pdf_path}")
    
    plt.close()
    
    # Create additional detailed plots
    create_detailed_growth_timeline(results, output_dir)
    create_phase_analysis_plot(results, output_dir)


def plot_growth_trajectory(ax, results):
    """Plot overall growth trajectory with phase annotations."""
    # Extract historical data
    historical = results.get('historical_data', {})
    if not historical:
        # Fallback to embedded data
        years = [2005, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 
                2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
        species = [1950, 2285, 2618, 2841, 3186, 3439, 3707, 4404, 
                  5027, 5766, 6590, 7406, 9110, 10434, 11273, 15049, 
                  21351, 28911]
    else:
        years = historical['years']
        species = historical['total_species']
    
    # Plot main trajectory
    ax.plot(years, species, 'o-', linewidth=3, markersize=8, color='#1f77b4', label='Observed Growth')
    
    # Add phase backgrounds
    phases = results.get('growth_phases', {}).get('phase_definitions', {})
    phase_colors = ['#ffcccc', '#ccffcc', '#ccccff', '#ffffcc', '#ffccff', '#ccffff', '#ffeecc']
    
    for i, (phase_name, phase_info) in enumerate(phases.items()):
        start_year, end_year = phase_info['years']
        color = phase_colors[i % len(phase_colors)]
        ax.axvspan(start_year, end_year, alpha=0.3, color=color, label=phase_name.replace('_', ' ').title())
    
    # Customize
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Total Viral Species', fontsize=12)
    ax.set_title('20-Year Viral Species Growth Trajectory', fontsize=14, fontweight='bold')
    ax.set_xlim(2004, 2025)
    ax.grid(True, alpha=0.3)
    
    # Format y-axis to show thousands
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))
    
    # Add trend annotation
    ax.text(0.05, 0.95, f'Growth: 1,950 → 28,911 species\n1,383% increase over 20 years', 
            transform=ax.transAxes, fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))


def plot_growth_phases(ax, results):
    """Plot growth phases comparison."""
    phase_stats = results.get('growth_phases', {}).get('phase_statistics', {})
    
    if not phase_stats:
        ax.text(0.5, 0.5, 'No phase data available', ha='center', va='center')
        return
    
    # Prepare data
    phases = []
    growth_rates = []
    durations = []
    
    phase_order = ['foundation', 'standardization', 'molecular_revolution', 
                   'reorganization', 'pandemic_response', 'metagenomics_explosion', 'ai_era']
    
    for phase in phase_order:
        if phase in phase_stats:
            stats = phase_stats[phase]
            phases.append(phase.replace('_', ' ').title())
            growth_rates.append(stats['annual_growth_rate'])
            durations.append(stats['duration_years'])
    
    # Create bar plot with duration-weighted colors
    bars = ax.bar(range(len(phases)), growth_rates, alpha=0.8)
    
    # Color bars by growth rate
    colors = plt.cm.plasma(np.linspace(0, 1, len(bars)))
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    # Customize
    ax.set_xticks(range(len(phases)))
    ax.set_xticklabels(phases, rotation=45, ha='right')
    ax.set_ylabel('Annual Growth Rate (%)', fontsize=12)
    ax.set_title('Growth Rate by Technology Era', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for i, (bar, rate) in enumerate(zip(bars, growth_rates)):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{rate:.1f}%', ha='center', va='bottom', fontsize=10)


def plot_technology_correlation(ax, results):
    """Plot technology adoption vs growth correlation."""
    tech_corr = results.get('technology_correlation', {})
    
    if not tech_corr:
        ax.text(0.5, 0.5, 'No technology correlation data', ha='center', va='center')
        return
    
    # Technology adoption scores
    tech_scores = tech_corr.get('technology_adoption_scores', {})
    
    # Historical data for species additions
    years = [2005, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 
            2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    additions = [0, 335, 333, 223, 345, 253, 268, 697, 623, 739, 
                824, 816, 1704, 1324, 839, 3776, 6302, 7560]
    
    tech_values = [tech_scores.get(year, 0.5) for year in years]
    
    # Create dual-axis plot
    ax2 = ax.twinx()
    
    # Plot technology adoption
    line1 = ax.plot(years, tech_values, 'o-', color='#ff7f0e', linewidth=2, 
                   markersize=6, label='Technology Adoption')
    
    # Plot species additions
    line2 = ax2.plot(years, additions, 's-', color='#2ca02c', linewidth=2, 
                    markersize=6, label='Annual Species Additions')
    
    # Customize
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Technology Adoption Score', fontsize=12, color='#ff7f0e')
    ax2.set_ylabel('Annual Species Additions', fontsize=12, color='#2ca02c')
    ax.set_title('Technology Adoption vs Discovery Rate', fontsize=14, fontweight='bold')
    
    # Set y-limits
    ax.set_ylim(0, 1.1)
    ax2.set_ylim(0, max(additions) * 1.1)
    
    # Add correlation info
    corr_info = tech_corr.get('immediate_correlation', {})
    if corr_info:
        corr_val = corr_info.get('correlation', 0)
        ax.text(0.05, 0.95, f'Correlation: {corr_val:.3f}\n({corr_info.get("strength", "unknown")})', 
                transform=ax.transAxes, fontsize=10, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Legends
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='center right')


def plot_growth_models(ax, results):
    """Plot different growth models comparison."""
    models = results.get('statistical_models', {})
    
    if not models:
        ax.text(0.5, 0.5, 'No model data available', ha='center', va='center')
        return
    
    # Historical data
    years = np.array([2005, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 
                     2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024])
    species = np.array([1950, 2285, 2618, 2841, 3186, 3439, 3707, 4404, 
                       5027, 5766, 6590, 7406, 9110, 10434, 11273, 15049, 
                       21351, 28911])
    
    # Plot observed data
    ax.scatter(years, species, color='black', s=50, label='Observed', zorder=5)
    
    # Extended years for model comparison
    years_ext = np.linspace(2005, 2025, 100)
    
    # Plot models if available
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    model_names = ['linear', 'polynomial', 'exponential']
    
    for i, model_name in enumerate(model_names):
        if model_name in models and 'error' not in models[model_name]:
            model = models[model_name]
            
            if model_name == 'linear':
                slope = model['slope']
                intercept = model['intercept']
                y_pred = slope * years_ext + intercept
                r2 = model['r_squared']
                ax.plot(years_ext, y_pred, '--', color=colors[i], linewidth=2, 
                       label=f'Linear (R² = {r2:.3f})')
            
            elif model_name == 'polynomial' and 'parameters' in model:
                params = model['parameters']
                y_pred = (params[0] * (years_ext - 2005)**3 + 
                         params[1] * (years_ext - 2005)**2 + 
                         params[2] * (years_ext - 2005) + params[3])
                r2 = model['r_squared']
                ax.plot(years_ext, y_pred, '-', color=colors[i], linewidth=2, 
                       label=f'Polynomial (R² = {r2:.3f})')
            
            elif model_name == 'exponential' and 'parameters' in model:
                params = model['parameters']
                y_pred = params[0] * np.exp(params[1] * (years_ext - 2005)) + params[2]
                r2 = model['r_squared']
                ax.plot(years_ext, y_pred, '-.', color=colors[i], linewidth=2, 
                       label=f'Exponential (R² = {r2:.3f})')
    
    # Customize
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Total Species', fontsize=12)
    ax.set_title('Growth Model Comparison', fontsize=14, fontweight='bold')
    ax.set_xlim(2004, 2026)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Format y-axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))


def plot_annual_additions(ax, results):
    """Plot annual species additions pattern."""
    # Historical data
    years = [2005, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 
            2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    additions = [0, 335, 333, 223, 345, 253, 268, 697, 623, 739, 
                824, 816, 1704, 1324, 839, 3776, 6302, 7560]
    
    # Create bar plot
    bars = ax.bar(years, additions, alpha=0.8, width=0.8)
    
    # Color bars by magnitude
    colors = plt.cm.viridis(np.array(additions) / max(additions))
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    # Highlight breakthrough years (>2000 species)
    for i, (year, addition) in enumerate(zip(years, additions)):
        if addition > 2000:
            bars[i].set_edgecolor('red')
            bars[i].set_linewidth(3)
            ax.text(year, addition + 200, f'{addition:,}', 
                   ha='center', va='bottom', fontsize=10, fontweight='bold', color='red')
    
    # Customize
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Species Added', fontsize=12)
    ax.set_title('Annual Species Additions Pattern', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add mean line
    mean_additions = np.mean(additions)
    ax.axhline(y=mean_additions, color='orange', linestyle='--', linewidth=2, 
              label=f'Mean: {mean_additions:.0f}')
    ax.legend()


def plot_future_projections(ax, results):
    """Plot future growth projections."""
    predictions = results.get('predictions', {})
    
    if not predictions:
        ax.text(0.5, 0.5, 'No prediction data available', ha='center', va='center')
        return
    
    # Historical data
    historical_years = [2020, 2021, 2022, 2023, 2024]
    historical_species = [10434, 11273, 15049, 21351, 28911]
    
    # Future projections
    future_years = predictions.get('projection_years', [2025, 2026, 2027, 2028, 2029])
    scenarios = predictions.get('scenarios', {})
    
    # Plot historical data
    ax.plot(historical_years, historical_species, 'o-', color='black', linewidth=3, 
           markersize=8, label='Historical (2020-2024)')
    
    # Plot projections
    colors = ['#2ca02c', '#ff7f0e', '#d62728']
    scenario_names = ['conservative', 'realistic', 'optimistic']
    
    for i, scenario in enumerate(scenario_names):
        if scenario in scenarios:
            values = scenarios[scenario]['values']
            # Connect from last historical point
            full_years = [2024] + future_years
            full_values = [28911] + values
            ax.plot(full_years, full_values, '--', color=colors[i], linewidth=2, 
                   marker='s', markersize=6, label=f'{scenario.title()} Projection')
    
    # Customize
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Total Species', fontsize=12)
    ax.set_title('Future Growth Projections (2025-2029)', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Format y-axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))
    
    # Add projection range
    if scenarios:
        conservative_2029 = scenarios.get('conservative', {}).get('values', [0])[-1]
        optimistic_2029 = scenarios.get('optimistic', {}).get('values', [0])[-1]
        ax.fill_between([2025, 2029], [conservative_2029, conservative_2029], 
                       [optimistic_2029, optimistic_2029], alpha=0.2, color='gray',
                       label='Projection Range')


def plot_family_patterns(ax, results):
    """Plot family-level growth patterns."""
    family_patterns = results.get('family_patterns', {})
    
    if not family_patterns:
        ax.text(0.5, 0.5, 'No family pattern data', ha='center', va='center')
        return
    
    # Family categories
    categories = family_patterns.get('family_categories', {})
    
    if categories:
        cat_names = []
        growth_rates = []
        
        for cat_name, cat_data in categories.items():
            cat_names.append(cat_name.replace('_', ' ').title())
            growth_rates.append(cat_data['avg_annual_growth'])
        
        # Create horizontal bar plot
        bars = ax.barh(range(len(cat_names)), growth_rates, alpha=0.8)
        
        # Color bars
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        for bar, color in zip(bars, colors):
            bar.set_color(color)
        
        # Customize
        ax.set_yticks(range(len(cat_names)))
        ax.set_yticklabels(cat_names)
        ax.set_xlabel('Average Annual Growth (%)', fontsize=12)
        ax.set_title('Family Growth Rate Categories', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (bar, rate) in enumerate(zip(bars, growth_rates)):
            ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                    f'{rate:.1f}%', va='center', fontsize=10)


def plot_breakthrough_years(ax, results):
    """Plot breakthrough years analysis."""
    growth_drivers = results.get('growth_drivers', {})
    breakthrough_years = growth_drivers.get('key_breakthrough_years', [])
    
    if not breakthrough_years:
        ax.text(0.5, 0.5, 'No breakthrough data available', ha='center', va='center')
        return
    
    # Prepare data
    years = [item['year'] for item in breakthrough_years]
    additions = [item['species_added'] for item in breakthrough_years]
    fold_increase = [item['fold_increase'] for item in breakthrough_years]
    
    # Create scatter plot
    scatter = ax.scatter(years, additions, s=[f*100 for f in fold_increase], 
                        alpha=0.7, c=fold_increase, cmap='Reds')
    
    # Add labels for top years
    for item in breakthrough_years[:3]:  # Top 3
        ax.annotate(f"{item['year']}\n{item['species_added']:,}", 
                   (item['year'], item['species_added']),
                   xytext=(10, 10), textcoords='offset points',
                   ha='left', fontsize=9,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))
    
    # Customize
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Species Added', fontsize=12)
    ax.set_title('Breakthrough Discovery Years', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Fold Increase vs Average', fontsize=10)


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


def create_detailed_growth_timeline(results, output_dir):
    """Create a detailed timeline with annotations."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), height_ratios=[2, 1])
    
    # Historical data
    years = [2005, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 
            2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    species = [1950, 2285, 2618, 2841, 3186, 3439, 3707, 4404, 
              5027, 5766, 6590, 7406, 9110, 10434, 11273, 15049, 
              21351, 28911]
    additions = [0, 335, 333, 223, 345, 253, 268, 697, 623, 739, 
                824, 816, 1704, 1324, 839, 3776, 6302, 7560]
    
    # Top plot: Cumulative species
    ax1.plot(years, species, 'o-', linewidth=3, markersize=8, color='#1f77b4')
    ax1.set_ylabel('Total Viral Species', fontsize=14)
    ax1.set_title('20-Year Viral Species Discovery Timeline', fontsize=18, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K'))
    
    # Add major milestones
    milestones = {
        2009: '454 sequencing\nwidespread',
        2010: 'Illumina\ndominance',
        2019: 'Caudovirales\ndissolution', 
        2020: 'COVID-19\nresponse',
        2023: 'AI/LLM\nintegration'
    }
    
    for year, milestone in milestones.items():
        if year in years:
            idx = years.index(year)
            ax1.annotate(milestone, (year, species[idx]), 
                        xytext=(10, 20), textcoords='offset points',
                        ha='left', fontsize=10, 
                        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.7),
                        arrowprops=dict(arrowstyle='->', color='black'))
    
    # Bottom plot: Annual additions
    bars = ax2.bar(years, additions, alpha=0.8, width=0.8)
    colors = plt.cm.viridis(np.array(additions) / max(additions))
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    ax2.set_xlabel('Year', fontsize=14)
    ax2.set_ylabel('Annual Additions', fontsize=14)
    ax2.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    # Save
    output_path = output_dir / "growth_timeline_detailed.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Detailed timeline saved to: {output_path}")


def create_phase_analysis_plot(results, output_dir):
    """Create comprehensive phase analysis plot."""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Phase statistics
    phase_stats = results.get('growth_phases', {}).get('phase_statistics', {})
    
    # 1. Growth rates by phase
    ax = axes[0, 0]
    if phase_stats:
        phases = list(phase_stats.keys())
        rates = [phase_stats[p]['annual_growth_rate'] for p in phases]
        
        bars = ax.bar(range(len(phases)), rates, color=plt.cm.plasma(np.linspace(0, 1, len(phases))))
        ax.set_xticks(range(len(phases)))
        ax.set_xticklabels([p.replace('_', ' ').title() for p in phases], rotation=45)
        ax.set_ylabel('Annual Growth Rate (%)')
        ax.set_title('Growth Rate by Phase')
    
    # 2. Duration vs Growth Rate
    ax = axes[0, 1]
    if phase_stats:
        durations = [phase_stats[p]['duration_years'] for p in phases]
        scatter = ax.scatter(durations, rates, s=100, alpha=0.7, c=range(len(phases)), cmap='viridis')
        ax.set_xlabel('Phase Duration (years)')
        ax.set_ylabel('Annual Growth Rate (%)')
        ax.set_title('Duration vs Growth Rate')
        ax.grid(True, alpha=0.3)
    
    # 3. Technology correlation timeline
    ax = axes[1, 0]
    tech_corr = results.get('technology_correlation', {})
    if tech_corr:
        tech_scores = tech_corr.get('technology_adoption_scores', {})
        if tech_scores:
            years_tech = list(tech_scores.keys())
            scores = list(tech_scores.values())
            ax.plot(years_tech, scores, 'o-', linewidth=2, markersize=6)
            ax.set_xlabel('Year')
            ax.set_ylabel('Technology Adoption Score')
            ax.set_title('Technology Adoption Timeline')
            ax.grid(True, alpha=0.3)
    
    # 4. Summary statistics
    ax = axes[1, 1]
    ax.axis('off')
    
    summary_text = "Growth Pattern Summary:\n\n"
    
    # Calculate key statistics
    if phase_stats:
        fastest_phase = max(phase_stats.items(), key=lambda x: x[1]['annual_growth_rate'])
        slowest_phase = min(phase_stats.items(), key=lambda x: x[1]['annual_growth_rate'])
        
        summary_text += f"• Fastest growing phase:\n  {fastest_phase[0].replace('_', ' ').title()}\n  ({fastest_phase[1]['annual_growth_rate']:.1f}% annually)\n\n"
        summary_text += f"• Slowest growing phase:\n  {slowest_phase[0].replace('_', ' ').title()}\n  ({slowest_phase[1]['annual_growth_rate']:.1f}% annually)\n\n"
        
        total_growth = (28911 - 1950) / 1950 * 100
        summary_text += f"• Total 20-year growth: {total_growth:.0f}%\n"
        summary_text += f"• Average annual growth: {total_growth/20:.1f}%\n"
    
    ax.text(0.1, 0.9, summary_text, transform=ax.transAxes, fontsize=12,
            verticalalignment='top', family='monospace')
    
    plt.suptitle('Comprehensive Growth Phase Analysis', fontsize=18, fontweight='bold')
    plt.tight_layout()
    
    # Save
    output_path = output_dir / "phase_analysis_comprehensive.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Phase analysis saved to: {output_path}")


if __name__ == "__main__":
    create_growth_pattern_visualizations()