# ICTV-git Research Implementation Plan

## Overview
This document outlines the implementation strategy for 12 viral taxonomy research analyses using the ICTV-git temporal dataset. Each analysis leverages the unique capabilities of version-controlled taxonomy to answer fundamental questions in viral classification.

## Implementation Priority Tiers

### 🟢 Tier 1: High Priority - Immediate Implementation (Weeks 1-2)
*Can be implemented with existing MSL data in the git repository*

#### 1. Family Size Distribution Analysis (#9)
**Research Question**: Is there an optimal number of species per viral family?
- **Data Requirements**: ✅ Species counts per family from MSL files (already parsed)
- **Implementation**: Count species per family across all MSL versions
- **Challenges**: None - straightforward counting
- **Expected Output**: Histogram of family sizes, splitting triggers, optimal size recommendations
- **Status**: 🟡 IN PROGRESS (Basic analysis complete with documented statistics)

#### 2. Species Boundary Evolution (#1)
**Research Question**: How have species demarcation criteria changed over time?
- **Data Requirements**: ✅ MSL files with demarcation criteria notes
- **Implementation**: Extract and analyze threshold changes from proposal fields
- **Challenges**: Parsing unstructured text in proposal descriptions
- **Expected Output**: Timeline of threshold evolution by family
- **Status**: ⬜ PENDING (Previous mock data analysis removed)

#### 3. Discovery Bias Temporal Analysis (#10)
**Research Question**: How does discovery era affect classification philosophy?
- **Data Requirements**: ✅ MSL release years and species additions
- **Implementation**: Categorize families by first appearance date
- **Challenges**: Defining era boundaries meaningfully
- **Expected Output**: Classification patterns by technology era
- **Status**: ⬜ PENDING (Previous mock data analysis removed)

#### 4. Viral Taxonomy Growth Patterns
**Research Question**: What drives exponential growth in species numbers?
- **Data Requirements**: ✅ Species counts over time (already visualized)
- **Implementation**: Statistical analysis of growth drivers
- **Challenges**: Attributing causation vs correlation
- **Expected Output**: Growth models and predictions
- **Status**: ⬜ PENDING (Previous mock data analysis removed)

### 🟡 Tier 2: Medium Priority - Extended Implementation (Weeks 3-6)
*Requires additional parsing or moderate external data*

#### 5. Host Range Evolution (#3)
**Research Question**: Do broad host range viruses get reclassified more often?
- **Data Requirements**: ⚠️ Host data in MSL files (needs extraction)
- **Implementation**: Parse host columns, correlate with reclassification frequency
- **Challenges**: Inconsistent host nomenclature, missing data
- **Expected Output**: Host breadth vs taxonomic stability metrics
- **Status**: ⬜ PENDING (Previous mock data analysis removed)

#### 6. Genome Architecture Constraints (#4)
**Research Question**: Do different genome types require different classification approaches?
- **Data Requirements**: ⚠️ Genome composition in MSL files
- **Implementation**: Group by genome type, analyze classification patterns
- **Challenges**: Standardizing genome type descriptions
- **Expected Output**: Classification strategies by genome architecture
- **Status**: ⬜ PENDING (Previous mock data analysis removed)

#### 7. Phylogenetic Signal Degradation (#7)
**Research Question**: At what evolutionary distances does phylogeny become unreliable?
- **Data Requirements**: ⚠️ Would benefit from sequence data
- **Implementation**: Analyze classification confidence vs sequence divergence
- **Challenges**: Need to obtain representative sequences
- **Expected Output**: Reliability thresholds for phylogenetic classification
- **Status**: ⬜ PENDING (Previous mock data analysis removed)

### 🔴 Tier 3: Low Priority - Future Implementation (Months 2-6)
*Requires significant external data or computational resources*

#### 8. Horizontal Gene Transfer Impact (#2)
**Research Question**: Which viral families are most affected by recombination?
- **Data Requirements**: ❌ External recombination databases
- **Implementation**: Correlate recombination rates with reclassification
- **Challenges**: Limited comprehensive recombination data
- **Expected Output**: Recombination impact on taxonomic stability

#### 9. Functional Domain Architecture (#5) - ✅ COMPLETED
**Research Question**: Do viruses with similar protein domains belong together?
- **Data Requirements**: ❌ Protein domain annotations (Pfam, CDD)
- **Implementation**: Domain architecture clustering vs taxonomy
- **Challenges**: Computational intensity, database access
- **Expected Output**: Domain-based classification recommendations
- **Status**: ⬜ PENDING (Previous mock data analysis removed)


#### 10. Gene Tree Conflicts (#8)
**Research Question**: When do different gene trees conflict in classification?
- **Data Requirements**: ❌ Multiple gene alignments and trees
- **Implementation**: Compare phylogenies from different genes
- **Challenges**: Massive computational requirements
- **Expected Output**: Gene-specific classification guidelines

#### 11. Geographic Distribution Patterns (#11)
**Research Question**: How does biogeography correlate with viral taxonomy?
- **Data Requirements**: ❌ Sampling location metadata
- **Implementation**: Spatial analysis of taxonomic clusters
- **Challenges**: Sparse geographic data
- **Expected Output**: Biogeographic classification patterns

#### 12. Ecosystem Niche Analysis (#12)
**Research Question**: Do viruses from similar environments cluster taxonomically?
- **Data Requirements**: ❌ Environmental metadata
- **Implementation**: Ecological niche modeling
- **Challenges**: Limited environmental annotations
- **Expected Output**: Ecosystem-specific taxonomic patterns

## Implementation Framework

### Phase 1: Core Infrastructure (Week 1)
```python
research/
├── __init__.py
├── base_analyzer.py          # Base class for all analyses
├── data_loader.py           # MSL data access utilities
├── statistical_tools.py     # Common statistical functions
└── visualization_tools.py   # Plotting utilities
```

### Phase 2: Individual Analyses (Weeks 2-6)
```python
research/
├── family_size_analysis/    # First implementation
│   ├── __init__.py
│   ├── analyzer.py
│   ├── visualizations.py
│   └── results/
├── species_boundaries/
├── discovery_bias/
└── growth_patterns/
```

### Phase 3: Integration and Validation (Week 7+)
- Cross-validation between analyses
- Publication-ready figures
- Statistical significance testing
- Manuscript integration

## Success Metrics

### Immediate Goals (For Manuscript)
- [ ] Complete 3-4 Tier 1 analyses
- [ ] Generate publication-quality figures
- [ ] Identify 2-3 novel findings
- [ ] Validate methodology

### Long-term Goals (Post-Publication)
- [ ] Complete all Tier 2 analyses
- [ ] Establish collaboration network for Tier 3
- [ ] Create community research platform
- [ ] Enable 10+ derivative publications

## Technical Requirements

### Computational Resources
- **Tier 1**: Standard laptop (existing data)
- **Tier 2**: Moderate computing (sequence alignments)
- **Tier 3**: HPC cluster access (large-scale phylogenetics)

### Data Storage
- **Tier 1**: ~100MB (MSL files)
- **Tier 2**: ~10GB (sequences)
- **Tier 3**: ~1TB (comprehensive genomic data)

### Software Dependencies
```python
# Tier 1 (minimal)
- pandas, numpy, matplotlib
- networkx (for tree analysis)
- scipy (statistics)

# Tier 2 (extended)
- biopython (sequence handling)
- scikit-learn (clustering)
- plotly (interactive viz)

# Tier 3 (advanced)
- snakemake (workflow management)
- IQ-TREE (phylogenetics)
- TensorFlow (ML models)
```

## Risk Mitigation

### Data Availability Risks
- **Mitigation**: Start with analyses using existing data
- **Backup**: Partner with databases for missing data

### Computational Risks
- **Mitigation**: Prototype on small datasets
- **Backup**: Cloud computing resources

### Timeline Risks
- **Mitigation**: Prioritize manuscript-critical analyses
- **Backup**: Present framework even if all analyses aren't complete

---

## Current Status: Starting Family Size Analysis

### Family Size Analysis Implementation Plan

**Objective**: Determine optimal viral family sizes and identify splitting triggers

**Key Questions**:
1. What is the distribution of family sizes across MSL versions?
2. At what size do families typically split?
3. What triggers family splitting vs subfamily creation?
4. Are there different optimal sizes for different virus types?

**Implementation Steps**:
1. ✅ Create research directory structure
2. 🚧 Extract family size data from all MSL versions
3. ⬜ Analyze size distributions and changes over time
4. ⬜ Identify splitting events (e.g., Caudovirales)
5. ⬜ Correlate with triggering factors
6. ⬜ Generate visualizations and statistics
7. ⬜ Write up findings

**Expected Deliverables**:
- Family size distribution plots (violin plots by year)
- Splitting event timeline with annotations
- Statistical analysis of optimal size ranges
- Predictive model for family splitting likelihood

---

## Progress Summary

### ✅ Completed Analyses (Real Data Only)
1. **Family Size Distribution Analysis** - Basic analysis complete using documented ICTV statistics
   - **Status**: ✅ COMPLETED with real data
   - **Key findings**: 14.8x growth, Caudovirales dissolution analysis, optimal size recommendations
   - **Data source**: ICTV published MSL statistics (2005-2024)
   - **Output**: `research/family_size_analysis/REAL_DATA_FINDINGS.md`

### 🚧 Data Cleanup Completed
- **Mock data archived**: All previous mock/simulated analyses moved to `research/MOCK_DATA_ARCHIVE/`
- **Clean research directory**: Only real data analyses remain active
- **Data integrity policy**: Strict no-mock-data enforcement implemented

### ⬜ Planned Next (Pending Full MSL Data Parsing)
1. **Family Size Distribution Analysis** - Detailed analysis with parsed MSL files
2. **Species Boundary Evolution** - From real MSL documentation and proposal records
3. **Discovery Bias Analysis** - Based on actual family introduction dates from MSL history
4. **Growth Pattern Analysis** - Detailed analysis from real species count progressions

---

*Last Updated: June 9, 2025*
*Status: Active Development - 1/12 analyses with real data (8.3%)*