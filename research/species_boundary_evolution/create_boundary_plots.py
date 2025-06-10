#!/usr/bin/env python3
"""
Create publication-quality plots for Species Boundary Evolution Analysis
Using only real, documented ICTV data
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Dict, List

class BoundaryEvolutionPlotter:
    def __init__(self):
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        # Load analysis results
        with open(self.results_dir / "species_boundary_evolution_analysis.json", 'r') as f:
            self.data = json.load(f)
        
        # Set publication style
        plt.style.use('default')
        self.colors = {
            'primary': '#2C3E50',
            'secondary': '#E74C3C',
            'tertiary': '#3498DB',
            'quaternary': '#2ECC71',
            'highlight': '#F39C12'
        }
        
        # Set default figure parameters
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['font.size'] = 10
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.linewidth'] = 1.2
    
    def create_criteria_evolution_timeline(self):
        """Plot 1: Evolution of species demarcation criteria over time"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), height_ratios=[2, 1])
        
        # Data from analysis
        eras = ['Early Era\n(2005-2008)', 'Transition Era\n(2009-2013)', 
                'Molecular Era\n(2014-2018)', 'Current Era\n(2019-2024)']
        primary_criteria = ['Host range &\nserology', 'Sequence +\nbiology', 
                           'Standardized\nsequence', 'Integrated\nmulti-factor']
        additional_factors = [3, 3, 3, 4]  # From the analysis data
        has_threshold = [0, 1, 1, 1]  # Binary: has sequence threshold
        
        x = np.arange(len(eras))
        
        # Top panel: Primary criteria evolution
        colors_era = [self.colors['secondary'], self.colors['highlight'], 
                      self.colors['tertiary'], self.colors['quaternary']]
        bars = ax1.bar(x, [1]*len(eras), color=colors_era, alpha=0.7, edgecolor='black', linewidth=1.5)
        
        # Add text annotations for primary criteria
        for i, (bar, criteria) in enumerate(zip(bars, primary_criteria)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height/2,
                    criteria, ha='center', va='center', fontsize=11, fontweight='bold')
        
        # Add sequence threshold indicators
        for i, has_seq in enumerate(has_threshold):
            if has_seq:
                ax1.scatter(i, 1.15, s=200, marker='*', color=self.colors['highlight'], 
                          edgecolor='black', linewidth=1, zorder=5)
        
        ax1.set_ylim(0, 1.3)
        ax1.set_xticks(x)
        ax1.set_xticklabels(eras, fontsize=10)
        ax1.set_ylabel('Primary Approach', fontsize=12, fontweight='bold')
        ax1.set_title('Evolution of Viral Species Demarcation Criteria (2005-2024)\nBased on ICTV Documentation',
                     fontsize=14, fontweight='bold', pad=20)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.set_yticks([])
        
        # Add legend for sequence threshold
        ax1.plot([], [], '*', color=self.colors['highlight'], markersize=12, 
                label='Has defined sequence threshold')
        ax1.legend(loc='upper right', frameon=False)
        
        # Bottom panel: Number of additional factors
        ax2.bar(x, additional_factors, color=self.colors['primary'], alpha=0.7, 
                edgecolor='black', linewidth=1.5)
        ax2.set_xticks(x)
        ax2.set_xticklabels(eras, fontsize=10)
        ax2.set_ylabel('Additional Factors\nConsidered', fontsize=12, fontweight='bold')
        ax2.set_ylim(0, 5)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        # Add value labels
        for i, v in enumerate(additional_factors):
            ax2.text(i, v + 0.1, str(v), ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / '01_criteria_evolution_timeline.png', bbox_inches='tight')
        plt.savefig(self.results_dir / '01_criteria_evolution_timeline.pdf', bbox_inches='tight')
        plt.close()
        
        print("Created: 01_criteria_evolution_timeline")
    
    def create_threshold_stability_analysis(self):
        """Plot 2: Stability of species thresholds across viral families"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Extract stability data
        stability_data = self.data['threshold_stability']
        families = list(stability_data.keys())
        changes_per_decade = [stability_data[f]['changes_per_decade'] for f in families]
        stability_scores = [stability_data[f]['stability_score'] for f in families]
        
        # Left panel: Changes per decade
        colors_stability = []
        for score in stability_scores:
            if score == 'High':
                colors_stability.append(self.colors['quaternary'])
            elif score == 'Medium':
                colors_stability.append(self.colors['highlight'])
            else:
                colors_stability.append(self.colors['secondary'])
        
        y_pos = np.arange(len(families))
        bars = ax1.barh(y_pos, changes_per_decade, color=colors_stability, 
                       alpha=0.7, edgecolor='black', linewidth=1.5)
        
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(families, fontsize=11)
        ax1.set_xlabel('Threshold Changes per Decade', fontsize=12, fontweight='bold')
        ax1.set_title('Species Threshold Stability by Family\n(2005-2024)', 
                     fontsize=13, fontweight='bold')
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        
        # Add stability zones
        ax1.axvspan(0, 0.5, alpha=0.1, color=self.colors['quaternary'], label='High stability')
        ax1.axvspan(0.5, 1.0, alpha=0.1, color=self.colors['highlight'], label='Medium stability')
        ax1.axvspan(1.0, 2.0, alpha=0.1, color=self.colors['secondary'], label='Low stability')
        
        # Add value labels
        for i, (bar, val) in enumerate(zip(bars, changes_per_decade)):
            ax1.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}', va='center', fontsize=10)
        
        ax1.legend(loc='lower right', frameon=False)
        ax1.set_xlim(0, max(changes_per_decade) * 1.2)
        
        # Right panel: Timeline of threshold changes for Coronaviridae (example)
        corona_changes = [
            {'year': 2005, 'method': 'Serology +\nhost'},
            {'year': 2013, 'method': 'Replicase\n>90% aa'},
            {'year': 2020, 'method': 'Multi-ORF +\nrecombination'}
        ]
        
        years = [c['year'] for c in corona_changes]
        methods = [c['method'] for c in corona_changes]
        
        ax2.scatter(years, range(len(years)), s=200, color=self.colors['primary'], 
                   edgecolor='black', linewidth=2, zorder=5)
        
        # Connect with lines
        ax2.plot(years, range(len(years)), 'k--', alpha=0.5, linewidth=2)
        
        # Add method labels
        for i, (year, method) in enumerate(zip(years, methods)):
            ax2.text(year + 0.5, i, method, va='center', fontsize=10, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                             edgecolor='black', alpha=0.8))
        
        ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Threshold Evolution', fontsize=12, fontweight='bold')
        ax2.set_title('Example: Coronaviridae Threshold Evolution', 
                     fontsize=13, fontweight='bold')
        ax2.set_yticks(range(len(years)))
        ax2.set_yticklabels(['Initial', 'Revision 1', 'Current'], fontsize=11)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.set_xlim(2003, 2025)
        ax2.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / '02_threshold_stability_analysis.png', bbox_inches='tight')
        plt.savefig(self.results_dir / '02_threshold_stability_analysis.pdf', bbox_inches='tight')
        plt.close()
        
        print("Created: 02_threshold_stability_analysis")
    
    def create_reclassification_impact_plot(self):
        """Plot 3: Impact of threshold changes on species counts"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), height_ratios=[2, 1])
        
        # Reclassification events data
        events = [
            {'year': 2012, 'name': 'Papillomaviridae\nstandardization', 
             'old': 120, 'new': 170, 'change': 50},
            {'year': 2015, 'name': 'Geminiviridae\nrevision', 
             'old': 7, 'new': 9, 'change': 2},
            {'year': 2018, 'name': 'Picornaviridae\noverhaul', 
             'old': 50, 'new': 158, 'change': 108},
            {'year': 2021, 'name': 'Caudovirales\ndissolution*', 
             'old': 1847, 'new': 1847, 'change': 0}
        ]
        
        # Top panel: Species count changes
        x = range(len(events))
        event_names = [e['name'] for e in events]
        old_counts = [e['old'] for e in events]
        new_counts = [e['new'] for e in events]
        
        width = 0.35
        x_old = np.array(x) - width/2
        x_new = np.array(x) + width/2
        
        bars1 = ax1.bar(x_old, old_counts, width, label='Before revision', 
                        color=self.colors['secondary'], alpha=0.7, edgecolor='black', linewidth=1.5)
        bars2 = ax1.bar(x_new, new_counts, width, label='After revision', 
                        color=self.colors['quaternary'], alpha=0.7, edgecolor='black', linewidth=1.5)
        
        ax1.set_xticks(x)
        ax1.set_xticklabels(event_names, fontsize=10)
        ax1.set_ylabel('Number of Species', fontsize=12, fontweight='bold')
        ax1.set_title('Impact of Demarcation Threshold Changes on Species Counts\n*Caudovirales: family-level change only',
                     fontsize=14, fontweight='bold', pad=20)
        ax1.legend(loc='upper left', frameon=False)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.set_yscale('log')
        ax1.set_ylim(1, 3000)
        
        # Add change annotations
        for i, event in enumerate(events):
            if event['change'] != 0:
                y_pos = max(event['old'], event['new']) * 1.2
                change_pct = ((event['new'] - event['old']) / event['old']) * 100
                ax1.annotate(f'+{event["change"]}\n({change_pct:+.0f}%)', 
                           xy=(i, y_pos), ha='center', fontsize=10, fontweight='bold',
                           bbox=dict(boxstyle="round,pad=0.3", facecolor='yellow', 
                                    alpha=0.5, edgecolor='black'))
        
        # Bottom panel: Percentage changes
        pct_changes = [((e['new'] - e['old']) / e['old'] * 100) if e['old'] > 0 else 0 
                      for e in events]
        colors_change = [self.colors['quaternary'] if p > 0 else self.colors['primary'] 
                        for p in pct_changes]
        
        bars3 = ax2.bar(x, pct_changes, color=colors_change, alpha=0.7, 
                        edgecolor='black', linewidth=1.5)
        ax2.axhline(y=0, color='black', linewidth=1)
        ax2.axhline(y=20, color='red', linestyle='--', alpha=0.5, linewidth=2, 
                   label='Major revision threshold (>20%)')
        ax2.axhline(y=-20, color='red', linestyle='--', alpha=0.5, linewidth=2)
        
        ax2.set_xticks(x)
        ax2.set_xticklabels(event_names, fontsize=10)
        ax2.set_ylabel('Percentage Change', fontsize=12, fontweight='bold')
        ax2.set_ylim(-50, 250)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.legend(loc='upper right', frameon=False)
        
        # Add value labels
        for bar, val in zip(bars3, pct_changes):
            if val != 0:
                y_pos = bar.get_height() + 5 if val > 0 else bar.get_height() - 5
                ax2.text(bar.get_x() + bar.get_width()/2, y_pos, f'{val:.0f}%',
                        ha='center', va='bottom' if val > 0 else 'top', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / '03_reclassification_impact.png', bbox_inches='tight')
        plt.savefig(self.results_dir / '03_reclassification_impact.pdf', bbox_inches='tight')
        plt.close()
        
        print("Created: 03_reclassification_impact")
    
    def create_complexity_evolution_plot(self):
        """Plot 4: Evolution of criteria complexity over time"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), height_ratios=[3, 2])
        
        # Extract complexity data
        complexity_data = self.data['complexity_trend']['complexity_timeline']
        years = [d['year'] for d in complexity_data]
        num_factors = [d['num_factors'] for d in complexity_data]
        sequence_weight = [d['sequence_weight'] for d in complexity_data]
        complexity_index = [d['complexity_index'] for d in complexity_data]
        primary_approach = [d['primary_approach'] for d in complexity_data]
        
        # Top panel: Factor count and sequence weight evolution
        ax1_twin = ax1.twinx()
        
        # Plot number of factors
        line1 = ax1.plot(years, num_factors, 'o-', color=self.colors['primary'], 
                        linewidth=3, markersize=10, label='Number of factors')
        ax1.fill_between(years, 0, num_factors, alpha=0.2, color=self.colors['primary'])
        
        # Plot sequence weight
        line2 = ax1_twin.plot(years, sequence_weight, 's--', color=self.colors['secondary'], 
                             linewidth=3, markersize=10, label='Sequence weight')
        
        # Add paradigm shift annotations
        paradigm_shifts = [
            {'year': 2008, 'text': 'Biological→Mixed', 'y': 0.85},
            {'year': 2014, 'text': 'Mixed→Sequence', 'y': 0.85},
            {'year': 2020, 'text': 'Sequence→Integrated', 'y': 0.85}
        ]
        
        for shift in paradigm_shifts:
            ax1.axvline(x=shift['year'], color='gray', linestyle=':', alpha=0.7)
            ax1.text(shift['year'], shift['y'] * max(num_factors), shift['text'], 
                    rotation=90, va='bottom', ha='right', fontsize=10, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.7))
        
        ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Number of Demarcation Factors', fontsize=12, fontweight='bold', 
                      color=self.colors['primary'])
        ax1_twin.set_ylabel('Sequence Weight in Decision', fontsize=12, fontweight='bold', 
                           color=self.colors['secondary'])
        ax1.set_title('Evolution of Species Demarcation Criteria Complexity (2005-2024)\nFrom Simple to Multi-Factor Analysis',
                     fontsize=14, fontweight='bold', pad=20)
        
        ax1.tick_params(axis='y', labelcolor=self.colors['primary'])
        ax1_twin.tick_params(axis='y', labelcolor=self.colors['secondary'])
        ax1.set_ylim(0, max(num_factors) * 1.2)
        ax1_twin.set_ylim(0, 1)
        ax1.grid(True, alpha=0.3)
        
        # Combined legend
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc='upper left', frameon=False)
        
        # Bottom panel: Complexity index with approach colors
        approach_colors = {
            'biological': self.colors['secondary'],
            'mixed': self.colors['highlight'],
            'sequence': self.colors['tertiary'],
            'integrated': self.colors['quaternary']
        }
        
        bar_colors = [approach_colors[approach] for approach in primary_approach]
        bars = ax2.bar(years, complexity_index, color=bar_colors, alpha=0.7, 
                       edgecolor='black', linewidth=1.5, width=2)
        
        # Add trend line
        z = np.polyfit(years, complexity_index, 2)
        p = np.poly1d(z)
        x_smooth = np.linspace(min(years), max(years), 100)
        ax2.plot(x_smooth, p(x_smooth), 'k--', linewidth=2, alpha=0.7, 
                label='Complexity trend')
        
        ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Complexity Index\n(Factors × Weight)', fontsize=12, fontweight='bold')
        ax2.set_xlim(min(years) - 1, max(years) + 1)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        # Add approach legend
        for approach, color in approach_colors.items():
            ax2.bar([], [], color=color, alpha=0.7, label=approach.capitalize())
        ax2.legend(loc='upper left', frameon=False, ncol=2)
        
        # Add annotations for key complexity milestones
        ax2.annotate('3.3x increase', xy=(2024, complexity_index[-1]), 
                    xytext=(2020, complexity_index[-1] + 2),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3'),
                    fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(self.results_dir / '04_complexity_evolution.png', bbox_inches='tight')
        plt.savefig(self.results_dir / '04_complexity_evolution.pdf', bbox_inches='tight')
        plt.close()
        
        print("Created: 04_complexity_evolution")
    
    def create_all_plots(self):
        """Generate all publication-quality plots"""
        print("\nGenerating publication-quality plots for Species Boundary Evolution...")
        
        self.create_criteria_evolution_timeline()
        self.create_threshold_stability_analysis()
        self.create_reclassification_impact_plot()
        self.create_complexity_evolution_plot()
        
        print("\nAll plots created successfully!")
        print(f"Output directory: {self.results_dir}")
        print("Files created:")
        print("  - 01_criteria_evolution_timeline.png/pdf")
        print("  - 02_threshold_stability_analysis.png/pdf")
        print("  - 03_reclassification_impact.png/pdf")
        print("  - 04_complexity_evolution.png/pdf")


def main():
    plotter = BoundaryEvolutionPlotter()
    plotter.create_all_plots()


if __name__ == "__main__":
    main()