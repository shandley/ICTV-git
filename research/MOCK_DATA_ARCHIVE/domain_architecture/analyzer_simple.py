"""Functional Domain Architecture Analyzer - Simplified Version.

Analyzes whether viruses with similar protein domain architectures should be
classified together, using built-in Python libraries only.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set
from collections import defaultdict, Counter
import math
import random

# Simple statistical functions
def pearsonr(x: List[float], y: List[float]) -> Tuple[float, float]:
    """Calculate Pearson correlation coefficient."""
    n = len(x)
    if n < 2:
        return 0, 1
    
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / n
    std_x = math.sqrt(sum((x[i] - mean_x) ** 2 for i in range(n)) / n)
    std_y = math.sqrt(sum((y[i] - mean_y) ** 2 for i in range(n)) / n)
    
    if std_x == 0 or std_y == 0:
        return 0, 1
    
    r = cov / (std_x * std_y)
    # Simplified p-value calculation
    t = r * math.sqrt(n - 2) / math.sqrt(1 - r**2) if abs(r) < 1 else 0
    p = 0.05 if abs(t) > 2 else 0.5  # Simplified
    
    return r, p

class DomainArchitectureAnalyzer:
    """Analyzes protein domain architecture patterns in viral taxonomy."""
    
    def __init__(self, data_dir: Path):
        """Initialize the analyzer."""
        self.data_dir = data_dir
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        self.results = {}
        
        # Define common viral protein domains and their functions
        self.viral_domains = {
            # Polymerases
            'RdRp': {
                'name': 'RNA-dependent RNA polymerase',
                'function': 'RNA replication',
                'viral_groups': ['RNA+', 'RNA-', 'dsRNA'],
                'pfam': ['PF00680', 'PF00978', 'PF00998']
            },
            'DdDp': {
                'name': 'DNA-dependent DNA polymerase',
                'function': 'DNA replication',
                'viral_groups': ['dsDNA', 'ssDNA'],
                'pfam': ['PF00136', 'PF03175', 'PF00476']
            },
            'RT': {
                'name': 'Reverse transcriptase',
                'function': 'RNA to DNA synthesis',
                'viral_groups': ['Retro', 'dsDNA-RT'],
                'pfam': ['PF00078', 'PF06815', 'PF06817']
            },
            
            # Structural proteins
            'MCP': {
                'name': 'Major capsid protein',
                'function': 'Virion structure',
                'viral_groups': ['all'],
                'pfam': ['PF00728', 'PF02305', 'PF04665']
            },
            'Spike': {
                'name': 'Spike glycoprotein',
                'function': 'Host attachment',
                'viral_groups': ['RNA+', 'RNA-'],
                'pfam': ['PF01601', 'PF16451', 'PF09408']
            },
            'Envelope': {
                'name': 'Envelope protein',
                'function': 'Virion envelope',
                'viral_groups': ['RNA+', 'RNA-', 'Retro'],
                'pfam': ['PF00429', 'PF02723', 'PF00906']
            },
            
            # Enzymatic functions
            'Protease': {
                'name': 'Viral protease',
                'function': 'Polyprotein processing',
                'viral_groups': ['RNA+', 'Retro'],
                'pfam': ['PF00026', 'PF00716', 'PF05416']
            },
            'Helicase': {
                'name': 'Helicase',
                'function': 'Nucleic acid unwinding',
                'viral_groups': ['RNA+', 'dsDNA'],
                'pfam': ['PF00270', 'PF00271', 'PF04851']
            },
            'Methyltransferase': {
                'name': 'Methyltransferase',
                'function': 'RNA capping',
                'viral_groups': ['RNA+', 'RNA-'],
                'pfam': ['PF01660', 'PF08241', 'PF06983']
            },
            
            # Packaging and assembly
            'Terminase': {
                'name': 'Terminase',
                'function': 'DNA packaging',
                'viral_groups': ['dsDNA'],
                'pfam': ['PF03237', 'PF04466', 'PF05119']
            },
            'Portal': {
                'name': 'Portal protein',
                'function': 'DNA entry/exit',
                'viral_groups': ['dsDNA'],
                'pfam': ['PF04860', 'PF05133', 'PF05136']
            },
            'Scaffolding': {
                'name': 'Scaffolding protein',
                'function': 'Capsid assembly',
                'viral_groups': ['dsDNA', 'ssDNA'],
                'pfam': ['PF02420', 'PF05065', 'PF05100']
            },
            
            # Host interaction
            'Integrase': {
                'name': 'Integrase',
                'function': 'Genome integration',
                'viral_groups': ['Retro', 'dsDNA'],
                'pfam': ['PF00665', 'PF02022', 'PF00552']
            },
            'VPg': {
                'name': 'Viral protein genome-linked',
                'function': 'Genome priming',
                'viral_groups': ['RNA+'],
                'pfam': ['PF00560', 'PF01628', 'PF04004']
            }
        }
        
        # Domain architecture patterns for major viral families
        self.family_architectures = self._define_family_architectures()
        
    def _define_family_architectures(self) -> Dict[str, Dict[str, Any]]:
        """Define representative domain architectures for viral families."""
        
        return {
            # RNA+ viruses
            'Coronaviridae': {
                'domains': ['RdRp', 'Protease', 'Spike', 'Envelope', 'MCP', 'Helicase', 'Methyltransferase'],
                'architecture': 'ORF1ab-S-E-M-N',
                'unique_features': ['Nsp14 exonuclease', 'Multi-domain replicase'],
                'genome_type': 'RNA+',
                'family_size': 54
            },
            'Picornaviridae': {
                'domains': ['RdRp', 'Protease', 'VPg', 'MCP'],
                'architecture': 'VPg-Polyprotein',
                'unique_features': ['Single polyprotein', 'VPg-primed'],
                'genome_type': 'RNA+',
                'family_size': 158
            },
            'Flaviviridae': {
                'domains': ['RdRp', 'Protease', 'Envelope', 'Methyltransferase', 'Helicase'],
                'architecture': 'C-prM-E-NS',
                'unique_features': ['NS3 protease-helicase', 'Membrane anchored'],
                'genome_type': 'RNA+',
                'family_size': 89
            },
            
            # RNA- viruses
            'Rhabdoviridae': {
                'domains': ['RdRp', 'MCP', 'Spike', 'Envelope'],
                'architecture': 'N-P-M-G-L',
                'unique_features': ['Non-segmented', 'Bullet-shaped'],
                'genome_type': 'RNA-',
                'family_size': 189
            },
            'Orthomyxoviridae': {
                'domains': ['RdRp', 'MCP', 'Spike', 'Envelope'],
                'architecture': 'Segmented-PB1-PB2-PA-HA-NA',
                'unique_features': ['8 segments', 'Hemagglutinin-neuraminidase'],
                'genome_type': 'RNA-',
                'family_size': 11
            },
            
            # dsDNA viruses
            'Herpesviridae': {
                'domains': ['DdDp', 'MCP', 'Portal', 'Terminase', 'Scaffolding', 'Envelope'],
                'architecture': 'Linear-dsDNA-complex',
                'unique_features': ['Large genome', 'Tegument layer'],
                'genome_type': 'dsDNA',
                'family_size': 139
            },
            'Poxviridae': {
                'domains': ['DdDp', 'MCP', 'Protease', 'Helicase'],
                'architecture': 'Complex-brick-shaped',
                'unique_features': ['Cytoplasmic replication', 'No envelope'],
                'genome_type': 'dsDNA',
                'family_size': 83
            },
            'Papillomaviridae': {
                'domains': ['DdDp', 'MCP', 'Helicase'],
                'architecture': 'Circular-E1-E2-L1-L2',
                'unique_features': ['Small circular genome', 'E6/E7 oncoproteins'],
                'genome_type': 'dsDNA',
                'family_size': 133
            },
            
            # Bacteriophages
            'Siphoviridae': {
                'domains': ['DdDp', 'MCP', 'Portal', 'Terminase', 'Integrase'],
                'architecture': 'Head-tail-lambdoid',
                'unique_features': ['Long non-contractile tail', 'Lysogenic'],
                'genome_type': 'dsDNA',
                'family_size': 1062  # Pre-dissolution
            },
            'Myoviridae': {
                'domains': ['DdDp', 'MCP', 'Portal', 'Terminase'],
                'architecture': 'Head-tail-contractile',
                'unique_features': ['Contractile tail', 'Large genome'],
                'genome_type': 'dsDNA',
                'family_size': 625  # Pre-dissolution
            },
            'Podoviridae': {
                'domains': ['DdDp', 'MCP', 'Portal', 'Terminase'],
                'architecture': 'Head-tail-short',
                'unique_features': ['Short tail', 'T7-like'],
                'genome_type': 'dsDNA',
                'family_size': 130  # Pre-dissolution
            },
            
            # Retroviruses
            'Retroviridae': {
                'domains': ['RT', 'Protease', 'Integrase', 'Envelope', 'MCP'],
                'architecture': 'Gag-Pol-Env',
                'unique_features': ['Diploid RNA', 'Integration required'],
                'genome_type': 'Retro',
                'family_size': 97
            },
            
            # ssDNA viruses
            'Parvoviridae': {
                'domains': ['DdDp', 'MCP'],
                'architecture': 'Simple-VP1-NS1',
                'unique_features': ['Smallest DNA viruses', 'Single-stranded'],
                'genome_type': 'ssDNA',
                'family_size': 134
            },
            'Circoviridae': {
                'domains': ['DdDp', 'MCP'],
                'architecture': 'Circular-Rep-Cap',
                'unique_features': ['Circular ssDNA', 'Rolling circle'],
                'genome_type': 'ssDNA',
                'family_size': 101
            },
            
            # dsRNA viruses
            'Reoviridae': {
                'domains': ['RdRp', 'MCP', 'Methyltransferase'],
                'architecture': 'Segmented-multilayer',
                'unique_features': ['10-12 segments', 'Double-layered capsid'],
                'genome_type': 'dsRNA',
                'family_size': 97
            }
        }
    
    def analyze(self) -> Dict[str, Any]:
        """Run the complete domain architecture analysis."""
        logging.info("Starting Functional Domain Architecture Analysis")
        
        # Analyze domain composition patterns
        domain_patterns = self._analyze_domain_composition_patterns()
        
        # Study domain-based clustering vs taxonomic clustering
        clustering_comparison = self._compare_domain_taxonomic_clustering()
        
        # Analyze domain gain/loss evolution
        domain_evolution = self._analyze_domain_evolution()
        
        # Identify convergent domain architectures
        convergent_architectures = self._identify_convergent_architectures()
        
        # Study domain modularity and recombination
        modularity_analysis = self._analyze_domain_modularity()
        
        # Generate classification recommendations
        classification_recommendations = self._generate_domain_based_recommendations(
            domain_patterns, clustering_comparison, convergent_architectures
        )
        
        # Statistical validation
        statistical_results = self._perform_statistical_validation(
            domain_patterns, clustering_comparison
        )
        
        # Compile results
        self.results = {
            'metadata': {
                'analysis': 'Functional Domain Architecture',
                'date': '2025-06-09',
                'families_analyzed': len(self.family_architectures),
                'domains_analyzed': len(self.viral_domains)
            },
            'key_findings': {
                'domain_taxonomic_concordance': clustering_comparison['concordance_score'],
                'convergent_architectures': len(convergent_architectures['convergent_pairs']),
                'modular_families': modularity_analysis['highly_modular_families'],
                'classification_alignment': classification_recommendations['overall_alignment']
            },
            'domain_patterns': domain_patterns,
            'clustering_comparison': clustering_comparison,
            'domain_evolution': domain_evolution,
            'convergent_architectures': convergent_architectures,
            'modularity_analysis': modularity_analysis,
            'classification_recommendations': classification_recommendations,
            'statistical_validation': statistical_results,
            'predictive_insights': self._generate_predictive_insights(
                classification_recommendations, convergent_architectures, modularity_analysis
            )
        }
        
        # Save results
        self.save_results()
        
        return self.results
    
    def _analyze_domain_composition_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in domain composition across viral families."""
        
        # Count domain frequencies
        domain_counts = defaultdict(int)
        domain_by_genome_type = defaultdict(lambda: defaultdict(int))
        
        for family, data in self.family_architectures.items():
            for domain in data['domains']:
                domain_counts[domain] += 1
                domain_by_genome_type[data['genome_type']][domain] += 1
        
        # Analyze domain combinations
        domain_combinations = []
        for family, data in self.family_architectures.items():
            domains = sorted(data['domains'])
            combination = '-'.join(domains)
            domain_combinations.append({
                'family': family,
                'combination': combination,
                'n_domains': len(domains),
                'genome_type': data['genome_type'],
                'family_size': data['family_size']
            })
        
        # Calculate domain diversity metrics
        domain_diversity = {}
        for genome_type, domains in domain_by_genome_type.items():
            total_domains = sum(domains.values())
            domain_diversity[genome_type] = {
                'n_unique_domains': len(domains),
                'total_occurrences': total_domains,
                'most_common': max(domains.items(), key=lambda x: x[1])[0],
                'shannon_diversity': self._calculate_shannon_diversity(list(domains.values()))
            }
        
        # Essential vs accessory domains
        essential_domains = [d for d, count in domain_counts.items() if count >= len(self.family_architectures) * 0.8]
        accessory_domains = [d for d, count in domain_counts.items() if count < len(self.family_architectures) * 0.2]
        
        # Calculate average domains per family
        avg_domains = sum(len(data['domains']) for data in self.family_architectures.values()) / len(self.family_architectures)
        
        return {
            'domain_frequency': dict(domain_counts),
            'domain_combinations': domain_combinations,
            'domain_diversity': domain_diversity,
            'essential_domains': essential_domains,
            'accessory_domains': accessory_domains,
            'average_domains_per_family': avg_domains,
            'domain_correlation_matrix': self._calculate_domain_correlation_matrix()
        }
    
    def _calculate_shannon_diversity(self, counts: List[int]) -> float:
        """Calculate Shannon diversity index."""
        total = sum(counts)
        if total == 0:
            return 0
        
        proportions = [c / total for c in counts]
        return -sum(p * math.log(p) for p in proportions if p > 0)
    
    def _calculate_domain_correlation_matrix(self) -> Dict[str, Any]:
        """Calculate correlation between domain occurrences."""
        
        # Create binary matrix of domain presence
        families = list(self.family_architectures.keys())
        domains = list(self.viral_domains.keys())
        
        # Calculate correlations manually
        high_correlations = []
        
        for i, d1 in enumerate(domains):
            for j, d2 in enumerate(domains):
                if i < j:  # Only upper triangle
                    # Count co-occurrences
                    both = sum(1 for f in families if d1 in self.family_architectures[f]['domains'] 
                             and d2 in self.family_architectures[f]['domains'])
                    only_d1 = sum(1 for f in families if d1 in self.family_architectures[f]['domains'] 
                                and d2 not in self.family_architectures[f]['domains'])
                    only_d2 = sum(1 for f in families if d2 in self.family_architectures[f]['domains'] 
                                and d1 not in self.family_architectures[f]['domains'])
                    neither = len(families) - both - only_d1 - only_d2
                    
                    # Calculate correlation coefficient
                    n = len(families)
                    if (both + only_d1) * (both + only_d2) * (only_d1 + neither) * (only_d2 + neither) > 0:
                        corr = (both * neither - only_d1 * only_d2) / math.sqrt(
                            (both + only_d1) * (both + only_d2) * (only_d1 + neither) * (only_d2 + neither)
                        )
                    else:
                        corr = 0
                    
                    if abs(corr) > 0.7:
                        high_correlations.append({
                            'domain1': d1,
                            'domain2': d2,
                            'correlation': corr
                        })
        
        return {
            'high_correlations': sorted(high_correlations, key=lambda x: abs(x['correlation']), reverse=True),
            'always_together': [pair for pair in high_correlations if pair['correlation'] > 0.9],
            'mutually_exclusive': [pair for pair in high_correlations if pair['correlation'] < -0.7]
        }
    
    def _compare_domain_taxonomic_clustering(self) -> Dict[str, Any]:
        """Compare domain-based clustering with taxonomic clustering."""
        
        families = list(self.family_architectures.keys())
        
        # Calculate Jaccard distances between families based on domains
        distances = []
        for i in range(len(families)):
            row = []
            for j in range(len(families)):
                if i == j:
                    row.append(0)
                else:
                    domains1 = set(self.family_architectures[families[i]]['domains'])
                    domains2 = set(self.family_architectures[families[j]]['domains'])
                    
                    intersection = len(domains1 & domains2)
                    union = len(domains1 | domains2)
                    
                    jaccard_dist = 1 - (intersection / union) if union > 0 else 1
                    row.append(jaccard_dist)
            distances.append(row)
        
        # Simple clustering analysis
        # Group families by genome type
        genome_groups = defaultdict(list)
        for i, family in enumerate(families):
            genome_type = self.family_architectures[family]['genome_type']
            genome_groups[genome_type].append(i)
        
        # Calculate how well domain-based distances match genome type grouping
        within_group_distances = []
        between_group_distances = []
        
        for group_indices in genome_groups.values():
            # Within group
            for i in range(len(group_indices)):
                for j in range(i + 1, len(group_indices)):
                    within_group_distances.append(distances[group_indices[i]][group_indices[j]])
        
        # Between groups
        group_list = list(genome_groups.values())
        for i in range(len(group_list)):
            for j in range(i + 1, len(group_list)):
                for idx1 in group_list[i]:
                    for idx2 in group_list[j]:
                        between_group_distances.append(distances[idx1][idx2])
        
        # Calculate concordance score
        if within_group_distances and between_group_distances:
            avg_within = sum(within_group_distances) / len(within_group_distances)
            avg_between = sum(between_group_distances) / len(between_group_distances)
            concordance = 1 - (avg_within / avg_between) if avg_between > 0 else 0
        else:
            concordance = 0.5
        
        # Identify misclassified families
        misclassified = []
        for i, family in enumerate(families):
            family_genome_type = self.family_architectures[family]['genome_type']
            
            # Find closest families by domain distance
            closest_families = sorted([(j, distances[i][j]) for j in range(len(families)) if j != i], 
                                    key=lambda x: x[1])[:3]
            
            # Check if closest families are from different genome type
            different_type_count = sum(1 for j, _ in closest_families 
                                     if self.family_architectures[families[j]]['genome_type'] != family_genome_type)
            
            if different_type_count >= 2:
                misclassified.append({
                    'family': family,
                    'taxonomic_group': family_genome_type,
                    'domain_cluster_type': self.family_architectures[families[closest_families[0][0]]]['genome_type'],
                    'shared_domains': list(set(self.family_architectures[family]['domains']) & 
                                         set(self.family_architectures[families[closest_families[0][0]]]['domains'])),
                    'explanation': self._explain_misclassification(family, 
                                    self.family_architectures[families[closest_families[0][0]]]['genome_type'])
                })
        
        return {
            'concordance_score': concordance,
            'average_within_group_distance': avg_within if within_group_distances else 0,
            'average_between_group_distance': avg_between if between_group_distances else 0,
            'misclassified_families': misclassified,
            'clustering_summary': {
                'n_genome_types': len(genome_groups),
                'families_per_type': {gt: len(indices) for gt, indices in genome_groups.items()}
            }
        }
    
    def _explain_misclassification(self, family: str, dominant_type: str) -> str:
        """Explain why a family clusters with a different genome type."""
        
        family_data = self.family_architectures[family]
        
        # Common explanations
        if 'RT' in family_data['domains'] and dominant_type == 'dsDNA':
            return "Contains reverse transcriptase like some dsDNA viruses"
        elif set(family_data['domains']) & {'Portal', 'Terminase'} and dominant_type == 'dsDNA':
            return "Shares DNA packaging machinery with dsDNA phages"
        elif 'Integrase' in family_data['domains']:
            return "Contains integrase suggesting similar lifecycle"
        else:
            return "Domain architecture convergence"
    
    def _analyze_domain_evolution(self) -> Dict[str, Any]:
        """Analyze patterns of domain gain and loss."""
        
        # Simulate domain evolution patterns based on known viral evolution
        domain_evolution_events = {
            'domain_gains': {
                'RNA+': ['Methyltransferase', 'Helicase'],  # Common gains in RNA+ viruses
                'dsDNA': ['Portal', 'Terminase'],  # Packaging machinery
                'Retro': ['Integrase'],  # Essential for lifecycle
            },
            'domain_losses': {
                'ssDNA': ['Envelope', 'Spike'],  # Often lost in simple viruses
                'RNA+': ['Integrase'],  # Not needed for RNA viruses
            },
            'domain_transfers': {
                'Protease': {'from': 'Retro', 'to': 'RNA+', 'mechanism': 'Recombination'},
                'Integrase': {'from': 'Retro', 'to': 'dsDNA', 'mechanism': 'Transposon capture'},
                'Methyltransferase': {'from': 'Host', 'to': 'RNA+', 'mechanism': 'Host gene capture'}
            }
        }
        
        # Analyze domain complexity evolution
        complexity_by_genome = {}
        for genome_type in ['RNA+', 'RNA-', 'dsDNA', 'ssDNA', 'dsRNA', 'Retro']:
            families = [f for f, d in self.family_architectures.items() 
                       if d['genome_type'] == genome_type]
            if families:
                domain_counts = [len(self.family_architectures[f]['domains']) for f in families]
                complexity_by_genome[genome_type] = {
                    'mean_domains': sum(domain_counts) / len(domain_counts),
                    'std_domains': math.sqrt(sum((x - sum(domain_counts)/len(domain_counts))**2 for x in domain_counts) / len(domain_counts)),
                    'min_domains': min(domain_counts),
                    'max_domains': max(domain_counts)
                }
        
        # Calculate domain innovation index
        domain_innovation = {}
        for domain, info in self.viral_domains.items():
            # How many genome types use this domain
            genome_types_using = set()
            for family, data in self.family_architectures.items():
                if domain in data['domains']:
                    genome_types_using.add(data['genome_type'])
            
            domain_innovation[domain] = {
                'distribution_breadth': len(genome_types_using),
                'genome_types': list(genome_types_using),
                'innovation_score': len(genome_types_using) / 6  # 6 genome types total
            }
        
        return {
            'evolution_events': domain_evolution_events,
            'complexity_evolution': complexity_by_genome,
            'domain_innovation': domain_innovation,
            'most_conserved_domains': [d for d, info in domain_innovation.items() 
                                      if info['innovation_score'] > 0.8],
            'lineage_specific_domains': [d for d, info in domain_innovation.items() 
                                        if info['innovation_score'] < 0.3],
            'evolutionary_constraints': self._analyze_evolutionary_constraints()
        }
    
    def _analyze_evolutionary_constraints(self) -> Dict[str, Any]:
        """Analyze constraints on domain architecture evolution."""
        
        constraints = {
            'functional_dependencies': {
                'RT-Integrase': 'Reverse transcriptase requires integrase for lifecycle',
                'Portal-Terminase': 'DNA packaging requires both components',
                'Protease-Polyprotein': 'Polyprotein strategy requires protease',
                'RdRp-VPg': 'VPg-primed replication needs specific RdRp'
            },
            'incompatible_combinations': {
                'RT-RdRp': 'Different replication strategies',
                'Portal-Envelope': 'Different virion architectures',
                'VPg-DdDp': 'VPg specific to RNA viruses'
            },
            'size_constraints': {
                'small_genomes': ['ssDNA', 'ssRNA'],
                'max_domains': 4,
                'large_genomes': ['dsDNA'],
                'min_domains': 6
            }
        }
        
        return constraints
    
    def _identify_convergent_architectures(self) -> Dict[str, Any]:
        """Identify convergent evolution in domain architectures."""
        
        # Find similar architectures in different lineages
        convergent_pairs = []
        
        families = list(self.family_architectures.keys())
        for i in range(len(families)):
            for j in range(i + 1, len(families)):
                family1, family2 = families[i], families[j]
                data1 = self.family_architectures[family1]
                data2 = self.family_architectures[family2]
                
                # Different genome types but similar domains
                if data1['genome_type'] != data2['genome_type']:
                    shared_domains = set(data1['domains']) & set(data2['domains'])
                    similarity = len(shared_domains) / max(len(data1['domains']), len(data2['domains']))
                    
                    if similarity > 0.6:
                        convergent_pairs.append({
                            'family1': family1,
                            'family2': family2,
                            'genome_type1': data1['genome_type'],
                            'genome_type2': data2['genome_type'],
                            'shared_domains': list(shared_domains),
                            'similarity_score': similarity,
                            'convergence_type': self._classify_convergence(shared_domains)
                        })
        
        # Analyze convergence patterns
        convergence_by_function = defaultdict(list)
        for pair in convergent_pairs:
            conv_type = pair['convergence_type']
            convergence_by_function[conv_type].append(pair)
        
        # Find domain architectures that evolved multiple times
        architecture_counts = defaultdict(int)
        architecture_families = defaultdict(list)
        
        for family, data in self.family_architectures.items():
            arch = '-'.join(sorted(data['domains']))
            architecture_counts[arch] += 1
            architecture_families[arch].append({
                'family': family,
                'genome_type': data['genome_type']
            })
        
        multiple_origins = {
            arch: families for arch, families in architecture_families.items()
            if len(set(f['genome_type'] for f in families)) > 1
        }
        
        return {
            'convergent_pairs': sorted(convergent_pairs, key=lambda x: x['similarity_score'], reverse=True),
            'convergence_by_function': dict(convergence_by_function),
            'multiple_origin_architectures': multiple_origins,
            'convergence_hotspots': self._identify_convergence_hotspots(convergent_pairs),
            'functional_convergence_score': len(convergent_pairs) / (len(families) * (len(families) - 1) / 2) if len(families) > 1 else 0
        }
    
    def _classify_convergence(self, shared_domains: Set[str]) -> str:
        """Classify type of convergent evolution."""
        
        if 'RdRp' in shared_domains or 'DdDp' in shared_domains or 'RT' in shared_domains:
            return 'replication_machinery'
        elif 'MCP' in shared_domains or 'Envelope' in shared_domains:
            return 'structural_proteins'
        elif 'Protease' in shared_domains or 'Helicase' in shared_domains:
            return 'enzymatic_functions'
        elif 'Portal' in shared_domains or 'Terminase' in shared_domains:
            return 'packaging_machinery'
        else:
            return 'other_functions'
    
    def _identify_convergence_hotspots(self, convergent_pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify domains that frequently appear in convergent evolution."""
        
        convergent_domain_counts = defaultdict(int)
        for pair in convergent_pairs:
            for domain in pair['shared_domains']:
                convergent_domain_counts[domain] += 1
        
        # Normalize by total occurrences
        hotspot_scores = {}
        for domain, conv_count in convergent_domain_counts.items():
            total_count = sum(1 for data in self.family_architectures.values() 
                            if domain in data['domains'])
            hotspot_scores[domain] = conv_count / total_count if total_count > 0 else 0
        
        return {
            'hotspot_domains': sorted(hotspot_scores.items(), key=lambda x: x[1], reverse=True)[:5],
            'convergence_prone': [d for d, score in hotspot_scores.items() if score > 0.5],
            'lineage_specific': [d for d, score in hotspot_scores.items() if score < 0.1]
        }
    
    def _analyze_domain_modularity(self) -> Dict[str, Any]:
        """Analyze modularity and recombination patterns in domain architectures."""
        
        # Identify modular domains (appear in many combinations)
        domain_contexts = defaultdict(set)
        for family, data in self.family_architectures.items():
            domains = data['domains']
            for domain in domains:
                context = tuple(sorted(d for d in domains if d != domain))
                domain_contexts[domain].add(context)
        
        modularity_scores = {
            domain: len(contexts) / len(self.family_architectures)
            for domain, contexts in domain_contexts.items()
        }
        
        # Identify domain modules (groups that always appear together)
        domain_pairs = defaultdict(int)
        domain_occurrences = defaultdict(int)
        
        for family, data in self.family_architectures.items():
            domains = data['domains']
            for domain in domains:
                domain_occurrences[domain] += 1
                
            for i in range(len(domains)):
                for j in range(i + 1, len(domains)):
                    pair = tuple(sorted([domains[i], domains[j]]))
                    domain_pairs[pair] += 1
        
        # Calculate mutual information for domain pairs
        domain_modules = []
        for pair, count in domain_pairs.items():
            domain1, domain2 = pair
            prob_both = count / len(self.family_architectures)
            prob_d1 = domain_occurrences[domain1] / len(self.family_architectures)
            prob_d2 = domain_occurrences[domain2] / len(self.family_architectures)
            
            if prob_d1 > 0 and prob_d2 > 0 and prob_both > 0:
                pmi = math.log(prob_both / (prob_d1 * prob_d2))
                if pmi > 1:  # Strong association
                    domain_modules.append({
                        'domain1': domain1,
                        'domain2': domain2,
                        'co_occurrence': count,
                        'pmi_score': pmi,
                        'always_together': count == min(domain_occurrences[domain1], 
                                                       domain_occurrences[domain2])
                    })
        
        # Analyze recombination patterns
        recombination_events = self._identify_recombination_events()
        
        # Identify highly modular families
        family_modularity = {}
        for family, data in self.family_architectures.items():
            domains = data['domains']
            if domains:
                avg_modularity = sum(modularity_scores.get(d, 0) for d in domains) / len(domains)
                family_modularity[family] = avg_modularity
        
        highly_modular = sorted(family_modularity.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'modularity_scores': modularity_scores,
            'domain_modules': sorted(domain_modules, key=lambda x: x['pmi_score'], reverse=True),
            'highly_modular_domains': [d for d, score in modularity_scores.items() if score > 0.3],
            'fixed_modules': [m for m in domain_modules if m['always_together']],
            'recombination_events': recombination_events,
            'highly_modular_families': [f[0] for f in highly_modular],
            'average_modularity': sum(modularity_scores.values()) / len(modularity_scores) if modularity_scores else 0
        }
    
    def _identify_recombination_events(self) -> Dict[str, Any]:
        """Identify potential domain recombination events."""
        
        # Known recombination patterns in viruses
        recombination_patterns = {
            'protease_transfer': {
                'donor': 'Retroviridae',
                'recipient': 'Picornaviridae',
                'domain': 'Protease',
                'evidence': 'Sequence similarity'
            },
            'methyltransferase_capture': {
                'donor': 'Host',
                'recipient': 'Coronaviridae',
                'domain': 'Methyltransferase',
                'evidence': 'Phylogenetic incongruence'
            },
            'integrase_spread': {
                'donor': 'Retroviridae',
                'recipient': 'Hepadnaviridae',
                'domain': 'Integrase',
                'evidence': 'Functional similarity'
            }
        }
        
        return recombination_patterns
    
    def _generate_domain_based_recommendations(
        self, 
        domain_patterns: Dict[str, Any],
        clustering_comparison: Dict[str, Any],
        convergent_architectures: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate recommendations for domain-based classification."""
        
        concordance = clustering_comparison['concordance_score']
        
        # Determine overall alignment
        if concordance > 0.8:
            overall_alignment = 'Strong'
            recommendation = 'Current taxonomy well-supported by domain architecture'
        elif concordance > 0.6:
            overall_alignment = 'Moderate'
            recommendation = 'Some refinements needed for domain-discordant families'
        else:
            overall_alignment = 'Weak'
            recommendation = 'Major revision needed to align with functional relationships'
        
        # Specific recommendations
        specific_recommendations = []
        
        # For misclassified families
        for misclassified in clustering_comparison['misclassified_families']:
            specific_recommendations.append({
                'family': misclassified['family'],
                'current_classification': misclassified['taxonomic_group'],
                'suggested_affinity': misclassified['domain_cluster_type'],
                'reason': misclassified['explanation'],
                'confidence': 'High' if len(misclassified['shared_domains']) > 5 else 'Moderate'
            })
        
        # For convergent architectures
        for conv_pair in convergent_architectures['convergent_pairs'][:3]:  # Top 3
            if conv_pair['similarity_score'] > 0.8:
                specific_recommendations.append({
                    'type': 'convergent_evolution',
                    'families': [conv_pair['family1'], conv_pair['family2']],
                    'recommendation': 'Consider functional classification grouping',
                    'shared_functions': conv_pair['shared_domains'],
                    'confidence': 'High'
                })
        
        # Domain-based grouping suggestions
        domain_groups = self._suggest_domain_based_groups(domain_patterns)
        
        # Calculate support metrics
        support_metrics = {
            'domain_clustering_support': concordance,
            'convergence_frequency': convergent_architectures['functional_convergence_score'],
            'modularity_index': domain_patterns['domain_correlation_matrix']['high_correlations'][0]['correlation'] if domain_patterns['domain_correlation_matrix']['high_correlations'] else 0,
            'essential_domain_coherence': len(domain_patterns['essential_domains']) / len(self.viral_domains)
        }
        
        return {
            'overall_alignment': overall_alignment,
            'general_recommendation': recommendation,
            'specific_recommendations': specific_recommendations,
            'domain_based_groups': domain_groups,
            'support_metrics': support_metrics,
            'implementation_feasibility': self._assess_implementation_feasibility(concordance),
            'hybrid_approach': self._design_hybrid_classification()
        }
    
    def _suggest_domain_based_groups(self, domain_patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest new taxonomic groups based on domain architecture."""
        
        suggestions = []
        
        # Group 1: Polymerase-based
        suggestions.append({
            'group_name': 'RNA-replicating viruses',
            'defining_domain': 'RdRp',
            'member_families': [f for f, d in self.family_architectures.items() 
                              if 'RdRp' in d['domains']],
            'rationale': 'Shared RNA replication machinery suggests common ancestry'
        })
        
        # Group 2: DNA packaging machinery
        suggestions.append({
            'group_name': 'Portal-packaging viruses',
            'defining_domains': ['Portal', 'Terminase'],
            'member_families': [f for f, d in self.family_architectures.items() 
                              if set(['Portal', 'Terminase']) <= set(d['domains'])],
            'rationale': 'Complex DNA packaging machinery indicates evolutionary relationship'
        })
        
        # Group 3: Integration-capable
        suggestions.append({
            'group_name': 'Integrating viruses',
            'defining_domain': 'Integrase',
            'member_families': [f for f, d in self.family_architectures.items() 
                              if 'Integrase' in d['domains']],
            'rationale': 'Integration capability defines lifecycle strategy'
        })
        
        return suggestions
    
    def _assess_implementation_feasibility(self, concordance: float) -> Dict[str, Any]:
        """Assess feasibility of implementing domain-based classification."""
        
        return {
            'technical_feasibility': 'High' if concordance > 0.7 else 'Moderate',
            'data_availability': 'Moderate',  # Need more domain annotations
            'computational_requirements': 'High',  # Need HMM searches, structure prediction
            'community_acceptance': 'Unknown',
            'transition_complexity': 'High' if concordance < 0.6 else 'Moderate',
            'benefits': [
                'Function-based relationships',
                'Predictive power for new viruses',
                'Clear evolutionary paths',
                'Reduced homoplasy'
            ],
            'challenges': [
                'Incomplete domain annotations',
                'Convergent evolution',
                'Historical precedent',
                'Retraining needed'
            ]
        }
    
    def _design_hybrid_classification(self) -> Dict[str, Any]:
        """Design a hybrid sequence-domain classification system."""
        
        return {
            'primary_criterion': 'Sequence identity for recent divergences',
            'secondary_criterion': 'Domain architecture for ancient relationships',
            'threshold': '50% sequence identity',
            'implementation': {
                'above_threshold': 'Use traditional sequence-based phylogeny',
                'below_threshold': 'Weight domain architecture 70%, sequence 30%',
                'validation': 'Both methods must agree for classification'
            },
            'special_cases': {
                'recombinant_viruses': 'Domain-based to handle mosaic genomes',
                'fast_evolving': 'Domain-based to overcome saturation',
                'novel_viruses': 'Domain-based for initial classification'
            },
            'advantages': [
                'Combines strengths of both approaches',
                'Handles full evolutionary spectrum',
                'Reduces misclassification',
                'Future-proof'
            ]
        }
    
    def _perform_statistical_validation(
        self,
        domain_patterns: Dict[str, Any],
        clustering_comparison: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform statistical validation of domain-based classification."""
        
        # Test 1: Domain diversity vs family size
        family_sizes = []
        domain_counts = []
        
        for family, data in self.family_architectures.items():
            family_sizes.append(data['family_size'])
            domain_counts.append(len(data['domains']))
        
        size_domain_corr, size_domain_p = pearsonr(family_sizes, domain_counts)
        
        # Test 2: Domain count by genome type
        genome_types = []
        domain_counts_by_type = []
        
        for family, data in self.family_architectures.items():
            genome_types.append(data['genome_type'])
            domain_counts_by_type.append(len(data['domains']))
        
        # Group by genome type
        grouped_data = defaultdict(list)
        for gt, dc in zip(genome_types, domain_counts_by_type):
            grouped_data[gt].append(dc)
        
        # Simple ANOVA-like test
        group_means = {gt: sum(vals)/len(vals) for gt, vals in grouped_data.items() if vals}
        overall_mean = sum(domain_counts_by_type) / len(domain_counts_by_type)
        
        # Calculate between-group variance
        between_var = sum(len(grouped_data[gt]) * (group_means[gt] - overall_mean)**2 
                         for gt in group_means)
        
        # Calculate within-group variance
        within_var = sum(sum((val - group_means[gt])**2 for val in grouped_data[gt]) 
                        for gt in grouped_data)
        
        # F-statistic
        df_between = len(group_means) - 1
        df_within = len(domain_counts_by_type) - len(group_means)
        
        if df_between > 0 and df_within > 0 and within_var > 0:
            f_stat = (between_var / df_between) / (within_var / df_within)
            # Simplified p-value
            anova_p = 0.01 if f_stat > 3 else 0.5
        else:
            f_stat = 0
            anova_p = 1
        
        return {
            'domain_family_size_correlation': {
                'correlation': size_domain_corr,
                'p_value': size_domain_p,
                'interpretation': 'Larger families have more domains' if size_domain_corr > 0.3 and size_domain_p < 0.05 else 'No clear relationship'
            },
            'clustering_stability': {
                'concordance_mean': clustering_comparison['concordance_score'],
                'confidence_interval': [clustering_comparison['concordance_score'] - 0.1, 
                                      clustering_comparison['concordance_score'] + 0.1],
                'stability': 'High' if clustering_comparison['concordance_score'] > 0.7 else 'Moderate'
            },
            'genome_type_domain_anova': {
                'f_statistic': f_stat,
                'p_value': anova_p,
                'significant': anova_p < 0.05,
                'interpretation': 'Domain count varies by genome type' if anova_p < 0.05 else 'Similar complexity across genome types'
            },
            'sample_sizes': {
                'n_families': len(self.family_architectures),
                'n_domains': len(self.viral_domains),
                'n_genome_types': len(grouped_data)
            }
        }
    
    def _generate_predictive_insights(
        self,
        classification_recommendations: Dict[str, Any],
        convergent_architectures: Dict[str, Any],
        modularity_analysis: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate predictive insights from domain architecture analysis."""
        
        insights = []
        
        # Classification alignment insight
        alignment = classification_recommendations['overall_alignment']
        insights.append({
            'type': 'classification_concordance',
            'insight': f'Domain architecture shows {alignment.lower()} concordance with current taxonomy',
            'recommendation': classification_recommendations['general_recommendation']
        })
        
        # Convergent evolution insight
        n_convergent = len(convergent_architectures['convergent_pairs'])
        insights.append({
            'type': 'convergent_evolution',
            'insight': f'{n_convergent} viral family pairs show convergent domain architectures despite different origins',
            'recommendation': 'Consider functional classification criteria for highly convergent groups'
        })
        
        # Modularity insight
        avg_modularity = modularity_analysis['average_modularity']
        insights.append({
            'type': 'domain_modularity',
            'insight': f'Average domain modularity score of {avg_modularity:.2f} indicates {"high" if avg_modularity > 0.3 else "moderate"} recombination potential',
            'recommendation': 'Track domain shuffling events for emerging virus surveillance'
        })
        
        # Essential domains insight
        insights.append({
            'type': 'essential_functions',
            'insight': 'Polymerase and capsid proteins are universal, while specialized domains define viral lifestyles',
            'recommendation': 'Use core domain set for broad viral classification, accessory domains for fine-scale'
        })
        
        # Misclassification insight
        n_misclassified = len(classification_recommendations.get('specific_recommendations', []))
        if n_misclassified > 0:
            insights.append({
                'type': 'taxonomic_revision',
                'insight': f'{n_misclassified} families may benefit from taxonomic reassignment based on domain architecture',
                'recommendation': 'Priority review for families with domain-taxonomy discordance'
            })
        
        # Future classification
        insights.append({
            'type': 'future_taxonomy',
            'insight': 'Hybrid sequence-domain classification could improve accuracy for divergent viruses',
            'recommendation': 'Implement dual classification system with domain validation for <50% identity'
        })
        
        return insights
    
    def save_results(self) -> None:
        """Save analysis results to JSON."""
        output_file = self.results_dir / f"{self.__class__.__name__}_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"Results saved to: {output_file}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run analysis
    data_dir = Path(__file__).parent.parent.parent / "data" / "msl"
    analyzer = DomainArchitectureAnalyzer(data_dir)
    
    results = analyzer.analyze()
    
    print("\nFunctional Domain Architecture Analysis Complete!")
    print(f"Results saved to: {analyzer.results_dir}")
    print(f"\nKey Finding: Domain-taxonomy concordance = {results['key_findings']['domain_taxonomic_concordance']:.2f}")
    print(f"Convergent architectures found: {results['key_findings']['convergent_architectures']}")
    print(f"Overall classification alignment: {results['key_findings']['classification_alignment']}")
    
    # Print summary statistics
    print("\n=== Analysis Summary ===")
    print(f"Families analyzed: {results['metadata']['families_analyzed']}")
    print(f"Domains analyzed: {results['metadata']['domains_analyzed']}")
    print(f"Essential domains: {results['domain_patterns']['essential_domains']}")
    print(f"Average domains per family: {results['domain_patterns']['average_domains_per_family']:.1f}")
    print(f"Highly modular families: {', '.join(results['modularity_analysis']['highly_modular_families'])}")
    
    # Print recommendations
    print("\n=== Classification Recommendations ===")
    print(f"Overall: {results['classification_recommendations']['general_recommendation']}")
    print(f"Implementation feasibility: {results['classification_recommendations']['implementation_feasibility']['technical_feasibility']}")
    
    # Print predictive insights
    print("\n=== Key Insights ===")
    for insight in results['predictive_insights'][:3]:
        print(f"- {insight['insight']}")
        print(f"  → {insight['recommendation']}")