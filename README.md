# ICTV-git: Git-Based Version Control for Viral Taxonomy

## Overview

ICTV-git revolutionizes viral taxonomy management by applying git version control principles to the International Committee on Taxonomy of Viruses (ICTV) classification system. This project addresses critical issues in current taxonomy management including breaking changes without migration paths, lost institutional knowledge, and version incompatibility between publications.

## The Problem

The recent Caudovirales reclassification exemplifies the crisis in viral taxonomy:
- 50+ years of ecological and phenotypic data associations were broken overnight
- Three morphology-based families (Myoviridae, Podoviridae, Siphoviridae) were abolished
- Replaced with 22 new genomics-based families with no clear migration path
- Thousands of research papers now reference obsolete classifications
- Databases updated inconsistently, creating chaos across platforms

## The Solution

Git-based taxonomy management provides:
- **Full version history** - Track every taxonomic change with complete provenance
- **Branching workflows** - Propose and test alternative classifications
- **Semantic diffs** - Visualize meaningful taxonomic changes
- **Community collaboration** - Fork, modify, and propose improvements
- **Automated migration** - Convert between taxonomy versions programmatically
- **Evidence linking** - Connect classifications to supporting data

## Project Structure

```
viral-taxonomy/
├── realms/              # Taxonomic hierarchy as directory structure
│   └── riboviria/       # Each virus stored as YAML with full metadata
├── evidence/            # Supporting phylogenies, genomes, proposals
└── tools/               # Conversion and analysis utilities
```

## Key Features

### Version Control
- Complete history of all taxonomic changes since 2008
- Git commits document rationale for each reclassification
- Branches for proposals and working group development

### Transparent Decision Making
- Every classification linked to evidence (phylogenies, genomes, publications)
- Proposal documents integrated into commit messages
- Community can review and comment on changes

### Automated Tools
- Convert between MSL versions automatically
- Generate migration reports for database updates
- API for programmatic access to any taxonomy version

## Getting Started

### Prerequisites
- Python 3.8+
- Git
- Basic understanding of viral taxonomy

### Installation
```bash
git clone https://github.com/shandley/ICTV-git.git
cd ICTV-git
pip install -r requirements.txt
```

### Quick Example
```python
# Access any historical taxonomy version
from ictv_git import TaxonomyRepo

repo = TaxonomyRepo()
classification = repo.get_classification("Escherichia phage T4", version="MSL36")
# Returns: {"family": "Myoviridae", "genus": "T4virus"}

classification = repo.get_classification("Escherichia phage T4", version="MSL37")  
# Returns: {"family": "Straboviridae", "genus": "Tequatrovirus"}

# Generate migration mapping
migration = repo.map_family("Myoviridae", from_version="MSL36", to_version="MSL37")
# Returns mapping to all descendant families
```

## Project Status

**Current Phase**: Data Analysis & Proof of Concept

- [x] Project architecture design
- [ ] Historical MSL data collection
- [ ] Caudovirales case study development
- [ ] Prototype implementation
- [ ] Community feedback collection

## Use Cases

### For Researchers
- Maintain reproducibility across taxonomy versions
- Track classification changes for specific viruses
- Understand rationale behind reclassifications

### For Database Maintainers
- Automated migration between taxonomy versions
- Consistent updates across platforms
- Full audit trail for changes

### For ICTV
- Transparent proposal development
- Community input on classifications
- Version control for official releases

## Contributing

We welcome contributions! Key areas where help is needed:
- MSL data parsing and validation
- Visualization tools for taxonomic changes
- Testing with real-world use cases
- Documentation and tutorials

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Research Applications

This temporal dataset enables novel research including:
- Viral species boundary evolution over time
- Impact of sequencing technology on classification philosophy  
- Optimal family size analysis
- Phylogenetic signal degradation studies
- Geographic and ecological patterns in viral taxonomy

## Citation

If you use ICTV-git in your research, please cite:
```
[Citation will be added upon publication]
```

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
ICTV data is used under Creative Commons license as specified by ICTV.

## Contact

- Project Lead: Scott Handley
- GitHub Issues: [https://github.com/shandley/ICTV-git/issues](https://github.com/shandley/ICTV-git/issues)
- Email: [Contact information]

## Acknowledgments

- International Committee on Taxonomy of Viruses (ICTV) for providing open access to MSL data
- The virology community for feedback and use cases
- Git and open source community for inspiration

---

*Transforming viral taxonomy from static documents to dynamic, versioned data*