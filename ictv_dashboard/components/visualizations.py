"""
Interactive Visualization Components for ICTV Dashboard

Convert static plots to interactive Plotly visualizations with 
real-time parameter updates.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any

def create_interactive_plots(assessments: List[Dict[str, Any]], 
                           weights: Dict[str, float],
                           thresholds: Dict[str, int]) -> Dict[str, go.Figure]:
    """Create all interactive dashboard plots."""
    
    if not assessments:
        # Return empty plots if no data
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False
        )
        return {
            'risk_distribution': empty_fig,
            'intervention_distribution': empty_fig,
            'risk_matrix': empty_fig,
            'intervention_timeline': empty_fig
        }
    
    df = pd.DataFrame(assessments)
    
    plots = {}
    
    # 1. Risk Distribution
    plots['risk_distribution'] = create_risk_distribution(df)
    
    # 2. Intervention Distribution
    plots['intervention_distribution'] = create_intervention_distribution(df)
    
    # 3. Interactive Risk Matrix
    plots['risk_matrix'] = create_risk_matrix(df)
    
    # 4. Intervention Timeline
    plots['intervention_timeline'] = create_intervention_timeline(df)
    
    return plots

def create_risk_distribution(df: pd.DataFrame) -> go.Figure:
    """Create interactive risk category distribution chart."""
    
    # Count families by risk category
    category_counts = df['risk_category'].value_counts()
    
    # Define colors for consistency
    colors = {
        'Low Risk': '#4caf50',
        'Medium Risk': '#ffc107', 
        'High Risk': '#ff9800',
        'Crisis': '#f44336'
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=category_counts.index,
            y=category_counts.values,
            marker_color=[colors.get(cat, '#666666') for cat in category_counts.index],
            text=category_counts.values,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Families: %{y}<br><extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="Current Risk Distribution<br><sub>ICTV Family Instability Assessment</sub>",
        xaxis_title="Risk Category",
        yaxis_title="Number of Families",
        showlegend=False,
        height=400,
        template='plotly_white'
    )
    
    return fig

def create_intervention_distribution(df: pd.DataFrame) -> go.Figure:
    """Create interactive intervention type distribution chart."""
    
    # Count families by intervention type
    intervention_counts = df['intervention_type'].value_counts()
    
    # Define colors for intervention types
    colors = {
        'Monitor': '#4caf50',
        'Review': '#ffc107',
        'Split': '#ff9800', 
        'Emergency': '#f44336'
    }
    
    fig = go.Figure(data=[
        go.Bar(
            x=intervention_counts.index,
            y=intervention_counts.values,
            marker_color=[colors.get(int_type, '#666666') for int_type in intervention_counts.index],
            text=intervention_counts.values,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Families: %{y}<br><extra></extra>'
        )
    ])
    
    fig.update_layout(
        title="Recommended Interventions<br><sub>Proactive Management Strategy</sub>",
        xaxis_title="Intervention Type",
        yaxis_title="Number of Families",
        showlegend=False,
        height=400,
        template='plotly_white'
    )
    
    return fig

def create_risk_matrix(df: pd.DataFrame) -> go.Figure:
    """Create interactive family risk assessment matrix."""
    
    # Create color mapping
    color_map = {
        'Low Risk': '#4caf50',
        'Medium Risk': '#ffc107',
        'High Risk': '#ff9800',
        'Crisis': '#f44336'
    }
    
    fig = go.Figure()
    
    # Add scatter plot with risk zones
    fig.add_trace(go.Scatter(
        x=df['current_size'],
        y=df['risk_score'],
        mode='markers',
        marker=dict(
            size=df['growth_rate'] * 500 + 10,  # Size based on growth rate
            color=[color_map.get(cat, '#666666') for cat in df['risk_category']],
            opacity=0.7,
            line=dict(width=1, color='darkgray')
        ),
        text=df['family_name'],
        hovertemplate=
        '<b>%{text}</b><br>' +
        'Size: %{x} species<br>' +
        'Risk Score: %{y:.1f}/10<br>' +
        'Growth Rate: %{marker.size}<br>' +
        '<extra></extra>',
        name='Families'
    ))
    
    # Add risk zone backgrounds
    fig.add_shape(
        type="rect",
        x0=0, y0=0, x1=2000, y1=3,
        fillcolor="rgba(76, 175, 80, 0.1)",
        line=dict(width=0),
        layer="below"
    )
    
    fig.add_shape(
        type="rect", 
        x0=0, y0=3, x1=2000, y1=5,
        fillcolor="rgba(255, 193, 7, 0.1)",
        line=dict(width=0),
        layer="below"
    )
    
    fig.add_shape(
        type="rect",
        x0=0, y0=5, x1=2000, y1=10,
        fillcolor="rgba(255, 152, 0, 0.1)", 
        line=dict(width=0),
        layer="below"
    )
    
    # Add zone labels
    fig.add_annotation(
        x=50, y=1.5,
        text="OPTIMAL<br>ZONE",
        showarrow=False,
        font=dict(size=14, color='green'),
        bgcolor="rgba(255,255,255,0.8)"
    )
    
    fig.add_annotation(
        x=200, y=4,
        text="WARNING<br>ZONE", 
        showarrow=False,
        font=dict(size=14, color='orange'),
        bgcolor="rgba(255,255,255,0.8)"
    )
    
    fig.add_annotation(
        x=800, y=7,
        text="DANGER<br>ZONE",
        showarrow=False,
        font=dict(size=14, color='red'),
        bgcolor="rgba(255,255,255,0.8)"
    )
    
    fig.update_layout(
        title="Family Risk Assessment Matrix<br><sub>Bubble Size = Growth Rate | Color = Risk Category</sub>",
        xaxis_title="Family Size (Number of Species)",
        yaxis_title="Risk Score (0-10)",
        xaxis_type="log",
        yaxis=dict(range=[0, 10]),
        height=500,
        template='plotly_white',
        showlegend=False
    )
    
    return fig

def create_intervention_timeline(df: pd.DataFrame) -> go.Figure:
    """Create intervention timeline and workload projection."""
    
    # Filter families needing intervention
    intervention_families = df[df['intervention_type'].isin(['Split', 'Emergency'])].copy()
    
    if intervention_families.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No immediate interventions needed",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color='green')
        )
        fig.update_layout(
            title="Predicted Intervention Timeline<br><sub>Proactive Management Schedule</sub>",
            height=400,
            template='plotly_white'
        )
        return fig
    
    # Create subplot with timeline and workload
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Predicted Intervention Timeline', 'Projected Committee Workload'),
        vertical_spacing=0.15,
        row_heights=[0.6, 0.4]
    )
    
    # Timeline plot (top)
    current_year = 2025
    
    # Simulate intervention timeline based on risk scores
    intervention_families['predicted_year'] = current_year + (
        intervention_families['risk_score'] / 10 * 2
    )  # Higher risk = sooner intervention
    
    # Add timeline scatter
    fig.add_trace(
        go.Scatter(
            x=intervention_families['predicted_year'],
            y=list(range(len(intervention_families))),
            mode='markers+text',
            marker=dict(
                size=15,
                color=['#ff9800' if it == 'Split' else '#f44336' 
                       for it in intervention_families['intervention_type']],
                symbol='circle'
            ),
            text=intervention_families['family_name'],
            textposition='middle right',
            hovertemplate='<b>%{text}</b><br>Predicted: %{x:.1f}<br><extra></extra>',
            showlegend=False
        ),
        row=1, col=1
    )
    
    # Workload projection (bottom)
    years = np.arange(current_year, current_year + 3, 0.25)
    workload_scores = []
    
    for year in years:
        # Calculate workload based on interventions in that timeframe
        active_interventions = intervention_families[
            (intervention_families['predicted_year'] >= year - 0.5) & 
            (intervention_families['predicted_year'] <= year + 0.5)
        ]
        
        workload = len(active_interventions) * 5  # 5 units per intervention
        workload_scores.append(workload)
    
    fig.add_trace(
        go.Bar(
            x=years,
            y=workload_scores,
            marker_color='steelblue',
            opacity=0.7,
            showlegend=False
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title="Predicted Intervention Timeline<br><sub>Proactive Management Schedule</sub>",
        height=600,
        template='plotly_white'
    )
    
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_yaxes(title_text="Intervention Sequence", row=1, col=1)
    fig.update_yaxes(title_text="Committee Workload Score", row=2, col=1)
    
    return fig