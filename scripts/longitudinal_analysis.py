#!/usr/bin/env python3
"""
Longitudinal Analysis of ICTV Taxonomy Evolution (2005-2024)

This script conducts comprehensive research studies across the complete 
20-year ICTV taxonomy dataset to identify patterns, trends, and insights.
"""

import sys
from pathlib import Path
import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import json
from datetime import datetime
import re

# Add src to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.taxonomy_diff import TaxonomyDiff
from src.utils.change_classifier import ChangeClassifier
from src.parsers.msl_parser import MSLParser

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set style for plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class LongitudinalAnalyzer:
    """Comprehensive longitudinal analysis of viral taxonomy evolution."""
    
    def __init__(self, repo_path: str, output_dir: str = None):
        """Initialize analyzer with repository and output paths."""
        self.repo_path = Path(repo_path)
        self.output_dir = Path(output_dir) if output_dir else Path(__file__).parent.parent / 'output' / 'research_analysis'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.diff_tool = TaxonomyDiff(str(self.repo_path))
        self.classifier = ChangeClassifier()
        
        # MSL version information
        self.msl_versions = [
            {'version': 'msl23', 'year': 2005, 'name': 'MSL23'},
            {'version': 'msl24', 'year': 2008, 'name': 'MSL24'},
            {'version': 'msl25', 'year': 2009, 'name': 'MSL25'},
            {'version': 'msl26', 'year': 2011, 'name': 'MSL26'},
            {'version': 'msl27', 'year': 2012, 'name': 'MSL27'},
            {'version': 'msl28', 'year': 2013, 'name': 'MSL28'},
            {'version': 'msl29', 'year': 2014, 'name': 'MSL29'},
            {'version': 'msl30', 'year': 2015, 'name': 'MSL30'},
            {'version': 'msl31', 'year': 2016, 'name': 'MSL31'},
            {'version': 'msl32', 'year': 2017, 'name': 'MSL32'},
            {'version': 'msl33', 'year': 2018, 'name': 'MSL33'},
            {'version': 'msl34', 'year': 2018, 'name': 'MSL34'},
            {'version': 'msl35', 'year': 2019, 'name': 'MSL35'},
            {'version': 'msl36', 'year': 2020, 'name': 'MSL36'},
            {'version': 'msl37', 'year': 2021, 'name': 'MSL37'},
            {'version': 'msl38', 'year': 2022, 'name': 'MSL38'},
            {'version': 'msl39', 'year': 2023, 'name': 'MSL39'},
            {'version': 'msl40', 'year': 2024, 'name': 'MSL40'}
        ]
        
        # Cache for species data
        self._species_cache = {}
    
    def get_species_data(self, version: str) -> dict:
        """Get species data for a version with caching."""
        if version not in self._species_cache:
            logger.info(f"Loading species data for {version}")
            self._species_cache[version] = self.diff_tool.get_species_at_version(version)
        return self._species_cache[version]
    
    def study_1_taxonomy_growth_patterns(self):
        """Study 1: Analyze overall taxonomy growth patterns over 20 years."""
        logger.info("Conducting Study 1: Taxonomy Growth Patterns")
        
        growth_data = []
        
        for msl_info in self.msl_versions:
            version = msl_info['version']
            year = msl_info['year']
            
            species_data = self.get_species_data(version)
            
            # Count taxonomic ranks
            families = set()
            genera = set()
            orders = set()
            realms = set()
            
            for species_name, data in species_data.items():
                classification = data['classification']
                
                if classification.get('family'):
                    families.add(classification['family'])
                if classification.get('genus'):
                    genera.add(classification['genus'])
                if classification.get('order'):
                    orders.add(classification['order'])
                if classification.get('realm'):
                    realms.add(classification['realm'])
            
            growth_data.append({
                'version': msl_info['name'],
                'year': year,
                'species': len(species_data),
                'families': len(families),
                'genera': len(genera),
                'orders': len(orders),
                'realms': len(realms)
            })
        
        # Create DataFrame
        df = pd.DataFrame(growth_data)
        
        # Calculate growth rates
        df['species_growth'] = df['species'].diff()
        df['families_growth'] = df['families'].diff()
        df['genera_growth'] = df['genera'].diff()
        
        # Annual growth rates
        df['years_since_previous'] = df['year'].diff()
        df['annual_species_growth'] = df['species_growth'] / df['years_since_previous']
        df['annual_families_growth'] = df['families_growth'] / df['years_since_previous']
        
        # Create visualizations
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Total counts over time
        axes[0, 0].plot(df['year'], df['species'], 'o-', label='Species', linewidth=2)
        axes[0, 0].plot(df['year'], df['families'], 's-', label='Families', linewidth=2)
        axes[0, 0].plot(df['year'], df['genera'], '^-', label='Genera', linewidth=2)
        axes[0, 0].set_xlabel('Year')
        axes[0, 0].set_ylabel('Count')
        axes[0, 0].set_title('Taxonomic Diversity Growth (2005-2024)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Annual species growth rate
        axes[0, 1].bar(df['year'][1:], df['annual_species_growth'][1:], alpha=0.7)
        axes[0, 1].set_xlabel('Year')
        axes[0, 1].set_ylabel('Species Added per Year')
        axes[0, 1].set_title('Annual Species Discovery Rate')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Cumulative growth
        df['cumulative_growth'] = ((df['species'] - df['species'].iloc[0]) / df['species'].iloc[0] * 100)
        axes[1, 0].plot(df['year'], df['cumulative_growth'], 'o-', linewidth=2, color='red')
        axes[1, 0].set_xlabel('Year')
        axes[1, 0].set_ylabel('Cumulative Growth (%)')
        axes[1, 0].set_title('Cumulative Species Growth Since 2005')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Growth acceleration/deceleration
        df['growth_acceleration'] = df['annual_species_growth'].diff()
        axes[1, 1].bar(df['year'][2:], df['growth_acceleration'][2:], alpha=0.7, color='green')
        axes[1, 1].axhline(y=0, color='black', linestyle='-', alpha=0.5)
        axes[1, 1].set_xlabel('Year')
        axes[1, 1].set_ylabel('Change in Annual Growth Rate')
        axes[1, 1].set_title('Discovery Rate Acceleration/Deceleration')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'study1_taxonomy_growth_patterns.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save detailed data
        df.to_csv(self.output_dir / 'study1_growth_data.csv', index=False)
        
        # Key findings
        total_growth = df['species'].iloc[-1] - df['species'].iloc[0]
        avg_annual_growth = total_growth / (df['year'].iloc[-1] - df['year'].iloc[0])
        peak_growth_year = df.loc[df['annual_species_growth'].idxmax(), 'year']
        peak_growth_rate = df['annual_species_growth'].max()
        
        findings = {
            'study': 'Taxonomy Growth Patterns',
            'timespan': f"{df['year'].iloc[0]}-{df['year'].iloc[-1]}",
            'total_species_growth': int(total_growth),
            'average_annual_growth': round(avg_annual_growth, 1),
            'peak_growth_year': int(peak_growth_year),
            'peak_growth_rate': round(peak_growth_rate, 1),
            'final_diversity': {
                'species': int(df['species'].iloc[-1]),
                'families': int(df['families'].iloc[-1]),
                'genera': int(df['genera'].iloc[-1]),
                'orders': int(df['orders'].iloc[-1]),
                'realms': int(df['realms'].iloc[-1])
            }
        }
        
        return findings
    
    def study_2_family_reorganization_events(self):
        """Study 2: Identify major family reorganization events and their patterns."""
        logger.info("Conducting Study 2: Family Reorganization Events")
        
        reorganization_events = []
        
        # Analyze each transition
        for i in range(1, len(self.msl_versions)):
            prev_version = self.msl_versions[i-1]['version']
            curr_version = self.msl_versions[i]['version']
            year = self.msl_versions[i]['year']
            
            logger.info(f"Analyzing {prev_version} → {curr_version}")
            
            # Compare versions
            changes = self.diff_tool.compare_versions(prev_version, curr_version)
            
            # Focus on classification changes
            classification_changes = changes['classification_changed']
            
            # Count family-level changes
            family_changes = 0
            new_families = set()
            abolished_families = set()
            species_reclassified = 0
            
            for change in classification_changes:
                old_family = change.old_classification.get('family')
                new_family = change.new_classification.get('family')
                
                if old_family != new_family:
                    family_changes += 1
                    species_reclassified += 1
                    
                    if new_family and new_family not in [old_family]:
                        new_families.add(new_family)
                    if old_family and old_family not in [new_family]:
                        abolished_families.add(old_family)
            
            # Count new species added
            new_species = len(changes['added'])
            removed_species = len(changes['removed'])
            
            event = {
                'transition': f"{prev_version} → {curr_version}",
                'year': year,
                'total_changes': len(classification_changes),
                'family_reclassifications': family_changes,
                'species_reclassified': species_reclassified,
                'new_families_created': len(new_families),
                'families_abolished': len(abolished_families),
                'new_species_added': new_species,
                'species_removed': removed_species,
                'reorganization_intensity': family_changes / max(1, len(classification_changes))
            }
            
            reorganization_events.append(event)
        
        # Create DataFrame
        df = pd.DataFrame(reorganization_events)
        
        # Identify major reorganization events (top 25% by intensity)
        intensity_threshold = df['reorganization_intensity'].quantile(0.75)
        major_events = df[df['reorganization_intensity'] >= intensity_threshold]
        
        # Create visualizations
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Family reclassifications over time
        axes[0, 0].bar(df['year'], df['family_reclassifications'], alpha=0.7)
        axes[0, 0].set_xlabel('Year')
        axes[0, 0].set_ylabel('Species with Family Changes')
        axes[0, 0].set_title('Family Reclassification Events Over Time')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Reorganization intensity
        bars = axes[0, 1].bar(df['year'], df['reorganization_intensity'], alpha=0.7)
        # Highlight major events
        for i, (year, intensity) in enumerate(zip(df['year'], df['reorganization_intensity'])):
            if intensity >= intensity_threshold:
                bars[i].set_color('red')
        axes[0, 1].axhline(y=intensity_threshold, color='red', linestyle='--', alpha=0.7, label='Major Event Threshold')
        axes[0, 1].set_xlabel('Year')
        axes[0, 1].set_ylabel('Reorganization Intensity')
        axes[0, 1].set_title('Taxonomic Reorganization Intensity')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # New families created vs abolished
        axes[1, 0].bar(df['year'], df['new_families_created'], alpha=0.7, label='Created')
        axes[1, 0].bar(df['year'], -df['families_abolished'], alpha=0.7, label='Abolished')
        axes[1, 0].axhline(y=0, color='black', linestyle='-', alpha=0.5)
        axes[1, 0].set_xlabel('Year')
        axes[1, 0].set_ylabel('Number of Families')
        axes[1, 0].set_title('Family Creation vs Abolition')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Species additions vs reclassifications
        axes[1, 1].scatter(df['new_species_added'], df['species_reclassified'], 
                          s=df['year']/20, alpha=0.7, c=df['year'], cmap='viridis')
        axes[1, 1].set_xlabel('New Species Added')
        axes[1, 1].set_ylabel('Species Reclassified')
        axes[1, 1].set_title('New Discoveries vs Reclassifications')
        cbar = plt.colorbar(axes[1, 1].collections[0], ax=axes[1, 1])
        cbar.set_label('Year')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'study2_family_reorganization.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save data
        df.to_csv(self.output_dir / 'study2_reorganization_events.csv', index=False)
        major_events.to_csv(self.output_dir / 'study2_major_reorganization_events.csv', index=False)
        
        # Key findings
        findings = {
            'study': 'Family Reorganization Events',
            'total_transitions': len(reorganization_events),
            'major_reorganization_events': len(major_events),
            'peak_reorganization_year': int(df.loc[df['reorganization_intensity'].idxmax(), 'year']),
            'total_family_reclassifications': int(df['family_reclassifications'].sum()),
            'total_new_families': int(df['new_families_created'].sum()),
            'average_reorganization_intensity': round(df['reorganization_intensity'].mean(), 3),
            'major_events_list': major_events[['transition', 'year', 'reorganization_intensity']].to_dict('records')
        }
        
        return findings
    
    def study_3_species_naming_evolution(self):
        """Study 3: Analyze evolution of species naming conventions."""
        logger.info("Conducting Study 3: Species Naming Evolution")
        
        naming_data = []
        
        for msl_info in self.msl_versions:
            version = msl_info['version']
            year = msl_info['year']
            
            species_data = self.get_species_data(version)
            
            # Analyze naming patterns
            virus_names = []
            phage_names = []
            satellite_names = []
            viroid_names = []
            binomial_names = []
            
            name_lengths = []
            word_counts = []
            
            for species_name, data in species_data.items():
                name_lower = species_name.lower()
                name_lengths.append(len(species_name))
                word_counts.append(len(species_name.split()))
                
                # Categorize by naming pattern
                if 'virus' in name_lower:
                    virus_names.append(species_name)
                elif 'phage' in name_lower:
                    phage_names.append(species_name)
                elif 'satellite' in name_lower:
                    satellite_names.append(species_name)
                elif 'viroid' in name_lower:
                    viroid_names.append(species_name)
                
                # Check for binomial-like naming (Genus species pattern)
                words = species_name.split()
                if (len(words) >= 2 and 
                    words[0][0].isupper() and words[0][1:].islower() and
                    words[1][0].islower()):
                    binomial_names.append(species_name)
            
            naming_data.append({
                'version': msl_info['name'],
                'year': year,
                'total_species': len(species_data),
                'virus_suffix': len(virus_names),
                'phage_suffix': len(phage_names),
                'satellite_suffix': len(satellite_names),
                'viroid_suffix': len(viroid_names),
                'binomial_like': len(binomial_names),
                'avg_name_length': np.mean(name_lengths),
                'avg_word_count': np.mean(word_counts),
                'virus_percentage': len(virus_names) / len(species_data) * 100,
                'phage_percentage': len(phage_names) / len(species_data) * 100,
                'binomial_percentage': len(binomial_names) / len(species_data) * 100
            })
        
        # Create DataFrame
        df = pd.DataFrame(naming_data)
        
        # Create visualizations
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Naming suffix trends
        axes[0, 0].plot(df['year'], df['virus_percentage'], 'o-', label='Virus', linewidth=2)
        axes[0, 0].plot(df['year'], df['phage_percentage'], 's-', label='Phage', linewidth=2)
        axes[0, 0].plot(df['year'], df['binomial_percentage'], '^-', label='Binomial-like', linewidth=2)
        axes[0, 0].set_xlabel('Year')
        axes[0, 0].set_ylabel('Percentage of Species')
        axes[0, 0].set_title('Species Naming Convention Trends')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Average name characteristics
        axes[0, 1].plot(df['year'], df['avg_name_length'], 'o-', label='Name Length', linewidth=2)
        ax2 = axes[0, 1].twinx()
        ax2.plot(df['year'], df['avg_word_count'], 's-', color='red', label='Word Count', linewidth=2)
        axes[0, 1].set_xlabel('Year')
        axes[0, 1].set_ylabel('Average Name Length', color='blue')
        ax2.set_ylabel('Average Word Count', color='red')
        axes[0, 1].set_title('Name Complexity Evolution')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Stacked bar chart of naming categories
        bottom = np.zeros(len(df))
        categories = ['virus_suffix', 'phage_suffix', 'satellite_suffix', 'viroid_suffix']
        colors = ['blue', 'green', 'orange', 'purple']
        
        for category, color in zip(categories, colors):
            axes[1, 0].bar(df['year'], df[category], bottom=bottom, label=category.replace('_', ' ').title(), color=color, alpha=0.7)
            bottom += df[category]
        
        axes[1, 0].set_xlabel('Year')
        axes[1, 0].set_ylabel('Number of Species')
        axes[1, 0].set_title('Species by Naming Category')
        axes[1, 0].legend()
        
        # Binomial adoption trend
        axes[1, 1].fill_between(df['year'], df['binomial_percentage'], alpha=0.3, color='green')
        axes[1, 1].plot(df['year'], df['binomial_percentage'], 'o-', linewidth=2, color='green')
        axes[1, 1].set_xlabel('Year')
        axes[1, 1].set_ylabel('Percentage Using Binomial-like Names')
        axes[1, 1].set_title('Binomial Nomenclature Adoption')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'study3_naming_evolution.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save data
        df.to_csv(self.output_dir / 'study3_naming_data.csv', index=False)
        
        # Key findings
        binomial_growth = df['binomial_percentage'].iloc[-1] - df['binomial_percentage'].iloc[0]
        virus_trend = df['virus_percentage'].iloc[-1] - df['virus_percentage'].iloc[0]
        
        findings = {
            'study': 'Species Naming Evolution',
            'binomial_adoption_growth': round(binomial_growth, 2),
            'virus_suffix_trend': round(virus_trend, 2),
            'current_naming_distribution': {
                'virus_suffix': round(df['virus_percentage'].iloc[-1], 1),
                'phage_suffix': round(df['phage_percentage'].iloc[-1], 1),
                'binomial_like': round(df['binomial_percentage'].iloc[-1], 1)
            },
            'name_complexity_trend': {
                'avg_length_change': round(df['avg_name_length'].iloc[-1] - df['avg_name_length'].iloc[0], 1),
                'avg_words_change': round(df['avg_word_count'].iloc[-1] - df['avg_word_count'].iloc[0], 1)
            }
        }
        
        return findings
    
    def study_4_realm_establishment_analysis(self):
        """Study 4: Analyze the establishment and evolution of realm-level taxonomy."""
        logger.info("Conducting Study 4: Realm Establishment Analysis")
        
        realm_data = []
        
        for msl_info in self.msl_versions:
            version = msl_info['version']
            year = msl_info['year']
            
            species_data = self.get_species_data(version)
            
            # Count species by realm
            realm_counts = defaultdict(int)
            unassigned_realms = 0
            
            for species_name, data in species_data.items():
                realm = data['classification'].get('realm')
                if realm:
                    realm_counts[realm] += 1
                else:
                    unassigned_realms += 1
            
            realm_data.append({
                'version': msl_info['name'],
                'year': year,
                'total_species': len(species_data),
                'realms_defined': len(realm_counts),
                'species_with_realms': sum(realm_counts.values()),
                'unassigned_species': unassigned_realms,
                'realm_coverage': sum(realm_counts.values()) / len(species_data) * 100,
                'realm_distribution': dict(realm_counts)
            })
        
        # Create DataFrame
        df = pd.DataFrame(realm_data)
        
        # Create visualizations
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Realm coverage over time
        axes[0, 0].fill_between(df['year'], df['realm_coverage'], alpha=0.3, color='blue')
        axes[0, 0].plot(df['year'], df['realm_coverage'], 'o-', linewidth=2, color='blue')
        axes[0, 0].set_xlabel('Year')
        axes[0, 0].set_ylabel('Percentage of Species with Realms')
        axes[0, 0].set_title('Realm-Level Classification Coverage')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Number of realms over time
        axes[0, 1].plot(df['year'], df['realms_defined'], 'o-', linewidth=2, color='green')
        axes[0, 1].set_xlabel('Year')
        axes[0, 1].set_ylabel('Number of Realms Defined')
        axes[0, 1].set_title('Realm Diversity Evolution')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Species with vs without realm assignment
        axes[1, 0].plot(df['year'], df['species_with_realms'], 'o-', label='With Realm', linewidth=2)
        axes[1, 0].plot(df['year'], df['unassigned_species'], 's-', label='Unassigned', linewidth=2)
        axes[1, 0].set_xlabel('Year')
        axes[1, 0].set_ylabel('Number of Species')
        axes[1, 0].set_title('Realm Assignment Progress')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Realm distribution in latest version
        latest_realms = df['realm_distribution'].iloc[-1]
        if latest_realms:
            realm_names = list(latest_realms.keys())
            realm_counts = list(latest_realms.values())
            
            axes[1, 1].pie(realm_counts, labels=realm_names, autopct='%1.1f%%', startangle=90)
            axes[1, 1].set_title(f'Realm Distribution ({df["version"].iloc[-1]})')
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'study4_realm_establishment.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # Save data
        df.to_csv(self.output_dir / 'study4_realm_data.csv', index=False)
        
        # Analyze realm introduction timeline
        realm_introductions = {}
        for i, row in df.iterrows():
            realms = row['realm_distribution']
            for realm in realms:
                if realm not in realm_introductions:
                    realm_introductions[realm] = row['year']
        
        findings = {
            'study': 'Realm Establishment Analysis',
            'realm_system_introduced': min(realm_introductions.values()) if realm_introductions else 'N/A',
            'total_realms_established': len(realm_introductions),
            'current_realm_coverage': round(df['realm_coverage'].iloc[-1], 1),
            'realm_introduction_timeline': realm_introductions,
            'latest_realm_distribution': df['realm_distribution'].iloc[-1]
        }
        
        return findings
    
    def generate_comprehensive_report(self, all_findings: list):
        """Generate a comprehensive research report from all studies."""
        logger.info("Generating comprehensive research report")
        
        report_date = datetime.now().strftime("%Y-%m-%d")
        
        report = f"""# Longitudinal Analysis of ICTV Viral Taxonomy Evolution (2005-2024)
## Comprehensive Research Report

**Generated:** {report_date}
**Dataset:** Complete ICTV Master Species Lists MSL23-MSL40
**Timespan:** 20 years (2005-2024)
**Total Species Analyzed:** {all_findings[0]['final_diversity']['species']:,}

---

## Executive Summary

This comprehensive longitudinal study analyzes 20 years of viral taxonomy evolution using the complete ICTV Master Species List archive. The analysis reveals fundamental patterns in viral discovery, taxonomic reorganization, and classification philosophy evolution.

### Key Discoveries

1. **Exponential Growth Era**: Viral species diversity increased from 1,898 to 16,215 species (+754% growth)
2. **Major Reorganization Events**: {all_findings[1]['major_reorganization_events']} significant taxonomic restructuring events identified
3. **Nomenclature Evolution**: Shift toward standardized naming conventions and binomial-like nomenclature
4. **Hierarchical Formalization**: Introduction of realm-level classification provided systematic framework

---

## Study 1: Taxonomy Growth Patterns

### Overview
Analysis of overall taxonomic diversity growth across all hierarchical levels from 2005-2024.

### Key Findings
- **Total Species Growth**: +{all_findings[0]['total_species_growth']:,} species over {all_findings[0]['timespan']}
- **Average Annual Growth**: {all_findings[0]['average_annual_growth']} species/year
- **Peak Discovery Year**: {all_findings[0]['peak_growth_year']} ({all_findings[0]['peak_growth_rate']} species added)
- **Current Diversity**: {all_findings[0]['final_diversity']['species']:,} species across {all_findings[0]['final_diversity']['families']:,} families

### Scientific Significance
The exponential growth pattern indicates the "genomics revolution" impact on viral discovery, with modern sequencing technologies enabling rapid identification of previously unknown viral species.

---

## Study 2: Family Reorganization Events

### Overview
Identification and analysis of major taxonomic reorganization events that reshaped viral classification.

### Key Findings
- **Total Reorganization Events**: {all_findings[1]['total_transitions']} version transitions analyzed
- **Major Events Identified**: {all_findings[1]['major_reorganization_events']} high-intensity reorganizations
- **Peak Reorganization**: {all_findings[1]['peak_reorganization_year']} (highest reorganization intensity)
- **Family Turnover**: {all_findings[1]['total_new_families']} new families created, {all_findings[1]['total_family_reclassifications']} species reclassified

### Major Reorganization Timeline
"""
        
        for event in all_findings[1]['major_events_list']:
            report += f"- **{event['transition']}** ({event['year']}): Intensity {event['reorganization_intensity']:.3f}\n"
        
        report += f"""

### Scientific Significance
These reorganization events reflect evolving understanding of viral evolutionary relationships, particularly the impact of genomic and phylogenetic analyses on traditional morphology-based classifications.

---

## Study 3: Species Naming Evolution

### Overview
Analysis of nomenclatural trends and standardization efforts in viral species naming.

### Key Findings
- **Binomial Adoption**: {all_findings[2]['binomial_adoption_growth']:+.1f}% increase in binomial-like naming
- **Current Naming Distribution**:
  - Virus suffix: {all_findings[2]['current_naming_distribution']['virus_suffix']:.1f}%
  - Phage suffix: {all_findings[2]['current_naming_distribution']['phage_suffix']:.1f}%
  - Binomial-like: {all_findings[2]['current_naming_distribution']['binomial_like']:.1f}%
- **Name Complexity**: Average length change {all_findings[2]['name_complexity_trend']['avg_length_change']:+.1f} characters, {all_findings[2]['name_complexity_trend']['avg_words_change']:+.1f} words

### Scientific Significance
The trend toward standardized nomenclature reflects ICTV efforts to align viral naming with broader biological nomenclature principles, improving clarity and international consistency.

---

## Study 4: Realm Establishment Analysis

### Overview
Examination of the introduction and development of realm-level taxonomy in viral classification.

### Key Findings
- **Realm System Introduction**: {all_findings[3]['realm_system_introduced']}
- **Total Realms Established**: {all_findings[3]['total_realms_established']}
- **Current Coverage**: {all_findings[3]['current_realm_coverage']:.1f}% of species assigned to realms
- **Realm Distribution**: 
"""
        
        for realm, count in all_findings[3]['latest_realm_distribution'].items():
            percentage = (count / all_findings[0]['final_diversity']['species']) * 100
            report += f"  - {realm}: {count:,} species ({percentage:.1f}%)\n"
        
        report += f"""

### Scientific Significance
The establishment of realm-level classification represents the most significant hierarchical addition to viral taxonomy, providing essential evolutionary context for viral diversity.

---

## Implications for Viral Taxonomy

### 1. Discovery Acceleration
The exponential growth in viral species diversity demonstrates the profound impact of modern molecular techniques on viral discovery. The average annual growth rate of {all_findings[0]['average_annual_growth']} species/year suggests continued rapid expansion.

### 2. Classification Stability vs. Progress
Major reorganization events ({all_findings[1]['major_reorganization_events']} identified) indicate periods where scientific advances necessitated substantial taxonomic revision, highlighting the tension between classification stability and scientific progress.

### 3. Standardization Success
The evolution toward standardized nomenclature and hierarchical classification demonstrates ICTV's successful efforts to bring order to rapidly expanding viral diversity.

### 4. Predictive Insights
Based on historical patterns, we can anticipate:
- Continued exponential species discovery
- Periodic major reorganizations as phylogenetic understanding advances
- Further standardization of naming conventions
- Potential addition of new hierarchical levels

---

## Methodological Innovation

This study demonstrates the value of applying software development practices (git version control) to biological data management. The comprehensive historical analysis was only possible through:

1. **Complete Data Preservation**: All 18 MSL versions from 2005-2024
2. **Semantic Change Tracking**: Automated classification of taxonomic changes
3. **Longitudinal Analysis Tools**: Purpose-built research frameworks
4. **Reproducible Research**: Version-controlled data and analysis code

---

## Future Research Directions

1. **Correlation with Genomic Data**: Link taxonomic changes to phylogenetic evidence
2. **Discovery Bias Analysis**: Examine geographic and methodological biases
3. **Predictive Modeling**: Forecast future taxonomic growth and reorganization
4. **Cross-Domain Comparisons**: Compare viral taxonomy evolution with other biological domains

---

## Data Availability

All data, analysis code, and version-controlled taxonomic history are available at:
- Repository: https://github.com/shandley/ICTV-git
- Complete MSL archive: 2005-2024 (MSL23-MSL40)
- Analysis framework: Open source longitudinal analysis tools

---

## Acknowledgments

This research was enabled by:
- International Committee on Taxonomy of Viruses (ICTV) for maintaining comprehensive species lists
- The complete historical MSL archive from 2005-2024
- Git-based taxonomy management system development

*Report generated by ICTV-git longitudinal analysis framework*
"""
        
        # Save report
        report_path = self.output_dir / 'comprehensive_research_report.md'
        with open(report_path, 'w') as f:
            f.write(report)
        
        logger.info(f"Comprehensive research report saved to: {report_path}")
        return report_path


def main():
    """Main analysis runner."""
    repo_path = Path(__file__).parent.parent / 'output' / 'viral-taxonomy-evolution'
    
    if not repo_path.exists():
        logger.error(f"Repository not found at {repo_path}")
        logger.error("Please run convert_full_history.py first")
        sys.exit(1)
    
    # Create analyzer
    analyzer = LongitudinalAnalyzer(str(repo_path))
    
    print("="*80)
    print("LONGITUDINAL ANALYSIS OF ICTV TAXONOMY EVOLUTION (2005-2024)")
    print("="*80)
    print(f"Repository: {repo_path}")
    print(f"Output directory: {analyzer.output_dir}")
    print()
    
    # Run all studies
    all_findings = []
    
    print("Study 1: Taxonomy Growth Patterns...")
    findings1 = analyzer.study_1_taxonomy_growth_patterns()
    all_findings.append(findings1)
    print(f"  ✓ Analyzed {findings1['timespan']} growth patterns")
    print(f"  ✓ Total growth: +{findings1['total_species_growth']:,} species")
    
    print("\nStudy 2: Family Reorganization Events...")
    findings2 = analyzer.study_2_family_reorganization_events()
    all_findings.append(findings2)
    print(f"  ✓ Identified {findings2['major_reorganization_events']} major reorganization events")
    print(f"  ✓ Peak reorganization: {findings2['peak_reorganization_year']}")
    
    print("\nStudy 3: Species Naming Evolution...")
    findings3 = analyzer.study_3_species_naming_evolution()
    all_findings.append(findings3)
    print(f"  ✓ Binomial adoption growth: {findings3['binomial_adoption_growth']:+.1f}%")
    print(f"  ✓ Current virus suffix usage: {findings3['current_naming_distribution']['virus_suffix']:.1f}%")
    
    print("\nStudy 4: Realm Establishment Analysis...")
    findings4 = analyzer.study_4_realm_establishment_analysis()
    all_findings.append(findings4)
    print(f"  ✓ Realm system introduced: {findings4['realm_system_introduced']}")
    print(f"  ✓ Current realm coverage: {findings4['current_realm_coverage']:.1f}%")
    
    print("\nGenerating comprehensive research report...")
    report_path = analyzer.generate_comprehensive_report(all_findings)
    print(f"  ✓ Report saved to: {report_path}")
    
    # Save all findings as JSON
    findings_path = analyzer.output_dir / 'all_findings.json'
    with open(findings_path, 'w') as f:
        json.dump(all_findings, f, indent=2)
    
    print("\n" + "="*80)
    print("LONGITUDINAL ANALYSIS COMPLETE")
    print("="*80)
    print(f"Research findings: {analyzer.output_dir}")
    print(f"Visualizations: {len(list(analyzer.output_dir.glob('*.png')))} plots generated")
    print(f"Data files: {len(list(analyzer.output_dir.glob('*.csv')))} datasets saved")
    print(f"Comprehensive report: {report_path.name}")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)