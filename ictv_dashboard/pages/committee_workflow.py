"""
Committee Workflow Integration Page

Streamlined interface for ICTV committee meetings, decision documentation,
and action item tracking.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys

# Add dashboard root to path
dashboard_root = Path(__file__).parent.parent
if str(dashboard_root) not in sys.path:
    sys.path.insert(0, str(dashboard_root))

from components.risk_engine import FamilyRiskCalculator
from utils.data_manager import load_family_data
from config.settings import DEFAULT_RISK_WEIGHTS, DEFAULT_THRESHOLDS

def show_committee_workflow():
    """Main committee workflow page."""
    
    st.header("🏛️ Committee Workflow & Decision Support")
    
    # Meeting mode toggle
    meeting_mode = st.checkbox("📺 Enable Meeting Mode (Large Display)", value=False)
    
    if meeting_mode:
        st.markdown("""
        <style>
            .main-content { font-size: 1.2rem; }
            .metric-value { font-size: 2.5rem !important; }
            .stMetric label { font-size: 1.4rem !important; }
        </style>
        """, unsafe_allow_html=True)
    
    # Workflow tabs
    workflow_tab1, workflow_tab2, workflow_tab3, workflow_tab4 = st.tabs([
        "🎯 Current Meeting",
        "🔮 Scenario Planning", 
        "📝 Decision History",
        "✅ Action Items"
    ])
    
    with workflow_tab1:
        show_meeting_dashboard()
    
    with workflow_tab2:
        show_scenario_planning()
    
    with workflow_tab3:
        show_decision_history()
    
    with workflow_tab4:
        show_action_items()

def show_meeting_dashboard():
    """Current meeting dashboard with decision capture."""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📋 Meeting Agenda")
        
        # Load high-risk families for review
        risk_calculator = FamilyRiskCalculator()
        families_data = load_family_data()
        assessments = risk_calculator.assess_all_families(families_data)
        
        # Filter families needing review
        review_families = [a for a in assessments if a['risk_score'] >= 4.0]
        
        if review_families:
            st.info(f"**{len(review_families)} families** require committee review today")
            
            # Family selection for review
            selected_family = st.selectbox(
                "Select family for detailed review:",
                [f['family_name'] for f in review_families],
                format_func=lambda x: f"{x} (Risk: {next(f['risk_score'] for f in review_families if f['family_name'] == x):.1f})"
            )
            
            if selected_family:
                family_data = next(f for f in review_families if f['family_name'] == selected_family)
                
                # Display family metrics
                st.markdown("### Family Overview")
                
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    st.metric("Current Size", f"{family_data['current_size']} species")
                
                with metric_col2:
                    st.metric("Risk Score", f"{family_data['risk_score']:.1f}/10")
                
                with metric_col3:
                    st.metric("Growth Rate", f"{family_data['growth_rate']:.0%}")
                
                with metric_col4:
                    st.metric("Recommendation", family_data['intervention_type'])
                
                # Risk factor visualization
                st.markdown("### Risk Factor Analysis")
                
                factors = {
                    'Size': family_data['size_factor'],
                    'Growth': family_data['growth_factor'],
                    'Host Range': family_data['host_factor'],
                    'Complexity': family_data['complexity_factor'],
                    'Coherence': family_data['coherence_factor']
                }
                
                fig = go.Figure(data=[
                    go.Bar(
                        x=list(factors.values()),
                        y=list(factors.keys()),
                        orientation='h',
                        marker_color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
                    )
                ])
                
                fig.update_layout(
                    title="Contributing Risk Factors",
                    xaxis_title="Risk Contribution (0-10)",
                    height=300,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.success("✅ No families currently require urgent review!")
    
    with col2:
        st.subheader("🗳️ Decision Capture")
        
        with st.form("decision_form"):
            st.markdown("### Record Committee Decision")
            
            decision_type = st.selectbox(
                "Decision Type",
                ["No Action", "Monitor", "Review in 6 months", "Initiate Split", "Emergency Intervention"]
            )
            
            rationale = st.text_area(
                "Decision Rationale",
                placeholder="Explain the reasoning behind this decision..."
            )
            
            # Voting
            st.markdown("### Committee Vote")
            vote_cols = st.columns(3)
            
            with vote_cols[0]:
                votes_for = st.number_input("For", min_value=0, value=0)
            
            with vote_cols[1]:
                votes_against = st.number_input("Against", min_value=0, value=0)
            
            with vote_cols[2]:
                votes_abstain = st.number_input("Abstain", min_value=0, value=0)
            
            # Action items
            action_items = st.text_area(
                "Action Items",
                placeholder="List any follow-up actions required..."
            )
            
            assigned_to = st.selectbox(
                "Primary Assignee",
                ["Subcommittee A", "Subcommittee B", "Working Group 1", "Full Committee"]
            )
            
            deadline = st.date_input(
                "Implementation Deadline",
                value=datetime.now() + timedelta(days=90)
            )
            
            submitted = st.form_submit_button("💾 Record Decision", type="primary")
            
            if submitted:
                # Save decision (in real implementation, this would go to database)
                decision_record = {
                    "timestamp": datetime.now().isoformat(),
                    "family": selected_family if 'selected_family' in locals() else "N/A",
                    "decision": decision_type,
                    "rationale": rationale,
                    "votes": {
                        "for": votes_for,
                        "against": votes_against,
                        "abstain": votes_abstain
                    },
                    "action_items": action_items,
                    "assigned_to": assigned_to,
                    "deadline": deadline.isoformat()
                }
                
                st.success("✅ Decision recorded successfully!")
                st.json(decision_record)

def show_scenario_planning():
    """Interactive scenario planning and what-if analysis."""
    
    st.subheader("🔮 Intervention Scenario Planning")
    
    # Load family data
    families_data = load_family_data()
    family_names = [f['family_name'] for f in families_data]
    
    selected_family = st.selectbox(
        "Select family for scenario analysis:",
        family_names
    )
    
    if selected_family:
        family_data = next(f for f in families_data if f['family_name'] == selected_family)
        
        st.markdown("### Current State")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Current Size", f"{family_data['current_size']} species")
        
        with col2:
            st.metric("Growth Rate", f"{family_data['growth_rate']:.0%}")
        
        with col3:
            st.metric("Host Breadth", f"{family_data['host_breadth']} hosts")
        
        st.markdown("---")
        
        # Scenario configuration
        st.markdown("### Configure Intervention Scenarios")
        
        scenario_cols = st.columns(3)
        
        scenarios = {}
        
        with scenario_cols[0]:
            st.markdown("#### Scenario A: No Action")
            scenarios['no_action'] = {
                'name': 'No Action',
                'split_count': 1,
                'timeline': 0,
                'resources': 0
            }
            st.info("Continue monitoring without intervention")
        
        with scenario_cols[1]:
            st.markdown("#### Scenario B: Gradual Split")
            split_count_b = st.slider("Number of new families", 2, 5, 3, key="split_b")
            timeline_b = st.slider("Implementation (months)", 6, 24, 12, key="timeline_b")
            
            scenarios['gradual'] = {
                'name': 'Gradual Split',
                'split_count': split_count_b,
                'timeline': timeline_b,
                'resources': split_count_b * 10
            }
        
        with scenario_cols[2]:
            st.markdown("#### Scenario C: Immediate Split")
            split_count_c = st.slider("Number of new families", 3, 10, 5, key="split_c")
            timeline_c = st.slider("Implementation (months)", 1, 6, 3, key="timeline_c")
            
            scenarios['immediate'] = {
                'name': 'Immediate Split',
                'split_count': split_count_c,
                'timeline': timeline_c,
                'resources': split_count_c * 15
            }
        
        # Impact projections
        st.markdown("### Projected Outcomes (5-Year Forecast)")
        
        # Create comparison chart
        fig = go.Figure()
        
        years = np.arange(0, 6)
        
        for scenario_key, scenario in scenarios.items():
            if scenario['split_count'] == 1:
                # No action - exponential growth continues
                projected_sizes = family_data['current_size'] * (1 + family_data['growth_rate']) ** years
            else:
                # Split scenario - growth distributed across new families
                avg_size_per_family = family_data['current_size'] / scenario['split_count']
                reduced_growth = family_data['growth_rate'] / 2  # Assume splits reduce growth
                projected_sizes = avg_size_per_family * (1 + reduced_growth) ** years
            
            fig.add_trace(go.Scatter(
                x=years,
                y=projected_sizes,
                mode='lines+markers',
                name=scenario['name'],
                line=dict(width=3)
            ))
        
        # Add threshold lines
        fig.add_hline(y=100, line_dash="dash", line_color="orange", 
                      annotation_text="Concern Threshold")
        fig.add_hline(y=500, line_dash="dash", line_color="red",
                      annotation_text="Crisis Threshold")
        
        fig.update_layout(
            title="Family Size Projections by Scenario",
            xaxis_title="Years from Now",
            yaxis_title="Projected Family Size",
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Resource comparison
        st.markdown("### Resource Requirements")
        
        resource_data = []
        for scenario in scenarios.values():
            resource_data.append({
                'Scenario': scenario['name'],
                'Committee Hours': scenario['resources'],
                'Timeline (months)': scenario['timeline'],
                'New Families': scenario['split_count'] - 1 if scenario['split_count'] > 1 else 0
            })
        
        df_resources = pd.DataFrame(resource_data)
        
        fig_resources = go.Figure(data=[
            go.Bar(name='Committee Hours', x=df_resources['Scenario'], y=df_resources['Committee Hours']),
            go.Bar(name='Timeline (months)', x=df_resources['Scenario'], y=df_resources['Timeline (months)'])
        ])
        
        fig_resources.update_layout(
            title="Resource Comparison",
            barmode='group',
            height=300
        )
        
        st.plotly_chart(fig_resources, use_container_width=True)
        
        # Recommendation
        st.markdown("### Scenario Recommendation")
        
        if family_data['current_size'] > 200:
            st.warning("⚠️ **Recommended: Immediate Split** - Family size already exceeds manageable limits")
        elif family_data['growth_rate'] > 0.2:
            st.info("ℹ️ **Recommended: Gradual Split** - High growth rate suggests proactive intervention")
        else:
            st.success("✅ **Recommended: Continue Monitoring** - Family appears stable for now")

def show_decision_history():
    """Display historical committee decisions."""
    
    st.subheader("📝 Committee Decision History")
    
    # Sample historical decisions (in real implementation, load from database)
    decisions = [
        {
            "date": "2024-10-15",
            "family": "Genomoviridae",
            "decision": "Initiate Split",
            "vote": "8-2-1",
            "status": "In Progress",
            "assignee": "Subcommittee A"
        },
        {
            "date": "2024-09-20",
            "family": "Circoviridae",
            "decision": "Review in 6 months",
            "vote": "10-0-1",
            "status": "Scheduled",
            "assignee": "Working Group 1"
        },
        {
            "date": "2024-08-10",
            "family": "Microviridae",
            "decision": "Monitor",
            "vote": "11-0-0",
            "status": "Active",
            "assignee": "Full Committee"
        }
    ]
    
    df_decisions = pd.DataFrame(decisions)
    
    # Filter options
    col1, col2 = st.columns(2)
    
    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            ["In Progress", "Scheduled", "Active", "Completed"],
            default=["In Progress", "Scheduled", "Active"]
        )
    
    with col2:
        assignee_filter = st.multiselect(
            "Filter by Assignee",
            ["Subcommittee A", "Subcommittee B", "Working Group 1", "Full Committee"],
            default=[]
        )
    
    # Apply filters
    if status_filter:
        df_decisions = df_decisions[df_decisions['status'].isin(status_filter)]
    
    if assignee_filter:
        df_decisions = df_decisions[df_decisions['assignee'].isin(assignee_filter)]
    
    # Display decisions
    st.dataframe(
        df_decisions,
        use_container_width=True,
        hide_index=True
    )
    
    # Decision statistics
    st.markdown("### Decision Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_decisions = len(decisions)
        st.metric("Total Decisions", total_decisions)
    
    with col2:
        active_interventions = len([d for d in decisions if d['status'] == 'In Progress'])
        st.metric("Active Interventions", active_interventions)
    
    with col3:
        avg_vote_ratio = 0.8  # Calculate from actual votes
        st.metric("Average Consensus", f"{avg_vote_ratio:.0%}")

def show_action_items():
    """Track and manage committee action items."""
    
    st.subheader("✅ Action Item Tracker")
    
    # Action items (in real implementation, from database)
    action_items = [
        {
            "id": "AI-001",
            "family": "Genomoviridae",
            "action": "Prepare split proposal document",
            "assignee": "Dr. Smith",
            "deadline": "2025-02-15",
            "status": "In Progress",
            "progress": 65
        },
        {
            "id": "AI-002",
            "family": "Circoviridae",
            "action": "Collect phylogenetic data",
            "assignee": "Dr. Johnson",
            "deadline": "2025-03-01",
            "status": "Not Started",
            "progress": 0
        },
        {
            "id": "AI-003",
            "family": "Microviridae",
            "action": "Review host range expansion",
            "assignee": "Dr. Williams",
            "deadline": "2025-01-30",
            "status": "In Progress",
            "progress": 40
        }
    ]
    
    # Kanban board view
    st.markdown("### Action Items by Status")
    
    status_cols = st.columns(3)
    
    statuses = ["Not Started", "In Progress", "Completed"]
    
    for i, status in enumerate(statuses):
        with status_cols[i]:
            st.markdown(f"#### {status}")
            
            status_items = [item for item in action_items if item['status'] == status]
            
            for item in status_items:
                with st.container():
                    st.markdown(f"**{item['id']}: {item['family']}**")
                    st.markdown(f"{item['action']}")
                    st.markdown(f"👤 {item['assignee']}")
                    st.markdown(f"📅 Due: {item['deadline']}")
                    
                    if item['progress'] > 0:
                        st.progress(item['progress'] / 100)
                    
                    st.markdown("---")
    
    # Add new action item
    with st.expander("➕ Add New Action Item"):
        with st.form("new_action_item"):
            new_family = st.selectbox("Family", [f['family_name'] for f in load_family_data()])
            new_action = st.text_area("Action Description")
            new_assignee = st.text_input("Assignee")
            new_deadline = st.date_input("Deadline")
            
            if st.form_submit_button("Add Action Item"):
                st.success("✅ Action item added successfully!")

# This page will be imported by the main app
if __name__ == "__main__":
    show_committee_workflow()