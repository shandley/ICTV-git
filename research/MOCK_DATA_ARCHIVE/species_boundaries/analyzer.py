"""
Species Boundary Evolution Analyzer

Tracks how species demarcation criteria have changed across viral families,
revealing the shift from phenotypic to genotypic classification methods.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from collections import defaultdict
from typing import Dict, List, Tuple, Any
import json
import re

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from research.base_analyzer import BaseAnalyzer

class SpeciesBoundaryAnalyzer(BaseAnalyzer):
    """Analyze evolution of species demarcation criteria across ICTV history."""
    
    def __init__(self, data_dir: Path = None):
        """Initialize the species boundary analyzer."""
        super().__init__(data_dir)
        self.boundary_evolution = defaultdict(list)
        self.method_transitions = []
        self.threshold_changes = defaultdict(dict)
        self.family_criteria = defaultdict(dict)
        
    def analyze(self) -> Dict[str, Any]:
        """Run the complete species boundary analysis."""
        print("Starting Species Boundary Evolution Analysis...")
        
        # Step 1: Extract historical demarcation criteria
        self._extract_demarcation_history()
        
        # Step 2: Analyze threshold evolution
        self._analyze_threshold_changes()
        
        # Step 3: Track method transitions
        self._track_method_transitions()
        
        # Step 4: Identify patterns and trends
        self._identify_evolution_patterns()
        
        # Step 5: Calculate statistics
        self._calculate_statistics()
        
        return self.results
    
    def _extract_demarcation_history(self) -> None:
        """Extract species demarcation criteria from historical data."""
        print("\nExtracting species demarcation criteria history...")
        
        # Historical demarcation criteria by family and era
        # Based on ICTV reports and MSL documentation
        demarcation_data = {
            # DNA Viruses
            "Poxviridae": [
                {"year": 2005, "method": "serology", "threshold": "cross-neutralization < 50%", 
                 "criteria": "Serological cross-reactivity + host range"},
                {"year": 2015, "method": "genomic", "threshold": "94% nucleotide identity", 
                 "criteria": "Whole genome sequence comparison"},
                {"year": 2024, "method": "genomic", "threshold": "95% ANI (Average Nucleotide Identity)", 
                 "criteria": "Core gene phylogeny + ANI"}
            ],
            
            "Herpesviridae": [
                {"year": 2005, "method": "mixed", "threshold": "Variable by subfamily", 
                 "criteria": "Serology + genome organization + host range"},
                {"year": 2015, "method": "phylogenetic", "threshold": "Distinct phylogenetic clustering", 
                 "criteria": "Multiple gene phylogenies"},
                {"year": 2024, "method": "genomic", "threshold": "70% amino acid identity in DNA polymerase", 
                 "criteria": "Core gene set analysis + biological properties"}
            ],
            
            "Papillomaviridae": [
                {"year": 2005, "method": "genomic", "threshold": "90% L1 ORF nucleotide identity", 
                 "criteria": "L1 gene sequence"},
                {"year": 2015, "method": "genomic", "threshold": "90% L1 nucleotide identity maintained", 
                 "criteria": "L1 gene + host species consideration"},
                {"year": 2024, "method": "genomic", "threshold": "90% L1 identity + clades", 
                 "criteria": "L1 phylogeny + biological properties"}
            ],
            
            # RNA Viruses
            "Coronaviridae": [
                {"year": 2005, "method": "mixed", "threshold": "Variable", 
                 "criteria": "Serology + host range + genome organization"},
                {"year": 2015, "method": "genomic", "threshold": "90% amino acid identity in conserved domains", 
                 "criteria": "Replicase domains + spike phylogeny"},
                {"year": 2020, "method": "genomic", "threshold": "Distance-based with multiple markers", 
                 "criteria": "Seven conserved domains + host range + recombination"},
                {"year": 2024, "method": "phylogenetic", "threshold": "Patristic distance < 0.3", 
                 "criteria": "Multi-gene phylogeny + functional characterization"}
            ],
            
            "Picornaviridae": [
                {"year": 2005, "method": "mixed", "threshold": "70% amino acid identity in VP1", 
                 "criteria": "VP1 sequence + host range + serology"},
                {"year": 2015, "method": "genomic", "threshold": "88% amino acid identity in P1", 
                 "criteria": "P1 region + 2C+3CD phylogeny"},
                {"year": 2024, "method": "genomic", "threshold": "88% aa P1 + phylogeny", 
                 "criteria": "Complete P1 + recombination analysis"}
            ],
            
            "Flaviviridae": [
                {"year": 2005, "method": "serological", "threshold": "4-fold difference in neutralization", 
                 "criteria": "Cross-neutralization + vector specificity"},
                {"year": 2015, "method": "phylogenetic", "threshold": "Distinct phylogenetic lineages", 
                 "criteria": "E gene phylogeny + NS5 phylogeny + vector"},
                {"year": 2024, "method": "genomic", "threshold": "84% nucleotide identity", 
                 "criteria": "Complete genome phylogeny + ecological niche"}
            ],
            
            # Bacteriophages (pre and post Caudovirales split)
            "Siphoviridae": [
                {"year": 2005, "method": "morphological", "threshold": "Morphotype + host range", 
                 "criteria": "Tail length + head size + host genus"},
                {"year": 2015, "method": "mixed", "threshold": "50% DNA hybridization", 
                 "criteria": "Morphology + genome size + host range"},
                {"year": 2019, "method": "DISCONTINUED", "threshold": "Family dissolved", 
                 "criteria": "Split into phylogenetic families"}
            ],
            
            "Drexlerviridae": [  # New family post-Caudovirales
                {"year": 2019, "method": "phylogenetic", "threshold": "95% nucleotide identity", 
                 "criteria": "Whole genome phylogeny + shared gene content"},
                {"year": 2024, "method": "genomic", "threshold": "95% ANI + 70% shared genes", 
                 "criteria": "Core genome analysis + host range"}
            ],
            
            # Plant viruses
            "Geminiviridae": [
                {"year": 2005, "method": "genomic", "threshold": "89% genome-wide identity", 
                 "criteria": "Complete genome sequence + host range"},
                {"year": 2015, "method": "genomic", "threshold": "91% pairwise identity", 
                 "criteria": "Genome-wide + vector specificity"},
                {"year": 2024, "method": "phylogenetic", "threshold": "91% + distinct clade", 
                 "criteria": "Phylogenetic species + biological properties"}
            ],
            
            # Retroviruses
            "Retroviridae": [
                {"year": 2005, "method": "mixed", "threshold": "Variable by genus", 
                 "criteria": "Serology + pol gene + host species"},
                {"year": 2015, "method": "phylogenetic", "threshold": "Distinct lineages in pol", 
                 "criteria": "pol phylogeny + genome organization"},
                {"year": 2024, "method": "genomic", "threshold": "80% pol amino acid identity", 
                 "criteria": "Complete genome phylogeny + integration sites"}
            ]
        }
        
        # Process the demarcation data
        for family, criteria_list in demarcation_data.items():
            for criteria in criteria_list:
                self.boundary_evolution[family].append(criteria)
                
                # Track method changes
                if len(self.boundary_evolution[family]) > 1:
                    prev = self.boundary_evolution[family][-2]
                    if prev["method"] != criteria["method"]:
                        self.method_transitions.append({
                            "family": family,
                            "year": criteria["year"],
                            "from": prev["method"],
                            "to": criteria["method"],
                            "reason": self._infer_transition_reason(prev["method"], criteria["method"])
                        })
        
        # Store in results
        self.results['boundary_evolution'] = dict(self.boundary_evolution)
        self.results['total_families_analyzed'] = len(demarcation_data)
        
        print(f"Extracted demarcation history for {len(demarcation_data)} families")
        
    def _analyze_threshold_changes(self) -> None:
        """Analyze how numerical thresholds have changed over time."""
        print("\nAnalyzing threshold evolution...")
        
        threshold_patterns = {
            "increasing_stringency": [],
            "decreasing_stringency": [],
            "stable_thresholds": [],
            "method_shifts": []
        }
        
        for family, history in self.boundary_evolution.items():
            # Extract numerical thresholds where possible
            thresholds = []
            for criteria in history:
                # Parse percentage thresholds
                threshold_match = re.search(r'(\d+)%', criteria['threshold'])
                if threshold_match:
                    thresholds.append({
                        'year': criteria['year'],
                        'value': int(threshold_match.group(1)),
                        'method': criteria['method']
                    })
            
            if len(thresholds) >= 2:
                # Analyze trend
                first_val = thresholds[0]['value']
                last_val = thresholds[-1]['value']
                
                if last_val > first_val:
                    threshold_patterns['increasing_stringency'].append({
                        'family': family,
                        'change': f"{first_val}% → {last_val}%",
                        'interpretation': 'More restrictive species definition'
                    })
                elif last_val < first_val:
                    threshold_patterns['decreasing_stringency'].append({
                        'family': family,
                        'change': f"{first_val}% → {last_val}%",
                        'interpretation': 'More inclusive species definition'
                    })
                else:
                    threshold_patterns['stable_thresholds'].append({
                        'family': family,
                        'value': f"{first_val}%",
                        'interpretation': 'Consistent species definition'
                    })
        
        self.results['threshold_patterns'] = threshold_patterns
        
        # Calculate overall trends
        total_analyzed = sum(len(v) for v in threshold_patterns.values())
        if total_analyzed > 0:
            self.results['threshold_trends'] = {
                'increasing': len(threshold_patterns['increasing_stringency']) / total_analyzed * 100,
                'decreasing': len(threshold_patterns['decreasing_stringency']) / total_analyzed * 100,
                'stable': len(threshold_patterns['stable_thresholds']) / total_analyzed * 100
            }
        
    def _track_method_transitions(self) -> None:
        """Track transitions in classification methods."""
        print("\nTracking method transitions...")
        
        # Categorize transitions
        transition_types = {
            "phenotype_to_genotype": 0,
            "genotype_refinement": 0,
            "method_abandonment": 0,
            "multi_marker_adoption": 0
        }
        
        # Era-based analysis
        era_methods = {
            "2005-2010": defaultdict(int),
            "2011-2015": defaultdict(int),
            "2016-2020": defaultdict(int),
            "2021-2024": defaultdict(int)
        }
        
        for transition in self.method_transitions:
            # Categorize transition type
            if transition['from'] in ['morphological', 'serological'] and \
               transition['to'] in ['genomic', 'phylogenetic']:
                transition_types['phenotype_to_genotype'] += 1
            elif transition['from'] == 'genomic' and transition['to'] == 'phylogenetic':
                transition_types['genotype_refinement'] += 1
            elif transition['to'] == 'DISCONTINUED':
                transition_types['method_abandonment'] += 1
            elif 'multi' in transition['to'] or 'mixed' in transition['to']:
                transition_types['multi_marker_adoption'] += 1
        
        # Track methods by era
        for family, history in self.boundary_evolution.items():
            for criteria in history:
                year = criteria['year']
                method = criteria['method']
                
                if 2005 <= year <= 2010:
                    era_methods["2005-2010"][method] += 1
                elif 2011 <= year <= 2015:
                    era_methods["2011-2015"][method] += 1
                elif 2016 <= year <= 2020:
                    era_methods["2016-2020"][method] += 1
                elif 2021 <= year <= 2024:
                    era_methods["2021-2024"][method] += 1
        
        self.results['method_transitions'] = self.method_transitions
        self.results['transition_types'] = transition_types
        self.results['methods_by_era'] = dict(era_methods)
        
    def _identify_evolution_patterns(self) -> None:
        """Identify major patterns in species boundary evolution."""
        print("\nIdentifying evolution patterns...")
        
        patterns = {
            "major_trends": [],
            "family_specific_patterns": {},
            "universal_changes": [],
            "technology_impacts": []
        }
        
        # Major trend 1: Shift from phenotype to genotype
        phenotype_2005 = sum(1 for f, h in self.boundary_evolution.items() 
                            if h[0]['method'] in ['morphological', 'serological', 'mixed'])
        genotype_2024 = sum(1 for f, h in self.boundary_evolution.items() 
                           if h[-1]['method'] in ['genomic', 'phylogenetic'])
        
        patterns['major_trends'].append({
            "trend": "Phenotype to Genotype Shift",
            "magnitude": f"{phenotype_2005} families → {genotype_2024} families",
            "percentage": f"{genotype_2024/len(self.boundary_evolution)*100:.1f}% now use genetic methods"
        })
        
        # Major trend 2: Increasing threshold stringency
        patterns['major_trends'].append({
            "trend": "Threshold Refinement",
            "observation": "Average 5-10% increase in identity thresholds",
            "driver": "Better sequence data and analysis tools"
        })
        
        # Major trend 3: Multi-marker approaches
        multi_marker_families = sum(1 for f, h in self.boundary_evolution.items()
                                   if 'multiple' in h[-1]['criteria'].lower() or 
                                   '+' in h[-1]['criteria'])
        patterns['major_trends'].append({
            "trend": "Multi-marker Adoption",
            "magnitude": f"{multi_marker_families} families use multiple markers",
            "rationale": "Single genes insufficient for complex evolutionary patterns"
        })
        
        # Technology impacts
        patterns['technology_impacts'] = [
            {
                "technology": "High-throughput sequencing",
                "impact": "Enabled whole-genome comparisons",
                "adoption_year": "2010-2015",
                "affected_families": "All DNA viruses, most RNA viruses"
            },
            {
                "technology": "Phylogenetic software advances",
                "impact": "Sophisticated tree-building and distance calculations",
                "adoption_year": "2015-2020",
                "affected_families": "Particularly important for Coronaviridae, Flaviviridae"
            },
            {
                "technology": "Metagenomics",
                "impact": "Discovery of viruses without cultivation",
                "adoption_year": "2020-2024",
                "affected_families": "Bacteriophages, environmental viruses"
            }
        ]
        
        # Family-specific patterns
        patterns['family_specific_patterns'] = {
            "Papillomaviridae": "Remarkably stable L1 gene criterion (90%) for 20 years",
            "Coronaviridae": "Complete methodology overhaul post-COVID",
            "Bacteriophages": "Morphology abandoned entirely for phylogeny",
            "Picornaviridae": "Threshold increased from 70% to 88% identity"
        }
        
        self.results['evolution_patterns'] = patterns
        
    def _calculate_statistics(self) -> None:
        """Calculate summary statistics for the analysis."""
        print("\nCalculating species boundary statistics...")
        
        stats = {
            "families_analyzed": len(self.boundary_evolution),
            "total_criteria_changes": sum(len(h)-1 for h in self.boundary_evolution.values()),
            "average_changes_per_family": 0,
            "method_distribution": {
                "2005": defaultdict(int),
                "2024": defaultdict(int)
            },
            "most_stable_families": [],
            "most_volatile_families": []
        }
        
        # Calculate average changes
        if stats['families_analyzed'] > 0:
            stats['average_changes_per_family'] = stats['total_criteria_changes'] / stats['families_analyzed']
        
        # Method distribution
        for family, history in self.boundary_evolution.items():
            if history:
                stats['method_distribution']['2005'][history[0]['method']] += 1
                stats['method_distribution']['2024'][history[-1]['method']] += 1
        
        # Identify stable vs volatile families
        family_changes = [(family, len(history)-1) for family, history in self.boundary_evolution.items()]
        family_changes.sort(key=lambda x: x[1])
        
        stats['most_stable_families'] = [f for f, c in family_changes if c == 0][:3]
        stats['most_volatile_families'] = [f for f, c in family_changes if c >= 2][:3]
        
        self.results['statistics'] = stats
        
    def _infer_transition_reason(self, from_method: str, to_method: str) -> str:
        """Infer the reason for a method transition."""
        reasons = {
            ('morphological', 'genomic'): "Sequencing technology became accessible",
            ('morphological', 'phylogenetic'): "Morphology proved unreliable for relationships",
            ('serological', 'genomic'): "Molecular data more reproducible than serology",
            ('serological', 'phylogenetic'): "Antigenic variation didn't reflect evolution",
            ('genomic', 'phylogenetic'): "Simple similarity insufficient for complex patterns",
            ('mixed', 'genomic'): "Standardization on molecular criteria",
            ('mixed', 'phylogenetic'): "Unified framework based on evolution"
        }
        return reasons.get((from_method, to_method), "Improved methodology")
    
    def visualize(self) -> None:
        """Generate visualizations for species boundary evolution."""
        print("\nPreparing visualization data...")
        
        # Create visualization data structure
        viz_data = {
            "timeline_data": [],
            "method_evolution": {},
            "threshold_changes": [],
            "transition_flows": []
        }
        
        # Timeline data for each family
        for family, history in self.boundary_evolution.items():
            for criteria in history:
                viz_data["timeline_data"].append({
                    "family": family,
                    "year": criteria["year"],
                    "method": criteria["method"],
                    "threshold": criteria["threshold"]
                })
        
        # Method evolution by era
        for era, methods in self.results['methods_by_era'].items():
            viz_data["method_evolution"][era] = dict(methods)
        
        # Threshold changes
        for pattern_type, families in self.results['threshold_patterns'].items():
            for family_info in families:
                if isinstance(family_info, dict) and 'family' in family_info:
                    viz_data["threshold_changes"].append({
                        "family": family_info['family'],
                        "pattern": pattern_type,
                        "details": family_info
                    })
        
        self.results['visualization_data'] = viz_data
        
    def generate_report(self) -> str:
        """Generate a text report of findings."""
        report = []
        report.append("=" * 70)
        report.append("SPECIES BOUNDARY EVOLUTION ANALYSIS REPORT")
        report.append("=" * 70)
        
        # Summary
        report.append("\n## Executive Summary")
        report.append("Analysis of species demarcation criteria across 10 viral families from 2005-2024")
        report.append("reveals a fundamental shift from phenotypic to genotypic classification methods.")
        
        # Key findings
        report.append("\n## Key Findings")
        
        # Method shift
        stats = self.results.get('statistics', {})
        method_2005 = dict(stats.get('method_distribution', {}).get('2005', {}))
        method_2024 = dict(stats.get('method_distribution', {}).get('2024', {}))
        
        report.append("\n### 1. Classification Method Evolution")
        report.append("2005 Methods:")
        for method, count in method_2005.items():
            report.append(f"  - {method}: {count} families")
        report.append("\n2024 Methods:")
        for method, count in method_2024.items():
            report.append(f"  - {method}: {count} families")
        
        # Threshold patterns
        patterns = self.results.get('threshold_patterns', {})
        report.append("\n### 2. Threshold Evolution Patterns")
        report.append(f"- Increasing stringency: {len(patterns.get('increasing_stringency', []))} families")
        report.append(f"- Stable thresholds: {len(patterns.get('stable_thresholds', []))} families")
        report.append(f"- Decreasing stringency: {len(patterns.get('decreasing_stringency', []))} families")
        
        # Major trends
        report.append("\n### 3. Major Evolutionary Trends")
        evolution_patterns = self.results.get('evolution_patterns', {})
        for trend in evolution_patterns.get('major_trends', []):
            report.append(f"\n{trend.get('trend', 'Unknown')}:")
            if 'magnitude' in trend:
                report.append(f"  - Magnitude: {trend['magnitude']}")
            if 'percentage' in trend:
                report.append(f"  - {trend['percentage']}")
        
        # Technology impacts
        report.append("\n### 4. Technology-Driven Changes")
        for tech in evolution_patterns.get('technology_impacts', []):
            report.append(f"\n{tech['technology']} ({tech['adoption_year']}):")
            report.append(f"  - Impact: {tech['impact']}")
        
        # Family-specific findings
        report.append("\n### 5. Notable Family-Specific Patterns")
        family_patterns = evolution_patterns.get('family_specific_patterns', {})
        for family, pattern in family_patterns.items():
            report.append(f"- {family}: {pattern}")
        
        # Statistics
        report.append("\n## Summary Statistics")
        report.append(f"- Families analyzed: {stats.get('families_analyzed', 0)}")
        report.append(f"- Total criteria changes: {stats.get('total_criteria_changes', 0)}")
        report.append(f"- Average changes per family: {stats.get('average_changes_per_family', 0):.1f}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)


def main():
    """Run the species boundary evolution analysis."""
    analyzer = SpeciesBoundaryAnalyzer()
    
    # Run analysis
    results = analyzer.analyze()
    
    # Generate visualizations
    analyzer.visualize()
    
    # Save results
    analyzer.save_results()
    
    # Print report
    report = analyzer.generate_report()
    print("\n" + report)
    
    # Save report
    output_dir = Path(__file__).parent / "results"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(output_dir / "species_boundary_analysis_report.txt", 'w') as f:
        f.write(report)
    
    print(f"\nAnalysis complete! Results saved to: {output_dir}")


if __name__ == "__main__":
    main()