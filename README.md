# ICTV-git: Git-based Viral Taxonomy Management

<p align="center">
  <img src="ICTV-GIT.png" alt="ICTV-git Logo" width="300">
</p>

<p align="center">
  <a href="https://github.com/shandley/ICTV-git/actions"><img src="https://img.shields.io/badge/build-passing-brightgreen.svg" alt="Build Status"></a>
  <a href="https://github.com/shandley/ICTV-git/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python Version"></a>
  <a href="https://github.com/shandley/ICTV-git/issues"><img src="https://img.shields.io/github/issues/shandley/ICTV-git.svg" alt="Issues"></a>
  <a href="https://shandley.github.io/ICTV-git/"><img src="https://img.shields.io/badge/docs-online-blue.svg" alt="Documentation"></a>
</p>

<p align="center">
  <strong>📚 <a href="https://shandley.github.io/ICTV-git/">View Documentation</a> | 🦠 <a href="https://github.com/shandley/ICTV-git">GitHub Repository</a></strong>
</p>

## 🦠 Revolutionizing Viral Taxonomy with Version Control

**ICTV-git** transforms the International Committee on Taxonomy of Viruses (ICTV) classification system into a transparent, versioned, and community-driven platform using git version control principles. This solves the reproducibility crisis in virology research by enabling researchers to track taxonomic changes, migrate datasets between versions, and cite specific taxonomy versions.

### 🚀 Major Achievements
- **✅ Complete 20-Year Git Repository**: All 18 MSL releases (2005-2024) preserved with full history
- **✅ Production REST API**: 30+ endpoints for programmatic access to all taxonomy data
- **✅ AI-Powered Features**: Natural language queries, classification suggestions, database sync
- **✅ Advanced Search**: Faceted search with performance optimization across 28,911 species
- **✅ Historical Analysis**: Track any virus through 20 years of taxonomic evolution

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
- 🤖 **AI Integration**: Natural language queries about taxonomy history
- 🔗 **Database Sync**: Real-time synchronization with GenBank, RefSeq, UniProt

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/shandley/ICTV-git.git
cd ICTV-git

# Create virtual environment (recommended)
python3 -m venv ictv_api_env
source ictv_api_env/bin/activate  # On Windows: ictv_api_env\Scripts\activate

# Install API dependencies
pip install -r requirements_api.txt

# Download all MSL data (or use existing data/)
python scripts/download_msl.py
```

### Basic Usage

```bash
# Build complete 20-year git repository
python scripts/complete_20_year_conversion.py

# Start the production REST API server
python scripts/run_api_server.py --dev
# API available at: http://localhost:8000
# Interactive docs: http://localhost:8000/docs

# Example API queries
curl http://localhost:8000/taxonomy/families
curl http://localhost:8000/historical/timeline
curl -X POST http://localhost:8000/ai/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What happened to Caudovirales in 2019?"}'

# Start the interactive web browser
streamlit run scripts/run_taxonomy_browser.py

# Compare two versions
python src/community_tools/version_comparator.py output/ictv_complete_20_year_taxonomy --version1 MSL35 --version2 MSL40
```

## 📸 Screenshots

### Interactive Taxonomy Browser
Browse viral taxonomy across 20 years with interactive visualizations:
- Hierarchical tree exploration
- Statistical dashboards
- Evolution timelines
- Advanced search and filtering

### Production REST API
Comprehensive programmatic access with 30+ endpoints:
- **Taxonomy API**: Species lookup, family hierarchies, validation
- **Historical API**: 20-year timeline, release comparisons, evolution tracking
- **AI API**: Natural language queries, classification suggestions, stability analysis
- **Search API**: Advanced search, faceted filtering, performance optimization
- **Documentation**: Auto-generated OpenAPI/Swagger at `/docs`

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

# Get species evolution across 20 years
response = requests.get("http://localhost:8000/historical/species/Tobacco mosaic virus/history")
history = response.json()

# Natural language query
nlq_response = requests.post("http://localhost:8000/ai/query", 
    json={"query": "How has Coronaviridae family changed since COVID?"})

# Compare releases
comparison = requests.get("http://localhost:8000/historical/compare/MSL35/MSL40")
print(f"Files changed: {comparison.json()['changes']['total_changes']}")
```

### For Taxonomists
- Visualize the impact of classification proposals
- Identify unstable taxonomic groups
- Track nomenclature standardization
- Analyze discovery patterns

## 📊 Key Discoveries

Our analysis of 20 years of ICTV data revealed:

- **1,383%** increase in viral species (1,950 → 28,911 in MSL23-MSL40)
- **7 distinct eras** of taxonomic evolution identified
- **Historic Caudovirales dissolution** (2019): 1,847+ species reclassified
- **COVID-19 response** (2020): Emergency taxonomy protocols documented
- **AI era** (2023-2024): Machine learning integration with 7,560 new species

## 🛠️ System Architecture

```
ICTV-git/
├── src/                           # Core library code
│   ├── parsers/                  # MSL file parsers
│   ├── converters/               # Git conversion tools
│   ├── utils/                    # Analysis utilities
│   ├── community_tools/          # Web/API interfaces
│   ├── advanced_features/        # AI & NLP capabilities
│   └── api/                      # REST API implementation
├── scripts/                      # CLI tools
├── data/                         # MSL Excel files
├── output/
│   └── ictv_complete_20_year_taxonomy/  # Complete git repository
├── tests/                        # Comprehensive test suite
└── docs/                         # Documentation
```

## 📚 Documentation

- [Getting Started Guide](docs/getting-started.md)
- [API Reference](docs/api_usage_examples.md) - 30+ REST endpoints
- [Dataset Migration Guide](docs/migration_guide.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Complete API Documentation](API_IMPLEMENTATION_COMPLETE.md)
- [Historical Conversion Guide](COMPLETE_20_YEAR_HISTORICAL_CONVERSION.md)

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas where we especially need help:
- Testing with different research workflows
- Integration with bioinformatics pipelines
- Visualization improvements
- Documentation and tutorials
- Mobile applications using our REST API
- Machine learning models for taxonomy prediction

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
- [API Documentation](http://localhost:8000/docs) (when server running)

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