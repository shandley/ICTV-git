# ICTV Git-Based Taxonomy System

## Project Overview
A revolutionary approach to scientific data management applying git version control principles to viral taxonomy. This project transforms the International Committee on Taxonomy of Viruses (ICTV) classification system into a transparent, versioned, and community-driven platform.

## Core Problem Statement
Current viral taxonomy management suffers from:
- **Breaking changes without migration paths** - The Caudovirales reclassification eliminated 50+ years of ecological/phenotypic data associations overnight
- **Lost institutional knowledge** - When families split, historical reasoning disappears
- **Opaque decision making** - Committee decisions happen behind closed doors with no community input
- **Version incompatibility** - 17 MSL releases since 2008, each incompatible with the others
- **Database chaos** - Inconsistent updates across platforms (GenBank, RefSeq, UniProt)
- **Reproducibility crisis** - Papers published months apart use incompatible taxonomies

## Technical Architecture

### Core Data Model
```
viral-taxonomy/
├── realms/                          # Highest taxonomic rank (-viria)
│   ├── riboviria/                   # RNA viruses realm
│   │   ├── kingdoms/                # Major evolutionary groupings (-virae)
│   │   │   └── orthornavirae/
│   │   │       └── phyla/           # Large monophyletic groups (-viricota)
│   │   │           └── pisuviricota/
│   │   │               └── classes/ # Related orders (-viricetes)
│   │   │                   └── pisoniviricetes/
│   │   │                       └── orders/    # Families with shared features (-virales)
│   │   │                           └── nidovirales/
│   │   │                               └── families/    # Genera with similar genomes (-viridae)
│   │   │                                   └── coronaviridae/
│   │   │                                       └── genera/    # Species with sequence similarity (-virus)
│   │   │                                           └── betacoronavirus/
│   │   │                                               └── species/    # Fundamental unit
│   │   │                                                   └── sars_cov_2.yaml
└── evidence/                        # Supporting data
    ├── phylogenies/                 # Tree files (content-addressable)
    ├── genomes/                     # Reference sequences
    └── proposals/                   # ICTV ratification documents
```

### Taxonomic Object Format (YAML)
```yaml
# species/sars_cov_2.yaml
scientific_name: "Severe acute respiratory syndrome-related coronavirus"
binomial: "Betacoronavirus covadicum"
genome:
  type: "ssRNA(+)"
  size: "29903 bp"
  segments: 1
classification:
  realm: "Riboviria"
  kingdom: "Orthornavirae"
  phylum: "Pisuviricota"
  class: "Pisoniviricetes"
  order: "Nidovirales"
  family: "Coronaviridae"
  subfamily: "Orthocoronavirinae"
  genus: "Betacoronavirus"
  subgenus: "Sarbecovirus"
hosts:
  - "Homo sapiens"
  - "Rhinolophus affinis"
evidence:
  phylogenetic_trees: ["sha256:abc123..."]
  exemplar_genomes: ["NC_045512.2"]
  key_publications: ["PMC7211627", "PMC7160186"]
history:
  created: "MSL35"
  last_modified: "MSL40"
  changes:
    - version: "MSL36"
      type: "host_update"
      description: "Added human as confirmed host"
      proposal: "2020.013M"
```

### Commit Message Format
```
Split Siphoviridae into 15 new families based on genomic analysis

- Move 1,847 species from family Siphoviridae to new families
- Create families: Drexlerviridae, Guelinviridae, Iobviridae...
- Based on major capsid protein phylogeny and genome organization
- Resolves paraphyletic grouping identified in proposal 2021.001B

Evidence: phylogeny_capsid_mcp_2021.tree, genome_synteny_analysis.csv
Proposal: https://ictv.global/files/proposals/2021.001B.pdf
Ratified: 2022-03-15
Affects: 1,847 species across 321 genera
```

## Data Sources

### ICTV Master Species Lists (MSL)
Available from: https://ictv.global/msl

**Direct Download URLs**:
```python
MSL_DOWNLOAD_URLS = {
    'MSL40': 'https://ictv.global/sites/default/files/MSL/ICTV_Master_Species_List_2024_MSL40.v1.xlsx',
    'MSL39': 'https://ictv.global/sites/default/files/MSL/ICTV_Master_Species_List_2023_MSL39.v3.xlsx',
    'MSL38': 'https://ictv.global/sites/default/files/MSL/ICTV_Master_Species_List_2022_MSL38.v3.xlsx',
    'MSL37': 'https://ictv.global/sites/default/files/MSL/ICTV_Master_Species_List_2021_MSL37.v1.xlsx'
}
```

### MSL File Structure
Each Excel file contains:
- **MSL sheet**: Complete taxonomy with all 15 ranks
- **Column Definitions**: Field explanations
- **Taxa Renamed**: Changes since previous release
- **Taxon Counts**: Statistics by rank

### Expected Column Variations
```python
COLUMN_VARIATIONS = {
    'Species': ['Species', 'Virus name', 'Virus Name', 'Species name'],
    'Genus': ['Genus'],
    'Family': ['Family'],
    'Order': ['Order'],
    'Class': ['Class'],
    'Phylum': ['Phylum'],
    'Kingdom': ['Kingdom'],
    'Realm': ['Realm'],
    'Genome_Composition': ['Genome Composition', 'Genome composition', 'Baltimore group'],
    'Host': ['Host', 'Host source', 'Host range', 'Natural host'],
    'Proposal': ['Proposal', 'TaxoProp', 'Taxonomy proposal']
}
```

## Implementation Phases

### Phase 1: Data Analysis & Proof of Concept ⬅️ CURRENT PHASE
**Objective**: Parse ICTV data and create compelling Caudovirales case study

**Tasks**:
- [ ] Download historical MSL files (2008-2025)
- [ ] Parse Excel data structure and schema changes
- [ ] Focus on Caudovirales reclassification disaster
- [ ] Create prototype git repository structure
- [ ] Generate before/after visualizations

**Deliverables**:
- MSL parsing scripts
- Caudovirales timeline visualization
- Demo git repository
- Visual diff demonstrations

### Phase 2: Technical Implementation
**Objective**: Build functional git-based taxonomy system

**Tasks**:
- [ ] Design semantic diff algorithms
- [ ] Build MSL → git conversion tools
- [ ] Implement merge conflict resolution
- [ ] Create web interface
- [ ] Develop API

**Deliverables**:
- Working git taxonomy database
- Conversion tools
- Web interface
- API documentation

### Phase 3: Community Validation & Publication
**Objective**: Validate with virologists and publish

**Tasks**:
- [ ] Beta test with taxonomists
- [ ] Gather ICTV feedback
- [ ] Benchmark performance
- [ ] Write paper
- [ ] Submit to journal

**Deliverables**:
- Peer-reviewed publication
- Public tools
- Performance metrics

## Research Applications

### Enabled Research Questions
1. **Species Boundary Evolution**: How have demarcation criteria changed over time?
2. **Horizontal Gene Transfer**: Which families are destabilized by recombination?
3. **Host Range Evolution**: Do generalist viruses have unstable taxonomy?
4. **Genome Architecture**: Do different genome types require different classification approaches?
5. **Phylogenetic Limits**: At what sequence divergence does phylogeny fail?
6. **Family Size Optimization**: Is there an ideal number of species per family?
7. **Discovery Bias**: How does discovery era affect classification philosophy?
8. **Biogeographic Patterns**: Does geography correlate with taxonomy?

## Development Guidelines

### MVP Implementation (Phase 1)
```python
# Start with single file processing
def process_single_msl_file(file_path: str) -> bool:
    """Process one MSL file and create YAML outputs."""
    parser = MSLParser(file_path)
    species_list = parser.extract_species_records()
    
    # Create simple test structure
    output_dir = Path('output_test')
    output_dir.mkdir(exist_ok=True)
    
    # Save first 10 species for validation
    for i, species in enumerate(species_list[:10]):
        yaml_file = output_dir / f"species_{i:03d}.yaml"
        yaml_file.write_text(species.to_yaml())
    
    return True
```

### Error Handling Strategy
- Wrap all file operations in try-except blocks
- Log errors but continue processing when possible
- Validate data at multiple checkpoints
- Provide debugging helpers for MSL structure analysis

### Git Integration
```python
# Simple git workflow for testing
def simple_git_workflow(taxonomy_dir: str):
    """Basic git operations."""
    repo_path = Path(taxonomy_dir)
    
    # Initialize if needed
    if not (repo_path / '.git').exists():
        repo = git.Repo.init(repo_path)
    else:
        repo = git.Repo(repo_path)
    
    # Stage YAML files
    yaml_files = list(repo_path.glob('**/*.yaml'))
    if yaml_files:
        repo.index.add([str(f.relative_to(repo_path)) for f in yaml_files])
        repo.index.commit(f"Add {len(yaml_files)} species files")
    
    return repo
```

## Success Metrics
- **Technical**: Convert all historical ICTV data successfully
- **Performance**: Faster queries than current databases
- **Usability**: Positive taxonomist feedback
- **Impact**: Adoption by other taxonomy communities
- **Academic**: Top-tier journal publication
- **Long-term**: Transform scientific data management practices

## Why ICTV?
- **Perfect pain point**: Caudovirales disaster affects every phage researcher
- **Rich data**: Complete MSL history since 2008
- **High stakes**: Affects vaccine development and outbreak response
- **Clear value**: Benefits obvious to any virologist
- **Manageable scope**: Focused domain for proof-of-concept
- **Creative Commons**: Data freely available for academic use

## Expected Outcomes
- **Immediate**: Solve Caudovirales classification chaos
- **Short-term**: Enable reproducible viral research
- **Medium-term**: Community-driven taxonomy development
- **Long-term**: Model for all scientific data management

## Key Differentiators
- **Version control**: Full history tracking like software development
- **Branching**: Multiple classification hypotheses can coexist
- **Transparency**: Every decision traceable to evidence
- **Community input**: Fork, modify, propose changes
- **Migration tools**: Automated conversion between versions
- **Semantic diffs**: Meaningful change visualization

---

*This project represents a paradigm shift in scientific data management, using viral taxonomy as a compelling proof-of-concept that could transform how all scientific communities handle evolving classification systems.*