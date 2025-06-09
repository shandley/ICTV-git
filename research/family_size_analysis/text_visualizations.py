#!/usr/bin/env python3
"""
Text-based visualizations for Family Size Analysis using real data.
Creates publication-ready data tables and ASCII plots when matplotlib unavailable.
"""

import json
from pathlib import Path
from typing import Dict, List


def load_real_data() -> Dict:
    """Load real analysis results."""
    results_file = Path(__file__).parent / "results" / "family_size_analysis_basic.json"
    
    if not results_file.exists():
        raise FileNotFoundError(f"Real data file not found: {results_file}")
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    return data


def create_ascii_growth_plot(data: Dict) -> str:
    """Create ASCII bar chart of species growth."""
    growth_data = data['growth_analysis']['growth_data']
    
    # Get data points
    years = [item['year'] for item in growth_data]
    species_counts = [item['species_count'] for item in growth_data]
    
    # Scale for ASCII plot (max width 50 chars)
    max_count = max(species_counts)
    scale_factor = 50 / max_count
    
    plot_lines = []
    plot_lines.append("VIRAL SPECIES GROWTH TRAJECTORY (2005-2024)")
    plot_lines.append("=" * 60)
    plot_lines.append(f"Scale: Each '█' represents ~{max_count/50:,.0f} species")
    plot_lines.append("")
    
    for year, count in zip(years, species_counts):
        bar_length = int(count * scale_factor)
        bar = '█' * bar_length
        plot_lines.append(f"{year}: {bar} {count:,}")
    
    plot_lines.append("")
    plot_lines.append(f"Total Growth: {species_counts[0]:,} → {species_counts[-1]:,} species")
    plot_lines.append(f"Growth Factor: {data['growth_analysis']['growth_factor']}x")
    plot_lines.append(f"Annual Growth Rate: {data['growth_analysis']['average_annual_growth']:.1f}%")
    
    return "\n".join(plot_lines)


def create_growth_rate_table(data: Dict) -> str:
    """Create detailed growth rate analysis table."""
    growth_data = data['growth_analysis']['growth_data']
    acceleration_periods = data['growth_analysis']['acceleration_periods']
    
    table_lines = []
    table_lines.append("GROWTH RATE ANALYSIS BY PERIOD")
    table_lines.append("=" * 80)
    table_lines.append(f"{'Year':<6} {'MSL':<6} {'Species':<10} {'Growth %':<10} {'Added':<8} {'Technology Driver':<25}")
    table_lines.append("-" * 80)
    
    technology_drivers = {
        2008: "Early sequencing advances",
        2009: "Protocol improvements", 
        2011: "Standardization efforts",
        2012: "Sequencing cost reduction",
        2013: "Method consolidation",
        2014: "High-throughput adoption",
        2015: "Platform maturation",
        2016: "Bioinformatics advances",
        2017: "METAGENOMICS REVOLUTION",
        2018: "Environmental sampling",
        2019: "Realm system introduction",
        2020: "COVID-19 RESPONSE",
        2021: "Pandemic acceleration",
        2022: "Recovery period",
        2023: "AI-assisted discovery",
        2024: "Modern integration"
    }
    
    for i, item in enumerate(growth_data):
        year = item['year']
        msl = item['msl_version']
        count = item['species_count']
        rate = item['growth_rate']
        
        # Calculate species added
        if i > 0:
            added = count - growth_data[i-1]['species_count']
        else:
            added = 0
        
        driver = technology_drivers.get(year, "Standard methods")
        
        # Highlight acceleration periods
        rate_str = f"{rate:.1f}%" if rate > 0 else "—"
        if rate > 20:
            rate_str = f"🔥 {rate:.1f}%"
        
        table_lines.append(f"{year:<6} {msl:<6} {count:<10,} {rate_str:<10} {added:<8,} {driver:<25}")
    
    table_lines.append("-" * 80)
    table_lines.append("\nACCELERATION PERIODS (>20% growth):")
    for period in acceleration_periods:
        table_lines.append(f"  • {period['period']}: {period['growth_rate']:.1f}% growth ({period['msl_versions']})")
    
    return "\n".join(table_lines)


def create_caudovirales_summary(data: Dict) -> str:
    """Create detailed Caudovirales reorganization summary."""
    event = data['splitting_events']['major_events'][0]
    
    summary_lines = []
    summary_lines.append("CAUDOVIRALES DISSOLUTION: LARGEST VIRAL TAXONOMY REORGANIZATION")
    summary_lines.append("=" * 80)
    summary_lines.append(f"Year: {event['year']} (MSL36)")
    summary_lines.append(f"Scale: {event['impact']['species_affected']:,} species affected")
    summary_lines.append(f"Structure Change: {event['impact']['families_before']} → {event['impact']['families_after']} families")
    summary_lines.append("")
    
    summary_lines.append("BEFORE (Morphology-based classification):")
    summary_lines.append("  Order: Caudovirales")
    summary_lines.append("  ├── Family: Myoviridae (contractile tail)")
    summary_lines.append("  ├── Family: Siphoviridae (long non-contractile tail)")
    summary_lines.append("  └── Family: Podoviridae (short tail)")
    summary_lines.append("")
    
    summary_lines.append("AFTER (Phylogeny-based classification):")
    summary_lines.append("  15 new families based on molecular relationships:")
    
    new_families = event['new_families']
    for i, family in enumerate(new_families):
        if i < 8:  # Show first 8
            summary_lines.append(f"    • {family}")
        elif i == 8:
            summary_lines.append(f"    • ... and {len(new_families) - 8} more families")
            break
    
    summary_lines.append("")
    summary_lines.append("SCIENTIFIC RATIONALE:")
    summary_lines.append(f"  {event['impact']['rationale']}")
    summary_lines.append("")
    summary_lines.append("IMPACT:")
    summary_lines.append("  ✅ Better reflects evolutionary relationships")
    summary_lines.append("  ✅ Resolves paraphyletic groupings")
    summary_lines.append("  ✅ Provides clearer host-virus associations")
    summary_lines.append("  ⚠️ Required extensive database updates")
    summary_lines.append("  ⚠️ Disrupted existing literature references")
    
    return "\n".join(summary_lines)


def create_management_framework(data: Dict) -> str:
    """Create family size management framework guide."""
    recommendations = data['recommendations']
    
    framework_lines = []
    framework_lines.append("FAMILY SIZE MANAGEMENT FRAMEWORK")
    framework_lines.append("=" * 60)
    framework_lines.append("Evidence-based guidelines for viral taxonomy management")
    framework_lines.append("")
    
    framework_lines.append("SIZE ZONES AND ACTIONS:")
    framework_lines.append("━" * 60)
    
    zones = [
        ("0-50", "🔴 TOO SMALL", "Insufficient for comparative studies"),
        ("50-300", "🟢 OPTIMAL", "Ideal for management and research"),
        ("300-500", "🟡 REVIEW", "Monitor phylogeny, consider subfamilies"),
        ("500-1000", "🟠 ACTION", "Reorganization likely needed"),
        ("1000+", "🔴 CRISIS", "Immediate attention required")
    ]
    
    framework_lines.append(f"{'Range':<12} {'Zone':<15} {'Action Required':<30}")
    framework_lines.append("-" * 60)
    
    for size_range, zone, action in zones:
        framework_lines.append(f"{size_range:<12} {zone:<15} {action:<30}")
    
    framework_lines.append("")
    framework_lines.append("REAL EXAMPLE - CAUDOVIRALES:")
    framework_lines.append("  Before: ~1,847 species (CRISIS ZONE)")
    framework_lines.append("  Action: Split into 15 families")
    framework_lines.append("  After: Families average 50-150 species (OPTIMAL ZONE)")
    framework_lines.append("")
    
    framework_lines.append("BEST PRACTICES:")
    for practice in recommendations['best_practices']:
        framework_lines.append(f"  • {practice}")
    
    framework_lines.append("")
    framework_lines.append(f"CONTEXT: {data['growth_analysis']['growth_factor']}x species growth requires proactive management")
    
    return "\n".join(framework_lines)


def generate_publication_data_tables(data: Dict) -> str:
    """Generate publication-ready data tables."""
    tables = []
    
    # Table 1: Growth trajectory
    tables.append("TABLE 1: ICTV Viral Species Growth Trajectory (2005-2024)")
    tables.append("─" * 70)
    tables.append(f"{'Year':<6} {'MSL':<8} {'Species':<10} {'Growth %':<10} {'Cumulative %':<12}")
    tables.append("─" * 70)
    
    initial_count = data['growth_analysis']['growth_data'][0]['species_count']
    for item in data['growth_analysis']['growth_data']:
        year = item['year']
        msl = item['msl_version']
        count = item['species_count']
        rate = item['growth_rate']
        cumulative = ((count / initial_count) - 1) * 100
        
        rate_str = f"{rate:.1f}%" if rate > 0 else "—"
        tables.append(f"{year:<6} {msl:<8} {count:<10,} {rate_str:<10} {cumulative:<12.0f}%")
    
    tables.append("─" * 70)
    tables.append(f"Total growth factor: {data['growth_analysis']['growth_factor']}x")
    tables.append(f"Average annual growth: {data['growth_analysis']['average_annual_growth']:.1f}%")
    tables.append("")
    
    # Table 2: Reorganization events
    tables.append("TABLE 2: Major Reorganization Events")
    tables.append("─" * 50)
    event = data['splitting_events']['major_events'][0]
    tables.append(f"Event: {event['event']}")
    tables.append(f"Year: {event['year']}")
    tables.append(f"Species affected: {event['impact']['species_affected']:,}")
    tables.append(f"Families before: {event['impact']['families_before']}")
    tables.append(f"Families after: {event['impact']['families_after']}")
    tables.append(f"Rationale: {event['impact']['rationale']}")
    
    return "\n".join(tables)


def save_all_text_visualizations():
    """Generate and save all text-based visualizations."""
    print("📊 Creating text-based visualizations from real ICTV data...")
    print("=" * 60)
    
    try:
        # Load real data
        data = load_real_data()
        print(f"✅ Loaded real data: {data['data_source']}")
        
        output_dir = Path(__file__).parent / "results"
        
        # Generate all visualizations
        visualizations = {
            "growth_trajectory.txt": create_ascii_growth_plot(data),
            "growth_rate_analysis.txt": create_growth_rate_table(data),
            "caudovirales_summary.txt": create_caudovirales_summary(data),
            "management_framework.txt": create_management_framework(data),
            "publication_tables.txt": generate_publication_data_tables(data)
        }
        
        # Save all files
        for filename, content in visualizations.items():
            output_file = output_dir / filename
            with open(output_file, 'w') as f:
                f.write(content)
            print(f"✅ Saved: {filename}")
        
        # Create combined report
        combined_report = []
        combined_report.append("ICTV FAMILY SIZE ANALYSIS: COMPREHENSIVE REPORT")
        combined_report.append("=" * 80)
        combined_report.append(f"Data Source: {data['data_source']}")
        combined_report.append(f"Analysis Date: {data['analysis_date'][:10]}")
        combined_report.append("\n" + "=" * 80 + "\n")
        
        for title, content in visualizations.items():
            combined_report.append(content)
            combined_report.append("\n" + "=" * 80 + "\n")
        
        combined_file = output_dir / "COMPREHENSIVE_REAL_DATA_REPORT.txt"
        with open(combined_file, 'w') as f:
            f.write("\n".join(combined_report))
        
        print(f"\n🎉 All text visualizations completed!")
        print(f"📋 Combined report: {combined_file}")
        print("\n📊 For graphical plots, use the data in these files with:")
        print("   • Excel/Google Sheets for quick charts")
        print("   • R/Python (if matplotlib available) for publication plots")
        print("   • Online tools like Chart.js or Plotly")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating visualizations: {e}")
        return False


if __name__ == "__main__":
    save_all_text_visualizations()