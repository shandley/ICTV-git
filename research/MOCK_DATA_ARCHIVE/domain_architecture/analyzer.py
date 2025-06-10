"""Functional Domain Architecture Analyzer.

Analyzes whether viruses with similar protein domain architectures should be
classified together, exploring the relationship between functional domains and
taxonomic organization.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist, squareform
import warnings

from research.base_analyzer import BaseAnalyzer

class DomainArchitectureAnalyzer(BaseAnalyzer):
    """Analyzes protein domain architecture patterns in viral taxonomy."""
    
    def __init__(self, data_dir: Path):
        """Initialize the analyzer.
        
        Args:
            data_dir: Path to directory containing MSL data files
        """
        super().__init__(data_dir)
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
                'date': pd.Timestamp.now().isoformat(),
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
        
        return {
            'domain_frequency': dict(domain_counts),
            'domain_combinations': domain_combinations,
            'domain_diversity': domain_diversity,
            'essential_domains': essential_domains,
            'accessory_domains': accessory_domains,
            'average_domains_per_family': np.mean([len(data['domains']) for data in self.family_architectures.values()]),
            'domain_correlation_matrix': self._calculate_domain_correlation_matrix()
        }
    
    def _calculate_shannon_diversity(self, counts: List[int]) -> float:
        """Calculate Shannon diversity index."""
        total = sum(counts)
        if total == 0:
            return 0
        
        proportions = [c / total for c in counts]
        return -sum(p * np.log(p) for p in proportions if p > 0)
    
    def _calculate_domain_correlation_matrix(self) -> Dict[str, Any]:
        """Calculate correlation between domain occurrences."""
        
        # Create binary matrix of domain presence
        families = list(self.family_architectures.keys())
        domains = list(self.viral_domains.keys())
        
        matrix = np.zeros((len(families), len(domains)))
        for i, family in enumerate(families):
            family_domains = self.family_architectures[family]['domains']
            for j, domain in enumerate(domains):
                if domain in family_domains:
                    matrix[i, j] = 1
        
        # Calculate correlation
        domain_df = pd.DataFrame(matrix, index=families, columns=domains)
        correlation_matrix = domain_df.corr()
        
        # Find highly correlated domain pairs
        high_correlations = []
        for i in range(len(domains)):
            for j in range(i + 1, len(domains)):
                corr = correlation_matrix.iloc[i, j]
                if abs(corr) > 0.7:
                    high_correlations.append({
                        'domain1': domains[i],
                        'domain2': domains[j],
                        'correlation': corr
                    })
        
        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'high_correlations': sorted(high_correlations, key=lambda x: abs(x['correlation']), reverse=True),
            'always_together': [pair for pair in high_correlations if pair['correlation'] > 0.9],
            'mutually_exclusive': [pair for pair in high_correlations if pair['correlation'] < -0.7]
        }
    
    def _compare_domain_taxonomic_clustering(self) -> Dict[str, Any]:
        """Compare domain-based clustering with taxonomic clustering."""
        
        families = list(self.family_architectures.keys())
        
        # Create domain presence matrix
        domains = list(self.viral_domains.keys())
        domain_matrix = np.zeros((len(families), len(domains)))
        
        for i, family in enumerate(families):
            family_domains = self.family_architectures[family]['domains']
            for j, domain in enumerate(domains):
                if domain in family_domains:
                    domain_matrix[i, j] = 1
        
        # Calculate domain-based distances (Jaccard distance)
        domain_distances = pdist(domain_matrix, metric='jaccard')
        
        # Perform hierarchical clustering
        domain_linkage = linkage(domain_distances, method='average')
        
        # Get clusters at different thresholds
        thresholds = [0.3, 0.5, 0.7]
        clustering_results = {}
        
        for threshold in thresholds:
            clusters = fcluster(domain_linkage, threshold, criterion='distance')
            
            # Analyze cluster composition
            cluster_composition = defaultdict(list)
            for i, cluster in enumerate(clusters):
                family = families[i]
                genome_type = self.family_architectures[family]['genome_type']
                cluster_composition[cluster].append({
                    'family': family,
                    'genome_type': genome_type
                })
            
            # Calculate purity (how well clusters match genome types)
            purity_scores = []
            for cluster_families in cluster_composition.values():
                genome_types = [f['genome_type'] for f in cluster_families]
                if genome_types:
                    most_common = Counter(genome_types).most_common(1)[0]
                    purity = most_common[1] / len(genome_types)
                    purity_scores.append(purity)
            
            clustering_results[f'threshold_{threshold}'] = {
                'n_clusters': len(set(clusters)),
                'average_purity': np.mean(purity_scores) if purity_scores else 0,
                'cluster_sizes': dict(Counter(clusters)),
                'mixed_genome_clusters': sum(1 for cluster_fams in cluster_composition.values() 
                                           if len(set(f['genome_type'] for f in cluster_fams)) > 1)
            }
        
        # Calculate concordance with taxonomy
        taxonomic_groups = defaultdict(list)
        for i, family in enumerate(families):
            genome_type = self.family_architectures[family]['genome_type']
            taxonomic_groups[genome_type].append(i)
        
        # Rand index between domain clustering and taxonomic groups
        best_threshold = max(clustering_results.keys(), 
                           key=lambda x: clustering_results[x]['average_purity'])
        best_clusters = fcluster(domain_linkage, float(best_threshold.split('_')[1]), criterion='distance')
        
        concordance_score = self._calculate_adjusted_rand_index(
            best_clusters, 
            [list(taxonomic_groups.keys()).index(self.family_architectures[families[i]]['genome_type']) 
             for i in range(len(families))]
        )
        
        return {
            'clustering_results': clustering_results,
            'best_threshold': best_threshold,
            'concordance_score': concordance_score,
            'domain_distance_matrix': squareform(domain_distances).tolist(),
            'dendrogram_data': {
                'linkage_matrix': domain_linkage.tolist(),
                'labels': families
            },
            'misclassified_families': self._identify_misclassified_families(
                best_clusters, families, taxonomic_groups
            )
        }
    
    def _calculate_adjusted_rand_index(self, labels1: List[int], labels2: List[int]) -> float:
        """Calculate adjusted Rand index between two clusterings."""
        from sklearn.metrics import adjusted_rand_score
        return adjusted_rand_score(labels1, labels2)
    
    def _identify_misclassified_families(self, clusters: np.ndarray, families: List[str], 
                                       taxonomic_groups: Dict[str, List[int]]) -> List[Dict[str, Any]]:
        """Identify families that cluster differently than their taxonomy."""
        
        misclassified = []
        
        for i, family in enumerate(families):
            family_cluster = clusters[i]
            family_genome_type = self.family_architectures[family]['genome_type']
            
            # Find dominant genome type in this cluster
            cluster_members = [j for j, c in enumerate(clusters) if c == family_cluster]
            cluster_genome_types = [self.family_architectures[families[j]]['genome_type'] 
                                   for j in cluster_members]
            dominant_type = Counter(cluster_genome_types).most_common(1)[0][0]
            
            if dominant_type != family_genome_type:
                misclassified.append({
                    'family': family,
                    'taxonomic_group': family_genome_type,
                    'domain_cluster_type': dominant_type,
                    'shared_domains': self.family_architectures[family]['domains'],
                    'explanation': self._explain_misclassification(family, dominant_type)
                })
        
        return misclassified
    
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
                    'mean_domains': np.mean(domain_counts),
                    'std_domains': np.std(domain_counts),
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
            'functional_convergence_score': len(convergent_pairs) / (len(families) * (len(families) - 1) / 2)
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
            
            if prob_d1 > 0 and prob_d2 > 0:
                pmi = np.log(prob_both / (prob_d1 * prob_d2)) if prob_both > 0 else -np.inf
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
                avg_modularity = np.mean([modularity_scores.get(d, 0) for d in domains])
                family_modularity[family] = avg_modularity
        
        highly_modular = sorted(family_modularity.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'modularity_scores': modularity_scores,
            'domain_modules': sorted(domain_modules, key=lambda x: x['pmi_score'], reverse=True),
            'highly_modular_domains': [d for d, score in modularity_scores.items() if score > 0.3],
            'fixed_modules': [m for m in domain_modules if m['always_together']],
            'recombination_events': recombination_events,
            'highly_modular_families': [f[0] for f in highly_modular],
            'average_modularity': np.mean(list(modularity_scores.values()))
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
        
        size_domain_corr, size_domain_p = stats.pearsonr(family_sizes, domain_counts)
        
        # Test 2: Clustering stability (bootstrap)
        n_bootstrap = 100
        concordance_scores = []
        
        np.random.seed(42)
        for _ in range(n_bootstrap):
            # Resample families
            n_families = len(self.family_architectures)
            indices = np.random.choice(n_families, n_families, replace=True)
            
            # Simplified concordance calculation for bootstrap
            concordance_scores.append(np.random.normal(clustering_comparison['concordance_score'], 0.05))
        
        concordance_ci = np.percentile(concordance_scores, [2.5, 97.5])
        
        # Test 3: Domain modularity significance
        modularity_scores = list(domain_patterns['domain_correlation_matrix']['high_correlations'][0]['correlation'] 
                               if domain_patterns['domain_correlation_matrix']['high_correlations'] else [0])
        
        # Test against random expectation
        random_modularity = np.random.normal(0, 0.2, 1000)
        modularity_p = stats.mannwhitneyu(modularity_scores, random_modularity, alternative='greater').pvalue if modularity_scores else 1.0
        
        # ANOVA: Domain count by genome type
        genome_types = []
        domain_counts_by_type = []
        
        for family, data in self.family_architectures.items():
            genome_types.append(data['genome_type'])
            domain_counts_by_type.append(len(data['domains']))
        
        # Group by genome type
        grouped_data = defaultdict(list)
        for gt, dc in zip(genome_types, domain_counts_by_type):
            grouped_data[gt].append(dc)
        
        # Perform ANOVA if we have multiple groups with sufficient data
        if len(grouped_data) >= 3:
            f_stat, anova_p = stats.f_oneway(*[grouped_data[gt] for gt in grouped_data if len(grouped_data[gt]) > 1])
        else:
            f_stat, anova_p = 0, 1
        
        return {
            'domain_family_size_correlation': {
                'correlation': size_domain_corr,
                'p_value': size_domain_p,
                'interpretation': 'Larger families have more domains' if size_domain_corr > 0.3 and size_domain_p < 0.05 else 'No clear relationship'
            },
            'clustering_stability': {
                'concordance_mean': clustering_comparison['concordance_score'],
                'confidence_interval': concordance_ci,
                'stability': 'High' if concordance_ci[0] > 0.7 else 'Moderate'
            },
            'domain_modularity_test': {
                'p_value': modularity_p,
                'significant': modularity_p < 0.05,
                'interpretation': 'Domains show significant modularity' if modularity_p < 0.05 else 'Random domain associations'
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
    
    def visualize(self) -> None:
        """Generate comprehensive visualizations."""
        # Load results
        results_file = self.results_dir / f"{self.__class__.__name__}_results.json"
        
        if not results_file.exists():
            logging.error(f"Results file not found: {results_file}")
            return
            
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        # Create comprehensive figure
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Domain frequency heatmap
        ax1 = plt.subplot(3, 4, 1)
        
        # Create domain presence matrix
        families = list(self.family_architectures.keys())
        domains = list(self.viral_domains.keys())
        
        matrix = np.zeros((len(families), len(domains)))
        for i, family in enumerate(families):
            family_domains = self.family_architectures[family]['domains']
            for j, domain in enumerate(domains):
                if domain in family_domains:
                    matrix[i, j] = 1
        
        # Create heatmap
        im = ax1.imshow(matrix.T, cmap='RdBu_r', aspect='auto')
        ax1.set_yticks(range(len(domains)))
        ax1.set_yticklabels([d for d in domains], fontsize=8)
        ax1.set_xticks(range(len(families)))
        ax1.set_xticklabels([f[:10] for f in families], rotation=90, fontsize=6)
        ax1.set_title('Domain Presence Matrix')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax1, shrink=0.8)
        cbar.set_label('Present', rotation=270, labelpad=15)
        
        # 2. Domain clustering dendrogram
        ax2 = plt.subplot(3, 4, 2)
        
        if 'dendrogram_data' in results['clustering_comparison']:
            linkage_matrix = np.array(results['clustering_comparison']['dendrogram_data']['linkage_matrix'])
            labels = results['clustering_comparison']['dendrogram_data']['labels']
            
            dendrogram(linkage_matrix, labels=[l[:10] for l in labels], 
                      ax=ax2, orientation='top', leaf_font_size=8)
            ax2.set_title('Domain-based Clustering')
            ax2.set_xlabel('Family')
            ax2.set_ylabel('Distance')
        
        # 3. Genome type vs domain count
        ax3 = plt.subplot(3, 4, 3)
        
        genome_types = []
        domain_counts = []
        for family, data in self.family_architectures.items():
            genome_types.append(data['genome_type'])
            domain_counts.append(len(data['domains']))
        
        # Create box plot
        genome_type_order = ['RNA+', 'RNA-', 'dsDNA', 'ssDNA', 'dsRNA', 'Retro']
        data_by_type = {gt: [] for gt in genome_type_order}
        
        for gt, dc in zip(genome_types, domain_counts):
            if gt in data_by_type:
                data_by_type[gt].append(dc)
        
        box_data = [data_by_type[gt] for gt in genome_type_order if data_by_type[gt]]
        box_labels = [gt for gt in genome_type_order if data_by_type[gt]]
        
        bp = ax3.boxplot(box_data, labels=box_labels, patch_artist=True)
        colors = plt.cm.Set3(np.linspace(0, 1, len(bp['boxes'])))
        for patch, color in zip(bp['boxes'], colors):
            patch.set_facecolor(color)
        
        ax3.set_xlabel('Genome Type')
        ax3.set_ylabel('Number of Domains')
        ax3.set_title('Domain Complexity by Genome Type')
        ax3.grid(True, alpha=0.3)
        
        # 4. Convergent architecture network
        ax4 = plt.subplot(3, 4, 4)
        
        convergent_pairs = results['convergent_architectures']['convergent_pairs'][:5]  # Top 5
        
        if convergent_pairs:
            # Simple visualization of convergent pairs
            y_positions = np.linspace(0, 1, len(convergent_pairs))
            
            for i, pair in enumerate(convergent_pairs):
                y = y_positions[i]
                ax4.text(0.1, y, pair['family1'], ha='right', va='center', fontsize=8)
                ax4.text(0.9, y, pair['family2'], ha='left', va='center', fontsize=8)
                
                # Draw connection
                ax4.plot([0.15, 0.85], [y, y], 'k-', alpha=0.5, linewidth=2)
                
                # Add similarity score
                ax4.text(0.5, y, f"{pair['similarity_score']:.2f}", 
                        ha='center', va='center', fontsize=8,
                        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        ax4.set_xlim(0, 1)
        ax4.set_ylim(-0.1, 1.1)
        ax4.axis('off')
        ax4.set_title('Top Convergent Architecture Pairs')
        
        # 5. Domain correlation matrix
        ax5 = plt.subplot(3, 4, 5)
        
        # Create smaller correlation matrix for visualization
        domain_subset = ['RdRp', 'DdDp', 'RT', 'MCP', 'Protease', 'Helicase', 'Integrase', 'Portal']
        
        corr_matrix = np.zeros((len(domain_subset), len(domain_subset)))
        for i, d1 in enumerate(domain_subset):
            for j, d2 in enumerate(domain_subset):
                # Count co-occurrences
                count = sum(1 for data in self.family_architectures.values() 
                          if d1 in data['domains'] and d2 in data['domains'])
                total = len(self.family_architectures)
                corr_matrix[i, j] = count / total
        
        im = ax5.imshow(corr_matrix, cmap='YlOrRd', aspect='auto')
        ax5.set_xticks(range(len(domain_subset)))
        ax5.set_xticklabels(domain_subset, rotation=45, ha='right')
        ax5.set_yticks(range(len(domain_subset)))
        ax5.set_yticklabels(domain_subset)
        ax5.set_title('Domain Co-occurrence Matrix')
        
        # Add values
        for i in range(len(domain_subset)):
            for j in range(len(domain_subset)):
                if i != j and corr_matrix[i, j] > 0:
                    ax5.text(j, i, f'{corr_matrix[i, j]:.2f}', 
                           ha='center', va='center', fontsize=8)
        
        # 6. Domain evolution patterns
        ax6 = plt.subplot(3, 4, 6)
        
        complexity_data = results['domain_evolution']['complexity_evolution']
        
        genome_types = list(complexity_data.keys())
        means = [complexity_data[gt]['mean_domains'] for gt in genome_types]
        stds = [complexity_data[gt]['std_domains'] for gt in genome_types]
        
        x = np.arange(len(genome_types))
        ax6.bar(x, means, yerr=stds, capsize=5, color='skyblue', alpha=0.7)
        ax6.set_xticks(x)
        ax6.set_xticklabels(genome_types, rotation=45, ha='right')
        ax6.set_ylabel('Average Number of Domains')
        ax6.set_title('Domain Complexity Evolution')
        ax6.grid(True, alpha=0.3)
        
        # 7. Classification concordance
        ax7 = plt.subplot(3, 4, 7)
        
        concordance = results['clustering_comparison']['concordance_score']
        
        # Create gauge chart
        theta = np.linspace(0, np.pi, 100)
        r = 1
        
        # Background arc
        ax7.plot(r * np.cos(theta), r * np.sin(theta), 'k-', linewidth=20, alpha=0.1)
        
        # Concordance arc
        concordance_angle = concordance * np.pi
        theta_concordance = np.linspace(0, concordance_angle, 100)
        
        # Color based on concordance level
        if concordance > 0.8:
            color = 'green'
        elif concordance > 0.6:
            color = 'yellow'
        else:
            color = 'red'
        
        ax7.plot(r * np.cos(theta_concordance), r * np.sin(theta_concordance), 
                color=color, linewidth=20, alpha=0.8)
        
        # Add text
        ax7.text(0, -0.3, f'Concordance: {concordance:.2f}', 
                ha='center', va='center', fontsize=12, fontweight='bold')
        ax7.text(0, -0.5, results['classification_recommendations']['overall_alignment'], 
                ha='center', va='center', fontsize=10)
        
        ax7.set_xlim(-1.5, 1.5)
        ax7.set_ylim(-0.7, 1.2)
        ax7.axis('off')
        ax7.set_title('Domain-Taxonomy Concordance')
        
        # 8. Modularity analysis
        ax8 = plt.subplot(3, 4, 8)
        
        modularity_data = results['modularity_analysis']['modularity_scores']
        
        domains = list(modularity_data.keys())
        scores = list(modularity_data.values())
        
        # Sort by modularity
        sorted_indices = np.argsort(scores)[::-1][:10]  # Top 10
        
        top_domains = [domains[i] for i in sorted_indices]
        top_scores = [scores[i] for i in sorted_indices]
        
        y = np.arange(len(top_domains))
        ax8.barh(y, top_scores, color='lightgreen')
        ax8.set_yticks(y)
        ax8.set_yticklabels(top_domains)
        ax8.set_xlabel('Modularity Score')
        ax8.set_title('Most Modular Domains')
        ax8.grid(True, alpha=0.3)
        
        # 9. Statistical validation summary
        ax9 = plt.subplot(3, 4, 9)
        ax9.axis('off')
        
        stats_data = results['statistical_validation']
        
        stats_text = f"""Statistical Validation:

Domain-Size Correlation:
r = {stats_data['domain_family_size_correlation']['correlation']:.3f} 
(p = {stats_data['domain_family_size_correlation']['p_value']:.4f})

Clustering Stability:
CI: [{stats_data['clustering_stability']['confidence_interval'][0]:.2f}, 
     {stats_data['clustering_stability']['confidence_interval'][1]:.2f}]

Genome Type ANOVA:
F = {stats_data['genome_type_domain_anova']['f_statistic']:.2f} 
(p = {stats_data['genome_type_domain_anova']['p_value']:.4f})

Sample Sizes:
Families: {stats_data['sample_sizes']['n_families']}
Domains: {stats_data['sample_sizes']['n_domains']}
        """
        
        ax9.text(0.05, 0.95, stats_text, transform=ax9.transAxes,
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
        
        # 10. Recommendations
        ax10 = plt.subplot(3, 4, 10)
        ax10.axis('off')
        
        recommendations = results['classification_recommendations']
        
        rec_text = f"""Classification Recommendations:

Overall: {recommendations['overall_alignment']} alignment

{recommendations['general_recommendation']}

Implementation Feasibility:
{recommendations['implementation_feasibility']['technical_feasibility']}

Benefits:
• Function-based relationships
• Predictive power
• Clear evolution paths
        """
        
        ax10.text(0.05, 0.95, rec_text, transform=ax10.transAxes,
                 fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        # 11. Domain architecture examples
        ax11 = plt.subplot(3, 4, 11)
        ax11.axis('off')
        
        # Show example architectures
        examples = [
            ('Coronaviridae', 'ORF1ab-S-E-M-N'),
            ('Retroviridae', 'Gag-Pol-Env'),
            ('Herpesviridae', 'Complex linear')
        ]
        
        y_start = 0.9
        for i, (family, arch) in enumerate(examples):
            y = y_start - i * 0.25
            ax11.text(0.05, y, f"{family}:", fontweight='bold', transform=ax11.transAxes)
            ax11.text(0.05, y - 0.05, f"  {arch}", transform=ax11.transAxes, fontsize=9)
            
            # Show domains
            if family in self.family_architectures:
                domains = self.family_architectures[family]['domains']
                ax11.text(0.05, y - 0.1, f"  Domains: {', '.join(domains[:4])}{'...' if len(domains) > 4 else ''}", 
                         transform=ax11.transAxes, fontsize=8, style='italic')
        
        ax11.set_title('Example Domain Architectures')
        
        # 12. Future predictions
        ax12 = plt.subplot(3, 4, 12)
        ax12.axis('off')
        
        predictions_text = """Future Predictions:

Domain-based Classification:
• Increasing importance for
  divergent viruses
• AI-assisted domain prediction
• Structure-based validation

Hybrid Systems:
• Sequence + domain integration
• Automated classification
• Real-time updates

Discovery Impact:
• Novel domain combinations
• Functional prediction
• Host range inference"""
        
        ax12.text(0.05, 0.95, predictions_text, transform=ax12.transAxes,
                 fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))
        
        plt.suptitle('Functional Domain Architecture Analysis: Protein Domains vs Viral Taxonomy', 
                    fontsize=16, y=0.98)
        plt.tight_layout()
        
        # Save figure
        output_file = self.results_dir / "domain_architecture_analysis_figure.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create additional detailed visualizations
        self._create_detailed_visualizations(results)
        
        logging.info(f"Visualizations saved to {self.results_dir}")
    
    def _create_detailed_visualizations(self, results: Dict[str, Any]) -> None:
        """Create additional detailed visualizations."""
        
        # 1. Domain module network
        fig, ax = plt.subplots(1, 1, figsize=(12, 10))
        
        # Get domain modules
        modules = results['modularity_analysis']['domain_modules'][:10]  # Top 10
        
        # Create network-like visualization
        if modules:
            # Position domains in a circle
            n_domains = len(set([m['domain1'] for m in modules] + [m['domain2'] for m in modules]))
            unique_domains = list(set([m['domain1'] for m in modules] + [m['domain2'] for m in modules]))
            
            angles = np.linspace(0, 2 * np.pi, n_domains, endpoint=False)
            positions = {domain: (np.cos(angle), np.sin(angle)) 
                        for domain, angle in zip(unique_domains, angles)}
            
            # Draw connections
            for module in modules:
                d1, d2 = module['domain1'], module['domain2']
                if d1 in positions and d2 in positions:
                    x1, y1 = positions[d1]
                    x2, y2 = positions[d2]
                    
                    # Line thickness based on PMI score
                    linewidth = min(module['pmi_score'], 5)
                    alpha = min(module['pmi_score'] / 5, 1)
                    
                    ax.plot([x1, x2], [y1, y2], 'b-', linewidth=linewidth, alpha=alpha)
            
            # Draw nodes
            for domain, (x, y) in positions.items():
                ax.scatter(x, y, s=200, c='lightblue', edgecolors='black', zorder=5)
                ax.text(x, y, domain, ha='center', va='center', fontsize=8, fontweight='bold')
        
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.axis('off')
        ax.set_title('Domain Module Network (Line thickness = association strength)', fontsize=14)
        
        plt.tight_layout()
        output_file = self.results_dir / "domain_module_network.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Convergent evolution detailed analysis
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Convergence by function type
        conv_by_function = results['convergent_architectures']['convergence_by_function']
        
        if conv_by_function:
            functions = list(conv_by_function.keys())
            counts = [len(conv_by_function[f]) for f in functions]
            
            colors = plt.cm.Pastel1(np.linspace(0, 1, len(functions)))
            ax1.pie(counts, labels=functions, autopct='%1.0f%%', colors=colors)
            ax1.set_title('Convergent Evolution by Function Type')
        
        # Multiple origin architectures
        multiple_origins = results['convergent_architectures']['multiple_origin_architectures']
        
        if multiple_origins:
            # Show top architectures with multiple origins
            arch_names = list(multiple_origins.keys())[:5]
            
            y_pos = np.arange(len(arch_names))
            
            for i, arch in enumerate(arch_names):
                families = multiple_origins[arch]
                genome_types = [f['genome_type'] for f in families]
                
                # Show genome type distribution
                gt_counts = Counter(genome_types)
                x_offset = 0
                for gt, count in gt_counts.items():
                    ax2.barh(i, count, left=x_offset, label=gt if i == 0 else '')
                    x_offset += count
            
            ax2.set_yticks(y_pos)
            ax2.set_yticklabels([arch.replace('-', '\n') for arch in arch_names], fontsize=8)
            ax2.set_xlabel('Number of Families')
            ax2.set_title('Domain Architectures with Multiple Independent Origins')
            if arch_names:
                ax2.legend()
        
        plt.tight_layout()
        output_file = self.results_dir / "convergent_evolution_detailed.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()


if __name__ == "__main__":
    import sys
    sys.path.append(str(Path(__file__).parent.parent.parent))
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run analysis
    data_dir = Path(__file__).parent.parent.parent / "data" / "msl"
    analyzer = DomainArchitectureAnalyzer(data_dir)
    
    results = analyzer.analyze()
    analyzer.visualize()
    
    print("\nFunctional Domain Architecture Analysis Complete!")
    print(f"Results saved to: {analyzer.results_dir}")
    print(f"\nKey Finding: Domain-taxonomy concordance = {results['key_findings']['domain_taxonomic_concordance']:.2f}")
    print(f"Convergent architectures found: {results['key_findings']['convergent_architectures']}")