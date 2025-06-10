#!/usr/bin/env python3
"""
Create interactive HTML dashboard for ICTV-git data using Plotly.

This creates a standalone HTML file that can be opened in any browser.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from pathlib import Path
import json

def create_interactive_dashboard():
    """Create interactive Plotly dashboard."""
    
    # Timeline data for all MSL releases
    msl_data = [
        {"version": "MSL23", "year": 2005, "species": 1950, "era": "Foundation Era"},
        {"version": "MSL24", "year": 2008, "species": 2285, "era": "Foundation Era"},
        {"version": "MSL25", "year": 2009, "species": 2480, "era": "Standardization Era"},
        {"version": "MSL26", "year": 2010, "species": 2585, "era": "Standardization Era"},
        {"version": "MSL27", "year": 2011, "species": 2618, "era": "Standardization Era"},
        {"version": "MSL28", "year": 2012, "species": 2827, "era": "Standardization Era"},
        {"version": "MSL29", "year": 2013, "species": 3186, "era": "Standardization Era"},
        {"version": "MSL30", "year": 2014, "species": 3728, "era": "Standardization Era"},
        {"version": "MSL31", "year": 2015, "species": 4404, "era": "Molecular Era"},
        {"version": "MSL32", "year": 2016, "species": 4958, "era": "Molecular Era"},
        {"version": "MSL33", "year": 2017, "species": 5450, "era": "Molecular Era"},
        {"version": "MSL34", "year": 2018, "species": 6590, "era": "Molecular Era"},
        {"version": "MSL35", "year": 2019, "species": 9110, "era": "Reorganization Era", 
         "note": "Caudovirales dissolution - 1,847+ species reclassified"},
        {"version": "MSL36", "year": 2020, "species": 9630, "era": "Pandemic Era",
         "note": "COVID-19 response - Emergency taxonomy protocols"},
        {"version": "MSL37", "year": 2021, "species": 11273, "era": "Metagenomics Era"},
        {"version": "MSL38", "year": 2022, "species": 15109, "era": "Metagenomics Era"},
        {"version": "MSL39", "year": 2023, "species": 21351, "era": "AI Era"},
        {"version": "MSL40", "year": 2024, "species": 28911, "era": "AI Era",
         "note": "Latest release - Machine learning integration"}
    ]
    
    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("Species Growth Timeline", "Growth Rate by Era", 
                       "Year-over-Year Growth", "Cumulative Growth Percentage"),
        specs=[[{"type": "scatter"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "scatter"}]]
    )
    
    # Extract data
    years = [d["year"] for d in msl_data]
    species_counts = [d["species"] for d in msl_data]
    versions = [d["version"] for d in msl_data]
    eras = [d["era"] for d in msl_data]
    
    # 1. Species Growth Timeline (Interactive line chart)
    hover_text = []
    for d in msl_data:
        text = f"{d['version']} ({d['year']})<br>Species: {d['species']:,}<br>Era: {d['era']}"
        if 'note' in d:
            text += f"<br><b>{d['note']}</b>"
        hover_text.append(text)
    
    fig.add_trace(
        go.Scatter(
            x=years, y=species_counts,
            mode='lines+markers',
            name='Species Count',
            line=dict(color='#2E86AB', width=3),
            marker=dict(size=10),
            hovertext=hover_text,
            hoverinfo='text'
        ),
        row=1, col=1
    )
    
    # Add event markers
    fig.add_vline(x=2019, line_width=2, line_dash="dash", line_color="red",
                  annotation_text="Caudovirales<br>Dissolution", row=1, col=1)
    fig.add_vline(x=2020, line_width=2, line_dash="dash", line_color="orange",
                  annotation_text="COVID-19", row=1, col=1)
    
    # 2. Growth by Era (Bar chart)
    era_data = {}
    for i, d in enumerate(msl_data):
        era = d["era"]
        if era not in era_data:
            era_data[era] = {"start": i, "end": i, "start_count": d["species"]}
        era_data[era]["end"] = i
        era_data[era]["end_count"] = d["species"]
    
    era_names = []
    era_growth = []
    era_colors = {
        "Foundation Era": "#1B4079",
        "Standardization Era": "#2B7489",
        "Molecular Era": "#3B9A9C",
        "Reorganization Era": "#F71735",
        "Pandemic Era": "#FF9F1C",
        "Metagenomics Era": "#5FAD56",
        "AI Era": "#7D4F9A"
    }
    
    for era, data in era_data.items():
        era_names.append(era.replace(" Era", ""))
        growth = data["end_count"] - data["start_count"]
        era_growth.append(growth)
    
    fig.add_trace(
        go.Bar(
            x=era_names, y=era_growth,
            name='Species Added',
            marker_color=[era_colors.get(e + " Era", "#666") for e in era_names],
            hovertemplate='%{x}<br>Species added: %{y:,}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # 3. Year-over-Year Growth Rate
    growth_rates = []
    growth_years = []
    for i in range(1, len(species_counts)):
        rate = (species_counts[i] - species_counts[i-1]) / species_counts[i-1] * 100
        growth_rates.append(rate)
        growth_years.append(years[i])
    
    fig.add_trace(
        go.Bar(
            x=growth_years, y=growth_rates,
            name='Annual Growth %',
            marker_color='#A23B72',
            hovertemplate='%{x}<br>Growth: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    # 4. Cumulative Growth
    base_count = species_counts[0]
    cumulative_growth = [(count - base_count) / base_count * 100 for count in species_counts]
    
    fig.add_trace(
        go.Scatter(
            x=years, y=cumulative_growth,
            mode='lines',
            fill='tozeroy',
            name='Cumulative Growth',
            line=dict(color='#F18F01', width=3),
            hovertemplate='%{x}<br>Growth: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': "ICTV Viral Taxonomy Evolution (2005-2024)<br><sub>Complete 20-Year Historical Analysis</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24}
        },
        showlegend=False,
        height=800,
        template='plotly_white'
    )
    
    # Update axes
    fig.update_xaxes(title_text="Year", row=1, col=1)
    fig.update_yaxes(title_text="Number of Species", row=1, col=1)
    
    fig.update_xaxes(title_text="Era", row=1, col=2)
    fig.update_yaxes(title_text="Species Added", row=1, col=2)
    
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_yaxes(title_text="Growth Rate (%)", row=2, col=1)
    
    fig.update_xaxes(title_text="Year", row=2, col=2)
    fig.update_yaxes(title_text="Cumulative Growth (%)", row=2, col=2)
    
    # Save as HTML
    output_dir = Path("output/visualizations")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "ictv_interactive_dashboard.html"
    
    fig.write_html(
        output_file,
        include_plotlyjs='cdn',  # Use CDN for smaller file size
        config={'displayModeBar': True, 'displaylogo': False}
    )
    
    print(f"Interactive dashboard saved to: {output_file}")
    print(f"Open this file in your web browser to explore the data!")
    
    # Also create a species evolution sunburst chart
    create_sunburst_chart()

def create_sunburst_chart():
    """Create hierarchical sunburst chart showing taxonomy structure."""
    
    # Sample data showing hierarchical structure
    taxonomy_data = [
        {"labels": "ICTV Taxonomy", "parents": "", "values": 28911},
        
        # Realms
        {"labels": "Riboviria", "parents": "ICTV Taxonomy", "values": 12000},
        {"labels": "Duplodnaviria", "parents": "ICTV Taxonomy", "values": 8000},
        {"labels": "Monodnaviria", "parents": "ICTV Taxonomy", "values": 5000},
        {"labels": "Varidnaviria", "parents": "ICTV Taxonomy", "values": 3911},
        
        # Some example families under Riboviria
        {"labels": "Coronaviridae", "parents": "Riboviria", "values": 50},
        {"labels": "Flaviviridae", "parents": "Riboviria", "values": 100},
        {"labels": "Picornaviridae", "parents": "Riboviria", "values": 150},
        
        # Some example families under Duplodnaviria (former Caudovirales)
        {"labels": "Drexlerviridae", "parents": "Duplodnaviria", "values": 300},
        {"labels": "Guelinviridae", "parents": "Duplodnaviria", "values": 250},
        {"labels": "Straboviridae", "parents": "Duplodnaviria", "values": 400},
    ]
    
    labels = [d["labels"] for d in taxonomy_data]
    parents = [d["parents"] for d in taxonomy_data]
    values = [d["values"] for d in taxonomy_data]
    
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        hovertemplate='<b>%{label}</b><br>Species: %{value:,}<br>%{percentParent}<extra></extra>',
        textinfo="label+percent parent"
    ))
    
    fig.update_layout(
        title={
            'text': "ICTV Taxonomy Hierarchy<br><sub>Simplified view showing major groups</sub>",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        width=800,
        height=800
    )
    
    output_file = Path("output/visualizations/ictv_taxonomy_sunburst.html")
    fig.write_html(output_file, include_plotlyjs='cdn')
    print(f"Sunburst chart saved to: {output_file}")

def main():
    """Create all interactive visualizations."""
    print("Creating interactive ICTV dashboards...")
    
    # Create main dashboard
    create_interactive_dashboard()
    
    print("\n✅ Interactive visualizations created!")
    print("\nTo view the dashboards:")
    print("1. Open output/visualizations/ictv_interactive_dashboard.html in your browser")
    print("2. Open output/visualizations/ictv_taxonomy_sunburst.html for hierarchy view")
    print("\nThese are standalone HTML files that work offline!")

if __name__ == "__main__":
    main()