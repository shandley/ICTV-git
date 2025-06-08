# Viral Taxonomy Research Applications for ICTV Git Repository

## Overview
Once the core ICTV git-based taxonomy system is established, the rich temporal dataset opens up numerous research opportunities to understand fundamental aspects of viral evolution, classification, and taxonomy. These applications leverage the complete historical record of taxonomic decisions with full provenance tracking.

## Core Viral Classification Concepts

### 1. Viral Species Boundary Evolution
Track how species demarcation criteria have changed over time:
```python
# How have pairwise identity thresholds evolved?
species_boundaries = analyze_historical_thresholds(
    picornaviruses={'1990': '70% AA identity', '2010': '88% AA identity', '2020': 'phylogenetic + host range'},
    coronaviruses={'2003': 'serology + morphology', '2020': 'RdRp phylogeny + spike protein'},
    bacteriophages={'2019': 'morphology-based', '2022': 'genome-wide ANI > 95%'}
)
# Prediction: Which virus families will adopt phylogenetic species concepts next?
```

**Research Questions:**
- How have molecular thresholds for species boundaries evolved across different virus families?
- Which families are transitioning from phenotypic to phylogenetic species concepts?
- Can we predict which families will require species boundary revisions based on accumulating sequence data?

### 2. Horizontal Gene Transfer Impact on Classification
```python
# Which viral families are most affected by recombination/reassortment?
hgt_instability = correlate_recombination_with_reclassification(
    high_recombination_families=['Picornaviridae', 'Orthomyxoviridae'],
    classification_stability_scores=frequency_of_taxonomic_changes
)
# Insight: Segmented RNA viruses require different classification approaches
```

**Research Questions:**
- Do virus families with higher recombination rates get reclassified more frequently?
- How do segmented genomes affect taxonomic stability compared to non-segmented genomes?
- Can we identify "recombination hotspots" that consistently cause classification problems?

### 3. Host Range Evolution and Taxonomic Stability
```python
# Do broad host range viruses get reclassified more often?
host_range_analysis = analyze_host_breadth_vs_taxonomy_changes(
    narrow_host_viruses=plant_specific_families,
    broad_host_viruses=arthropod_borne_families,
    reclassification_frequency=msl_change_tracking
)
# Finding: Viruses with expanding host ranges destabilize genus boundaries
```

**Research Questions:**
- Are generalist viruses (broad host range) taxonomically less stable than specialists?
- How does host jumping correlate with taxonomic reclassification events?
- Can host range evolution predict future taxonomic instability?

## Genome Architecture and Evolution

### 4. Genome Architecture Constraints on Classification
```python
# How do different genome types affect taxonomic decisions?
genome_constraints = analyze_classification_by_genome_type(
    segmented_genomes={'splits_common': True, 'reason': 'reassortment_creates_new_combinations'},
    circular_ssDNA={'ancient_splits': True, 'reason': 'deep_phylogenetic_divergence'},
    linear_dsDNA={'morphology_important': True, 'reason': 'capsid_structure_conserved'}
)
```

**Research Questions:**
- Do different genome architectures require different classification approaches?
- How do genome size constraints affect family-level organization?
- Are circular genomes taxonomically more stable than linear genomes?

### 5. Functional Domain Architecture and Taxonomy
```python
# Do viruses with similar protein domain arrangements belong together?
domain_architecture_analysis = correlate_protein_domains_with_classification(
    conserved_domain_patterns={'RNA_helicase + RdRp': 'order_level_marker'},
    domain_rearrangements={'gene_order_changes': 'family_splitting_trigger'},
    domain_acquisitions={'new_domains': 'species_boundary_expansion'}
)
```

**Research Questions:**
- Which protein domains are most informative for different taxonomic ranks?
- How do domain rearrangements correlate with taxonomic revisions?
- Can domain architecture predict optimal taxonomic placement?

### 6. Capsid Protein Evolution and Taxonomic Hierarchy
```python
# How do structural vs. non-structural genes correlate with different taxonomic ranks?
protein_evolution_rates = correlate_gene_conservation_with_taxonomy(
    capsid_proteins={'conservation_level': 'family', 'divergence_rate': 'slow'},
    replication_proteins={'conservation_level': 'order', 'divergence_rate': 'medium'},
    accessory_proteins={'conservation_level': 'species', 'divergence_rate': 'fast'}
)
```

**Research Questions:**
- Which genes are most reliable for classification at each taxonomic rank?
- How do structural constraints affect protein evolution rates in viruses?
- Do envelope proteins evolve differently than capsid proteins for classification purposes?

## Phylogenetic and Molecular Evolution

### 7. Phylogenetic Signal Degradation
```python
# At what evolutionary distances does phylogeny become unreliable for classification?
phylogenetic_limits = analyze_sequence_divergence_vs_classification_confidence(
    reliable_phylogeny_range={'protein_identity': '>30%', 'confidence': 'high'},
    twilight_zone={'protein_identity': '15-30%', 'confidence': 'moderate'},
    phylogenetic_noise={'protein_identity': '<15%', 'confidence': 'structure_needed'}
)
```

**Research Questions:**
- What are the phylogenetic limits for reliable viral classification?
- How do different genes perform at various taxonomic depths?
- When should structural data supplement phylogenetic analysis?

### 8. Polymerase Phylogeny vs. Structural Protein Phylogeny
```python
# When do different gene trees conflict in classification decisions?
gene_tree_conflicts = analyze_incongruent_phylogenies(
    replication_genes={'conservative_evolution': 'deep_relationships'},
    structural_genes={'adaptive_evolution': 'host_specific_changes'},
    resolution_strategy={'ICTV_preference': 'replication_genes_for_higher_ranks'}
)
```

**Research Questions:**
- How often do replication vs. structural gene phylogenies conflict?
- Which genes should take priority for classification at different taxonomic ranks?
- How does ICTV resolve phylogenetic conflicts in practice?

## Taxonomic Organization Patterns

### 9. Viral Family Size Distribution Patterns
```python
# Are there optimal family sizes in viral taxonomy?
family_size_evolution = track_family_splitting_patterns(
    large_families_that_split=['Siphoviridae → 15 families', 'Myoviridae → 12 families'],
    splitting_triggers=['phylogenetic_resolution', 'genome_architecture_diversity'],
    optimal_family_size_range=(20, 200)  # species per family
)
```

**Research Questions:**
- Is there an optimal number of species per viral family?
- What triggers family splitting vs. subfamily creation?
- Do different virus types have different optimal family sizes?

### 10. Temporal Bias in Virus Discovery
```python
# How does discovery era affect classification philosophy?
discovery_bias = analyze_classification_by_discovery_period(
    pre_sequencing_era={'basis': 'morphology + serology', 'families': 'broad'},
    early_sequencing_era={'basis': 'genome_organization', 'families': 'split_by_genome'},
    metagenomics_era={'basis': 'phylogeny_only', 'families': 'sequence_based'}
)
```

**Research Questions:**
- How has classification philosophy evolved with available technology?
- Are older classifications biased by limited methodological approaches?
- How should sequence-only viruses be integrated with traditionally characterized viruses?

## Ecological and Biogeographic Patterns

### 11. Geographic Distribution Patterns in Classification
```python
# How does biogeography correlate with viral taxonomy?
biogeographic_taxonomy = analyze_geographic_clustering_vs_phylogeny(
    geographically_restricted_families=['Antarctic_RNA_viruses'],
    cosmopolitan_families=['Coronaviridae'],
    classification_conflicts={'phylogeny_vs_geography': 'which_wins?'}
)
```

**Research Questions:**
- Do geographically restricted viruses form monophyletic groups?
- How does viral biogeography influence taxonomic boundaries?
- Should geographic distribution inform classification decisions?

### 12. Viral Ecosystem Niche and Taxonomic Boundaries
```python
# Do viruses from similar environments cluster taxonomically?
ecological_classification = correlate_habitat_with_taxonomy(
    marine_viruses={'taxonomic_clustering': 'moderate', 'driver': 'host_availability'},
    gut_viruses={'taxonomic_clustering': 'high', 'driver': 'chemical_environment'},
    soil_viruses={'taxonomic_clustering': 'low', 'driver': 'diverse_hosts'}
)
```

**Research Questions:**
- Do environmental pressures shape viral taxonomic organization?
- How does habitat specialization correlate with taxonomic boundaries?
- Are ecosystem-specific viruses more taxonomically cohesive?

## Implementation Strategy

### Phase 1: Core Analysis Infrastructure
- Develop automated phylogenetic analysis pipelines
- Create temporal data extraction tools
- Build statistical correlation frameworks
- Establish baseline measurements for all virus families

### Phase 2: Specific Research Applications
- Implement each research question as separate analysis modules
- Validate findings against known viral biology
- Cross-reference with external genomic and ecological databases
- Develop predictive models based on discovered patterns

### Phase 3: Community Research Platform
- Make analysis tools available to the broader virology community
- Enable custom research questions using the git taxonomy infrastructure
- Integrate with existing viral databases and research platforms
- Support collaborative hypothesis testing

## Expected Outcomes

### Scientific Insights
- Quantitative understanding of viral taxonomic principles
- Evidence-based classification guidelines
- Predictive models for taxonomic stability
- Universal patterns in viral diversity organization

### Methodological Advances
- Improved approaches for classifying sequence-only viruses
- Better integration of phylogenetic and ecological data
- Standardized metrics for taxonomic decision-making
- Automated quality assessment for viral classifications

### Community Benefits
- More transparent and consistent classification decisions
- Reduced taxonomic instability through predictive modeling
- Better integration between discovery and classification workflows
- Enhanced reproducibility in viral taxonomy research

## Data Requirements
- Complete ICTV MSL historical record (available)
- Viral genome sequences with temporal metadata
- Host range and ecological data
- Phylogenetic analysis results over time
- Publication and citation networks
- Geographic distribution data

## Success Metrics
- Number of novel viral taxonomy principles discovered
- Improvement in taxonomic prediction accuracy
- Reduction in classification controversies
- Increased community adoption of evidence-based approaches
- Number of publications enabled by the research platform

---

*These research applications represent the long-term scientific value of the ICTV git repository beyond its immediate utility for taxonomy management. Each application addresses fundamental questions in viral evolution and classification that have been difficult to study systematically due to lack of comprehensive temporal data.*