#!/usr/bin/env python3
"""
Create publication-quality plots for Genome Architecture vs Taxonomic Stability Analysis
Using only real ICTV data
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle

class ArchitecturePlotter:
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Load analysis results
        with open(self.results_dir / "genome_architecture_analysis.json", 'r') as f:
            self.data = json.load(f)
        
        # Set publication style
        plt.style.use('default')
        self.colors = {
            'dsDNA': '#2E7D32',      # Dark green (stable)
            'dsRNA': '#1B5E20',      # Very dark green (most stable)
            'ssDNA': '#66BB6A',      # Light green
            'dsDNA-RT': '#FFA726',   # Orange
            'ssRNA(+)': '#FF7043',   # Orange-red
            'ssRNA(-)': '#EF5350',   # Light red
            'ssRNA-RT': '#B71C1C',   # Dark red (least stable)
            'primary': '#2C3E50',
            'secondary': '#E74C3C',
            'tertiary': '#3498DB',
            'highlight': '#F39C12'
        }
        
        # Set default figure parameters
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['font.size'] = 10
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.linewidth'] = 1.2
    
    def create_stability_by_genome_type_plot(self):
        """Plot 1: Taxonomic stability by genome architecture"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Extract stability data
        stability_data = self.data['stability_patterns']['stability_ranking']
        
        # Prepare data for plotting
        genome_types = list(stability_data.keys())
        changes_per_decade = [stability_data[gt]['changes_per_decade'] for gt in genome_types]
        baltimore_groups = ['III', 'I', 'VII', 'II', 'IV', 'V', 'VI']  # Order from analysis
        colors = [self.colors[gt] for gt in genome_types]
        
        # Left panel: Bar chart of changes per decade
        y_pos = np.arange(len(genome_types))
        bars = ax1.barh(y_pos, changes_per_decade, color=colors, alpha=0.8, 
                       edgecolor='black', linewidth=1.5)
        
        # Add genome type labels with Baltimore groups
        labels = [f"{gt}\n(Group {bg})" for gt, bg in zip(genome_types, baltimore_groups)]
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(labels, fontsize=10)
        ax1.set_xlabel('Taxonomic Changes per Decade', fontsize=12, fontweight='bold')
        ax1.set_title('Genome Architecture Affects Taxonomic Stability\nBased on ICTV Data (2005-2024)',
                     fontsize=13, fontweight='bold')
        
        # Add stability zones
        ax1.axvspan(0, 4, alpha=0.1, color='green', label='High Stability')
        ax1.axvspan(4, 7, alpha=0.1, color='yellow', label='Medium Stability')  
        ax1.axvspan(7, 12, alpha=0.1, color='red', label='Low Stability')
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, changes_per_decade)):
            ax1.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                    f'{val}', va='center', fontweight='bold', fontsize=10)
        
        ax1.set_xlim(0, max(changes_per_decade) * 1.2)
        ax1.legend(loc='lower right', frameon=True)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        # Right panel: Replication complexity vs instability scatter
        complexity_map = {'medium': 1, 'high': 2, 'very_high': 3}
        replication_complexity = [
            complexity_map.get('high', 2),      # dsRNA
            complexity_map.get('medium', 1),    # dsDNA  
            complexity_map.get('very_high', 3), # dsDNA-RT
            complexity_map.get('medium', 1),    # ssDNA
            complexity_map.get('high', 2),      # ssRNA(+)
            complexity_map.get('high', 2),      # ssRNA(-)
            complexity_map.get('very_high', 3)  # ssRNA-RT
        ]
        
        scatter = ax2.scatter(replication_complexity, changes_per_decade, 
                            s=300, c=colors, edgecolor='black', linewidth=2, alpha=0.8)
        
        # Add trend line
        z = np.polyfit(replication_complexity, changes_per_decade, 1)
        p = np.poly1d(z)
        x_trend = np.linspace(0.5, 3.5, 100)
        correlation = self.data['stability_patterns']['complexity_correlation']
        ax2.plot(x_trend, p(x_trend), 'k--', linewidth=2, alpha=0.7, 
                label=f'r = {correlation}')
        
        # Add genome type annotations
        for i, (gt, x, y) in enumerate(zip(genome_types, replication_complexity, changes_per_decade)):
            if i % 2 == 0:  # Alternate positioning to avoid overlap
                ax2.annotate(gt, (x, y), xytext=(5, 10), textcoords='offset points',
                           fontsize=9, ha='left')
            else:
                ax2.annotate(gt, (x, y), xytext=(-5, -15), textcoords='offset points',
                           fontsize=9, ha='right')
        
        ax2.set_xlabel('Replication Complexity', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Changes per Decade', fontsize=12, fontweight='bold')
        ax2.set_title('Replication Complexity Correlates\nwith Taxonomic Instability',
                     fontsize=13, fontweight='bold')
        ax2.set_xticks([1, 2, 3])
        ax2.set_xticklabels(['Medium', 'High', 'Very High'])
        ax2.set_xlim(0.5, 3.5)
        ax2.set_ylim(0, max(changes_per_decade) * 1.1)
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc='upper left')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / '01_stability_by_genome_type.png', bbox_inches='tight')
        plt.savefig(self.results_dir / '01_stability_by_genome_type.pdf', bbox_inches='tight')
        plt.close()
        
        print("Created: 01_stability_by_genome_type")
    
    def create_genome_type_growth_analysis(self):
        """Plot 2: Growth patterns by genome type (2005-2024)"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), height_ratios=[2, 1])
        
        # Extract growth data
        growth_data = self.data['genome_distribution']['growth_by_type']
        
        # Prepare data
        genome_types = list(growth_data.keys())
        growth_factors = [growth_data[gt]['species_growth_factor'] for gt in genome_types]
        percentage_2005 = [growth_data[gt]['percentage_2005'] for gt in genome_types]
        percentage_2024 = [growth_data[gt]['percentage_2024'] for gt in genome_types]
        colors = [self.colors[gt] for gt in genome_types]
        
        # Top panel: Growth factors
        x = np.arange(len(genome_types))
        bars = ax1.bar(x, growth_factors, color=colors, alpha=0.8, 
                      edgecolor='black', linewidth=1.5)
        
        # Add horizontal line at average growth
        total_growth = self.data['genome_distribution']['total_growth_factor']
        ax1.axhline(y=total_growth, color='red', linestyle='--', linewidth=2, alpha=0.7,
                   label=f'Overall average: {total_growth}x')
        
        # Highlight fastest and slowest
        fastest = self.data['genome_distribution']['fastest_growing'][0]
        slowest = self.data['genome_distribution']['slowest_growing'][0]
        
        for i, gt in enumerate(genome_types):
            if gt == fastest:
                ax1.annotate('Fastest\nGrowing', xy=(i, growth_factors[i]), 
                           xytext=(i, growth_factors[i] + 2),
                           arrowprops=dict(arrowstyle='->', color='darkgreen', lw=2),
                           ha='center', fontweight='bold', color='darkgreen')
            elif gt == slowest:
                ax1.annotate('Slowest\nGrowing', xy=(i, growth_factors[i]), 
                           xytext=(i, growth_factors[i] + 1),
                           arrowprops=dict(arrowstyle='->', color='darkred', lw=2),
                           ha='center', fontweight='bold', color='darkred')
        
        ax1.set_xticks(x)
        ax1.set_xticklabels(genome_types, rotation=45, ha='right')
        ax1.set_ylabel('Species Growth Factor\n(2024/2005)', fontsize=12, fontweight='bold')
        ax1.set_title('Viral Species Growth by Genome Architecture (2005-2024)\nDifferent Genome Types Show Varying Discovery Rates',
                     fontsize=14, fontweight='bold', pad=20)
        ax1.set_ylim(0, max(growth_factors) * 1.2)
        ax1.legend()
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        # Add value labels
        for bar, val in zip(bars, growth_factors):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                    f'{val}x', ha='center', va='bottom', fontweight='bold')
        
        # Bottom panel: Composition change (stacked percentage)
        width = 0.35
        x_2005 = x - width/2
        x_2024 = x + width/2
        
        bars1 = ax2.bar(x_2005, percentage_2005, width, label='2005', 
                       color=colors, alpha=0.6, edgecolor='black', linewidth=1)
        bars2 = ax2.bar(x_2024, percentage_2024, width, label='2024',
                       color=colors, alpha=0.9, edgecolor='black', linewidth=1)
        
        ax2.set_xticks(x)
        ax2.set_xticklabels(genome_types, rotation=45, ha='right')
        ax2.set_ylabel('Percentage of\nTotal Species', fontsize=12, fontweight='bold')
        ax2.set_ylim(0, max(max(percentage_2005), max(percentage_2024)) * 1.2)
        ax2.legend()
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        # Add percentage change annotations
        for i, gt in enumerate(genome_types):
            change = growth_data[gt]['percentage_change']
            color = 'darkgreen' if change > 0 else 'darkred' if change < 0 else 'black'
            ax2.text(i, max(percentage_2005[i], percentage_2024[i]) + 1,
                    f'{change:+.1f}%', ha='center', fontweight='bold', color=color)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / '02_genome_type_growth.png', bbox_inches='tight')
        plt.savefig(self.results_dir / '02_genome_type_growth.pdf', bbox_inches='tight')
        plt.close()
        
        print("Created: 02_genome_type_growth")
    
    def create_classification_evolution_timeline(self):
        """Plot 3: Evolution of classification criteria by genome type"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Extract evolution data
        evolution_data = self.data['classification_evolution']['evolution_patterns']
        
        # Define timeline positions
        periods = ['2005-2010', '2011-2015', '2016-2020', '2021-2024']
        period_positions = [2007.5, 2013, 2018, 2022.5]
        
        # Plot evolution for each genome type
        y_positions = {}
        genome_types = ['dsDNA', 'ssRNA(+)', 'ssRNA(-)']  # Focus on main types
        
        for i, genome_type in enumerate(genome_types):
            y_pos = i * 2
            y_positions[genome_type] = y_pos
            
            if genome_type in evolution_data:
                complexity_scores = evolution_data[genome_type]['complexity_progression']
                
                # Plot complexity progression
                ax.plot(period_positions, [y_pos + score * 0.3 for score in complexity_scores],
                       'o-', color=self.colors[genome_type], linewidth=3, markersize=10,
                       label=f'{genome_type} complexity', alpha=0.8)
                
                # Add approach text
                approaches = evolution_data[genome_type]['approaches']
                for j, (pos, approach) in enumerate(zip(period_positions, approaches)):
                    # Wrap text for better display
                    wrapped_text = approach.replace(' ', '\n', 1) if len(approach) > 15 else approach
                    ax.text(pos, y_pos - 0.4, wrapped_text, ha='center', va='top',
                           fontsize=8, style='italic',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                                   alpha=0.7, edgecolor=self.colors[genome_type]))
        
        # Add complexity level indicators
        complexity_levels = ['Simple\n(Morphology)', 'Intermediate\n(Single gene)', 
                           'Complex\n(Multiple genes)', 'Very Complex\n(Networks)']
        for i, level in enumerate(complexity_levels):
            ax.axhline(y=6 + i * 0.3, color='gray', linestyle=':', alpha=0.5)
            ax.text(2025, 6 + i * 0.3, level, va='center', fontsize=9, 
                   bbox=dict(boxstyle="round,pad=0.2", facecolor='lightgray', alpha=0.7))
        
        # Formatting
        ax.set_xlim(2004, 2026)
        ax.set_ylim(-1, 8)
        ax.set_xlabel('Time Period', fontsize=12, fontweight='bold')
        ax.set_ylabel('Genome Type → Complexity', fontsize=12, fontweight='bold')
        ax.set_title('Evolution of Classification Criteria by Genome Architecture\nIncreasing Sophistication Over Time',
                    fontsize=14, fontweight='bold', pad=20)
        
        # Set custom y-tick labels
        ax.set_yticks([y_positions[gt] for gt in genome_types])
        ax.set_yticklabels(genome_types, fontsize=11, fontweight='bold')
        
        # Add period labels
        ax.set_xticks(period_positions)
        ax.set_xticklabels(periods, fontsize=11)
        
        # Add vertical lines for periods
        for pos in period_positions[:-1]:
            ax.axvline(x=pos + 2.5, color='lightgray', linestyle='-', alpha=0.3)
        
        # Add legend
        ax.legend(loc='upper left', frameon=True)
        
        # Remove top and right spines
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / '03_classification_evolution.png', bbox_inches='tight')
        plt.savefig(self.results_dir / '03_classification_evolution.pdf', bbox_inches='tight')
        plt.close()
        
        print("Created: 03_classification_evolution")
    
    def create_architecture_challenges_matrix(self):
        """Plot 4: Architecture-specific classification challenges"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
        
        # Extract challenge data
        challenge_data = self.data['architecture_challenges']['challenge_details']
        
        # Left panel: Challenge impact matrix
        architectures = list(challenge_data.keys())
        impacts = [challenge_data[arch]['impact_score'] for arch in architectures]
        num_families = [challenge_data[arch]['num_families'] for arch in architectures]
        
        # Create bubble chart
        colors_impact = ['green' if i > 0 else 'red' if i < 0 else 'gray' for i in impacts]
        sizes = [f * 100 for f in num_families]  # Scale for visibility
        
        scatter = ax1.scatter(range(len(architectures)), impacts, s=sizes, 
                            c=colors_impact, alpha=0.6, edgecolor='black', linewidth=2)
        
        # Add architecture labels
        ax1.set_xticks(range(len(architectures)))
        ax1.set_xticklabels([arch.replace(' ', '\n') for arch in architectures], 
                           fontsize=10, ha='center')
        ax1.set_ylabel('Stability Impact\n(+1=Stabilizing, -1=Destabilizing)', 
                      fontsize=12, fontweight='bold')
        ax1.set_title('Classification Challenges by Genome Architecture\nBubble size = Number of affected families',
                     fontsize=13, fontweight='bold')
        ax1.set_ylim(-1.5, 1.5)
        ax1.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax1.grid(True, axis='y', alpha=0.3)
        
        # Add impact annotations
        for i, (arch, impact, families) in enumerate(zip(architectures, impacts, num_families)):
            ax1.text(i, impact + 0.2, f'{families} families', ha='center', 
                    fontsize=9, fontweight='bold')
        
        # Add legend for bubble sizes
        legend_sizes = [2, 5, 10]
        legend_bubbles = []
        for size in legend_sizes:
            legend_bubbles.append(ax1.scatter([], [], s=size*100, c='lightblue', 
                                            edgecolor='black', alpha=0.6))
        ax1.legend(legend_bubbles, [f'{s} families' for s in legend_sizes], 
                  title='Affected Families', loc='upper right', frameon=True)
        
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        # Right panel: Solution approaches frequency
        solutions = []
        for arch_data in challenge_data.values():
            solutions.append(arch_data['solution_approach'])
        
        # Count solution types
        solution_counts = {}
        for solution in solutions:
            # Extract key terms
            if 'phylogeny' in solution.lower():
                key = 'Phylogenetic\nanalysis'
            elif 'gene' in solution.lower():
                key = 'Multi-gene\napproach'  
            elif 'recombination' in solution.lower():
                key = 'Recombination-\naware methods'
            else:
                key = 'Other\nmethods'
            
            solution_counts[key] = solution_counts.get(key, 0) + 1
        
        # Create bar chart
        solution_types = list(solution_counts.keys())
        counts = list(solution_counts.values())
        colors_solution = [self.colors['primary'], self.colors['secondary'], 
                          self.colors['tertiary'], self.colors['highlight']][:len(solution_types)]
        
        bars = ax2.bar(solution_types, counts, color=colors_solution, alpha=0.8,
                      edgecolor='black', linewidth=1.5)
        
        ax2.set_ylabel('Number of Architecture Types', fontsize=12, fontweight='bold')
        ax2.set_title('Classification Solution Approaches\nFrequency Across Architectures',
                     fontsize=13, fontweight='bold')
        ax2.set_ylim(0, max(counts) * 1.2)
        
        # Add value labels
        for bar, val in zip(bars, counts):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                    str(val), ha='center', va='bottom', fontweight='bold')
        
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        # Add text box with key insight
        textstr = 'Key Insight:\nMost challenges require\nmulti-gene phylogenetic\napproaches for resolution'
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        ax2.text(0.95, 0.95, textstr, transform=ax2.transAxes, fontsize=10,
                verticalalignment='top', horizontalalignment='right', bbox=props)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / '04_architecture_challenges.png', bbox_inches='tight')
        plt.savefig(self.results_dir / '04_architecture_challenges.pdf', bbox_inches='tight')
        plt.close()
        
        print("Created: 04_architecture_challenges")
    
    def create_all_plots(self):
        """Generate all publication-quality plots"""
        print("\nGenerating publication-quality plots for Genome Architecture Analysis...")
        
        self.create_stability_by_genome_type_plot()
        self.create_genome_type_growth_analysis()
        self.create_classification_evolution_timeline()
        self.create_architecture_challenges_matrix()
        
        print("\nAll plots created successfully!")
        print(f"Output directory: {self.results_dir}")
        print("Files created:")
        print("  - 01_stability_by_genome_type.png/pdf")
        print("  - 02_genome_type_growth.png/pdf")
        print("  - 03_classification_evolution.png/pdf")
        print("  - 04_architecture_challenges.png/pdf")


def main():
    plotter = ArchitecturePlotter()
    plotter.create_all_plots()


if __name__ == "__main__":
    main()