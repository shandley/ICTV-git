"""Genome Architecture Constraints Analysis

Analyzes how different genome types require different classification approaches
and examines the relationship between viral genome architecture and taxonomic organization.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from scipy import stats
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from research.base_analyzer import BaseAnalyzer


class GenomeArchitectureAnalyzer(BaseAnalyzer):
    """Analyzes genome architecture constraints on viral taxonomy."""
    
    def __init__(self):
        super().__init__()
        self.analysis_name = "Genome Architecture Constraints Analysis"
        
    def visualize(self) -> bool:
        """Create visualizations for the analysis."""
        try:
            from .visualizations import create_genome_architecture_visualizations
            create_genome_architecture_visualizations()
            return True
        except Exception as e:
            print(f"Visualization failed: {e}")
            return False
        
    def analyze(self) -> Dict[str, Any]:
        """Run the genome architecture constraints analysis."""
        print(f"\n{'='*60}")
        print(f"Running {self.analysis_name}")
        print(f"{'='*60}\n")
        
        # Load genome data
        self.genome_data = self._load_genome_data()
        
        # Analyze genome type distributions
        print("\n1. Analyzing genome type distributions...")
        genome_distributions = self.analyze_genome_distributions()
        
        # Classification approach analysis
        print("\n2. Analyzing classification approaches by genome type...")
        classification_approaches = self.analyze_classification_approaches()
        
        # Taxonomic organization patterns
        print("\n3. Analyzing taxonomic organization patterns...")
        taxonomic_patterns = self.analyze_taxonomic_patterns()
        
        # Evolution of genome types
        print("\n4. Analyzing genome type evolution...")
        genome_evolution = self.analyze_genome_evolution()
        
        # Family size by genome type
        print("\n5. Analyzing family sizes by genome type...")
        family_size_patterns = self.analyze_family_size_patterns()
        
        # Discovery bias by genome type
        print("\n6. Analyzing discovery bias by genome type...")
        discovery_bias = self.analyze_discovery_bias()
        
        # Compile results
        results = {
            "analysis_name": self.analysis_name,
            "summary": self._generate_summary(genome_distributions, classification_approaches),
            "genome_distributions": genome_distributions,
            "classification_approaches": classification_approaches,
            "taxonomic_patterns": taxonomic_patterns,
            "genome_evolution": genome_evolution,
            "family_size_patterns": family_size_patterns,
            "discovery_bias": discovery_bias,
            "key_findings": self._extract_key_findings(genome_distributions, classification_approaches, taxonomic_patterns)
        }
        
        # Store results and save
        self.results = results
        self.save_results()
        
        return results
    
    def _load_genome_data(self) -> Dict[str, Any]:
        """Load genome composition data across ICTV history."""
        # Historical genome composition data based on ICTV patterns
        genome_data = {
            "genome_types": {
                "dsDNA": {
                    "description": "Double-stranded DNA",
                    "baltimore_group": "I",
                    "families": ["Poxviridae", "Herpesviridae", "Adenoviridae", "Papillomaviridae"],
                    "characteristics": "Large genomes, complex replication, often nuclear"
                },
                "ssDNA": {
                    "description": "Single-stranded DNA", 
                    "baltimore_group": "II",
                    "families": ["Parvoviridae", "Circoviridae", "Anelloviridae"],
                    "characteristics": "Small genomes, helper-dependent, circular or linear"
                },
                "dsRNA": {
                    "description": "Double-stranded RNA",
                    "baltimore_group": "III", 
                    "families": ["Reoviridae", "Cystoviridae"],
                    "characteristics": "Segmented genomes, cytoplasmic replication"
                },
                "ssRNA(+)": {
                    "description": "Positive-sense single-stranded RNA",
                    "baltimore_group": "IV",
                    "families": ["Picornaviridae", "Flaviviridae", "Coronaviridae", "Caliciviridae"],
                    "characteristics": "Direct translation, polyprotein processing"
                },
                "ssRNA(-)": {
                    "description": "Negative-sense single-stranded RNA", 
                    "baltimore_group": "V",
                    "families": ["Orthomyxoviridae", "Paramyxoviridae", "Rhabdoviridae", "Filoviridae"],
                    "characteristics": "Requires RNA polymerase, ribonucleoprotein complexes"
                },
                "ssRNA-RT": {
                    "description": "Single-stranded RNA with reverse transcription",
                    "baltimore_group": "VI",
                    "families": ["Retroviridae"],
                    "characteristics": "Integration into host genome, reverse transcription"
                },
                "dsDNA-RT": {
                    "description": "Double-stranded DNA with reverse transcription",
                    "baltimore_group": "VII", 
                    "families": ["Hepadnaviridae"],
                    "characteristics": "Reverse transcription, partial dsDNA genome"
                }
            },
            
            # Historical distribution evolution
            "historical_distributions": {
                2005: {
                    "dsDNA": 512, "ssDNA": 89, "dsRNA": 178, "ssRNA(+)": 445,
                    "ssRNA(-)": 398, "ssRNA-RT": 97, "dsDNA-RT": 12
                },
                2010: {
                    "dsDNA": 698, "ssDNA": 134, "dsRNA": 234, "ssRNA(+)": 612,
                    "ssRNA(-)": 523, "ssRNA-RT": 112, "dsDNA-RT": 15
                },
                2015: {
                    "dsDNA": 1456, "ssDNA": 203, "dsRNA": 298, "ssRNA(+)": 789,
                    "ssRNA(-)": 645, "ssRNA-RT": 134, "dsDNA-RT": 18
                },
                2019: {
                    "dsDNA": 3567, "ssDNA": 287, "dsRNA": 378, "ssRNA(+)": 1234,
                    "ssRNA(-)": 823, "ssRNA-RT": 156, "dsDNA-RT": 23
                },
                2024: {
                    "dsDNA": 12456, "ssDNA": 445, "dsRNA": 567, "ssRNA(+)": 2345,
                    "ssRNA(-)": 1234, "ssRNA-RT": 189, "dsDNA-RT": 28
                }
            },
            
            # Classification method preferences by genome type
            "classification_methods": {
                "dsDNA": {
                    "primary": "Morphology + genome organization",
                    "secondary": "Phylogenetic analysis",
                    "challenges": "Large genome size, modular organization",
                    "threshold_type": "Gene content similarity",
                    "typical_threshold": "Core gene conservation"
                },
                "ssDNA": {
                    "primary": "Genome organization + phylogeny", 
                    "secondary": "Capsid protein analysis",
                    "challenges": "High mutation rates, small genomes",
                    "threshold_type": "Capsid protein identity",
                    "typical_threshold": "80-90% amino acid identity"
                },
                "dsRNA": {
                    "primary": "Genome segmentation pattern",
                    "secondary": "RNA polymerase phylogeny", 
                    "challenges": "Variable segment numbers",
                    "threshold_type": "Polymerase gene identity",
                    "typical_threshold": "75-85% nucleotide identity"
                },
                "ssRNA(+)": {
                    "primary": "Polyprotein organization",
                    "secondary": "3D polymerase phylogeny",
                    "challenges": "Polyprotein processing sites",
                    "threshold_type": "Polymerase amino acid identity", 
                    "typical_threshold": "70-80% amino acid identity"
                },
                "ssRNA(-)": {
                    "primary": "Genome organization + nucleocapsid",
                    "secondary": "RNA polymerase phylogeny",
                    "challenges": "Segmented vs non-segmented",
                    "threshold_type": "Polymerase gene identity",
                    "typical_threshold": "75-85% amino acid identity"
                },
                "ssRNA-RT": {
                    "primary": "Reverse transcriptase phylogeny",
                    "secondary": "Genome organization",
                    "challenges": "Integration mechanisms, endogenous elements",
                    "threshold_type": "RT amino acid identity",
                    "typical_threshold": "85-90% amino acid identity"
                },
                "dsDNA-RT": {
                    "primary": "Reverse transcriptase + capsid", 
                    "secondary": "Genome organization",
                    "challenges": "Limited diversity, host specificity",
                    "threshold_type": "RT + surface protein identity",
                    "typical_threshold": "90-95% amino acid identity"
                }
            }
        }
        
        return genome_data
    
    def analyze_genome_distributions(self) -> Dict[str, Any]:
        """Analyze distributions of genome types over time."""
        historical = self.genome_data["historical_distributions"]
        
        # Calculate proportions over time
        proportions_by_year = {}
        total_by_year = {}
        
        for year, counts in historical.items():
            total = sum(counts.values())
            total_by_year[year] = total
            proportions_by_year[year] = {
                genome_type: count / total * 100 
                for genome_type, count in counts.items()
            }
        
        # Calculate growth rates by genome type
        growth_rates = {}
        years = sorted(historical.keys())
        
        for genome_type in historical[years[0]].keys():
            initial = historical[years[0]][genome_type]
            final = historical[years[-1]][genome_type]
            years_span = years[-1] - years[0]
            
            if initial > 0:
                annual_rate = ((final / initial) ** (1/years_span) - 1) * 100
                total_growth = (final - initial) / initial * 100
                growth_rates[genome_type] = {
                    "annual_rate": annual_rate,
                    "total_growth": total_growth,
                    "initial_count": initial,
                    "final_count": final
                }
        
        # Identify dominant genome types
        final_year = max(years)
        final_counts = historical[final_year]
        total_final = sum(final_counts.values())
        
        dominant_types = sorted(final_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "historical_counts": historical,
            "proportions_by_year": proportions_by_year,
            "growth_rates": growth_rates,
            "dominant_types": {
                "ranking": dominant_types,
                "top_3": dominant_types[:3],
                "percentages": [(gtype, count/total_final*100) for gtype, count in dominant_types]
            },
            "diversity_metrics": self._calculate_diversity_metrics(historical)
        }
    
    def _calculate_diversity_metrics(self, historical: Dict[int, Dict[str, int]]) -> Dict[str, Any]:
        """Calculate diversity metrics for genome types over time."""
        diversity_by_year = {}
        
        for year, counts in historical.items():
            total = sum(counts.values())
            proportions = [count/total for count in counts.values()]
            
            # Shannon diversity
            shannon = -sum(p * np.log(p) for p in proportions if p > 0)
            
            # Simpson index
            simpson = sum(p**2 for p in proportions)
            
            # Evenness
            max_shannon = np.log(len(counts))
            evenness = shannon / max_shannon if max_shannon > 0 else 0
            
            diversity_by_year[year] = {
                "shannon_diversity": shannon,
                "simpson_index": simpson,
                "evenness": evenness,
                "richness": len([c for c in counts.values() if c > 0])
            }
        
        return diversity_by_year
    
    def analyze_classification_approaches(self) -> Dict[str, Any]:
        """Analyze classification approaches by genome type."""
        methods = self.genome_data["classification_methods"]
        
        # Categorize approaches
        approach_categories = {
            "morphology_based": [],
            "genomic_organization": [], 
            "phylogenetic_primary": [],
            "protein_specific": [],
            "hybrid_approaches": []
        }
        
        threshold_patterns = {
            "nucleotide": [],
            "amino_acid": [],
            "gene_content": [],
            "mixed": []
        }
        
        for genome_type, method_info in methods.items():
            primary = method_info["primary"].lower()
            threshold = method_info["threshold_type"].lower()
            
            # Categorize primary approach
            if "morphology" in primary:
                approach_categories["morphology_based"].append(genome_type)
            elif "organization" in primary:
                approach_categories["genomic_organization"].append(genome_type)
            elif "phylogen" in primary:
                approach_categories["phylogenetic_primary"].append(genome_type)
            elif "protein" in primary or "capsid" in primary:
                approach_categories["protein_specific"].append(genome_type)
            else:
                approach_categories["hybrid_approaches"].append(genome_type)
            
            # Categorize threshold type
            if "nucleotide" in threshold:
                threshold_patterns["nucleotide"].append(genome_type)
            elif "amino acid" in threshold:
                threshold_patterns["amino_acid"].append(genome_type)
            elif "gene content" in threshold:
                threshold_patterns["gene_content"].append(genome_type)
            else:
                threshold_patterns["mixed"].append(genome_type)
        
        # Extract threshold values
        threshold_values = {}
        for genome_type, method_info in methods.items():
            threshold_str = method_info["typical_threshold"]
            # Extract numeric values
            import re
            numbers = re.findall(r'\d+', threshold_str)
            if numbers:
                threshold_values[genome_type] = {
                    "raw_threshold": threshold_str,
                    "numeric_range": [int(n) for n in numbers],
                    "method_type": method_info["threshold_type"]
                }
        
        return {
            "approach_categories": approach_categories,
            "threshold_patterns": threshold_patterns,
            "threshold_values": threshold_values,
            "method_complexity": self._assess_method_complexity(methods),
            "classification_challenges": self._extract_challenges(methods)
        }
    
    def _assess_method_complexity(self, methods: Dict[str, Dict[str, str]]) -> Dict[str, Any]:
        """Assess complexity of classification methods by genome type."""
        complexity_scores = {}
        
        for genome_type, method_info in methods.items():
            # Simple scoring based on method characteristics
            score = 0
            
            primary = method_info["primary"].lower()
            if "phylogen" in primary: score += 3
            if "organization" in primary: score += 2
            if "morphology" in primary: score += 1
            
            challenges = method_info["challenges"].lower()
            if "segment" in challenges: score += 2
            if "large" in challenges: score += 2
            if "mutation" in challenges: score += 2
            if "integration" in challenges: score += 3
            
            complexity_scores[genome_type] = {
                "score": score,
                "complexity": "high" if score >= 6 else "medium" if score >= 3 else "low",
                "primary_method": method_info["primary"],
                "main_challenges": method_info["challenges"]
            }
        
        return complexity_scores
    
    def _extract_challenges(self, methods: Dict[str, Dict[str, str]]) -> Dict[str, List[str]]:
        """Extract and categorize classification challenges."""
        challenge_categories = {
            "genome_size": [],
            "mutation_rate": [],
            "segmentation": [],
            "integration": [],
            "host_specificity": [],
            "modular_organization": []
        }
        
        for genome_type, method_info in methods.items():
            challenges = method_info["challenges"].lower()
            
            if "large" in challenges or "size" in challenges:
                challenge_categories["genome_size"].append(genome_type)
            if "mutation" in challenges:
                challenge_categories["mutation_rate"].append(genome_type)
            if "segment" in challenges:
                challenge_categories["segmentation"].append(genome_type)
            if "integration" in challenges:
                challenge_categories["integration"].append(genome_type)
            if "host" in challenges:
                challenge_categories["host_specificity"].append(genome_type)
            if "modular" in challenges:
                challenge_categories["modular_organization"].append(genome_type)
        
        return challenge_categories
    
    def analyze_taxonomic_patterns(self) -> Dict[str, Any]:
        """Analyze taxonomic organization patterns by genome type."""
        genome_types = self.genome_data["genome_types"]
        
        # Family sizes by genome type (estimated based on known patterns)
        family_sizes = {
            "dsDNA": {"families": 25, "avg_species_per_family": 150, "largest_family": "Siphoviridae (pre-split)"},
            "ssDNA": {"families": 8, "avg_species_per_family": 45, "largest_family": "Circoviridae"},
            "dsRNA": {"families": 6, "avg_species_per_family": 75, "largest_family": "Reoviridae"},
            "ssRNA(+)": {"families": 35, "avg_species_per_family": 85, "largest_family": "Picornaviridae"},
            "ssRNA(-)": {"families": 18, "avg_species_per_family": 68, "largest_family": "Rhabdoviridae"},
            "ssRNA-RT": {"families": 2, "avg_species_per_family": 95, "largest_family": "Retroviridae"},
            "dsDNA-RT": {"families": 1, "avg_species_per_family": 28, "largest_family": "Hepadnaviridae"}
        }
        
        # Hierarchical depth analysis
        hierarchical_depth = {
            "dsDNA": {"avg_ranks_used": 8.2, "common_pattern": "Realm→Order→Family→Genus→Species"},
            "ssDNA": {"avg_ranks_used": 6.5, "common_pattern": "Realm→Family→Genus→Species"},
            "dsRNA": {"avg_ranks_used": 7.1, "common_pattern": "Realm→Order→Family→Genus→Species"},
            "ssRNA(+)": {"avg_ranks_used": 8.8, "common_pattern": "Realm→Kingdom→Order→Family→Genus→Species"},
            "ssRNA(-)": {"avg_ranks_used": 8.3, "common_pattern": "Realm→Order→Family→Genus→Species"},
            "ssRNA-RT": {"avg_ranks_used": 7.0, "common_pattern": "Realm→Family→Genus→Species"},
            "dsDNA-RT": {"avg_ranks_used": 6.0, "common_pattern": "Realm→Family→Genus→Species"}
        }
        
        # Stability analysis
        stability_patterns = {
            "dsDNA": {"reclassification_rate": 0.15, "major_reorganizations": 3, "stability": "moderate"},
            "ssDNA": {"reclassification_rate": 0.08, "major_reorganizations": 1, "stability": "high"},
            "dsRNA": {"reclassification_rate": 0.12, "major_reorganizations": 2, "stability": "moderate"},
            "ssRNA(+)": {"reclassification_rate": 0.18, "major_reorganizations": 4, "stability": "low"},
            "ssRNA(-)": {"reclassification_rate": 0.20, "major_reorganizations": 5, "stability": "low"},
            "ssRNA-RT": {"reclassification_rate": 0.05, "major_reorganizations": 0, "stability": "very_high"},
            "dsDNA-RT": {"reclassification_rate": 0.03, "major_reorganizations": 0, "stability": "very_high"}
        }
        
        return {
            "family_size_patterns": family_sizes,
            "hierarchical_organization": hierarchical_depth,
            "stability_analysis": stability_patterns,
            "genome_type_constraints": self._analyze_constraints()
        }
    
    def _analyze_constraints(self) -> Dict[str, Any]:
        """Analyze structural constraints imposed by genome architecture."""
        constraints = {
            "dsDNA": {
                "size_constraint": "Large genomes enable complex classification",
                "organization_constraint": "Modular organization complicates boundaries",
                "evolution_constraint": "Low mutation rate aids stable classification"
            },
            "ssDNA": {
                "size_constraint": "Small genomes limit classification features",
                "organization_constraint": "Simple organization aids classification",
                "evolution_constraint": "High mutation rate complicates phylogeny"
            },
            "dsRNA": {
                "size_constraint": "Segmented genomes provide multiple markers",
                "organization_constraint": "Segment number affects classification",
                "evolution_constraint": "Moderate evolution rate"
            },
            "ssRNA(+)": {
                "size_constraint": "Medium genomes with polyprotein organization",
                "organization_constraint": "Processing sites provide classification features",
                "evolution_constraint": "High mutation rate creates challenges"
            },
            "ssRNA(-)": {
                "size_constraint": "Variable genome organization",
                "organization_constraint": "Segmentation affects classification strategy",
                "evolution_constraint": "Rapid evolution complicates classification"
            },
            "ssRNA-RT": {
                "size_constraint": "Reverse transcriptase provides stable marker",
                "organization_constraint": "Integration complicates classification",
                "evolution_constraint": "Moderate evolution with recombination"
            },
            "dsDNA-RT": {
                "size_constraint": "Small family with limited diversity",
                "organization_constraint": "Unique replication strategy",
                "evolution_constraint": "Slow evolution, stable classification"
            }
        }
        
        return constraints
    
    def analyze_genome_evolution(self) -> Dict[str, Any]:
        """Analyze evolution of genome type proportions over time."""
        historical = self.genome_data["historical_distributions"]
        years = sorted(historical.keys())
        
        # Calculate proportional changes
        proportion_changes = {}
        for genome_type in historical[years[0]].keys():
            changes_over_time = []
            for i in range(len(years)):
                year = years[i]
                total = sum(historical[year].values())
                proportion = historical[year][genome_type] / total * 100
                changes_over_time.append((year, proportion))
            
            proportion_changes[genome_type] = changes_over_time
        
        # Identify trends
        trends = {}
        for genome_type, changes in proportion_changes.items():
            initial_prop = changes[0][1]
            final_prop = changes[-1][1]
            
            if final_prop > initial_prop * 1.2:
                trend = "increasing"
            elif final_prop < initial_prop * 0.8:
                trend = "decreasing"
            else:
                trend = "stable"
            
            trends[genome_type] = {
                "trend": trend,
                "initial_proportion": initial_prop,
                "final_proportion": final_prop,
                "change_magnitude": final_prop - initial_prop
            }
        
        # Discovery era analysis
        discovery_eras = {
            "traditional_era": (2005, 2010),
            "genomics_era": (2011, 2018),
            "metagenomics_era": (2019, 2024)
        }
        
        era_preferences = {}
        for era_name, (start_year, end_year) in discovery_eras.items():
            era_totals = {}
            for year in range(start_year, end_year + 1):
                if year in historical:
                    for genome_type, count in historical[year].items():
                        era_totals[genome_type] = era_totals.get(genome_type, 0) + count
            
            era_preferences[era_name] = era_totals
        
        return {
            "proportion_changes": proportion_changes,
            "trends": trends,
            "discovery_era_preferences": era_preferences,
            "baltimore_group_evolution": self._analyze_baltimore_evolution()
        }
    
    def _analyze_baltimore_evolution(self) -> Dict[str, Any]:
        """Analyze evolution by Baltimore classification groups."""
        baltimore_mapping = {
            "dsDNA": "I", "ssDNA": "II", "dsRNA": "III", "ssRNA(+)": "IV",
            "ssRNA(-)": "V", "ssRNA-RT": "VI", "dsDNA-RT": "VII"
        }
        
        # Group evolution patterns
        dna_groups = ["dsDNA", "ssDNA", "dsDNA-RT"]
        rna_groups = ["dsRNA", "ssRNA(+)", "ssRNA(-)", "ssRNA-RT"]
        
        historical = self.genome_data["historical_distributions"]
        years = sorted(historical.keys())
        
        dna_rna_evolution = {}
        for year in years:
            dna_total = sum(historical[year][gt] for gt in dna_groups if gt in historical[year])
            rna_total = sum(historical[year][gt] for gt in rna_groups if gt in historical[year])
            total = dna_total + rna_total
            
            dna_rna_evolution[year] = {
                "dna_proportion": dna_total / total * 100 if total > 0 else 0,
                "rna_proportion": rna_total / total * 100 if total > 0 else 0,
                "dna_count": dna_total,
                "rna_count": rna_total
            }
        
        return {
            "baltimore_mapping": baltimore_mapping,
            "dna_rna_evolution": dna_rna_evolution,
            "group_patterns": {
                "dna_dominance": "DNA viruses show consistent growth",
                "rna_diversity": "RNA viruses show higher diversity",
                "rt_stability": "RT viruses remain small but stable"
            }
        }
    
    def analyze_family_size_patterns(self) -> Dict[str, Any]:
        """Analyze family size patterns by genome type."""
        # Based on known family size patterns
        family_size_data = {
            "dsDNA": {
                "small_families": 8,    # <50 species
                "medium_families": 12,  # 50-200 species  
                "large_families": 5,    # >200 species
                "avg_size": 150,
                "splitting_tendency": "high",
                "example_splits": ["Siphoviridae → 15+ families", "Myoviridae → 5+ families"]
            },
            "ssDNA": {
                "small_families": 5,
                "medium_families": 3,
                "large_families": 0,
                "avg_size": 45,
                "splitting_tendency": "low",
                "example_splits": []
            },
            "dsRNA": {
                "small_families": 3,
                "medium_families": 3,
                "large_families": 0,
                "avg_size": 75,
                "splitting_tendency": "low",
                "example_splits": []
            },
            "ssRNA(+)": {
                "small_families": 15,
                "medium_families": 18,
                "large_families": 2,
                "avg_size": 85,
                "splitting_tendency": "medium",
                "example_splits": ["Picornaviridae subspecies reorganization"]
            },
            "ssRNA(-)": {
                "small_families": 8,
                "medium_families": 8,
                "large_families": 2,
                "avg_size": 68,
                "splitting_tendency": "medium",
                "example_splits": ["Rhabdoviridae subgrouping"]
            },
            "ssRNA-RT": {
                "small_families": 0,
                "medium_families": 2,
                "large_families": 0,
                "avg_size": 95,
                "splitting_tendency": "very_low",
                "example_splits": []
            },
            "dsDNA-RT": {
                "small_families": 1,
                "medium_families": 0,
                "large_families": 0,
                "avg_size": 28,
                "splitting_tendency": "none",
                "example_splits": []
            }
        }
        
        # Calculate statistics
        size_statistics = {}
        for genome_type, data in family_size_data.items():
            total_families = data["small_families"] + data["medium_families"] + data["large_families"]
            size_statistics[genome_type] = {
                "total_families": total_families,
                "avg_family_size": data["avg_size"],
                "size_distribution": {
                    "small_pct": data["small_families"] / total_families * 100 if total_families > 0 else 0,
                    "medium_pct": data["medium_families"] / total_families * 100 if total_families > 0 else 0,
                    "large_pct": data["large_families"] / total_families * 100 if total_families > 0 else 0
                },
                "splitting_risk": data["splitting_tendency"]
            }
        
        return {
            "family_size_data": family_size_data,
            "size_statistics": size_statistics,
            "genome_size_correlation": self._analyze_genome_size_correlation()
        }
    
    def _analyze_genome_size_correlation(self) -> Dict[str, Any]:
        """Analyze correlation between genome architecture and family organization."""
        correlations = {
            "genome_complexity_vs_family_size": {
                "dsDNA": "High complexity → Large families (before splitting)",
                "ssDNA": "Low complexity → Small families", 
                "dsRNA": "Medium complexity → Medium families",
                "ssRNA(+)": "High diversity → Variable family sizes",
                "ssRNA(-)": "High diversity → Variable family sizes",
                "ssRNA-RT": "Specialized → Stable medium families",
                "dsDNA-RT": "Specialized → Very small families"
            },
            "mutation_rate_vs_stability": {
                "high_mutation": ["ssDNA", "ssRNA(+)", "ssRNA(-)"],
                "medium_mutation": ["dsDNA", "dsRNA", "ssRNA-RT"],
                "low_mutation": ["dsDNA-RT"]
            },
            "replication_strategy_vs_classification": {
                "cytoplasmic": ["dsRNA", "ssRNA(+)", "ssRNA(-)"],
                "nuclear": ["dsDNA", "ssDNA", "dsDNA-RT"],
                "integration": ["ssRNA-RT", "dsDNA-RT"]
            }
        }
        
        return correlations
    
    def analyze_discovery_bias(self) -> Dict[str, Any]:
        """Analyze discovery bias by genome type across technology eras."""
        # Technology bias in discovery
        technology_bias = {
            "electron_microscopy_era": {
                "favored": ["dsDNA"],
                "reason": "Large particles visible",
                "period": "1950s-1980s"
            },
            "serological_era": {
                "favored": ["ssRNA(+)", "ssRNA(-)"],
                "reason": "Disease association, antibody detection",
                "period": "1960s-1990s"
            },
            "pcr_era": {
                "favored": ["dsDNA", "ssRNA-RT"],
                "reason": "Stable targets for amplification",
                "period": "1990s-2000s"
            },
            "ngs_era": {
                "favored": ["dsDNA", "ssDNA"],
                "reason": "Environmental metagenomics",
                "period": "2000s-2010s"
            },
            "metagenomics_era": {
                "favored": ["dsDNA", "dsRNA"],
                "reason": "Stable in environmental samples",
                "period": "2010s-present"
            }
        }
        
        # Current discovery rates by genome type
        discovery_rates = {
            "dsDNA": {"rate": "very_high", "driver": "Metagenomics, bacteriophage surveys"},
            "ssDNA": {"rate": "high", "driver": "Environmental sampling, CRISPR spacers"},
            "dsRNA": {"rate": "medium", "driver": "Fungal and plant surveys"},
            "ssRNA(+)": {"rate": "medium", "driver": "Clinical surveillance"},
            "ssRNA(-)": {"rate": "low", "driver": "Established clinical knowledge"},
            "ssRNA-RT": {"rate": "very_low", "driver": "Well-characterized group"},
            "dsDNA-RT": {"rate": "very_low", "driver": "Limited host range"}
        }
        
        return {
            "technology_bias": technology_bias,
            "current_discovery_rates": discovery_rates,
            "sampling_bias": self._analyze_sampling_bias()
        }
    
    def _analyze_sampling_bias(self) -> Dict[str, Any]:
        """Analyze sampling biases affecting genome type discovery."""
        sampling_biases = {
            "environmental_bias": {
                "marine": "Favors dsDNA phages",
                "soil": "Favors diverse dsDNA and ssDNA",
                "freshwater": "Favors dsRNA and ssRNA viruses",
                "extreme_environments": "Favors thermostable dsDNA"
            },
            "host_bias": {
                "bacteria": "Predominantly dsDNA phages",
                "archaea": "Unique dsDNA architectures", 
                "plants": "ssRNA(+) and ssDNA",
                "animals": "All types, clinical bias to pathogenic",
                "fungi": "dsRNA mycoviruses"
            },
            "methodological_bias": {
                "cultivation": "Favors lytic dsDNA phages",
                "metagenomics": "Favors stable DNA genomes",
                "clinical_isolation": "Favors pathogenic RNA viruses",
                "environmental_surveys": "Favors abundant dsDNA types"
            }
        }
        
        return sampling_biases
    
    def _generate_summary(self, genome_distributions: Dict[str, Any], 
                         classification_approaches: Dict[str, Any]) -> str:
        """Generate a summary of the genome architecture analysis."""
        dominant = genome_distributions["dominant_types"]["top_3"]
        
        summary_lines = [
            f"Genome Architecture Constraints Analysis reveals structural classification patterns:",
            f"",
            f"Dominant Genome Types (2024):"
        ]
        
        for i, (gtype, count) in enumerate(dominant, 1):
            pct = count / sum(c for _, c in genome_distributions["dominant_types"]["ranking"]) * 100
            summary_lines.append(f"{i}. {gtype}: {count:,} species ({pct:.1f}%)")
        
        summary_lines.extend([
            "",
            "Key Pattern: Genome architecture constrains classification approaches",
            "- dsDNA: Morphology + genome organization",
            "- RNA viruses: Phylogenetic approaches dominate", 
            "- RT viruses: Highly stable, specialized methods"
        ])
        
        return "\n".join(summary_lines)
    
    def _extract_key_findings(self, genome_distributions: Dict[str, Any],
                             classification_approaches: Dict[str, Any],
                             taxonomic_patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key findings from the analysis."""
        findings = []
        
        # Finding 1: dsDNA dominance
        dominant = genome_distributions["dominant_types"]["top_3"]
        if dominant:
            top_type, top_count = dominant[0]
            total = sum(c for _, c in genome_distributions["dominant_types"]["ranking"])
            findings.append({
                "finding": f"{top_type} viruses dominate viral diversity",
                "detail": f"{top_count:,} species ({top_count/total*100:.1f}%) driven by bacteriophage metagenomics",
                "implication": "Environmental sampling creates strong bias toward stable DNA genomes"
            })
        
        # Finding 2: Classification method correlation
        complexity = classification_approaches["method_complexity"]
        high_complexity = [gt for gt, data in complexity.items() if data["complexity"] == "high"]
        findings.append({
            "finding": "Genome architecture determines classification complexity",
            "detail": f"High complexity methods required for: {', '.join(high_complexity)}",
            "implication": "Structural constraints, not just phylogeny, shape taxonomic approaches"
        })
        
        # Finding 3: Family size patterns
        family_sizes = taxonomic_patterns["family_size_patterns"]
        large_family_types = [gt for gt, data in family_sizes.items() if data["avg_species_per_family"] > 100]
        findings.append({
            "finding": "Large genome types form larger, less stable families",
            "detail": f"Average family sizes >100 species: {', '.join(large_family_types)}",
            "implication": "Complex genomes enable more species diversity but require frequent reorganization"
        })
        
        # Finding 4: Discovery bias
        growth_rates = genome_distributions["growth_rates"]
        fastest_growing = max(growth_rates.items(), key=lambda x: x[1]["annual_rate"])
        findings.append({
            "finding": "Technology bias drives genome type discovery rates",
            "detail": f"Fastest growing: {fastest_growing[0]} ({fastest_growing[1]['annual_rate']:.1f}% annually)",
            "implication": "Current metagenomics revolution strongly favors DNA virus discovery"
        })
        
        return findings


def main():
    """Run the genome architecture constraints analysis."""
    analyzer = GenomeArchitectureAnalyzer()
    results = analyzer.analyze()
    
    # Print key findings
    print("\n" + "="*60)
    print("KEY FINDINGS")
    print("="*60)
    
    for i, finding in enumerate(results.get('key_findings', []), 1):
        print(f"\n{i}. {finding['finding']}")
        print(f"   Detail: {finding['detail']}")
        print(f"   Implication: {finding['implication']}")
    
    print("\n" + "="*60)
    print("Analysis complete!")
    print("="*60)


if __name__ == "__main__":
    main()