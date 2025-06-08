#!/usr/bin/env python3
"""
Generate visual HTML report for taxonomy changes.

This script creates an interactive HTML report showing
the Caudovirales reclassification.
"""

import sys
from pathlib import Path
import json
import logging

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_html_report():
    """Generate HTML visualization report."""
    
    # Load the migration data
    output_dir = Path(__file__).parent.parent / 'output'
    
    try:
        with open(output_dir / 'caudovirales_migration_flow.json') as f:
            flow_data = json.load(f)
        
        with open(output_dir / 'caudovirales_migration_stats.json') as f:
            stats_data = json.load(f)
    except FileNotFoundError:
        logger.error("Migration data not found. Please run analyze_caudovirales_migration.py first")
        return False
    
    # Generate HTML report
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ICTV Caudovirales Reclassification Report</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <script src="https://unpkg.com/d3-sankey@0.12.3/dist/d3-sankey.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 10px;
        }}
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }}
        .section {{
            margin: 30px 0;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat-card {{
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 20px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 36px;
            font-weight: bold;
            color: #2c5282;
            margin: 10px 0;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        .old-family {{
            color: #dc3545;
        }}
        .new-family {{
            color: #28a745;
        }}
        .migration-chart {{
            margin: 30px 0;
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 20px;
        }}
        .node rect {{
            cursor: pointer;
        }}
        .node text {{
            font: 12px sans-serif;
            pointer-events: none;
        }}
        .link {{
            fill: none;
            stroke-opacity: 0.5;
        }}
        .link:hover {{
            stroke-opacity: 0.8;
        }}
        .family-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .family-table th {{
            background-color: #f8f9fa;
            padding: 12px;
            text-align: left;
            border-bottom: 2px solid #dee2e6;
        }}
        .family-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #dee2e6;
        }}
        .removed {{
            color: #dc3545;
            font-weight: bold;
        }}
        .citation {{
            background-color: #e9ecef;
            padding: 15px;
            border-radius: 5px;
            margin-top: 30px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>ICTV Caudovirales Reclassification Analysis</h1>
        <div class="subtitle">Tracking the dissolution of morphology-based families (MSL36 → MSL37)</div>
        
        <div class="section">
            <h2>Summary Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-label">Caudovirales Species (MSL36)</div>
                    <div class="stat-number">{stats_data['before']['total_species']:,}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Caudovirales Species (MSL37)</div>
                    <div class="stat-number">{stats_data['after']['total_species']:,}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Species Migrated</div>
                    <div class="stat-number">{sum(m['total'] for m in stats_data['migration_summary'].values())}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">New Families Created</div>
                    <div class="stat-number">{stats_data['after']['new_families_count']}</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>Old Morphology-Based Families (MSL36)</h2>
            <table class="family-table">
                <thead>
                    <tr>
                        <th>Family</th>
                        <th>Species Count</th>
                        <th>Fate in MSL37</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Add old families data
    for family, count in stats_data['before']['families'].items():
        fate = "Partially migrated" if family in stats_data['migration_summary'] else "Retained"
        html_content += f"""
                    <tr>
                        <td class="old-family">{family}</td>
                        <td>{count:,}</td>
                        <td>{fate}</td>
                    </tr>
"""
    
    html_content += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>Migration Flow Visualization</h2>
            <div class="migration-chart">
                <div id="sankey"></div>
            </div>
        </div>
        
        <div class="section">
            <h2>Detailed Migration Summary</h2>
"""
    
    # Add migration details
    for old_family, migration in stats_data['migration_summary'].items():
        if migration['total'] > 0:
            html_content += f"""
            <h3>{old_family} → New Families</h3>
            <table class="family-table">
                <thead>
                    <tr>
                        <th>New Family</th>
                        <th>Species Count</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
"""
            for new_family, count in migration['top_destinations']:
                percentage = (count / migration['total']) * 100
                html_content += f"""
                    <tr>
                        <td class="new-family">{new_family}</td>
                        <td>{count}</td>
                        <td>{percentage:.1f}%</td>
                    </tr>
"""
            html_content += """
                </tbody>
            </table>
"""
    
    html_content += f"""
        </div>
        
        <div class="citation">
            <strong>Data Source:</strong> International Committee on Taxonomy of Viruses (ICTV)<br>
            <strong>Analysis:</strong> ICTV-git project - Git-based version control for viral taxonomy<br>
            <strong>Generated:</strong> {Path(__file__).parent.parent.name} repository
        </div>
    </div>
    
    <script>
        // Load flow data
        const flowData = {json.dumps(flow_data)};
        
        // Set dimensions
        const margin = {{top: 10, right: 10, bottom: 10, left: 10}};
        const width = 1100 - margin.left - margin.right;
        const height = 600 - margin.top - margin.bottom;
        
        // Create SVG
        const svg = d3.select("#sankey")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${{margin.left}},${{margin.top}})`);
        
        // Create sankey diagram
        const sankey = d3.sankey()
            .nodeWidth(15)
            .nodePadding(10)
            .extent([[1, 1], [width - 1, height - 6]]);
        
        // Process data
        const {{nodes, links}} = sankey(flowData);
        
        // Color scale
        const color = d3.scaleOrdinal()
            .domain(["old_family", "new_family", "removed"])
            .range(["#dc3545", "#28a745", "#6c757d"]);
        
        // Add links
        svg.append("g")
            .selectAll("path")
            .data(links)
            .enter().append("path")
            .attr("class", "link")
            .attr("d", d3.sankeyLinkHorizontal())
            .attr("stroke", d => color(d.source.type))
            .attr("stroke-width", d => Math.max(1, d.width))
            .append("title")
            .text(d => `${{d.source.name}} → ${{d.target.name}}: ${{d.value}} species`);
        
        // Add nodes
        const node = svg.append("g")
            .selectAll("g")
            .data(nodes)
            .enter().append("g");
        
        node.append("rect")
            .attr("x", d => d.x0)
            .attr("y", d => d.y0)
            .attr("height", d => d.y1 - d.y0)
            .attr("width", d => d.x1 - d.x0)
            .attr("fill", d => color(d.type))
            .append("title")
            .text(d => `${{d.name}}: ${{d.value}} species`);
        
        node.append("text")
            .attr("x", d => d.x0 < width / 2 ? d.x1 + 6 : d.x0 - 6)
            .attr("y", d => (d.y1 + d.y0) / 2)
            .attr("dy", "0.35em")
            .attr("text-anchor", d => d.x0 < width / 2 ? "start" : "end")
            .text(d => d.name)
            .filter(d => d.x0 < width / 2)
            .attr("x", d => d.x1 + 6);
    </script>
</body>
</html>
"""
    
    # Save HTML report
    report_path = output_dir / 'caudovirales_visual_report.html'
    with open(report_path, 'w') as f:
        f.write(html_content)
    
    logger.info(f"Visual report generated: {report_path}")
    print(f"\nVisual report saved to: {report_path}")
    print(f"Open in browser: file://{report_path.absolute()}")
    
    return True


if __name__ == "__main__":
    success = generate_html_report()
    sys.exit(0 if success else 1)