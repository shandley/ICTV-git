# Git-Based Scientific Taxonomy: Revolutionizing ICTV Data Management

## Project Vision
Transform scientific data management by applying git-like version control concepts to all scientific data, starting with viral taxonomy (ICTV) as a proof-of-concept.

## Core Problem Statement
Current scientific data management suffers from:
- **Breaking changes with no migration path** (e.g., Caudovirales reclassification)
- **Lost institutional knowledge** when taxonomies change
- **No community input** in major decisions
- **Database chaos** across platforms
- **Version incompatibility** between publications
- **Centralized bottlenecks** in committee-based systems

## Why ICTV as Starting Point?
- **Perfect pain point example**: Recent Caudovirales disaster
- **Rich historical data**: MSL files since 2008, proposals since 2008
- **High-stakes decisions**: Affects vaccine development, outbreak response
- **Obvious community need**: Current system frustrates researchers
- **Manageable scope**: Focused domain for proof-of-concept
- **Clear value proposition**: Immediate benefits obvious to any virologist

## Technical Architecture

### Core Data Model
```
Taxonomic objects as git objects:
├── Taxa (species, genus, family) → content-addressable objects
├── Viral genomes/sequences → blob objects  
├── Taxonomic relationships → tree objects (parent/child)
├── Phylogenetic evidence → referenced blob objects
└── Proposals/rationale → commit metadata
```

### Hierarchical Structure
```
/realm/subrealm/kingdom/subkingdom/phylum/subphylum/class/subclass/
order/suborder/family/subfamily/genus/subgenus/species
```

### Commit Examples
- `git add species/SARS_CoV_2.yaml` (new virus)
- `git mv family/Siphoviridae/* family/Drexlerviridae/` (reclassification)
- Commit message: "Split Siphoviridae based on genomic clustering analysis (Proposal 2019.001B)"

### Evidence Linking Format
```yaml
classification_evidence:
  phylogenetic_trees: [tree_hash_1, tree_hash_2]
  genome_sequences: [sequence_hash_list]
  publications: [pmid_list]
  rationale: "Monophyletic clade with >85% AAI in major capsid protein"
```

### Branching Strategy
- `main` → Official ICTV taxonomy
- `proposal/caudovirales-reclassification` → Major reclassification work
- `working-group/papillomavirus` → Specialist group branches
- `lab/smith-et-al` → Research group forks

## Available Data Sources

### ICTV Historical Data
- ✅ **Master Species Lists (MSL)**: Excel files for every release since 2008
- ✅ **Taxonomy proposals**: PDF documentation for every change  
- ✅ **Virus Metadata Resource (VMR)**: Links to GenBank sequences
- ✅ **Historical archives**: Complete records back to 1971
- ✅ **Creative Commons licensed**: Free for academic use

### Key Implementation URLs and File Locations

**Direct Download Links (for Claude Code)**:
```python
# Current MSL files (URLs subject to change - check ictv.global/msl for updates)
MSL_DOWNLOAD_URLS = {
    'MSL40': 'https://ictv.global/sites/default/files/MSL/ICTV_Master_Species_List_2024_MSL40.v1.xlsx',
    'MSL39': 'https://ictv.global/sites/default/files/MSL/ICTV_Master_Species_List_2023_MSL39.v3.xlsx',
    'MSL38': 'https://ictv.global/sites/default/files/MSL/ICTV_Master_Species_List_2022_MSL38.v3.xlsx',
    'MSL37': 'https://ictv.global/sites/default/files/MSL/ICTV_Master_Species_List_2021_MSL37.v1.xlsx'
}

# Fallback: Scrape from main MSL page
MSL_LIST_URL = 'https://ictv.global/msl'
```

**Expected MSL File Structure**:
```python
# Typical sheet names in MSL files
EXPECTED_SHEETS = {
    'main': ['MSL', 'Master Species List', 'Sheet1'],  # Main data
    'definitions': ['Column Definitions', 'Definitions'],
    'renamed': ['Taxa Renamed', 'Renamed Taxa'],
    'counts': ['Taxon Counts', 'Summary']
}

# Expected column variations across MSL versions
COLUMN_VARIATIONS = {
    'Species': ['Species', 'Virus name', 'Virus Name', 'Species name'],
    'Genus': ['Genus'],
    'Family': ['Family'],
    'Order': ['Order'],
    'Class': ['Class'],
    'Phylum': ['Phylum'],
    'Kingdom': ['Kingdom'],
    'Realm': ['Realm'],
    'Genome_Composition': ['Genome Composition', 'Genome composition', 'Baltimore group', 'Genome type'],
    'Host': ['Host', 'Host source', 'Host range', 'Natural host'],
    'Proposal': ['Proposal', 'TaxoProp', 'Taxonomy proposal', 'Proposal file']
}
```

### Important Notes for Claude Code Development

**1. Start Small - MVP Approach**:
```python
# Phase 1: Single file processing
def process_single_msl_file(file_path: str) -> bool:
    """Process one MSL file and create basic YAML output."""
    try:
        parser = MSLParser(file_path)
        species_list = parser.extract_species_records()
        
        # Create simple directory structure for testing
        output_dir = Path('output_test')
        output_dir.mkdir(exist_ok=True)
        
        # Save first 10 species as YAML for validation
        for i, species in enumerate(species_list[:10]):
            yaml_file = output_dir / f"species_{i:03d}.yaml"
            yaml_file.write_text(species.to_yaml())
        
        print(f"Successfully processed {len(species_list)} species")
        print(f"Saved first 10 species to {output_dir}")
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False
```

**2. Error Handling Strategy**:
```python
# Always wrap file operations in try-except
# Log errors but continue processing when possible
# Validate data at multiple stages

def robust_file_processing():
    """Example of robust error handling."""
    try:
        # Primary processing
        result = process_msl_file()
    except FileNotFoundError:
        print("MSL file not found - check download")
        return None
    except pd.errors.ExcelFileError:
        print("Invalid Excel file format")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        print("Continuing with partial results...")
        return partial_results
```

**3. Data Validation Checkpoints**:
```python
def validate_processing_pipeline():
    """Key validation steps."""
    # 1. File exists and is readable
    assert file_path.exists(), "MSL file missing"
    
    # 2. Excel file loads successfully
    assert workbook is not None, "Excel file corrupted"
    
    # 3. Main sheet found
    assert main_sheet_data is not None, "No main data sheet"
    
    # 4. Required columns present
    required_cols = ['Species', 'Genus']
    missing_cols = [col for col in required_cols if col not in df.columns]
    assert not missing_cols, f"Missing columns: {missing_cols}"
    
    # 5. Species objects created successfully
    assert len(species_list) > 0, "No species parsed"
    
    # 6. YAML generation works
    test_yaml = species_list[0].to_yaml()
    assert test_yaml, "YAML generation failed"
```

**4. Debugging Helpers**:
```python
def debug_msl_structure(file_path: str):
    """Analyze MSL file structure for debugging."""
    workbook = pd.ExcelFile(file_path)
    
    print(f"File: {file_path}")
    print(f"Sheets: {workbook.sheet_names}")
    
    for sheet_name in workbook.sheet_names:
        df = pd.read_excel(workbook, sheet_name, nrows=5)  # Just first 5 rows
        print(f"\nSheet '{sheet_name}':")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Sample data:")
        print(df.head(2).to_string())
```

**5. Git Integration (Start Simple)**:
```python
def simple_git_workflow(taxonomy_dir: str):
    """Basic git operations for testing."""
    import git
    
    repo_path = Path(taxonomy_dir)
    
    # Initialize repo if needed
    if not (repo_path / '.git').exists():
        repo = git.Repo.init(repo_path)
        print(f"Initialized git repo at {repo_path}")
    else:
        repo = git.Repo(repo_path)
    
    # Stage all YAML files
    yaml_files = list(repo_path.glob('**/*.yaml'))
    if yaml_files:
        repo.index.add([str(f.relative_to(repo_path)) for f in yaml_files])
        
        # Simple commit
        commit_msg = f"Add {len(yaml_files)} species files"
        repo.index.commit(commit_msg)
        print(f"Committed: {commit_msg}")
    
    return repo
```

## ICTV Data Structure Analysis

### Taxonomic Hierarchy (15 Ranks)
Based on analysis of ICTV documentation, the complete hierarchy is:

**Primary Ranks**:
1. **Realm** (-viria) - Highest rank, based on highly conserved hallmark genes
2. **Kingdom** (-virae) - Major evolutionary groupings within realms
3. **Phylum** (-viricota) - Large monophyletic groups
4. **Class** (-viricetes) - Related orders grouped together
5. **Order** (-virales) - Families sharing structural/replication features
6. **Family** (-viridae) - Genera with similar genome organization
7. **Genus** (-virus) - Species sharing significant sequence similarity
8. **Species** (binomial format since 2021) - Fundamental taxonomic unit

**Secondary Ranks** (optional):
- Subrealm (-vira), Subkingdom (-virites), Subphylum (-viricotina)
- Subclass (-viricetidae), Suborder (-virineae), Subfamily (-virinae), Subgenus (-virus)

### Current Scale (as of MSL40, 2024-2025)
- **11,273+ virus species** across all domains of life
- **6 established realms**: Adnaviria, Duplodnaviria, Monodnaviria, Riboviria, Ribozyviria, Varidnaviria
- **80% of species** assigned to family level
- **94% of species** assigned to realm level

### MSL File Structure
Each Excel file contains multiple sheets:
- **MSL sheet**: Complete taxonomy with columns for each rank
- **Column Definitions**: Explains field meanings
- **Taxa Renamed**: Changes since previous release
- **Taxon Counts**: Statistics by rank and change type

### Key Data Fields in MSL
- **Taxonomic hierarchy**: All 15 possible ranks
- **Genome composition**: DNA/RNA type, strandedness, size
- **Host information**: Which organisms the virus infects
- **Change tracking**: What changed since last release
- **Proposal links**: Reference to ratification documents
- **History links**: Complete taxonomic lineage changes

### Major Taxonomic Revolutions in Dataset

**1. Caudovirales Abolishment (MSL37, 2022)**
- Eliminated morphology-based families: Myoviridae, Podoviridae, Siphoviridae
- Replaced order Caudovirales with class Caudoviricetes
- Created 22 new families, 321 genera, 862 species
- Implemented binomial nomenclature for bacterial viruses

**2. 15-Rank System Introduction (2018)**
- Expanded from 5 ranks to 15 ranks
- Added realm, kingdom, phylum, class concepts
- Enabled classification of entire virosphere diversity

**3. Binomial Nomenclature (2021)**
- Mandated genus + species epithet format
- Applied to all 11,000+ virus species
- Brought viral taxonomy in line with cellular organisms

## Git Implementation Strategy

### Current Pain Points Identified

**1. Breaking Changes Without Migration Paths**
- Caudovirales reclassification affected thousands of virus classifications overnight
- No clear mapping between old Siphoviridae → new families
- Researchers lost 50+ years of phenotypic/ecological data associations
- Papers published before/after use incompatible taxonomies

**2. Opaque Decision Making**
- Major changes happen behind closed committee doors
- Community sees results, not the reasoning process
- No way to track "why" a particular classification decision was made
- Proposal PDFs exist but aren't linked to specific changes

**3. Version Hell**
- 17 different MSL releases since 2008, each incompatible
- Databases scramble to update classifications inconsistently
- No automated way to migrate data between versions
- Researchers stuck with outdated taxonomies for reproducibility

**4. Lost Institutional Knowledge**
- When families split, the historical reasoning disappears
- Phenotypic data becomes orphaned from new classifications
- Study group expertise isn't preserved in the taxonomy itself

### Git-Based Solution Architecture

**Repository Structure**:
```
viral-taxonomy/
├── realms/
│   ├── riboviria/
│   │   ├── kingdoms/
│   │   │   └── orthornavirae/
│   │   │       └── phyla/
│   │   │           └── pisuviricota/
│   │   │               └── classes/
│   │   │                   └── pisoniviricetes/
│   │   │                       └── orders/
│   │   │                           └── nidovirales/
│   │   │                               └── families/
│   │   │                                   └── coronaviridae/
│   │   │                                       └── genera/
│   │   │                                           └── betacoronavirus/
│   │   │                                               └── species/
│   │   │                                                   └── sars_cov_2.yaml
└── evidence/
    ├── phylogenies/
    ├── genomes/
    └── proposals/
```

**Taxonomic Object Format** (YAML):
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

**Commit Message Format**:
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

### Semantic Diff Examples

**Family Split Diff**:
```diff
# git diff MSL36..MSL37 families/siphoviridae/
- family: Siphoviridae
-   genera: [Lambdavirus, Phikzvirus, Tequatrovirus, ...]
+ family: Drexlerviridae  
+   genera: [Lambdavirus, Phikzvirus, ...]
+ family: Guelinviridae
+   genera: [Tequatrovirus, ...]
```

**Species Reclassification Diff**:
```diff
# git show sha256:commitid species/t4_phage.yaml
  scientific_name: "Escherichia virus T4"
- genus: "T4virus"  
- family: "Myoviridae"
+ genus: "Tequatrovirus"
+ family: "Straboviridae"
  evidence:
+   rationale: "Phylogenetic analysis shows grouping with Straboviridae"
+   proposal: "2021.092B"
```

### Branching Strategy

**Main Branches**:
- `main` → Official ICTV taxonomy (current MSL)
- `msl39` → Stable release branches for reproducibility
- `msl38` → Previous stable releases

**Development Branches**:
- `proposal/2024-caudovirales-revision` → Major taxonomic revisions
- `working-group/papillomavirus` → Study group development
- `community/metagenomic-viruses` → Community-contributed classifications

**Research Forks**:
- `lab/sullivan-marine-viruses` → Lab-specific taxonomic hypotheses
- `project/gut-virome-classification` → Project-specific needs

### Migration and Compatibility

**Automatic Mapping**:
```bash
# Convert old classifications to new system
git-taxonomy migrate \
  --from-version MSL36 \
  --to-version MSL37 \
  --input old_dataset.csv \
  --output migrated_dataset.csv \
  --report migration_report.html
```

**Compatibility Layers**:
```python
# API maintains backward compatibility
taxonomy = ICTVTaxonomy()
taxonomy.get_classification("Escherichia virus T4", version="MSL36")
# Returns: {"family": "Myoviridae", "genus": "T4virus"}

taxonomy.get_classification("Escherichia virus T4", version="MSL37") 
# Returns: {"family": "Straboviridae", "genus": "Tequatrovirus"}

taxonomy.map_classification("Myoviridae", from_version="MSL36", to_version="MSL37")
# Returns: ["Straboviridae", "Herelleviridae", "Tevenviridae", ...]
```

### Phase 1: Data Analysis & Proof of Concept
**Objective**: Understand ICTV data structure and create compelling demo

**Tasks**:
- [ ] Download historical MSL files (2008-2025)
- [ ] Parse Excel data to understand schema changes
- [ ] Identify major reclassification events
- [ ] Focus on Caudovirales case study
- [ ] Create git repository structure prototype
- [ ] Generate visual diffs showing "before/after" taxonomy changes

**Deliverables**:
- Data analysis scripts
- Caudovirales reclassification timeline
- Prototype git repository with sample data
- Visual diff demonstrations

### Phase 2: Technical Implementation
**Objective**: Build functional git-based taxonomy system

**Tasks**:
- [ ] Design semantic diff algorithms for taxonomy
- [ ] Implement conversion tools (MSL → git objects)
- [ ] Build merge conflict resolution for competing classifications
- [ ] Create web interface for browsing taxonomic history
- [ ] Develop API for programmatic access
- [ ] Integration with existing databases (GenBank, etc.)

**Deliverables**:
- Working git-based taxonomy database
- Conversion and sync tools
- Web interface prototype
- API documentation

### Phase 3: Community Validation & Paper
**Objective**: Validate with virologists and publish results

**Tasks**:
- [ ] Beta test with virus taxonomy experts
- [ ] Gather feedback from ICTV study group chairs
- [ ] Benchmark performance vs. current systems
- [ ] Document case studies beyond Caudovirales
- [ ] Write comprehensive paper
- [ ] Submit to high-impact journal

**Deliverables**:
- Peer-reviewed publication
- Community feedback reports
- Performance benchmarks
- Public repository and tools

## Paper Outline

### Title
"Git-Based Version Control for Scientific Taxonomy: A Case Study with ICTV Viral Classification"

### Abstract
- Problem: Current taxonomy management inadequate for modern science
- Solution: Git-like version control for scientific data
- Case study: ICTV viral taxonomy
- Results: Improved transparency, collaboration, reproducibility
- Impact: Framework applicable to all scientific domains

### Sections

**1. Introduction**
- Scientific data management crisis
- Version control success in software development
- Why taxonomy is perfect test case

**2. Current State of Viral Taxonomy**
- ICTV process and limitations
- Caudovirales reclassification case study
- Community pain points

**3. Git-Based Taxonomy Design**
- Technical architecture
- Data structures and relationships
- Branching and merging strategies
- Evidence linking and provenance

**4. Implementation and Results**
- Historical data conversion
- Performance metrics
- Case study demonstrations
- Community feedback

**5. Discussion**
- Advantages over current systems
- Scalability to other domains
- Integration challenges
- Future directions

**6. Conclusion**
- Paradigm shift needed
- Framework for broader adoption
- Call to action for scientific community

## Immediate Next Steps

### From Mobile (Now)
1. **Data Exploration**: Download and analyze ICTV MSL files
2. **Case Study Development**: Deep dive into Caudovirales changes
3. **Architecture Refinement**: Detail technical specifications
4. **Paper Drafting**: Begin introduction and problem statement

### From Computer (Later)
1. **Prototype Development**: Build working git repository
2. **Visualization Tools**: Create diff and timeline views
3. **Performance Testing**: Benchmark against current systems
4. **Community Outreach**: Contact ICTV researchers for feedback

## Success Metrics
- **Technical**: Successful conversion of all historical ICTV data
- **Performance**: Faster queries than current database
- **Usability**: Positive feedback from virus taxonomists
- **Impact**: Adoption by other taxonomic communities
- **Academic**: Publication in top-tier journal
- **Long-term**: Influence on scientific data management practices

## Resources Needed
- **Technical**: Git expertise, database design, web development
- **Domain**: Virology knowledge, ICTV connections
- **Academic**: Writing support, journal submission process
- **Community**: Beta testers, feedback from taxonomists

## Timeline
- **Month 1-2**: Data analysis and prototype
- **Month 3-4**: Technical implementation
- **Month 5-6**: Community validation and paper writing
- **Month 7-8**: Revision and submission
- **Month 9-12**: Review process and publication

---

*This project has the potential to fundamentally change how scientific data is managed across all domains. Starting with ICTV provides a focused, high-impact demonstration that could catalyze broader adoption of version control principles in science.*