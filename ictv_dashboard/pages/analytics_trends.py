"""
Analytics and Trend Analysis Page

Historical trend analysis, system health monitoring, and predictive analytics
for ICTV family management.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys

# Add dashboard root to path
dashboard_root = Path(__file__).parent.parent
if str(dashboard_root) not in sys.path:
    sys.path.insert(0, str(dashboard_root))

from components.risk_engine import FamilyRiskCalculator
from utils.data_manager import load_family_data, get_family_statistics
from config.settings import DEFAULT_RISK_WEIGHTS, RISK_CATEGORIES

def show_analytics_trends():
    """Main analytics and trends page."""
    
    st.header("📈 Analytics & Trend Analysis")
    
    # Analytics tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏥 System Health",
        "📊 Family Trends",
        "🎯 Intervention Success",
        "🔮 Predictive Analytics"
    ])
    
    with tab1:
        show_system_health()
    
    with tab2:
        show_family_trends()
    
    with tab3:
        show_intervention_success()
    
    with tab4:
        show_predictive_analytics()

def show_system_health():
    """Overall ICTV system health dashboard."""
    
    st.subheader("🏥 ICTV System Health Dashboard")
    
    # Calculate system metrics
    risk_calculator = FamilyRiskCalculator()
    families_data = load_family_data()
    assessments = risk_calculator.assess_all_families(families_data)
    system_health = risk_calculator.get_system_health(assessments)
    
    # System stability score (0-100)
    stability_score = int(system_health['system_stability'] * 10)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "System Stability Score",
            f"{stability_score}%",
            delta=f"+{stability_score - 65}%" if stability_score > 65 else f"{stability_score - 65}%",
            help="Overall health of the ICTV taxonomy system (0-100%)"
        )
    
    with col2:
        st.metric(
            "Total Families",
            system_health['total_families'],
            help="Number of viral families in the system"
        )
    
    with col3:
        st.metric(
            "Average Risk",
            f"{system_health['average_risk']:.1f}/10",
            delta="-0.3" if system_health['average_risk'] < 3.5 else "+0.5",
            help="Average risk score across all families"
        )
    
    with col4:
        st.metric(
            "Committee Workload",
            f"{system_health['intervention_workload']} units",
            help="Estimated committee hours needed for interventions"
        )
    
    # Risk distribution over time (simulated historical data)
    st.markdown("### Risk Distribution Evolution")
    
    # Generate simulated historical data
    months = pd.date_range(end=datetime.now(), periods=12, freq='M')
    risk_evolution_data = []
    
    for month in months:
        # Simulate risk distribution changes
        base_counts = system_health['families_by_category']
        for category, count in base_counts.items():
            # Add some random variation
            variation = np.random.normal(0, 0.1)
            adjusted_count = max(0, int(count * (1 + variation)))
            
            risk_evolution_data.append({
                'Date': month,
                'Category': category,
                'Count': adjusted_count
            })
    
    df_evolution = pd.DataFrame(risk_evolution_data)
    
    # Stacked area chart
    fig_evolution = px.area(
        df_evolution,
        x='Date',
        y='Count',
        color='Category',
        color_discrete_map={
            'Low Risk': '#4caf50',
            'Medium Risk': '#ffc107',
            'High Risk': '#ff9800',
            'Crisis': '#f44336'
        },
        title="Risk Category Distribution Over Time"
    )
    
    fig_evolution.update_layout(height=400)
    st.plotly_chart(fig_evolution, use_container_width=True)
    
    # System health indicators
    st.markdown("### Health Indicators")
    
    indicator_cols = st.columns(3)
    
    with indicator_cols[0]:
        # Stability trend
        stability_trend = [65, 68, 70, 72, 69, 67, stability_score]
        
        fig_stability = go.Figure()
        fig_stability.add_trace(go.Scatter(
            y=stability_trend,
            mode='lines+markers',
            line=dict(color='#4caf50' if stability_score > 65 else '#ff9800', width=3),
            marker=dict(size=8)
        ))
        
        fig_stability.update_layout(
            title="Stability Trend",
            yaxis_title="Score (%)",
            height=250,
            showlegend=False
        )
        
        st.plotly_chart(fig_stability, use_container_width=True)
    
    with indicator_cols[1]:
        # Intervention success rate
        success_rate = 0.78  # 78% success rate
        
        fig_success = go.Figure(go.Indicator(
            mode="gauge+number",
            value=success_rate * 100,
            title={'text': "Intervention Success Rate"},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#4caf50"},
                'steps': [
                    {'range': [0, 50], 'color': "#ffebee"},
                    {'range': [50, 70], 'color': "#fff3e0"},
                    {'range': [70, 100], 'color': "#e8f5e9"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig_success.update_layout(height=250)
        st.plotly_chart(fig_success, use_container_width=True)
    
    with indicator_cols[2]:
        # Committee efficiency
        avg_resolution_time = 4.2  # months
        
        fig_efficiency = go.Figure()
        fig_efficiency.add_trace(go.Bar(
            x=['Target', 'Actual'],
            y=[3.0, avg_resolution_time],
            marker_color=['#1f77b4', '#ff7f0e']
        ))
        
        fig_efficiency.update_layout(
            title="Avg Resolution Time",
            yaxis_title="Months",
            height=250,
            showlegend=False
        )
        
        st.plotly_chart(fig_efficiency, use_container_width=True)

def show_family_trends():
    """Individual family trend analysis."""
    
    st.subheader("📊 Family Risk Evolution")
    
    # Family selection
    families_data = load_family_data()
    selected_families = st.multiselect(
        "Select families to analyze:",
        [f['family_name'] for f in families_data],
        default=[families_data[0]['family_name'], families_data[1]['family_name']]
    )
    
    if selected_families:
        # Time range selection
        time_range = st.select_slider(
            "Time Range",
            options=["6 months", "1 year", "2 years", "5 years"],
            value="1 year"
        )
        
        # Generate trend data
        time_periods = {
            "6 months": 6,
            "1 year": 12,
            "2 years": 24,
            "5 years": 60
        }
        
        periods = time_periods[time_range]
        dates = pd.date_range(end=datetime.now(), periods=periods, freq='M')
        
        # Create trend chart
        fig = go.Figure()
        
        for family_name in selected_families:
            family_data = next(f for f in families_data if f['family_name'] == family_name)
            
            # Simulate historical risk scores
            base_risk = family_data['current_size'] / 50
            risk_scores = []
            
            for i in range(periods):
                # Add trend and noise
                trend = i * family_data['growth_rate'] / 12
                noise = np.random.normal(0, 0.2)
                risk = min(10, max(0, base_risk + trend + noise))
                risk_scores.append(risk)
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=risk_scores,
                mode='lines+markers',
                name=family_name,
                line=dict(width=3)
            ))
        
        # Add risk zone backgrounds
        fig.add_hrect(y0=0, y1=3, fillcolor="rgba(76, 175, 80, 0.1)", layer="below")
        fig.add_hrect(y0=3, y1=5, fillcolor="rgba(255, 193, 7, 0.1)", layer="below")
        fig.add_hrect(y0=5, y1=7, fillcolor="rgba(255, 152, 0, 0.1)", layer="below")
        fig.add_hrect(y0=7, y1=10, fillcolor="rgba(244, 67, 54, 0.1)", layer="below")
        
        fig.update_layout(
            title="Family Risk Score Evolution",
            xaxis_title="Date",
            yaxis_title="Risk Score (0-10)",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Growth rate comparison
        st.markdown("### Growth Rate Analysis")
        
        growth_data = []
        for family_name in selected_families:
            family_data = next(f for f in families_data if f['family_name'] == family_name)
            
            # Simulate quarterly growth rates
            for i in range(4):
                quarter = f"Q{i+1} 2024"
                growth = family_data['growth_rate'] * (1 + np.random.normal(0, 0.1))
                growth_data.append({
                    'Family': family_name,
                    'Quarter': quarter,
                    'Growth Rate': max(0, growth)
                })
        
        df_growth = pd.DataFrame(growth_data)
        
        fig_growth = px.bar(
            df_growth,
            x='Quarter',
            y='Growth Rate',
            color='Family',
            barmode='group',
            title="Quarterly Growth Rate Comparison"
        )
        
        fig_growth.update_layout(
            yaxis_title="Growth Rate (%)",
            yaxis_tickformat='.0%',
            height=350
        )
        
        st.plotly_chart(fig_growth, use_container_width=True)

def show_intervention_success():
    """Intervention success metrics and post-reorganization tracking."""
    
    st.subheader("🎯 Intervention Success Metrics")
    
    # Sample intervention data
    interventions = [
        {
            'family': 'Siphoviridae',
            'date': '2021-03-15',
            'type': 'Major Split',
            'pre_size': 1847,
            'post_families': 15,
            'stability_score': 8.2,
            'success': True
        },
        {
            'family': 'Podoviridae',
            'date': '2021-03-15',
            'type': 'Major Split',
            'pre_size': 517,
            'post_families': 8,
            'stability_score': 7.8,
            'success': True
        },
        {
            'family': 'Myoviridae',
            'date': '2021-03-15',
            'type': 'Major Split',
            'pre_size': 1088,
            'post_families': 12,
            'stability_score': 7.5,
            'success': True
        }
    ]
    
    # Success metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        success_rate = len([i for i in interventions if i['success']]) / len(interventions)
        st.metric("Overall Success Rate", f"{success_rate:.0%}")
    
    with col2:
        avg_stability = np.mean([i['stability_score'] for i in interventions])
        st.metric("Average Post-Split Stability", f"{avg_stability:.1f}/10")
    
    with col3:
        total_species = sum([i['pre_size'] for i in interventions])
        st.metric("Total Species Reorganized", f"{total_species:,}")
    
    # Before/After comparison
    st.markdown("### Intervention Impact Analysis")
    
    # Create before/after visualization
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Pre-Intervention", "Post-Intervention"),
        specs=[[{"type": "treemap"}, {"type": "treemap"}]]
    )
    
    # Pre-intervention (large families)
    pre_labels = [i['family'] for i in interventions]
    pre_values = [i['pre_size'] for i in interventions]
    
    fig.add_trace(go.Treemap(
        labels=pre_labels,
        values=pre_values,
        parents=[""] * len(pre_labels),
        textinfo="label+value",
        marker=dict(colorscale='Reds')
    ), row=1, col=1)
    
    # Post-intervention (distributed families)
    post_labels = []
    post_values = []
    post_parents = []
    
    for intervention in interventions:
        avg_size = intervention['pre_size'] // intervention['post_families']
        for i in range(min(5, intervention['post_families'])):  # Show first 5 families
            post_labels.append(f"New Family {i+1}")
            post_values.append(avg_size)
            post_parents.append(intervention['family'])
        
        post_labels.append(intervention['family'])
        post_values.append(0)
        post_parents.append("")
    
    fig.add_trace(go.Treemap(
        labels=post_labels,
        values=post_values,
        parents=post_parents,
        textinfo="label+value",
        marker=dict(colorscale='Greens')
    ), row=1, col=2)
    
    fig.update_layout(height=500, title_text="Family Reorganization Impact")
    st.plotly_chart(fig, use_container_width=True)
    
    # Stability tracking
    st.markdown("### Post-Intervention Stability Tracking")
    
    # Generate stability data over time
    months_post = pd.date_range(start='2021-04-01', periods=36, freq='M')
    
    fig_stability = go.Figure()
    
    for intervention in interventions[:3]:  # Show first 3
        # Simulate stability improvement
        initial_stability = 5.0
        stability_values = []
        
        for i, month in enumerate(months_post):
            # Stability improves over time after split
            improvement = (intervention['stability_score'] - initial_stability) * (1 - np.exp(-i/12))
            noise = np.random.normal(0, 0.1)
            stability = initial_stability + improvement + noise
            stability_values.append(min(10, max(0, stability)))
        
        fig_stability.add_trace(go.Scatter(
            x=months_post,
            y=stability_values,
            mode='lines',
            name=intervention['family'],
            line=dict(width=3)
        ))
    
    fig_stability.add_hline(y=7.0, line_dash="dash", line_color="green",
                           annotation_text="Target Stability")
    
    fig_stability.update_layout(
        title="Post-Split Stability Evolution",
        xaxis_title="Date",
        yaxis_title="Stability Score (0-10)",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_stability, use_container_width=True)

def show_predictive_analytics():
    """Predictive analytics and forecasting."""
    
    st.subheader("🔮 Predictive Analytics")
    
    # Load current data
    risk_calculator = FamilyRiskCalculator()
    families_data = load_family_data()
    assessments = risk_calculator.assess_all_families(families_data)
    
    # Prediction horizon
    horizon = st.select_slider(
        "Prediction Horizon",
        options=["1 year", "3 years", "5 years"],
        value="3 years"
    )
    
    horizon_years = int(horizon.split()[0])
    
    # High-risk family predictions
    st.markdown("### Families Likely to Require Intervention")
    
    # Calculate intervention probabilities
    predictions = []
    
    for assessment in assessments:
        # Enhanced prediction based on multiple factors
        base_prob = assessment['intervention_probability']
        
        # Adjust for time horizon
        time_adjusted_prob = 1 - (1 - base_prob) ** horizon_years
        
        if time_adjusted_prob > 0.3:  # Show only significant risks
            predictions.append({
                'Family': assessment['family_name'],
                'Current Risk': assessment['risk_score'],
                'Probability': time_adjusted_prob,
                'Predicted Year': 2025 + int(3 * (1 - time_adjusted_prob)),
                'Recommendation': assessment['intervention_type']
            })
    
    df_predictions = pd.DataFrame(predictions)
    
    if not df_predictions.empty:
        # Sort by probability
        df_predictions = df_predictions.sort_values('Probability', ascending=False)
        
        # Visualization
        fig_predictions = px.scatter(
            df_predictions,
            x='Predicted Year',
            y='Probability',
            size='Current Risk',
            color='Recommendation',
            hover_data=['Family'],
            title=f"Intervention Probability - {horizon} Horizon",
            color_discrete_map={
                'Monitor': '#4caf50',
                'Review': '#ffc107',
                'Split': '#ff9800',
                'Emergency': '#f44336'
            }
        )
        
        fig_predictions.update_layout(
            xaxis_title="Predicted Intervention Year",
            yaxis_title="Intervention Probability",
            yaxis_tickformat='.0%',
            height=400
        )
        
        st.plotly_chart(fig_predictions, use_container_width=True)
        
        # Detailed predictions table
        st.markdown("### Detailed Predictions")
        
        df_display = df_predictions[['Family', 'Current Risk', 'Probability', 'Predicted Year', 'Recommendation']].copy()
        df_display['Current Risk'] = df_display['Current Risk'].round(1)
        df_display['Probability'] = (df_display['Probability'] * 100).round(0).astype(int).astype(str) + '%'
        
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True
        )
    
    # System-wide predictions
    st.markdown("### System-Wide Forecasts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Predicted workload
        current_workload = risk_calculator.get_system_health(assessments)['intervention_workload']
        
        years = np.arange(2025, 2025 + horizon_years + 1)
        workload_projection = []
        
        for i, year in enumerate(years):
            # Exponential growth model
            projected = current_workload * (1.15 ** i)  # 15% annual growth
            workload_projection.append(projected)
        
        fig_workload = go.Figure()
        fig_workload.add_trace(go.Scatter(
            x=years,
            y=workload_projection,
            mode='lines+markers',
            fill='tozeroy',
            line=dict(color='#1f77b4', width=3)
        ))
        
        fig_workload.update_layout(
            title="Projected Committee Workload",
            xaxis_title="Year",
            yaxis_title="Workload Units",
            height=300
        )
        
        st.plotly_chart(fig_workload, use_container_width=True)
    
    with col2:
        # Predicted family count
        current_families = len(families_data)
        
        family_projection = []
        for i, year in enumerate(years):
            # Account for splits
            high_risk_count = len([a for a in assessments if a['risk_score'] > 5])
            splits_per_year = high_risk_count * 0.3  # 30% split probability
            projected = current_families + (splits_per_year * i * 3)  # 3 new families per split
            family_projection.append(int(projected))
        
        fig_families = go.Figure()
        fig_families.add_trace(go.Bar(
            x=years,
            y=family_projection,
            marker_color='#2ca02c'
        ))
        
        fig_families.update_layout(
            title="Projected Total Families",
            xaxis_title="Year",
            yaxis_title="Number of Families",
            height=300
        )
        
        st.plotly_chart(fig_families, use_container_width=True)
    
    # Recommendations
    st.markdown("### Strategic Recommendations")
    
    if current_workload > 50:
        st.warning("""
        ⚠️ **Resource Planning Required**
        - Current workload exceeds optimal capacity
        - Consider expanding committee or subcommittee structure
        - Prioritize high-probability interventions
        """)
    
    high_risk_percentage = len([a for a in assessments if a['risk_category'] in ['High Risk', 'Crisis']]) / len(assessments)
    
    if high_risk_percentage > 0.2:
        st.info("""
        ℹ️ **Proactive Intervention Recommended**
        - Over 20% of families in high-risk categories
        - Begin planning for multiple simultaneous interventions
        - Consider streamlined processes for common split patterns
        """)

# This page will be imported by the main app
if __name__ == "__main__":
    show_analytics_trends()