"""
Interactive web browser for exploring ICTV taxonomy across versions.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import yaml
from typing import Dict, List, Optional, Tuple
import networkx as nx
from datetime import datetime

class TaxonomyBrowser:
    """Interactive browser for exploring viral taxonomy."""
    
    def __init__(self, git_repo_path: str):
        self.repo_path = Path(git_repo_path)
        self.taxonomy_data = {}
        self.version_info = {}
        self._load_taxonomy_data()
    
    def _load_taxonomy_data(self):
        """Load taxonomy data from git repository."""
        # Load version information
        versions_file = self.repo_path / 'output' / 'version_info.json'
        if versions_file.exists():
            with open(versions_file, 'r') as f:
                self.version_info = json.load(f)
        
        # Load species data for each version
        for version_dir in sorted((self.repo_path / 'output').glob('MSL*')):
            if version_dir.is_dir():
                version = version_dir.name
                self.taxonomy_data[version] = self._load_version_data(version_dir)
    
    def _load_version_data(self, version_dir: Path) -> Dict:
        """Load all species data for a specific version."""
        species_data = []
        
        # Walk through the taxonomy structure
        for yaml_file in version_dir.rglob('*.yaml'):
            try:
                with open(yaml_file, 'r') as f:
                    species = yaml.safe_load(f)
                    if species:
                        # Add file path info for hierarchy
                        rel_path = yaml_file.relative_to(version_dir)
                        species['file_path'] = str(rel_path)
                        species['hierarchy_depth'] = len(rel_path.parts) - 1
                        species_data.append(species)
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")
        
        return {
            'species': species_data,
            'total': len(species_data),
            'path': version_dir
        }
    
    def create_taxonomy_tree(self, version: str) -> nx.DiGraph:
        """Create a networkx graph representation of the taxonomy."""
        G = nx.DiGraph()
        
        if version not in self.taxonomy_data:
            return G
        
        # Add nodes for each taxonomic level
        for species in self.taxonomy_data[version]['species']:
            classification = species.get('classification', {})
            
            # Build hierarchy path
            hierarchy = []
            for rank in ['realm', 'kingdom', 'phylum', 'class', 'order', 'family', 'genus']:
                if rank in classification and classification[rank]:
                    hierarchy.append((rank, classification[rank]))
            
            # Add species
            if 'scientific_name' in species:
                hierarchy.append(('species', species['scientific_name']))
            
            # Add edges
            for i in range(len(hierarchy) - 1):
                parent = hierarchy[i]
                child = hierarchy[i + 1]
                G.add_edge(f"{parent[0]}:{parent[1]}", f"{child[0]}:{child[1]}")
                G.nodes[f"{parent[0]}:{parent[1]}"]['rank'] = parent[0]
                G.nodes[f"{child[0]}:{child[1]}"]['rank'] = child[0]
        
        return G
    
    def render_web_interface(self):
        """Render the Streamlit web interface."""
        st.set_page_config(
            page_title="ICTV Taxonomy Browser",
            page_icon="🦠",
            layout="wide"
        )
        
        st.title("🦠 ICTV Git-Based Taxonomy Browser")
        st.markdown("Explore viral taxonomy across 20 years of evolution")
        
        # Sidebar for version selection
        with st.sidebar:
            st.header("Version Selection")
            
            available_versions = sorted(self.taxonomy_data.keys())
            if available_versions:
                selected_version = st.selectbox(
                    "Select MSL Version",
                    available_versions,
                    index=len(available_versions) - 1  # Default to latest
                )
                
                # Show version stats
                if selected_version in self.taxonomy_data:
                    st.metric(
                        "Total Species",
                        self.taxonomy_data[selected_version]['total']
                    )
                
                # Search functionality
                st.header("Search")
                search_term = st.text_input("Search species/genus/family")
                
                # Filter options
                st.header("Filters")
                show_realms = st.multiselect(
                    "Realms",
                    options=self._get_unique_values(selected_version, 'realm')
                )
                show_families = st.multiselect(
                    "Families",
                    options=self._get_unique_values(selected_version, 'family')
                )
        
        # Main content area
        tab1, tab2, tab3, tab4 = st.tabs([
            "🌳 Taxonomy Tree",
            "📊 Statistics",
            "🔍 Species Explorer",
            "📈 Evolution Timeline"
        ])
        
        with tab1:
            self._render_taxonomy_tree(selected_version, search_term)
        
        with tab2:
            self._render_statistics(selected_version)
        
        with tab3:
            self._render_species_explorer(
                selected_version, search_term, show_realms, show_families
            )
        
        with tab4:
            self._render_evolution_timeline()
    
    def _get_unique_values(self, version: str, rank: str) -> List[str]:
        """Get unique values for a taxonomic rank."""
        values = set()
        if version in self.taxonomy_data:
            for species in self.taxonomy_data[version]['species']:
                classification = species.get('classification', {})
                if rank in classification and classification[rank]:
                    values.add(classification[rank])
        return sorted(list(values))
    
    def _render_taxonomy_tree(self, version: str, search_term: str = ""):
        """Render interactive taxonomy tree visualization."""
        st.header("Taxonomy Tree Visualization")
        
        # Create tree
        G = self.create_taxonomy_tree(version)
        
        if search_term:
            # Highlight search results
            matching_nodes = [
                node for node in G.nodes()
                if search_term.lower() in node.lower()
            ]
            st.info(f"Found {len(matching_nodes)} matching nodes")
        
        # Create hierarchical layout
        if len(G.nodes()) > 0:
            # Use plotly for interactive tree
            fig = self._create_plotly_tree(G, search_term)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No taxonomy data available for this version")
    
    def _create_plotly_tree(self, G: nx.DiGraph, highlight_term: str = "") -> go.Figure:
        """Create an interactive Plotly tree visualization."""
        # Calculate positions using hierarchical layout
        pos = nx.spring_layout(G, k=3, iterations=50)
        
        # Create edge traces
        edge_traces = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_traces.append(
                go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=0.5, color='#888'),
                    hoverinfo='none'
                )
            )
        
        # Create node traces by rank
        rank_colors = {
            'realm': '#FF6B6B',
            'kingdom': '#FFA06B',
            'phylum': '#FFD06B',
            'class': '#6BFF6B',
            'order': '#6BD0FF',
            'family': '#6B6BFF',
            'genus': '#D06BFF',
            'species': '#FF6BD0'
        }
        
        node_traces = []
        for rank, color in rank_colors.items():
            rank_nodes = [
                node for node in G.nodes()
                if G.nodes[node].get('rank') == rank
            ]
            
            if rank_nodes:
                x_vals = [pos[node][0] for node in rank_nodes]
                y_vals = [pos[node][1] for node in rank_nodes]
                
                # Highlight matches
                colors = []
                for node in rank_nodes:
                    if highlight_term and highlight_term.lower() in node.lower():
                        colors.append('#FFD700')  # Gold for matches
                    else:
                        colors.append(color)
                
                node_traces.append(
                    go.Scatter(
                        x=x_vals,
                        y=y_vals,
                        mode='markers+text',
                        name=rank.title(),
                        text=[node.split(':')[1] for node in rank_nodes],
                        textposition="top center",
                        marker=dict(
                            size=10,
                            color=colors,
                            line=dict(width=2, color='white')
                        ),
                        hovertext=rank_nodes,
                        hoverinfo='text'
                    )
                )
        
        # Create figure
        fig = go.Figure(
            data=edge_traces + node_traces,
            layout=go.Layout(
                title=f"Taxonomy Tree - {version}",
                showlegend=True,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='white'
            )
        )
        
        return fig
    
    def _render_statistics(self, version: str):
        """Render taxonomy statistics dashboard."""
        st.header("Taxonomy Statistics")
        
        if version not in self.taxonomy_data:
            st.warning("No data available for this version")
            return
        
        species_list = self.taxonomy_data[version]['species']
        
        # Calculate statistics
        stats = self._calculate_statistics(species_list)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Species", stats['total_species'])
            st.metric("Total Genera", stats['total_genera'])
        
        with col2:
            st.metric("Total Families", stats['total_families'])
            st.metric("Total Orders", stats['total_orders'])
        
        with col3:
            st.metric("Total Classes", stats['total_classes'])
            st.metric("Total Phyla", stats['total_phyla'])
        
        with col4:
            st.metric("Total Kingdoms", stats['total_kingdoms'])
            st.metric("Total Realms", stats['total_realms'])
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Family size distribution
            fig = px.histogram(
                stats['family_sizes'],
                x='size',
                title="Family Size Distribution",
                labels={'size': 'Number of Species', 'count': 'Number of Families'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Realm composition
            fig = px.pie(
                stats['realm_composition'],
                values='count',
                names='realm',
                title="Species Distribution by Realm"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Genome type distribution
        if stats['genome_types']:
            fig = px.bar(
                stats['genome_types'],
                x='type',
                y='count',
                title="Genome Type Distribution",
                labels={'type': 'Genome Type', 'count': 'Number of Species'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _calculate_statistics(self, species_list: List[Dict]) -> Dict:
        """Calculate comprehensive statistics from species list."""
        stats = {
            'total_species': len(species_list),
            'total_genera': len(set(s.get('classification', {}).get('genus', '') 
                                  for s in species_list if s.get('classification', {}).get('genus'))),
            'total_families': len(set(s.get('classification', {}).get('family', '') 
                                    for s in species_list if s.get('classification', {}).get('family'))),
            'total_orders': len(set(s.get('classification', {}).get('order', '') 
                                  for s in species_list if s.get('classification', {}).get('order'))),
            'total_classes': len(set(s.get('classification', {}).get('class', '') 
                                   for s in species_list if s.get('classification', {}).get('class'))),
            'total_phyla': len(set(s.get('classification', {}).get('phylum', '') 
                                 for s in species_list if s.get('classification', {}).get('phylum'))),
            'total_kingdoms': len(set(s.get('classification', {}).get('kingdom', '') 
                                    for s in species_list if s.get('classification', {}).get('kingdom'))),
            'total_realms': len(set(s.get('classification', {}).get('realm', '') 
                                  for s in species_list if s.get('classification', {}).get('realm')))
        }
        
        # Family size distribution
        family_counts = {}
        for species in species_list:
            family = species.get('classification', {}).get('family')
            if family:
                family_counts[family] = family_counts.get(family, 0) + 1
        
        stats['family_sizes'] = pd.DataFrame([
            {'family': f, 'size': c} for f, c in family_counts.items()
        ])
        
        # Realm composition
        realm_counts = {}
        for species in species_list:
            realm = species.get('classification', {}).get('realm', 'Unassigned')
            realm_counts[realm] = realm_counts.get(realm, 0) + 1
        
        stats['realm_composition'] = pd.DataFrame([
            {'realm': r, 'count': c} for r, c in realm_counts.items()
        ])
        
        # Genome type distribution
        genome_counts = {}
        for species in species_list:
            genome_type = species.get('genome', {}).get('type', 'Unknown')
            genome_counts[genome_type] = genome_counts.get(genome_type, 0) + 1
        
        stats['genome_types'] = pd.DataFrame([
            {'type': t, 'count': c} for t, c in genome_counts.items()
        ])
        
        return stats
    
    def _render_species_explorer(self, version: str, search_term: str = "", 
                               filter_realms: List[str] = None, 
                               filter_families: List[str] = None):
        """Render detailed species explorer."""
        st.header("Species Explorer")
        
        if version not in self.taxonomy_data:
            st.warning("No data available for this version")
            return
        
        # Filter species
        species_list = self.taxonomy_data[version]['species']
        filtered_species = self._filter_species(
            species_list, search_term, filter_realms, filter_families
        )
        
        st.info(f"Showing {len(filtered_species)} of {len(species_list)} species")
        
        # Display species table
        if filtered_species:
            # Convert to dataframe for display
            df_data = []
            for species in filtered_species[:100]:  # Limit to 100 for performance
                df_data.append({
                    'Scientific Name': species.get('scientific_name', 'Unknown'),
                    'Genus': species.get('classification', {}).get('genus', ''),
                    'Family': species.get('classification', {}).get('family', ''),
                    'Order': species.get('classification', {}).get('order', ''),
                    'Realm': species.get('classification', {}).get('realm', ''),
                    'Genome Type': species.get('genome', {}).get('type', ''),
                    'Host': ', '.join(species.get('hosts', []))[:50]
                })
            
            df = pd.DataFrame(df_data)
            
            # Interactive table
            selected_indices = st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                selection_mode="single-row",
                on_select="rerun"
            )
            
            # Show detailed view for selected species
            if selected_indices and selected_indices.selection.rows:
                selected_idx = selected_indices.selection.rows[0]
                selected_species = filtered_species[selected_idx]
                
                st.subheader("Species Details")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.json({
                        'Scientific Name': selected_species.get('scientific_name'),
                        'Classification': selected_species.get('classification'),
                        'Genome': selected_species.get('genome'),
                        'History': selected_species.get('history')
                    })
                
                with col2:
                    st.json({
                        'Hosts': selected_species.get('hosts'),
                        'Evidence': selected_species.get('evidence'),
                        'File Path': selected_species.get('file_path')
                    })
    
    def _filter_species(self, species_list: List[Dict], search_term: str = "",
                       filter_realms: List[str] = None, 
                       filter_families: List[str] = None) -> List[Dict]:
        """Filter species based on search and filter criteria."""
        filtered = species_list
        
        # Search filter
        if search_term:
            search_lower = search_term.lower()
            filtered = [
                s for s in filtered
                if (search_lower in s.get('scientific_name', '').lower() or
                    search_lower in s.get('classification', {}).get('genus', '').lower() or
                    search_lower in s.get('classification', {}).get('family', '').lower())
            ]
        
        # Realm filter
        if filter_realms:
            filtered = [
                s for s in filtered
                if s.get('classification', {}).get('realm') in filter_realms
            ]
        
        # Family filter
        if filter_families:
            filtered = [
                s for s in filtered
                if s.get('classification', {}).get('family') in filter_families
            ]
        
        return filtered
    
    def _render_evolution_timeline(self):
        """Render evolution timeline across versions."""
        st.header("Taxonomy Evolution Timeline")
        
        # Collect data across all versions
        timeline_data = []
        for version in sorted(self.taxonomy_data.keys()):
            year = int(version.replace('MSL', '')) + 1987  # Approximate year
            stats = self._calculate_statistics(self.taxonomy_data[version]['species'])
            
            timeline_data.append({
                'Version': version,
                'Year': year,
                'Species': stats['total_species'],
                'Families': stats['total_families'],
                'Genera': stats['total_genera'],
                'Orders': stats['total_orders']
            })
        
        df = pd.DataFrame(timeline_data)
        
        # Multi-line chart
        fig = go.Figure()
        
        for column in ['Species', 'Families', 'Genera', 'Orders']:
            fig.add_trace(go.Scatter(
                x=df['Year'],
                y=df[column],
                mode='lines+markers',
                name=column,
                hovertemplate=f'{column}: %{{y}}<br>Year: %{{x}}<extra></extra>'
            ))
        
        fig.update_layout(
            title="Viral Taxonomy Growth Over Time",
            xaxis_title="Year",
            yaxis_title="Count",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Growth rate analysis
        if len(df) > 1:
            df['Species Growth Rate'] = df['Species'].pct_change() * 100
            
            fig2 = px.bar(
                df[1:],  # Skip first row with NaN
                x='Version',
                y='Species Growth Rate',
                title="Species Growth Rate by Version (%)",
                labels={'Species Growth Rate': 'Growth Rate (%)'}
            )
            st.plotly_chart(fig2, use_container_width=True)


def main():
    """Run the taxonomy browser as a standalone Streamlit app."""
    import sys
    
    if len(sys.argv) > 1:
        git_repo = sys.argv[1]
    else:
        git_repo = "output/git_taxonomy"
    
    browser = TaxonomyBrowser(git_repo)
    browser.render_web_interface()


if __name__ == "__main__":
    main()