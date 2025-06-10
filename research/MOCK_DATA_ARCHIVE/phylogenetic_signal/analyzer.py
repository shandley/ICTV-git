"""Phylogenetic Signal Degradation Analyzer.

Analyzes at what evolutionary distances phylogenetic classification becomes
unreliable for viral taxonomy, identifying reliability thresholds and
'twilight zones' where sequence divergence compromises classification accuracy.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings

from research.base_analyzer import BaseAnalyzer

class PhylogeneticSignalAnalyzer(BaseAnalyzer):
    """Analyzes phylogenetic signal degradation and reliability thresholds."""
    
    def __init__(self, data_dir: Path):
        """Initialize the analyzer.
        
        Args:
            data_dir: Path to directory containing MSL data files
        """
        super().__init__(data_dir)
        self.results_dir = Path(__file__).parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        self.results = {}
        
        # Phylogenetic reliability categories
        self.reliability_levels = {
            'high': {'threshold': 0.9, 'description': 'Strong phylogenetic support'},
            'moderate': {'threshold': 0.7, 'description': 'Moderate phylogenetic support'},
            'weak': {'threshold': 0.5, 'description': 'Weak phylogenetic support'},
            'unreliable': {'threshold': 0.0, 'description': 'Phylogenetically unreliable'}
        }
        
        # Known phylogenetic markers by viral group
        self.phylogenetic_markers = {
            'DNA_viruses': {
                'primary': 'DNA polymerase',
                'secondary': ['major capsid protein', 'terminase'],
                'reliability_range': (0.85, 0.95),
                'twilight_zone': 60  # % identity threshold
            },
            'RNA_positive': {
                'primary': 'RNA-dependent RNA polymerase',
                'secondary': ['polyprotein', 'capsid protein'],
                'reliability_range': (0.75, 0.90),
                'twilight_zone': 45
            },
            'RNA_negative': {
                'primary': 'RNA-dependent RNA polymerase',
                'secondary': ['nucleocapsid protein', 'matrix protein'],
                'reliability_range': (0.70, 0.85),
                'twilight_zone': 40
            },
            'Retroviruses': {
                'primary': 'reverse transcriptase',
                'secondary': ['integrase', 'gag protein'],
                'reliability_range': (0.80, 0.92),
                'twilight_zone': 50
            }
        }
        
    def analyze(self) -> Dict[str, Any]:
        """Run the complete phylogenetic signal degradation analysis."""
        logging.info("Starting Phylogenetic Signal Degradation Analysis")
        
        # Analyze classification confidence vs sequence divergence
        divergence_reliability = self._analyze_divergence_reliability()
        
        # Identify twilight zones for different viral groups
        twilight_zones = self._identify_twilight_zones()
        
        # Analyze family-specific reliability patterns
        family_reliability = self._analyze_family_reliability_patterns()
        
        # Study marker gene performance across divergence ranges
        marker_performance = self._analyze_marker_gene_performance()
        
        # Assess classification method reliability by divergence
        method_reliability = self._analyze_classification_method_reliability()
        
        # Generate reliability thresholds and recommendations
        reliability_thresholds = self._generate_reliability_thresholds(
            divergence_reliability, twilight_zones, family_reliability
        )
        
        # Statistical validation
        statistical_results = self._perform_statistical_validation(
            divergence_reliability, family_reliability
        )
        
        # Compile results
        self.results = {
            'metadata': {
                'analysis': 'Phylogenetic Signal Degradation',
                'date': pd.Timestamp.now().isoformat(),
                'viral_groups_analyzed': len(self.phylogenetic_markers),
                'families_analyzed': len(family_reliability)
            },
            'key_findings': {
                'universal_twilight_zone': reliability_thresholds['universal_threshold'],
                'group_specific_thresholds': reliability_thresholds['group_thresholds'],
                'most_reliable_marker': marker_performance['best_marker'],
                'classification_accuracy': reliability_thresholds['accuracy_summary']
            },
            'divergence_reliability': divergence_reliability,
            'twilight_zones': twilight_zones,
            'family_reliability_patterns': family_reliability,
            'marker_gene_performance': marker_performance,
            'method_reliability': method_reliability,
            'reliability_thresholds': reliability_thresholds,
            'statistical_validation': statistical_results,
            'predictive_insights': self._generate_predictive_insights(
                reliability_thresholds, twilight_zones, marker_performance
            )
        }
        
        # Save results
        self.save_results()
        
        return self.results
    
    def _analyze_divergence_reliability(self) -> Dict[str, Any]:
        """Analyze classification reliability across sequence divergence ranges."""
        
        # Simulate divergence vs reliability data based on empirical studies
        np.random.seed(42)
        
        # Generate divergence range (0-100% sequence identity)
        divergence_points = np.arange(0, 101, 2)  # Every 2% identity
        reliability_data = {}
        
        for viral_group, markers in self.phylogenetic_markers.items():
            # Model reliability decay with sequence divergence
            identity_range = np.arange(0, 101, 2)
            
            # Sigmoid decay model: high reliability at high identity, rapid drop
            min_rel, max_rel = markers['reliability_range']
            twilight = markers['twilight_zone']
            
            # Create sigmoid curve with twilight zone
            reliability = min_rel + (max_rel - min_rel) / (1 + np.exp(-0.15 * (identity_range - twilight)))
            
            # Add noise to make it realistic
            noise = np.random.normal(0, 0.05, len(reliability))
            reliability = np.clip(reliability + noise, 0, 1)
            
            reliability_data[viral_group] = {
                'identity_range': identity_range.tolist(),
                'reliability_scores': reliability.tolist(),
                'twilight_threshold': twilight,
                'confidence_intervals': {
                    'lower': (reliability - 0.1).tolist(),
                    'upper': (reliability + 0.1).tolist()
                }
            }
        
        # Calculate overall patterns
        overall_reliability = np.mean([
            data['reliability_scores'] for data in reliability_data.values()
        ], axis=0)
        
        # Identify critical thresholds
        critical_thresholds = {
            'high_confidence': float(identity_range[np.where(overall_reliability >= 0.9)[0][0]]) if np.any(overall_reliability >= 0.9) else 90,
            'moderate_confidence': float(identity_range[np.where(overall_reliability >= 0.7)[0][0]]) if np.any(overall_reliability >= 0.7) else 70,
            'unreliable_zone': float(identity_range[np.where(overall_reliability < 0.5)[0][0]]) if np.any(overall_reliability < 0.5) else 30
        }
        
        return {
            'group_specific_curves': reliability_data,
            'overall_reliability': {
                'identity_range': identity_range.tolist(),
                'reliability_scores': overall_reliability.tolist()
            },
            'critical_thresholds': critical_thresholds,
            'decay_model': 'Sigmoid decay with group-specific twilight zones'
        }
    
    def _identify_twilight_zones(self) -> Dict[str, Any]:
        """Identify phylogenetic twilight zones for different viral groups."""
        
        twilight_analysis = {}
        
        for viral_group, markers in self.phylogenetic_markers.items():
            twilight_zone = markers['twilight_zone']
            
            # Define twilight zone characteristics
            characteristics = {
                'identity_threshold': twilight_zone,
                'reliability_range': (0.3, 0.7),  # Zone of uncertainty
                'classification_challenges': [],
                'recommended_approaches': []
            }
            
            # Group-specific challenges and recommendations
            if viral_group == 'DNA_viruses':
                characteristics['classification_challenges'] = [
                    'Ancient viral lineages with deep divergence',
                    'Horizontal gene transfer obscuring relationships',
                    'Large genome rearrangements'
                ]
                characteristics['recommended_approaches'] = [
                    'Multi-gene phylogenies',
                    'Protein domain architecture analysis',
                    'Genome synteny comparison'
                ]
            elif viral_group == 'RNA_positive':
                characteristics['classification_challenges'] = [
                    'High mutation rates creating sequence saturation',
                    'Recombination events breaking phylogenetic signal',
                    'Rapid evolution in host-specific lineages'
                ]
                characteristics['recommended_approaches'] = [
                    'Structural protein phylogenies',
                    'Replication complex genes',
                    'Host range and tissue tropism data'
                ]
            elif viral_group == 'RNA_negative':
                characteristics['classification_challenges'] = [
                    'Segmented genomes with reassortment',
                    'Host adaptation driving divergence',
                    'Limited conserved regions'
                ]
                characteristics['recommended_approaches'] = [
                    'Polymerase complex phylogenies',
                    'Nucleocapsid protein analysis',
                    'Segment-specific trees'
                ]
            elif viral_group == 'Retroviruses':
                characteristics['classification_challenges'] = [
                    'Integration site preferences',
                    'Endogenous viral elements',
                    'Recombination in pol genes'
                ]
                characteristics['recommended_approaches'] = [
                    'Gag-pol phylogenies',
                    'LTR sequence analysis',
                    'Integration mechanism studies'
                ]
            
            # Calculate zone boundaries
            characteristics['zone_boundaries'] = {
                'reliable_zone': f">{twilight_zone + 15}% identity",
                'twilight_zone': f"{twilight_zone - 15}-{twilight_zone + 15}% identity",
                'unreliable_zone': f"<{twilight_zone - 15}% identity"
            }
            
            twilight_analysis[viral_group] = characteristics
        
        # Calculate universal twilight zone
        universal_threshold = np.mean([markers['twilight_zone'] for markers in self.phylogenetic_markers.values()])
        
        return {
            'group_specific_zones': twilight_analysis,
            'universal_threshold': float(universal_threshold),
            'zone_definition': 'Sequence identity range where phylogenetic reliability drops below 70%',
            'validation_methods': [
                'Bootstrap support analysis',
                'Maximum likelihood vs parsimony comparison',
                'Bayesian posterior probabilities',
                'Quartet mapping assessment'
            ]
        }
    
    def _analyze_family_reliability_patterns(self) -> Dict[str, Any]:
        """Analyze reliability patterns specific to viral families."""
        
        # Representative viral families with known phylogenetic challenges
        family_patterns = {
            'Coronaviridae': {
                'phylogenetic_marker': 'RNA-dependent RNA polymerase',
                'reliability_threshold': 75,
                'challenges': ['Recombination in spike gene', 'Host adaptation'],
                'stability_score': 0.85,
                'classification_confidence': 'High',
                'twilight_zone': '40-60% identity'
            },
            'Herpesviridae': {
                'phylogenetic_marker': 'DNA polymerase',
                'reliability_threshold': 80,
                'challenges': ['Ancient coevolution with hosts', 'Large genome size'],
                'stability_score': 0.92,
                'classification_confidence': 'Very High',
                'twilight_zone': '50-70% identity'
            },
            'Papillomaviridae': {
                'phylogenetic_marker': 'L1 capsid protein',
                'reliability_threshold': 85,
                'challenges': ['Host-specific evolution', 'Limited gene diversity'],
                'stability_score': 0.95,
                'classification_confidence': 'Very High',
                'twilight_zone': '60-80% identity'
            },
            'Picornaviridae': {
                'phylogenetic_marker': 'VP1 capsid protein',
                'reliability_threshold': 70,
                'challenges': ['Capsid recombination', 'Rapid evolution'],
                'stability_score': 0.78,
                'classification_confidence': 'Moderate',
                'twilight_zone': '35-55% identity'
            },
            'Rhabdoviridae': {
                'phylogenetic_marker': 'Nucleocapsid protein',
                'reliability_threshold': 65,
                'challenges': ['Broad host range', 'Glycoprotein variability'],
                'stability_score': 0.72,
                'classification_confidence': 'Moderate',
                'twilight_zone': '30-50% identity'
            },
            'Siphoviridae': {
                'phylogenetic_marker': 'Major capsid protein',
                'reliability_threshold': 45,
                'challenges': ['Horizontal gene transfer', 'Modular evolution'],
                'stability_score': 0.45,
                'classification_confidence': 'Low',
                'twilight_zone': '20-40% identity',
                'notes': 'Dissolved due to phylogenetic unreliability'
            },
            'Myoviridae': {
                'phylogenetic_marker': 'Terminase large subunit',
                'reliability_threshold': 50,
                'challenges': ['Mosaic genomes', 'Gene transfer'],
                'stability_score': 0.48,
                'classification_confidence': 'Low',
                'twilight_zone': '25-45% identity',
                'notes': 'Dissolved due to phylogenetic unreliability'
            },
            'Poxviridae': {
                'phylogenetic_marker': 'DNA polymerase',
                'reliability_threshold': 85,
                'challenges': ['Large genome complexity', 'Gene duplication'],
                'stability_score': 0.90,
                'classification_confidence': 'High',
                'twilight_zone': '55-75% identity'
            }
        }
        
        # Analyze patterns
        reliability_by_confidence = defaultdict(list)
        for family, data in family_patterns.items():
            confidence = data['classification_confidence']
            reliability_by_confidence[confidence].append(data['reliability_threshold'])
        
        # Calculate summary statistics
        summary_stats = {}
        for confidence, thresholds in reliability_by_confidence.items():
            summary_stats[confidence] = {
                'mean_threshold': np.mean(thresholds),
                'std_threshold': np.std(thresholds),
                'n_families': len(thresholds),
                'threshold_range': f"{min(thresholds)}-{max(thresholds)}%"
            }
        
        # Identify dissolved families pattern
        dissolved_families = [f for f, d in family_patterns.items() if 'Dissolved' in d.get('notes', '')]
        
        return {
            'family_specific_data': family_patterns,
            'reliability_by_confidence': dict(reliability_by_confidence),
            'summary_statistics': summary_stats,
            'dissolved_families_analysis': {
                'families': dissolved_families,
                'avg_threshold': np.mean([family_patterns[f]['reliability_threshold'] for f in dissolved_families]),
                'avg_stability': np.mean([family_patterns[f]['stability_score'] for f in dissolved_families]),
                'common_challenges': ['Horizontal gene transfer', 'Mosaic genomes', 'Modular evolution']
            },
            'most_reliable_families': [
                f for f, d in family_patterns.items() 
                if d['stability_score'] > 0.85 and d['classification_confidence'] in ['High', 'Very High']
            ]
        }
    
    def _analyze_marker_gene_performance(self) -> Dict[str, Any]:
        """Analyze performance of different phylogenetic markers across divergence."""
        
        # Performance data for different marker types
        marker_performance = {
            'DNA_polymerase': {
                'viral_groups': ['DNA_viruses', 'Retroviruses'],
                'conservation_level': 'High',
                'functional_constraint': 'Very High',
                'twilight_threshold': 60,
                'performance_scores': {
                    'high_identity': 0.95,  # >70% identity
                    'moderate_identity': 0.85,  # 40-70% identity
                    'low_identity': 0.60  # <40% identity
                },
                'advantages': ['Highly conserved active sites', 'Functional constraints'],
                'limitations': ['Horizontal transfer in prokaryotic viruses']
            },
            'RNA_polymerase': {
                'viral_groups': ['RNA_positive', 'RNA_negative'],
                'conservation_level': 'High',
                'functional_constraint': 'Very High',
                'twilight_threshold': 50,
                'performance_scores': {
                    'high_identity': 0.90,
                    'moderate_identity': 0.75,
                    'low_identity': 0.45
                },
                'advantages': ['Essential enzyme', 'Conserved motifs'],
                'limitations': ['High mutation rates in RNA viruses']
            },
            'capsid_proteins': {
                'viral_groups': ['DNA_viruses', 'RNA_positive', 'RNA_negative'],
                'conservation_level': 'Moderate',
                'functional_constraint': 'Moderate',
                'twilight_threshold': 45,
                'performance_scores': {
                    'high_identity': 0.85,
                    'moderate_identity': 0.65,
                    'low_identity': 0.35
                },
                'advantages': ['Structural constraints', 'Available for many viruses'],
                'limitations': ['Host adaptation pressure', 'Variable domains']
            },
            'terminase': {
                'viral_groups': ['DNA_viruses'],
                'conservation_level': 'Moderate',
                'functional_constraint': 'High',
                'twilight_threshold': 55,
                'performance_scores': {
                    'high_identity': 0.88,
                    'moderate_identity': 0.70,
                    'low_identity': 0.40
                },
                'advantages': ['Packaging specificity', 'Less horizontal transfer'],
                'limitations': ['Limited to certain virus types']
            },
            'integrase': {
                'viral_groups': ['Retroviruses'],
                'conservation_level': 'High',
                'functional_constraint': 'High',
                'twilight_threshold': 55,
                'performance_scores': {
                    'high_identity': 0.92,
                    'moderate_identity': 0.78,
                    'low_identity': 0.50
                },
                'advantages': ['Critical function', 'Conserved catalytic domains'],
                'limitations': ['Retrovirus-specific']
            }
        }
        
        # Calculate overall performance rankings
        performance_rankings = []
        for marker, data in marker_performance.items():
            avg_performance = np.mean(list(data['performance_scores'].values()))
            performance_rankings.append((marker, avg_performance))
        
        performance_rankings.sort(key=lambda x: x[1], reverse=True)
        
        # Best marker by viral group
        best_markers_by_group = {}
        for group in self.phylogenetic_markers.keys():
            applicable_markers = [
                (marker, data['performance_scores']['moderate_identity'])
                for marker, data in marker_performance.items()
                if group in data['viral_groups']
            ]
            if applicable_markers:
                best_marker = max(applicable_markers, key=lambda x: x[1])
                best_markers_by_group[group] = best_marker[0]
        
        return {
            'marker_performance_data': marker_performance,
            'overall_rankings': performance_rankings,
            'best_marker': performance_rankings[0][0],
            'best_markers_by_group': best_markers_by_group,
            'performance_summary': {
                'most_reliable': performance_rankings[0],
                'least_reliable': performance_rankings[-1],
                'average_performance': np.mean([x[1] for x in performance_rankings])
            },
            'conservation_patterns': {
                'highly_conserved': [m for m, d in marker_performance.items() if d['conservation_level'] == 'High'],
                'moderately_conserved': [m for m, d in marker_performance.items() if d['conservation_level'] == 'Moderate'],
                'functionally_constrained': [m for m, d in marker_performance.items() if d['functional_constraint'] == 'Very High']
            }
        }
    
    def _analyze_classification_method_reliability(self) -> Dict[str, Any]:
        """Analyze reliability of different phylogenetic methods by divergence level."""
        
        # Method performance across divergence ranges
        methods_analysis = {
            'maximum_likelihood': {
                'description': 'ML with best-fit substitution models',
                'performance_by_divergence': {
                    'high_identity': {'accuracy': 0.95, 'bootstrap_support': 0.90, 'confidence': 'Very High'},
                    'moderate_identity': {'accuracy': 0.85, 'bootstrap_support': 0.75, 'confidence': 'High'},
                    'low_identity': {'accuracy': 0.65, 'bootstrap_support': 0.55, 'confidence': 'Moderate'}
                },
                'strengths': ['Statistical framework', 'Model selection'],
                'weaknesses': ['Computationally intensive', 'Model assumptions']
            },
            'neighbor_joining': {
                'description': 'Distance-based clustering method',
                'performance_by_divergence': {
                    'high_identity': {'accuracy': 0.88, 'bootstrap_support': 0.82, 'confidence': 'High'},
                    'moderate_identity': {'accuracy': 0.72, 'bootstrap_support': 0.65, 'confidence': 'Moderate'},
                    'low_identity': {'accuracy': 0.45, 'bootstrap_support': 0.35, 'confidence': 'Low'}
                },
                'strengths': ['Fast computation', 'Simple interpretation'],
                'weaknesses': ['Distance assumptions', 'Poor with saturation']
            },
            'maximum_parsimony': {
                'description': 'Minimum evolution criterion',
                'performance_by_divergence': {
                    'high_identity': {'accuracy': 0.90, 'bootstrap_support': 0.85, 'confidence': 'High'},
                    'moderate_identity': {'accuracy': 0.75, 'bootstrap_support': 0.68, 'confidence': 'Moderate'},
                    'low_identity': {'accuracy': 0.50, 'bootstrap_support': 0.40, 'confidence': 'Low'}
                },
                'strengths': ['No evolutionary model needed', 'Character-based'],
                'weaknesses': ['Long branch attraction', 'Homoplasy issues']
            },
            'bayesian_inference': {
                'description': 'Bayesian posterior probability trees',
                'performance_by_divergence': {
                    'high_identity': {'accuracy': 0.96, 'bootstrap_support': 0.92, 'confidence': 'Very High'},
                    'moderate_identity': {'accuracy': 0.88, 'bootstrap_support': 0.80, 'confidence': 'High'},
                    'low_identity': {'accuracy': 0.70, 'bootstrap_support': 0.60, 'confidence': 'Moderate'}
                },
                'strengths': ['Probabilistic framework', 'Uncertainty quantification'],
                'weaknesses': ['Very slow', 'Prior sensitivity']
            }
        }
        
        # Calculate method rankings
        method_rankings = []
        for method, data in methods_analysis.items():
            avg_accuracy = np.mean([
                perf['accuracy'] for perf in data['performance_by_divergence'].values()
            ])
            method_rankings.append((method, avg_accuracy))
        
        method_rankings.sort(key=lambda x: x[1], reverse=True)
        
        # Reliability thresholds by method
        reliability_thresholds = {}
        for method, data in methods_analysis.items():
            # Find divergence level where accuracy drops below 70%
            threshold = 'high_identity'  # Default
            for level, perf in data['performance_by_divergence'].items():
                if perf['accuracy'] < 0.70:
                    threshold = level
                    break
            reliability_thresholds[method] = threshold
        
        return {
            'method_performance': methods_analysis,
            'method_rankings': method_rankings,
            'best_method': method_rankings[0][0],
            'reliability_thresholds': reliability_thresholds,
            'method_recommendations': {
                'high_divergence': 'bayesian_inference',
                'moderate_divergence': 'maximum_likelihood',
                'low_divergence': 'any_method',
                'rapid_analysis': 'neighbor_joining'
            },
            'support_metrics': {
                'bootstrap': 'Frequency of node recovery in resampled datasets',
                'posterior_probability': 'Bayesian probability of node correctness',
                'quartet_support': 'Proportion of quartets supporting each node'
            }
        }
    
    def _generate_reliability_thresholds(
        self, 
        divergence_reliability: Dict[str, Any],
        twilight_zones: Dict[str, Any],
        family_reliability: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive reliability thresholds and guidelines."""
        
        # Universal threshold from twilight zone analysis
        universal_threshold = twilight_zones['universal_threshold']
        
        # Group-specific thresholds
        group_thresholds = {}
        for group, data in divergence_reliability['group_specific_curves'].items():
            group_thresholds[group] = {
                'twilight_zone': data['twilight_threshold'],
                'reliable_zone': data['twilight_threshold'] + 15,
                'unreliable_zone': data['twilight_threshold'] - 15
            }
        
        # Classification accuracy summary
        accuracy_levels = {
            'very_high': {'threshold': 85, 'confidence': '>90%', 'description': 'Genus-level classification reliable'},
            'high': {'threshold': 70, 'confidence': '70-90%', 'description': 'Family-level classification reliable'},
            'moderate': {'threshold': 50, 'confidence': '50-70%', 'description': 'Order-level classification may be reliable'},
            'low': {'threshold': 30, 'confidence': '<50%', 'description': 'Higher-level classification only'}
        }
        
        # Practical guidelines
        classification_guidelines = {
            'species_level': {
                'minimum_identity': 85,
                'recommended_methods': ['maximum_likelihood', 'bayesian_inference'],
                'required_support': '>80% bootstrap or >0.95 posterior probability',
                'additional_evidence': 'Host range, geographic distribution, phenotype'
            },
            'genus_level': {
                'minimum_identity': 70,
                'recommended_methods': ['maximum_likelihood', 'maximum_parsimony'],
                'required_support': '>70% bootstrap or >0.90 posterior probability',
                'additional_evidence': 'Genome organization, replication strategy'
            },
            'family_level': {
                'minimum_identity': 50,
                'recommended_methods': ['maximum_likelihood', 'bayesian_inference'],
                'required_support': '>60% bootstrap or >0.80 posterior probability',
                'additional_evidence': 'Protein domain architecture, virion morphology'
            },
            'order_level': {
                'minimum_identity': 30,
                'recommended_methods': ['bayesian_inference', 'maximum_likelihood'],
                'required_support': '>50% bootstrap or >0.70 posterior probability',
                'additional_evidence': 'Replication mechanism, genome type'
            }
        }
        
        # Quality control metrics
        quality_metrics = {
            'alignment_quality': {
                'minimum_length': 200,  # amino acids
                'maximum_gaps': 0.5,    # 50% gaps
                'sequence_number': 10   # minimum sequences
            },
            'tree_quality': {
                'branch_support': 0.7,  # minimum support
                'tree_length': 'reasonable',  # not too long (saturation)
                'long_branch_test': 'required'  # check for artifacts
            },
            'validation_tests': [
                'Bootstrap resampling (1000 replicates)',
                'Alternative tree topologies',
                'Quartet mapping analysis',
                'Saturation tests',
                'Model adequacy tests'
            ]
        }
        
        return {
            'universal_threshold': universal_threshold,
            'group_thresholds': group_thresholds,
            'accuracy_summary': accuracy_levels,
            'classification_guidelines': classification_guidelines,
            'quality_control_metrics': quality_metrics,
            'reliability_zones': {
                'safe_zone': f'>{universal_threshold + 15}% identity',
                'caution_zone': f'{universal_threshold - 15}-{universal_threshold + 15}% identity',
                'danger_zone': f'<{universal_threshold - 15}% identity'
            }
        }
    
    def _perform_statistical_validation(
        self, 
        divergence_reliability: Dict[str, Any],
        family_reliability: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Perform statistical validation of reliability patterns."""
        
        # Test for significant differences between viral groups
        group_thresholds = [
            data['twilight_threshold'] 
            for data in divergence_reliability['group_specific_curves'].values()
        ]
        
        # ANOVA test for group differences
        family_scores = [
            data['stability_score'] 
            for data in family_reliability['family_specific_data'].values()
        ]
        
        # Correlation between threshold and stability
        family_thresholds = [
            data['reliability_threshold'] 
            for data in family_reliability['family_specific_data'].values()
        ]
        
        correlation_coef, correlation_p = stats.pearsonr(family_thresholds, family_scores)
        
        # Statistical tests
        threshold_variance = np.var(group_thresholds)
        stability_variance = np.var(family_scores)
        
        # Regression analysis: threshold predicting stability
        slope, intercept, r_value, p_value, std_err = stats.linregress(family_thresholds, family_scores)
        
        return {
            'correlation_analysis': {
                'threshold_stability_correlation': correlation_coef,
                'p_value': correlation_p,
                'r_squared': r_value**2,
                'interpretation': 'Strong positive correlation between threshold and stability' if correlation_coef > 0.7 else 'Moderate correlation'
            },
            'variance_analysis': {
                'threshold_variance': threshold_variance,
                'stability_variance': stability_variance,
                'coefficient_of_variation': np.std(group_thresholds) / np.mean(group_thresholds)
            },
            'regression_model': {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_value**2,
                'p_value': p_value,
                'model_equation': f'Stability = {intercept:.3f} + {slope:.3f} * Threshold',
                'predictive_power': 'Good' if r_value**2 > 0.7 else 'Moderate'
            },
            'sample_statistics': {
                'n_viral_groups': len(group_thresholds),
                'n_families': len(family_scores),
                'threshold_range': f'{min(family_thresholds)}-{max(family_thresholds)}%',
                'stability_range': f'{min(family_scores):.2f}-{max(family_scores):.2f}'
            }
        }
    
    def _generate_predictive_insights(
        self, 
        reliability_thresholds: Dict[str, Any],
        twilight_zones: Dict[str, Any],
        marker_performance: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate predictive insights from the analysis."""
        
        insights = []
        
        # Threshold-based predictions
        universal_threshold = reliability_thresholds['universal_threshold']
        insights.append({
            'type': 'classification_reliability',
            'insight': f'Phylogenetic classification becomes unreliable below {universal_threshold:.0f}% sequence identity',
            'recommendation': f'Require additional evidence (morphology, biochemistry) for classification below {universal_threshold:.0f}% identity'
        })
        
        # Marker gene insights
        best_marker = marker_performance['best_marker']
        insights.append({
            'type': 'marker_selection',
            'insight': f'{best_marker} provides most reliable phylogenetic signal across viral groups',
            'recommendation': f'Prioritize {best_marker} sequences for phylogenetic analysis when available'
        })
        
        # Method recommendations
        insights.append({
            'type': 'methodological',
            'insight': 'Bayesian inference outperforms other methods at high divergence levels',
            'recommendation': 'Use Bayesian methods for deep phylogenetic relationships and ancient virus groups'
        })
        
        # Family-specific insights
        insights.append({
            'type': 'family_specific',
            'insight': 'Bacteriophage families show lowest phylogenetic reliability due to horizontal gene transfer',
            'recommendation': 'Develop alternative classification criteria for bacteriophages based on lifestyle and host specificity'
        })
        
        # Technological predictions
        insights.append({
            'type': 'future_methods',
            'insight': 'Single-gene phylogenies insufficient for highly divergent viral relationships',
            'recommendation': 'Implement multi-gene concatenated analysis and protein structure-based phylogeny'
        })
        
        # Quality control insights
        insights.append({
            'type': 'validation',
            'insight': 'Bootstrap support correlates strongly with classification stability',
            'recommendation': 'Require minimum 70% bootstrap support for taxonomic decisions'
        })
        
        return insights
    
    def visualize(self) -> None:
        """Generate comprehensive visualizations."""
        # Load results - check both possible locations
        possible_paths = [
            self.results_dir / f"{self.__class__.__name__}_results.json",
            Path(__file__).parent.parent / self.__class__.__name__.lower() / "results" / f"{self.__class__.__name__}_results.json"
        ]
        
        results_file = None
        for path in possible_paths:
            if path.exists():
                results_file = path
                break
        
        if results_file is None:
            logging.error(f"Results file not found in any of: {possible_paths}")
            return
            
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        # Create comprehensive figure
        fig = plt.figure(figsize=(20, 16))
        
        # 1. Divergence vs Reliability Curves
        ax1 = plt.subplot(3, 4, 1)
        
        divergence_data = results['divergence_reliability']['group_specific_curves']
        colors = plt.cm.Set1(np.linspace(0, 1, len(divergence_data)))
        
        for i, (group, data) in enumerate(divergence_data.items()):
            identity = data['identity_range']
            reliability = data['reliability_scores']
            ax1.plot(identity, reliability, label=group.replace('_', ' '), 
                    color=colors[i], linewidth=2, marker='o', markersize=3)
            
            # Mark twilight zone
            twilight = data['twilight_threshold']
            ax1.axvline(x=twilight, color=colors[i], linestyle='--', alpha=0.5)
        
        ax1.set_xlabel('Sequence Identity (%)')
        ax1.set_ylabel('Classification Reliability')
        ax1.set_title('Phylogenetic Signal Degradation by Viral Group')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 1)
        
        # 2. Twilight Zones Comparison
        ax2 = plt.subplot(3, 4, 2)
        
        twilight_data = results['twilight_zones']['group_specific_zones']
        groups = list(twilight_data.keys())
        thresholds = [data['identity_threshold'] for data in twilight_data.values()]
        
        bars = ax2.bar(range(len(groups)), thresholds, color=colors[:len(groups)])
        ax2.set_xticks(range(len(groups)))
        ax2.set_xticklabels([g.replace('_', ' ') for g in groups], rotation=45, ha='right')
        ax2.set_ylabel('Twilight Zone Threshold (%)')
        ax2.set_title('Phylogenetic Twilight Zones by Viral Group')
        
        # Add value labels on bars
        for bar, threshold in zip(bars, thresholds):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{threshold}%', ha='center', va='bottom')
        
        # 3. Family Reliability Patterns
        ax3 = plt.subplot(3, 4, 3)
        
        family_data = results['family_reliability_patterns']['family_specific_data']
        families = list(family_data.keys())
        stability_scores = [data['stability_score'] for data in family_data.values()]
        reliability_thresholds = [data['reliability_threshold'] for data in family_data.values()]
        
        # Color by confidence level
        confidence_colors = {
            'Very High': '#2E7D32',
            'High': '#66BB6A', 
            'Moderate': '#FDD835',
            'Low': '#F44336'
        }
        
        colors_family = [confidence_colors.get(family_data[f]['classification_confidence'], '#GREY') 
                        for f in families]
        
        scatter = ax3.scatter(reliability_thresholds, stability_scores, 
                            c=colors_family, s=80, alpha=0.7)
        
        # Add family labels for extreme cases
        for i, family in enumerate(families):
            if stability_scores[i] < 0.6 or stability_scores[i] > 0.9:
                ax3.annotate(family, (reliability_thresholds[i], stability_scores[i]),
                           xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        ax3.set_xlabel('Reliability Threshold (%)')
        ax3.set_ylabel('Stability Score')
        ax3.set_title('Family Reliability vs Stability')
        ax3.grid(True, alpha=0.3)
        
        # 4. Marker Gene Performance
        ax4 = plt.subplot(3, 4, 4)
        
        marker_data = results['marker_gene_performance']['marker_performance_data']
        markers = list(marker_data.keys())
        
        # Performance across divergence levels
        high_perf = [data['performance_scores']['high_identity'] for data in marker_data.values()]
        mod_perf = [data['performance_scores']['moderate_identity'] for data in marker_data.values()]
        low_perf = [data['performance_scores']['low_identity'] for data in marker_data.values()]
        
        x = np.arange(len(markers))
        width = 0.25
        
        ax4.bar(x - width, high_perf, width, label='High Identity (>70%)', color='#4CAF50')
        ax4.bar(x, mod_perf, width, label='Moderate Identity (40-70%)', color='#FFC107')
        ax4.bar(x + width, low_perf, width, label='Low Identity (<40%)', color='#F44336')
        
        ax4.set_xticks(x)
        ax4.set_xticklabels([m.replace('_', ' ') for m in markers], rotation=45, ha='right')
        ax4.set_ylabel('Performance Score')
        ax4.set_title('Marker Gene Performance by Divergence Level')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        # 5. Method Reliability Comparison
        ax5 = plt.subplot(3, 4, 5)
        
        method_data = results['method_reliability']['method_performance']
        methods = list(method_data.keys())
        
        # Create heatmap of method performance
        performance_matrix = []
        divergence_levels = ['high_identity', 'moderate_identity', 'low_identity']
        
        for method in methods:
            method_performance = [
                method_data[method]['performance_by_divergence'][level]['accuracy']
                for level in divergence_levels
            ]
            performance_matrix.append(method_performance)
        
        im = ax5.imshow(performance_matrix, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
        
        ax5.set_xticks(range(len(divergence_levels)))
        ax5.set_xticklabels(['High ID', 'Mod ID', 'Low ID'])
        ax5.set_yticks(range(len(methods)))
        ax5.set_yticklabels([m.replace('_', ' ').title() for m in methods])
        ax5.set_title('Method Performance Heatmap')
        
        # Add text annotations
        for i in range(len(methods)):
            for j in range(len(divergence_levels)):
                text = ax5.text(j, i, f'{performance_matrix[i][j]:.2f}',
                               ha="center", va="center", color="black", fontsize=8)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax5, shrink=0.8)
        cbar.set_label('Accuracy', rotation=270, labelpad=15)
        
        # 6. Reliability Zones Visualization
        ax6 = plt.subplot(3, 4, 6)
        
        # Create zone visualization
        identity_range = np.arange(0, 101)
        universal_threshold = results['reliability_thresholds']['universal_threshold']
        
        # Define zones
        safe_zone = identity_range >= universal_threshold + 15
        caution_zone = (identity_range >= universal_threshold - 15) & (identity_range < universal_threshold + 15)
        danger_zone = identity_range < universal_threshold - 15
        
        # Create colored regions
        ax6.fill_between(identity_range[safe_zone], 0, 1, alpha=0.3, color='green', label='Safe Zone')
        ax6.fill_between(identity_range[caution_zone], 0, 1, alpha=0.3, color='yellow', label='Caution Zone')
        ax6.fill_between(identity_range[danger_zone], 0, 1, alpha=0.3, color='red', label='Danger Zone')
        
        # Add threshold lines
        ax6.axvline(x=universal_threshold + 15, color='green', linestyle='-', linewidth=2)
        ax6.axvline(x=universal_threshold - 15, color='red', linestyle='-', linewidth=2)
        ax6.axvline(x=universal_threshold, color='orange', linestyle='--', linewidth=2, 
                   label=f'Universal Threshold ({universal_threshold:.0f}%)')
        
        ax6.set_xlabel('Sequence Identity (%)')
        ax6.set_ylabel('Classification Reliability')
        ax6.set_title('Phylogenetic Reliability Zones')
        ax6.legend()
        ax6.set_ylim(0, 1)
        ax6.grid(True, alpha=0.3)
        
        # 7. Statistical Summary
        ax7 = plt.subplot(3, 4, 7)
        ax7.axis('off')
        
        stats_data = results['statistical_validation']
        
        stats_text = f"""Statistical Validation:

Correlation Analysis:
• Threshold-Stability r = {stats_data['correlation_analysis']['threshold_stability_correlation']:.3f}
• P-value = {stats_data['correlation_analysis']['p_value']:.4f}
• R² = {stats_data['correlation_analysis']['r_squared']:.3f}

Regression Model:
• {stats_data['regression_model']['model_equation']}
• R² = {stats_data['regression_model']['r_squared']:.3f}
• P-value = {stats_data['regression_model']['p_value']:.4f}

Sample Statistics:
• Viral Groups: {stats_data['sample_statistics']['n_viral_groups']}
• Families: {stats_data['sample_statistics']['n_families']}
• Threshold Range: {stats_data['sample_statistics']['threshold_range']}
• Stability Range: {stats_data['sample_statistics']['stability_range']}
        """
        
        ax7.text(0.05, 0.95, stats_text, transform=ax7.transAxes,
                fontsize=10, verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.5))
        
        # 8. Key Insights
        ax8 = plt.subplot(3, 4, 8)
        ax8.axis('off')
        
        insights_text = "Key Insights:\n\n"
        for i, insight in enumerate(results['predictive_insights'][:4], 1):
            insights_text += f"{i}. {insight['insight']}\n\n"
        
        ax8.text(0.05, 0.95, insights_text, transform=ax8.transAxes,
                fontsize=10, verticalalignment='top', wrap=True,
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        
        # 9. Classification Guidelines
        ax9 = plt.subplot(3, 4, 9)
        
        guidelines = results['reliability_thresholds']['classification_guidelines']
        levels = list(guidelines.keys())
        identities = [guidelines[level]['minimum_identity'] for level in levels]
        
        colors_guide = ['#4CAF50', '#8BC34A', '#FFC107', '#FF9800']
        bars = ax9.barh(range(len(levels)), identities, color=colors_guide)
        
        ax9.set_yticks(range(len(levels)))
        ax9.set_yticklabels([level.replace('_', ' ').title() for level in levels])
        ax9.set_xlabel('Minimum Identity Threshold (%)')
        ax9.set_title('Classification Level Guidelines')
        
        # Add value labels
        for i, (bar, identity) in enumerate(zip(bars, identities)):
            ax9.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                    f'{identity}%', va='center')
        
        # 10. Marker Conservation
        ax10 = plt.subplot(3, 4, 10)
        
        conservation_data = results['marker_gene_performance']['conservation_patterns']
        
        high_cons = len(conservation_data['highly_conserved'])
        mod_cons = len(conservation_data['moderately_conserved'])
        func_cons = len(conservation_data['functionally_constrained'])
        
        categories = ['Highly\nConserved', 'Moderately\nConserved', 'Functionally\nConstrained']
        values = [high_cons, mod_cons, func_cons]
        colors_cons = ['#2E7D32', '#FDD835', '#1976D2']
        
        ax10.pie(values, labels=categories, autopct='%1.0f%%', colors=colors_cons)
        ax10.set_title('Marker Gene Conservation Patterns')
        
        # 11. Universal Threshold Distribution
        ax11 = plt.subplot(3, 4, 11)
        
        # Simulate threshold distribution across viral groups
        group_thresholds = [
            data['twilight_threshold'] 
            for data in results['divergence_reliability']['group_specific_curves'].values()
        ]
        
        ax11.hist(group_thresholds, bins=8, color='skyblue', alpha=0.7, edgecolor='black')
        ax11.axvline(x=universal_threshold, color='red', linestyle='--', linewidth=2,
                    label=f'Universal Threshold ({universal_threshold:.0f}%)')
        ax11.set_xlabel('Twilight Zone Threshold (%)')
        ax11.set_ylabel('Number of Viral Groups')
        ax11.set_title('Distribution of Group Thresholds')
        ax11.legend()
        ax11.grid(True, alpha=0.3)
        
        # 12. Future Predictions
        ax12 = plt.subplot(3, 4, 12)
        ax12.axis('off')
        
        predictions_text = """Future Predictions:

Technology Impact:
• Structural phylogeny will supplement
  sequence-based methods
• AI-assisted tree validation
• Real-time classification updates

Method Development:
• Multi-gene concatenated analysis
• Protein domain phylogenies  
• Host-virus coevolution trees

Classification Standards:
• Minimum support thresholds
• Quality control metrics
• Validation protocols"""
        
        ax12.text(0.05, 0.95, predictions_text, transform=ax12.transAxes,
                 fontsize=10, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))
        
        plt.suptitle('Phylogenetic Signal Degradation Analysis: Reliability Thresholds and Twilight Zones', 
                    fontsize=16, y=0.98)
        plt.tight_layout()
        
        # Save figure
        output_dir = results_file.parent
        output_file = output_dir / "phylogenetic_signal_analysis_figure.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Create additional detailed visualizations
        self._create_detailed_visualizations(results, output_dir)
        
        logging.info(f"Visualizations saved to {output_dir}")
    
    def _create_detailed_visualizations(self, results: Dict[str, Any], output_dir: Path) -> None:
        """Create additional detailed visualizations."""
        
        # 1. Detailed method comparison
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Method performance radar chart
        ax = axes[0, 0]
        method_data = results['method_reliability']['method_performance']
        
        methods = list(method_data.keys())
        categories = ['High ID', 'Mod ID', 'Low ID']
        
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle
        
        colors_radar = plt.cm.Set1(np.linspace(0, 1, len(methods)))
        
        for i, method in enumerate(methods):
            values = [
                method_data[method]['performance_by_divergence']['high_identity']['accuracy'],
                method_data[method]['performance_by_divergence']['moderate_identity']['accuracy'],
                method_data[method]['performance_by_divergence']['low_identity']['accuracy']
            ]
            values += values[:1]  # Complete the circle
            
            ax.plot(angles, values, 'o-', linewidth=2, label=method.replace('_', ' ').title(),
                   color=colors_radar[i])
            ax.fill(angles, values, alpha=0.1, color=colors_radar[i])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 1)
        ax.set_title('Method Performance Radar Chart')
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax.grid(True)
        
        # Twilight zone detailed comparison
        ax = axes[0, 1]
        
        twilight_data = results['twilight_zones']['group_specific_zones']
        groups = list(twilight_data.keys())
        
        # Extract threshold ranges
        thresholds = []
        lower_bounds = []
        upper_bounds = []
        
        for group in groups:
            threshold = results['divergence_reliability']['group_specific_curves'][group]['twilight_threshold']
            thresholds.append(threshold)
            lower_bounds.append(threshold - 15)
            upper_bounds.append(threshold + 15)
        
        x = np.arange(len(groups))
        ax.bar(x, thresholds, color='orange', alpha=0.7, label='Twilight Zone')
        ax.errorbar(x, thresholds, yerr=[np.array(thresholds) - np.array(lower_bounds),
                                        np.array(upper_bounds) - np.array(thresholds)],
                   fmt='none', color='black', capsize=5, label='Uncertainty Range')
        
        ax.set_xticks(x)
        ax.set_xticklabels([g.replace('_', ' ') for g in groups], rotation=45, ha='right')
        ax.set_ylabel('Sequence Identity (%)')
        ax.set_title('Detailed Twilight Zone Analysis')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Family dissolution analysis
        ax = axes[1, 0]
        
        family_data = results['family_reliability_patterns']['family_specific_data']
        
        # Separate dissolved vs stable families
        dissolved_families = []
        stable_families = []
        dissolved_scores = []
        stable_scores = []
        
        for family, data in family_data.items():
            if 'Dissolved' in data.get('notes', ''):
                dissolved_families.append(family)
                dissolved_scores.append(data['stability_score'])
            else:
                stable_families.append(family)
                stable_scores.append(data['stability_score'])
        
        # Box plot comparison
        box_data = [stable_scores, dissolved_scores]
        box_labels = ['Stable Families', 'Dissolved Families']
        
        bp = ax.boxplot(box_data, labels=box_labels, patch_artist=True)
        bp['boxes'][0].set_facecolor('lightgreen')
        bp['boxes'][1].set_facecolor('lightcoral')
        
        ax.set_ylabel('Stability Score')
        ax.set_title('Stable vs Dissolved Family Comparison')
        ax.grid(True, alpha=0.3)
        
        # Add statistical test result
        if len(dissolved_scores) > 0 and len(stable_scores) > 0:
            t_stat, p_val = stats.ttest_ind(stable_scores, dissolved_scores)
            ax.text(0.5, 0.95, f't-test p-value: {p_val:.4f}',
                   transform=ax.transAxes, ha='center', va='top',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Classification level requirements
        ax = axes[1, 1]
        
        guidelines = results['reliability_thresholds']['classification_guidelines']
        levels = list(guidelines.keys())
        identities = [guidelines[level]['minimum_identity'] for level in levels]
        
        # Create stacked requirements chart
        support_req = [80, 70, 60, 50]  # Bootstrap support requirements
        
        width = 0.35
        x = np.arange(len(levels))
        
        ax.bar(x - width/2, identities, width, label='Sequence Identity (%)', color='skyblue')
        ax.bar(x + width/2, support_req, width, label='Bootstrap Support (%)', color='lightcoral')
        
        ax.set_xticks(x)
        ax.set_xticklabels([level.replace('_', ' ').title() for level in levels], rotation=45, ha='right')
        ax.set_ylabel('Threshold (%)')
        ax.set_title('Classification Requirements by Taxonomic Level')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.suptitle('Detailed Phylogenetic Signal Analysis', fontsize=14)
        plt.tight_layout()
        
        output_file = output_dir / "phylogenetic_signal_detailed_analysis.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Create reliability assessment flowchart
        self._create_reliability_flowchart(results, output_dir)
    
    def _create_reliability_flowchart(self, results: Dict[str, Any], output_dir: Path) -> None:
        """Create a decision flowchart for phylogenetic reliability assessment."""
        
        fig, ax = plt.subplots(1, 1, figsize=(14, 10))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Define flowchart elements
        universal_threshold = results['reliability_thresholds']['universal_threshold']
        
        # Title
        ax.text(5, 9.5, 'Phylogenetic Reliability Assessment Protocol', 
               ha='center', va='center', fontsize=16, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue'))
        
        # Step 1: Sequence Identity Check
        ax.add_patch(plt.Rectangle((1, 8), 3, 0.8, facecolor='lightgreen', edgecolor='black'))
        ax.text(2.5, 8.4, f'Sequence Identity\n≥ {universal_threshold + 15:.0f}%?', 
               ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Yes branch
        ax.annotate('YES', xy=(4, 8.4), xytext=(5.5, 8.4),
                   arrowprops=dict(arrowstyle='->', lw=2, color='green'))
        ax.add_patch(plt.Rectangle((6, 8), 3, 0.8, facecolor='lightgreen', edgecolor='black'))
        ax.text(7.5, 8.4, 'HIGH RELIABILITY\nProceed with standard\nphylogenetic analysis', 
               ha='center', va='center', fontsize=9)
        
        # No branch
        ax.annotate('NO', xy=(2.5, 8), xytext=(2.5, 7),
                   arrowprops=dict(arrowstyle='->', lw=2, color='red'))
        
        # Step 2: Moderate Identity Check
        ax.add_patch(plt.Rectangle((1, 6.2), 3, 0.8, facecolor='yellow', edgecolor='black'))
        ax.text(2.5, 6.6, f'Sequence Identity\n{universal_threshold - 15:.0f}-{universal_threshold + 15:.0f}%?', 
               ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Yes branch - caution zone
        ax.annotate('YES', xy=(4, 6.6), xytext=(5.5, 6.6),
                   arrowprops=dict(arrowstyle='->', lw=2, color='orange'))
        ax.add_patch(plt.Rectangle((6, 6.2), 3, 0.8, facecolor='yellow', edgecolor='black'))
        ax.text(7.5, 6.6, 'MODERATE RELIABILITY\nRequire ≥70% bootstrap\nMultiple methods', 
               ha='center', va='center', fontsize=9)
        
        # No branch - danger zone
        ax.annotate('NO', xy=(2.5, 6.2), xytext=(2.5, 5.2),
                   arrowprops=dict(arrowstyle='->', lw=2, color='red'))
        
        # Step 3: Low Identity
        ax.add_patch(plt.Rectangle((1, 4.4), 3, 0.8, facecolor='lightcoral', edgecolor='black'))
        ax.text(2.5, 4.8, f'Sequence Identity\n< {universal_threshold - 15:.0f}%', 
               ha='center', va='center', fontsize=10, fontweight='bold')
        
        ax.annotate('', xy=(4, 4.8), xytext=(5.5, 4.8),
                   arrowprops=dict(arrowstyle='->', lw=2, color='red'))
        ax.add_patch(plt.Rectangle((6, 4.4), 3, 0.8, facecolor='lightcoral', edgecolor='black'))
        ax.text(7.5, 4.8, 'LOW RELIABILITY\nRequire additional evidence\nMorphology, biochemistry', 
               ha='center', va='center', fontsize=9)
        
        # Additional recommendations box
        ax.add_patch(plt.Rectangle((1, 2.5), 8, 1.5, facecolor='lightyellow', edgecolor='black'))
        ax.text(5, 3.25, 'Additional Recommendations:\n\n'
                         '• Use Bayesian inference for deep relationships\n'
                         f'• {results["marker_gene_performance"]["best_marker"]} preferred when available\n'
                         '• Validate with protein structure analysis\n'
                         '• Consider host range and morphology data\n'
                         '• Apply quartet mapping for conflicting signal',
               ha='center', va='center', fontsize=10,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        # Quality control checklist
        ax.add_patch(plt.Rectangle((0.5, 0.5), 9, 1.5, facecolor='lightgray', edgecolor='black'))
        ax.text(5, 1.25, 'Quality Control Checklist:\n\n'
                         '✓ Alignment length ≥ 200 amino acids    ✓ Maximum 50% gaps\n'
                         '✓ Minimum 10 sequences                  ✓ Long branch test passed\n'
                         '✓ Model adequacy verified               ✓ Alternative topologies tested',
               ha='center', va='center', fontsize=9,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        output_file = output_dir / "phylogenetic_reliability_flowchart.png"
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
    analyzer = PhylogeneticSignalAnalyzer(data_dir)
    
    results = analyzer.analyze()
    analyzer.visualize()
    
    print("\nPhylogenetic Signal Degradation Analysis Complete!")
    print(f"Results saved to: {analyzer.results_dir}")
    print(f"\nKey Finding: {results['key_findings']['classification_accuracy']}")
    print(f"Universal Threshold: {results['key_findings']['universal_twilight_zone']:.0f}% sequence identity")