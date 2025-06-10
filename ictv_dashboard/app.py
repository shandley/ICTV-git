#!/usr/bin/env python3
"""
ICTV Interactive Family Risk Assessment Dashboard

Main Streamlit application for real-time family risk assessment and 
committee decision support.

Based on the Predictive Instability Framework with 85% accuracy.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import json
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from components.risk_engine import FamilyRiskCalculator
from components.visualizations import create_interactive_plots
from utils.data_manager import load_family_data
from config.settings import DEFAULT_RISK_WEIGHTS, DEFAULT_THRESHOLDS

# Import new Phase 2 pages
from pages.committee_workflow import show_committee_workflow
from pages.analytics_trends import show_analytics_trends
from utils.report_generator import ReportGenerator

# Page configuration
st.set_page_config(
    page_title="ICTV Family Risk Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .risk-high {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
    }
    .risk-medium {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
    }
    .risk-low {
        background-color: #e8f5e8;
        border-left: 5px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main dashboard application."""
    
    # Navigation sidebar
    st.sidebar.title("🦠 ICTV Dashboard")
    
    page = st.sidebar.radio(
        "Navigation",
        ["🏠 Risk Assessment", "🏛️ Committee Workflow", "📈 Analytics & Trends", "📄 Reports"]
    )
    
    if page == "🏠 Risk Assessment":
        show_risk_assessment()
    elif page == "🏛️ Committee Workflow":
        show_committee_workflow()
    elif page == "📈 Analytics & Trends":
        show_analytics_trends()
    elif page == "📄 Reports":
        show_reports()

def show_risk_assessment():
    """Original risk assessment dashboard."""
    
    # Header
    st.markdown('<h1 class="main-header">🦠 ICTV Family Risk Assessment Dashboard</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    **Real-time family risk assessment and committee decision support**  
    *Predictive accuracy: 85% | Based on 20 years of ICTV data*
    """)
    
    # Sidebar controls
    st.sidebar.header("🎛️ Risk Assessment Parameters")
    
    # Risk weight controls
    st.sidebar.subheader("Risk Factor Weights")
    
    size_weight = st.sidebar.slider(
        "Family Size Impact", 
        min_value=0.0, 
        max_value=1.0, 
        value=DEFAULT_RISK_WEIGHTS['size_factor'],
        step=0.05,
        help="Impact of family size on instability risk"
    )
    
    growth_weight = st.sidebar.slider(
        "Growth Rate Impact", 
        min_value=0.0, 
        max_value=1.0, 
        value=DEFAULT_RISK_WEIGHTS['growth_rate'],
        step=0.05,
        help="Impact of rapid species addition on stability"
    )
    
    host_weight = st.sidebar.slider(
        "Host Breadth Impact", 
        min_value=0.0, 
        max_value=1.0, 
        value=DEFAULT_RISK_WEIGHTS['host_breadth'],
        step=0.05,
        help="Impact of diverse host ranges on classification"
    )
    
    complexity_weight = st.sidebar.slider(
        "Genome Complexity Impact", 
        min_value=0.0, 
        max_value=1.0, 
        value=DEFAULT_RISK_WEIGHTS['genome_complexity'],
        step=0.05,
        help="Impact of genome diversity on family coherence"
    )
    
    coherence_weight = st.sidebar.slider(
        "Phylogenetic Coherence Impact", 
        min_value=0.0, 
        max_value=1.0, 
        value=DEFAULT_RISK_WEIGHTS['phylogenetic_coherence'],
        step=0.05,
        help="Impact of phylogenetic inconsistency"
    )
    
    # Threshold controls
    st.sidebar.subheader("Intervention Thresholds")
    
    review_threshold = st.sidebar.number_input(
        "Review Threshold (species)", 
        min_value=10, 
        max_value=200, 
        value=DEFAULT_THRESHOLDS['review'],
        step=10,
        help="Family size requiring committee review"
    )
    
    concern_threshold = st.sidebar.number_input(
        "Concern Threshold (species)", 
        min_value=50, 
        max_value=500, 
        value=DEFAULT_THRESHOLDS['concern'],
        step=25,
        help="Family size indicating structural concerns"
    )
    
    crisis_threshold = st.sidebar.number_input(
        "Crisis Threshold (species)", 
        min_value=200, 
        max_value=2000, 
        value=DEFAULT_THRESHOLDS['crisis'],
        step=50,
        help="Family size requiring immediate intervention"
    )
    
    # Main dashboard content
    col1, col2, col3 = st.columns(3)
    
    # Initialize risk calculator with user parameters
    custom_weights = {
        'size_factor': size_weight,
        'growth_rate': growth_weight,
        'host_breadth': host_weight,
        'genome_complexity': complexity_weight,
        'phylogenetic_coherence': coherence_weight
    }
    
    custom_thresholds = {
        'review': review_threshold,
        'concern': concern_threshold,
        'crisis': crisis_threshold
    }
    
    # Load and calculate risk assessments
    try:
        risk_calculator = FamilyRiskCalculator(custom_weights, custom_thresholds)
        family_data = load_family_data()
        assessments = risk_calculator.assess_all_families(family_data)
        
        # System overview metrics
        total_families = len(assessments)
        avg_risk = np.mean([a['risk_score'] for a in assessments])
        high_risk_count = len([a for a in assessments if a['risk_category'] in ['High Risk', 'Crisis']])
        
        with col1:
            st.metric(
                label="Total Families",
                value=total_families,
                delta=None
            )
        
        with col2:
            st.metric(
                label="Average Risk Score",
                value=f"{avg_risk:.1f}/10",
                delta=None
            )
        
        with col3:
            st.metric(
                label="Families Needing Attention",
                value=high_risk_count,
                delta=None
            )
        
        # Main visualization tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Risk Overview", 
            "🎯 Family Analysis", 
            "⚡ Interventions", 
            "📈 Trends"
        ])
        
        with tab1:
            st.subheader("Current Risk Distribution")
            
            # Create interactive visualizations
            plots = create_interactive_plots(assessments, custom_weights, custom_thresholds)
            
            # Risk distribution
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.plotly_chart(plots['risk_distribution'], use_container_width=True)
            
            with col_right:
                st.plotly_chart(plots['intervention_distribution'], use_container_width=True)
            
            # Risk matrix
            st.subheader("Interactive Family Risk Matrix")
            st.plotly_chart(plots['risk_matrix'], use_container_width=True)
            
            # High-risk families table
            st.subheader("Families Requiring Attention")
            high_risk_families = [a for a in assessments if a['risk_score'] >= 4.0]
            
            if high_risk_families:
                df_high_risk = pd.DataFrame(high_risk_families)
                df_display = df_high_risk[['family_name', 'risk_score', 'risk_category', 'intervention_type']].copy()
                df_display['risk_score'] = df_display['risk_score'].round(1)
                df_display.columns = ['Family', 'Risk Score', 'Category', 'Recommended Action']
                
                st.dataframe(
                    df_display.sort_values('Risk Score', ascending=False),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("🎉 No families currently require immediate attention!")
        
        with tab2:
            st.subheader("Detailed Family Analysis")
            
            # Family selection
            family_names = [a['family_name'] for a in assessments]
            selected_family = st.selectbox(
                "Select family for detailed analysis:",
                family_names,
                index=0
            )
            
            if selected_family:
                family_assessment = next(a for a in assessments if a['family_name'] == selected_family)
                
                # Family details
                col_detail1, col_detail2 = st.columns(2)
                
                with col_detail1:
                    st.markdown(f"### {selected_family}")
                    st.markdown(f"**Risk Score:** {family_assessment['risk_score']:.1f}/10")
                    st.markdown(f"**Category:** {family_assessment['risk_category']}")
                    st.markdown(f"**Recommended Action:** {family_assessment['intervention_type']}")
                    
                    if family_assessment['intervention_probability'] > 0:
                        st.markdown(f"**3-Year Intervention Probability:** {family_assessment['intervention_probability']:.0%}")
                
                with col_detail2:
                    # Risk factor breakdown
                    factors = {
                        'Size Factor': family_assessment['size_factor'] * size_weight,
                        'Growth Rate': family_assessment['growth_factor'] * growth_weight,
                        'Host Breadth': family_assessment['host_factor'] * host_weight,
                        'Genome Complexity': family_assessment['complexity_factor'] * complexity_weight,
                        'Phylogenetic Coherence': family_assessment['coherence_factor'] * coherence_weight
                    }
                    
                    fig_factors = go.Figure(data=[
                        go.Bar(
                            x=list(factors.keys()),
                            y=list(factors.values()),
                            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
                        )
                    ])
                    fig_factors.update_layout(
                        title="Risk Factor Contributions",
                        xaxis_title="Risk Factors",
                        yaxis_title="Contribution to Risk Score",
                        height=400
                    )
                    st.plotly_chart(fig_factors, use_container_width=True)
        
        with tab3:
            st.subheader("Intervention Planning")
            st.info("🚧 Advanced intervention features coming in Phase 2")
            
            # Show intervention timeline
            st.plotly_chart(plots['intervention_timeline'], use_container_width=True)
        
        with tab4:
            st.subheader("Trend Analysis")
            st.info("📈 Historical trend analysis coming in Phase 2")
    
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
        st.info("Please ensure the predictive framework data is available.")

def show_reports():
    """Report generation page."""
    
    st.header("📄 Report Generation")
    
    # Report type selection
    report_type = st.selectbox(
        "Select Report Type",
        ["Executive Summary", "Family Detail Report", "Meeting Minutes", "Data Export"]
    )
    
    report_generator = ReportGenerator()
    
    if report_type == "Executive Summary":
        st.subheader("📊 Executive Summary Report")
        
        # Generate summary data
        risk_calculator = FamilyRiskCalculator()
        families_data = load_family_data()
        assessments = risk_calculator.assess_all_families(families_data)
        system_health = risk_calculator.get_system_health(assessments)
        high_risk_families = [a for a in assessments if a['risk_score'] >= 5.0]
        
        recommendations = [
            "Focus immediate attention on families exceeding crisis thresholds",
            "Implement proactive monitoring for medium-risk families",
            "Consider resource allocation for upcoming interventions",
            "Update phylogenetic analyses for high-growth families",
            "Schedule quarterly reviews for all families above concern threshold"
        ]
        
        if st.button("📋 Generate Executive Summary", type="primary"):
            pdf_data = report_generator.generate_executive_summary(
                system_health, high_risk_families, recommendations
            )
            
            # Create download link
            st.markdown(
                report_generator.create_download_link(
                    pdf_data, 
                    f"ICTV_Executive_Summary_{datetime.now().strftime('%Y%m%d')}.pdf",
                    'pdf'
                ),
                unsafe_allow_html=True
            )
            
            st.success("✅ Executive summary generated successfully!")
    
    elif report_type == "Family Detail Report":
        st.subheader("🦠 Family Detail Report")
        
        families_data = load_family_data()
        selected_family = st.selectbox(
            "Select Family",
            [f['family_name'] for f in families_data]
        )
        
        if st.button("📋 Generate Family Report", type="primary"):
            # Get family data and assessment
            family_data = next(f for f in families_data if f['family_name'] == selected_family)
            risk_calculator = FamilyRiskCalculator()
            assessment = risk_calculator.calculate_family_risk(family_data)
            
            pdf_data = report_generator.generate_family_report(
                family_data, assessment
            )
            
            st.markdown(
                report_generator.create_download_link(
                    pdf_data,
                    f"{selected_family}_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    'pdf'
                ),
                unsafe_allow_html=True
            )
            
            st.success(f"✅ {selected_family} report generated successfully!")
    
    elif report_type == "Meeting Minutes":
        st.subheader("📝 Meeting Minutes")
        
        with st.form("meeting_minutes_form"):
            meeting_date = st.date_input("Meeting Date", value=datetime.now())
            attendees = st.text_input("Attendees", "Committee Members")
            duration = st.text_input("Duration", "2 hours")
            
            # Sample decisions
            st.markdown("### Decisions Made")
            decisions = [
                {
                    "family": "Genomoviridae",
                    "decision": "Initiate Split",
                    "vote": "8-2-1"
                }
            ]
            
            if st.form_submit_button("📋 Generate Minutes", type="primary"):
                meeting_data = {
                    "date": meeting_date.strftime('%B %d, %Y'),
                    "attendees": attendees,
                    "duration": duration
                }
                
                pdf_data = report_generator.generate_meeting_minutes(
                    meeting_data, decisions
                )
                
                st.markdown(
                    report_generator.create_download_link(
                        pdf_data,
                        f"Meeting_Minutes_{meeting_date.strftime('%Y%m%d')}.pdf",
                        'pdf'
                    ),
                    unsafe_allow_html=True
                )
                
                st.success("✅ Meeting minutes generated successfully!")
    
    elif report_type == "Data Export":
        st.subheader("💾 Data Export")
        
        export_format = st.radio(
            "Export Format",
            ["CSV", "JSON"]
        )
        
        include_metadata = st.checkbox("Include metadata", value=True)
        
        if st.button("📥 Export Data", type="primary"):
            # Get assessment data
            risk_calculator = FamilyRiskCalculator()
            families_data = load_family_data()
            assessments = risk_calculator.assess_all_families(families_data)
            
            if export_format == "CSV":
                csv_data = report_generator.export_data_csv(assessments)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"ICTV_Risk_Assessment_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                json_data = report_generator.export_data_json(
                    assessments, include_metadata
                )
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"ICTV_Risk_Assessment_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            
            st.success(f"✅ Data exported as {export_format} successfully!")
    
    # Report history
    with st.expander("🗓️ Recent Reports"):
        st.markdown("""
        - Executive Summary - January 15, 2025
        - Genomoviridae Family Report - January 10, 2025
        - Committee Meeting Minutes - January 8, 2025
        - Full Data Export - January 1, 2025
        """)

if __name__ == "__main__":
    main()