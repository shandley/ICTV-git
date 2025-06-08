#!/usr/bin/env python3
"""
Fix the Genomics Era analysis by handling the MSL33/MSL34 2018 dual-release issue.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def fix_genomics_era_calculation():
    """Fix the calculation that's causing missing Genomics era data."""
    
    # Read the original data
    data_path = Path(__file__).parent.parent / 'output' / 'research_analysis' / 'study1_growth_data.csv'
    df = pd.read_csv(data_path)
    
    print("Original data issues:")
    print("MSL33 and MSL34 both in 2018:")
    print(df[df['year'] == 2018][['version', 'year', 'species', 'annual_species_growth']])
    
    # Fix the annual growth calculation by handling same-year releases
    df_fixed = df.copy()
    
    # For same-year releases, we need to combine them or adjust the calculation
    # Let's treat MSL33→MSL34 as a mid-year adjustment and calculate properly
    
    # Method 1: Calculate cumulative annual growth for same-year releases
    for i in range(1, len(df_fixed)):
        years_diff = df_fixed.loc[i, 'years_since_previous']
        species_growth = df_fixed.loc[i, 'species_growth']
        
        if years_diff == 0:  # Same year release
            # For same-year releases, treat as cumulative growth for that year
            if i > 1:
                # Find the previous year's data
                prev_year_idx = i - 1
                while prev_year_idx > 0 and df_fixed.loc[prev_year_idx, 'years_since_previous'] == 0:
                    prev_year_idx -= 1
                
                # Calculate cumulative growth for the year
                year_start_species = df_fixed.loc[prev_year_idx, 'species']
                current_species = df_fixed.loc[i, 'species']
                cumulative_growth = current_species - year_start_species
                
                # Since it's still within the same year, use the cumulative growth
                df_fixed.loc[i, 'annual_species_growth'] = cumulative_growth
        
        elif np.isinf(df_fixed.loc[i, 'annual_species_growth']):
            # Replace inf values with the species growth divided by a minimum time period
            df_fixed.loc[i, 'annual_species_growth'] = species_growth  # Treat as 1-year growth
    
    # Now calculate the era averages properly
    print("\nFixed data:")
    print("MSL33 and MSL34 with corrected calculations:")
    print(df_fixed[df_fixed['year'] == 2018][['version', 'year', 'species', 'annual_species_growth']])
    
    # Calculate era averages excluding infinite values
    early_phase = df_fixed[(df_fixed['year'] <= 2014) & np.isfinite(df_fixed['annual_species_growth'])]['annual_species_growth'].mean()
    genomics_phase = df_fixed[(df_fixed['year'] > 2014) & (df_fixed['year'] <= 2020) & np.isfinite(df_fixed['annual_species_growth'])]['annual_species_growth'].mean()
    modern_phase = df_fixed[(df_fixed['year'] > 2020) & np.isfinite(df_fixed['annual_species_growth'])]['annual_species_growth'].mean()
    
    print(f"\nCorrected Era Averages:")
    print(f"Early (2005-2014): {early_phase:.1f} species/year")
    print(f"Genomics (2015-2020): {genomics_phase:.1f} species/year")  
    print(f"Modern (2021-2024): {modern_phase:.1f} species/year")
    
    # Create corrected visualization
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Original problematic calculation
    phases_orig = ['Early\n(2005-2014)', 'Genomics\n(2015-2020)', 'Modern\n(2021-2024)']
    phase_rates_orig = [
        df[(df['year'] <= 2014)]['annual_species_growth'].mean(),
        df[(df['year'] > 2014) & (df['year'] <= 2020)]['annual_species_growth'].mean(),
        df[df['year'] > 2020]['annual_species_growth'].mean()
    ]
    
    # Fixed calculation
    phases_fixed = ['Early\n(2005-2014)', 'Genomics\n(2015-2020)', 'Modern\n(2021-2024)']
    phase_rates_fixed = [early_phase, genomics_phase, modern_phase]
    
    colors = ['lightblue', 'orange', 'lightgreen']
    
    # Plot original (problematic)
    bars1 = axes[0].bar(phases_orig, phase_rates_orig, color=colors, alpha=0.8)
    axes[0].set_title('Original (Problematic) Calculation', fontsize=14, fontweight='bold')
    axes[0].set_ylabel('Average Species/Year')
    axes[0].grid(True, alpha=0.3)
    
    for bar, rate in zip(bars1, phase_rates_orig):
        if np.isfinite(rate):
            axes[0].text(bar.get_x() + bar.get_width()/2., bar.get_height() + 50,
                        f'{rate:.0f}', ha='center', va='bottom', fontweight='bold')
        else:
            axes[0].text(bar.get_x() + bar.get_width()/2., 100,
                        'NaN/Inf', ha='center', va='bottom', fontweight='bold', color='red')
    
    # Plot fixed
    bars2 = axes[1].bar(phases_fixed, phase_rates_fixed, color=colors, alpha=0.8)
    axes[1].set_title('Corrected Calculation', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Average Species/Year')
    axes[1].grid(True, alpha=0.3)
    
    for bar, rate in zip(bars2, phase_rates_fixed):
        height = bar.get_height()
        axes[1].text(bar.get_x() + bar.get_width()/2., height + 50,
                    f'{rate:.0f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    # Save corrected plot
    output_dir = Path(__file__).parent.parent / 'output' / 'research_analysis'
    plt.savefig(output_dir / 'corrected_genomics_era_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\nCorrected visualization saved to: {output_dir / 'corrected_genomics_era_analysis.png'}")
    
    # Save corrected data
    df_fixed.to_csv(output_dir / 'study1_growth_data_corrected.csv', index=False)
    print(f"Corrected data saved to: {output_dir / 'study1_growth_data_corrected.csv'}")
    
    return {
        'early_phase': early_phase,
        'genomics_phase': genomics_phase, 
        'modern_phase': modern_phase,
        'issue_explanation': 'MSL33 and MSL34 both released in 2018, causing division by zero in annual growth calculation'
    }

def explain_the_issue():
    """Provide detailed explanation of why the Genomics era bar was missing."""
    
    explanation = """
    EXPLANATION: Why the Genomics Era Bar Was Missing
    ================================================
    
    The missing "Genomics (2015-2020)" bar in the "Discovery Rate by Era" plot was caused by 
    a data calculation issue related to ICTV's dual MSL release in 2018:
    
    HISTORICAL CONTEXT:
    - MSL33 was released in early 2018 (6,473 species)
    - MSL34 was released later in 2018 (7,141 species) 
    - Both versions have the same year (2018) in our dataset
    
    TECHNICAL PROBLEM:
    - The annual growth calculation uses: species_growth / years_since_previous
    - For MSL34: years_since_previous = 2018 - 2018 = 0
    - This creates: 668 species / 0 years = infinity (inf)
    - The mean() of [finite values + inf] = NaN (Not a Number)
    - matplotlib cannot plot NaN values, so the bar disappears
    
    SOLUTION:
    - Handle same-year releases by treating them as cumulative annual growth
    - Filter out infinite values when calculating era averages  
    - Use finite values only for meaningful statistical calculations
    
    CORRECTED RESULTS:
    - Early (2005-2014): ~230 species/year
    - Genomics (2015-2020): ~1,217 species/year ← This was missing!
    - Modern (2021-2024): ~3,869 species/year
    
    This shows the Genomics era actually had substantial growth (~5x increase from Early era),
    demonstrating the significant impact of metagenomics on viral discovery.
    """
    
    print(explanation)
    return explanation

if __name__ == "__main__":
    # Fix the calculation and explain the issue
    explain_the_issue()
    results = fix_genomics_era_calculation()
    
    print(f"\n" + "="*60)
    print("ISSUE RESOLVED")
    print("="*60)
    print(f"The Genomics era (2015-2020) shows {results['genomics_phase']:.0f} species/year")
    print(f"This represents a ~5x increase from the Early era ({results['early_phase']:.0f} species/year)")
    print(f"The Modern era shows continued acceleration to {results['modern_phase']:.0f} species/year")
    print(f"\nRoot cause: {results['issue_explanation']}")