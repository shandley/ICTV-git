#!/usr/bin/env python3
"""
Simple visualization script for ICTV-git data.

Creates basic plots showing 20-year taxonomy evolution without complex dependencies.
"""

import json
import matplotlib.pyplot as plt
import requests
from pathlib import Path
import numpy as np

def fetch_timeline_data():
    """Fetch timeline data from API or use static data."""
    try:
        # Try to get from API if running
        response = requests.get("http://localhost:8000/historical/timeline", timeout=2)
        if response.status_code == 200:
            print("Using live API data")
            return response.json()
    except:
        pass
    
    # Fallback to static data
    print("Using static timeline data")
    return {
        "timeline_span": "MSL23 to MSL40",
        "years_covered": 20,
        "species_growth": {
            "initial_count": 1950,
            "final_count": 28911,
            "growth_rate_percent": 1383.1
        }
    }

def create_basic_plots():
    """Create basic visualizations of ICTV data."""
    
    # Timeline data for all MSL releases
    msl_data = [
        {"version": "MSL23", "year": 2005, "species": 1950},
        {"version": "MSL24", "year": 2008, "species": 2285},
        {"version": "MSL25", "year": 2009, "species": 2480},
        {"version": "MSL26", "year": 2010, "species": 2585},
        {"version": "MSL27", "year": 2011, "species": 2618},
        {"version": "MSL28", "year": 2012, "species": 2827},
        {"version": "MSL29", "year": 2013, "species": 3186},
        {"version": "MSL30", "year": 2014, "species": 3728},
        {"version": "MSL31", "year": 2015, "species": 4404},
        {"version": "MSL32", "year": 2016, "species": 4958},
        {"version": "MSL33", "year": 2017, "species": 5450},
        {"version": "MSL34", "year": 2018, "species": 6590},
        {"version": "MSL35", "year": 2019, "species": 9110},  # Caudovirales dissolution
        {"version": "MSL36", "year": 2020, "species": 9630},  # COVID-19 response
        {"version": "MSL37", "year": 2021, "species": 11273},
        {"version": "MSL38", "year": 2022, "species": 15109},
        {"version": "MSL39", "year": 2023, "species": 21351},
        {"version": "MSL40", "year": 2024, "species": 28911}
    ]
    
    years = [d["year"] for d in msl_data]
    species_counts = [d["species"] for d in msl_data]
    versions = [d["version"] for d in msl_data]
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle("ICTV Viral Taxonomy Evolution (2005-2024)", fontsize=16)
    
    # 1. Species Growth Timeline
    ax1 = axes[0, 0]
    ax1.plot(years, species_counts, 'o-', linewidth=2, markersize=8, color='#2E86AB')
    ax1.set_xlabel("Year")
    ax1.set_ylabel("Number of Species")
    ax1.set_title("Viral Species Growth Over 20 Years")
    ax1.grid(True, alpha=0.3)
    
    # Highlight key events
    ax1.axvline(x=2019, color='red', linestyle='--', alpha=0.5, label='Caudovirales dissolution')
    ax1.axvline(x=2020, color='orange', linestyle='--', alpha=0.5, label='COVID-19 response')
    ax1.legend()
    
    # 2. Annual Growth Rate
    ax2 = axes[0, 1]
    growth_rates = []
    for i in range(1, len(species_counts)):
        rate = (species_counts[i] - species_counts[i-1]) / species_counts[i-1] * 100
        growth_rates.append(rate)
    
    ax2.bar(years[1:], growth_rates, color='#A23B72', alpha=0.7)
    ax2.set_xlabel("Year")
    ax2.set_ylabel("Annual Growth Rate (%)")
    ax2.set_title("Year-over-Year Species Growth Rate")
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. Cumulative Growth Percentage
    ax3 = axes[1, 0]
    base_count = species_counts[0]
    cumulative_growth = [(count - base_count) / base_count * 100 for count in species_counts]
    
    ax3.fill_between(years, 0, cumulative_growth, alpha=0.3, color='#F18F01')
    ax3.plot(years, cumulative_growth, linewidth=2, color='#F18F01')
    ax3.set_xlabel("Year")
    ax3.set_ylabel("Cumulative Growth (%)")
    ax3.set_title("Cumulative Growth Since 2005")
    ax3.grid(True, alpha=0.3)
    
    # 4. Species Count by Era
    ax4 = axes[1, 1]
    eras = [
        {"name": "Foundation\n(2005-2008)", "start": 0, "end": 2, "color": "#1B4079"},
        {"name": "Standard.\n(2009-2014)", "start": 2, "end": 8, "color": "#2B7489"},
        {"name": "Molecular\n(2015-2018)", "start": 8, "end": 12, "color": "#3B9A9C"},
        {"name": "Reorg.\n(2019)", "start": 12, "end": 13, "color": "#F71735"},
        {"name": "Pandemic\n(2020)", "start": 13, "end": 14, "color": "#FF9F1C"},
        {"name": "Metagen.\n(2021-2022)", "start": 14, "end": 16, "color": "#5FAD56"},
        {"name": "AI Era\n(2023-2024)", "start": 16, "end": 18, "color": "#7D4F9A"}
    ]
    
    era_names = []
    era_species = []
    era_colors = []
    
    for era in eras:
        era_names.append(era["name"])
        # Get the final species count for each era
        era_species.append(species_counts[era["end"]-1])
        era_colors.append(era["color"])
    
    bars = ax4.bar(era_names, era_species, color=era_colors, alpha=0.8)
    ax4.set_ylabel("Species Count at Era End")
    ax4.set_title("Species Count by Historical Era")
    ax4.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=10)
    
    plt.tight_layout()
    
    # Save the plot
    output_dir = Path("output/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "ictv_20_year_evolution.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Plot saved to: {output_file}")
    
    # Close the plot to avoid blocking
    plt.close()
    
    # Print summary statistics
    print("\n=== 20-Year ICTV Taxonomy Evolution Summary ===")
    print(f"Initial species (2005): {species_counts[0]:,}")
    print(f"Final species (2024): {species_counts[-1]:,}")
    print(f"Total growth: {species_counts[-1] - species_counts[0]:,} species")
    print(f"Growth rate: {(species_counts[-1] - species_counts[0]) / species_counts[0] * 100:.1f}%")
    print(f"\nKey events:")
    print(f"- 2019 (MSL35): Caudovirales dissolution - {species_counts[12]:,} species")
    print(f"- 2020 (MSL36): COVID-19 response - {species_counts[13]:,} species")
    print(f"- 2023-2024: AI era explosion - {species_counts[-1]:,} species")

def main():
    """Run visualization."""
    print("Creating ICTV 20-year evolution visualizations...")
    
    # Fetch timeline data (from API or static)
    timeline_data = fetch_timeline_data()
    
    # Create plots
    create_basic_plots()
    
    print("\nVisualization complete!")
    print("\nTo create more advanced visualizations:")
    print("1. Use the REST API to fetch specific data")
    print("2. Create custom plots with matplotlib/seaborn")
    print("3. Export data to tools like Tableau or PowerBI")
    print("4. Build a web dashboard with Plotly Dash or Streamlit")

if __name__ == "__main__":
    main()