# ICTV-git: Git-based Viral Taxonomy Management

<p align="center">
  <img src="ICTV-GIT.png" alt="ICTV-git Logo" width="300">
</p>

<p align="center">
  <a href="https://github.com/shandley/ICTV-git/actions"><img src="https://img.shields.io/badge/build-passing-brightgreen.svg" alt="Build Status"></a>
  <a href="https://github.com/shandley/ICTV-git/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python Version"></a>
  <a href="https://github.com/shandley/ICTV-git/issues"><img src="https://img.shields.io/github/issues/shandley/ICTV-git.svg" alt="Issues"></a>
</p>

## 🦠 Revolutionizing Viral Taxonomy with Version Control

**ICTV-git** transforms the International Committee on Taxonomy of Viruses (ICTV) classification system into a transparent, versioned, and community-driven platform using git version control principles. This solves the reproducibility crisis in virology research by enabling researchers to track taxonomic changes, migrate datasets between versions, and cite specific taxonomy versions.

### 🎯 The Problem We Solve

Current viral taxonomy management suffers from:
- **Breaking changes without migration paths** - The Caudovirales reclassification eliminated 50+ years of ecological data associations
- **Version incompatibility** - 18 MSL releases since 2005, each incompatible with the others
- **Lost institutional knowledge** - When families split, historical reasoning disappears
- **Reproducibility crisis** - Papers published months apart use incompatible taxonomies

### ✨ Key Features

- 📊 **Complete History**: 20 years of ICTV taxonomy (2005-2024) under git version control
- 🔄 **Automatic Migration**: Update datasets between any taxonomy versions with validation
- 🌐 **Multiple Interfaces**: Interactive web browser, REST API, Python library, and CLI tools
- 📖 **Smart Citations**: Generate version-specific citations with git commit tracking
- 🔍 **Semantic Diffs**: Distinguish reclassifications from nomenclature changes
- 📈 **Research Analytics**: Discover patterns in viral diversity evolution

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/shandley/ICTV-git.git
cd ICTV-git

# Install dependencies
pip install -r requirements.txt

# Download all MSL data (or use existing data/)
python scripts/download_msl.py
```

### Basic Usage

```bash
# Convert MSL files to git structure
python scripts/convert_msl_to_git.py data/MSL38.xlsx

# Compare two versions
python src/community_tools/version_comparator.py output/git_taxonomy --version1 MSL37 --version2 MSL38

# Start the interactive web browser
streamlit run scripts/run_taxonomy_browser.py

# Start the REST API server
python scripts/run_taxonomy_api.py
```

## 📸 Screenshots

### Interactive Taxonomy Browser
Browse viral taxonomy across 20 years with interactive visualizations:
- Hierarchical tree exploration
- Statistical dashboards
- Evolution timelines
- Advanced search and filtering

### REST API
Programmatic access with comprehensive endpoints:
- Species lookup and search
- Version comparison
- Bulk data export (JSON/CSV/YAML)
- Citation generation

## 🎓 Research Applications

### For Virologists
- Track how your virus of interest has been classified over time
- Update legacy datasets to current taxonomy automatically
- Generate proper citations for reproducible research
- Understand the impact of major reorganizations

### For Bioinformaticians
```python
# Example: Track species through history
import requests

response = requests.get("http://localhost:8000/api/v1/history/Tobacco mosaic virus")
history = response.json()
print(f"First appeared: {history['first_appearance']}")
print(f"Classification changes: {len([h for h in history['history'] if h['found']])}")
```

### For Taxonomists
- Visualize the impact of classification proposals
- Identify unstable taxonomic groups
- Track nomenclature standardization
- Analyze discovery patterns

## 📊 Key Discoveries

Our analysis of 20 years of ICTV data revealed:

- **1,296.6%** increase in viral species (1,898 → 26,507)
- **5× acceleration** in discovery rate after 2015 (genomics revolution)
- **Peak discovery**: 6,433 species added in 2023 alone
- **Caudovirales clarification**: Order restructured, not abolished

## 🛠️ System Architecture

```
ICTV-git/
├── src/                    # Core library code
│   ├── parsers/           # MSL file parsers
│   ├── converters/        # Git conversion tools
│   ├── utils/             # Analysis utilities
│   └── community_tools/   # Web/API interfaces
├── scripts/               # CLI tools
├── data/                  # MSL Excel files
├── output/                # Generated git taxonomy
└── docs/                  # Documentation
```

## 📚 Documentation

- [Getting Started Guide](docs/getting-started.md)
- [API Reference](docs/api_usage_examples.md)
- [Dataset Migration Guide](docs/migration_guide.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas where we especially need help:
- Testing with different research workflows
- Integration with bioinformatics pipelines
- Visualization improvements
- Documentation and tutorials

## 📄 Citation

If you use ICTV-git in your research, please cite:

```bibtex
@software{ictv-git,
  author = {Handley, Scott},
  title = {ICTV-git: Git-based Viral Taxonomy Management},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  url = {https://github.com/shandley/ICTV-git}
}
```

Manuscript in preparation for submission to Nature Methods.

## 🔗 Links

- [ICTV Official Site](https://ictv.global)
- [Master Species Lists](https://ictv.global/msl)
- [Project Issues](https://github.com/shandley/ICTV-git/issues)

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