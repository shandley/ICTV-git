# ICTV-git Documentation

Welcome to the ICTV-git documentation! This project revolutionizes viral taxonomy management by applying git version control principles to the International Committee on Taxonomy of Viruses (ICTV) classification system.

## 🚀 Major Achievements

- **✅ Complete 20-Year Git Repository**: All 18 MSL releases (2005-2024) preserved with full history
- **✅ Production REST API**: 30+ endpoints for programmatic access to all taxonomy data
- **✅ AI-Powered Features**: Natural language queries, classification suggestions, database sync
- **✅ Advanced Search**: Faceted search with performance optimization across 28,911 species
- **✅ Historical Analysis**: Track any virus through 20 years of taxonomic evolution

## What is ICTV-git?

ICTV-git transforms static Excel-based taxonomy into a dynamic, versioned system that enables:

- 📊 **Historical Tracking**: Access any taxonomy version from 2005-2024
- 🔄 **Automated Migration**: Update datasets between incompatible versions
- 🔍 **Semantic Analysis**: Understand what changed and why
- 📖 **Proper Citations**: Generate version-specific references
- 🌐 **Multiple Interfaces**: Web browser, REST API, Python library
- 🤖 **AI Integration**: Natural language queries about taxonomy history
- 🔗 **Database Sync**: Real-time synchronization with GenBank, RefSeq, UniProt

## Quick Links

- [Getting Started](getting-started.md) - Installation and first steps
- [API Reference](api_usage_examples.md) - REST API documentation
- [Migration Guide](migration_guide.md) - Update datasets between versions
- [Validation Guide](validation_guide.md) - Data quality and validation
- [Examples](https://github.com/shandley/ICTV-git/tree/main/examples) - Code examples

## Key Features

### 1. Complete Historical Archive
- 18 MSL versions (2005-2024)
- 26,507 virus species
- Full taxonomic hierarchy preserved
- Git commits for every change

### 2. Research Tools
- **Interactive Browser**: Explore taxonomy visually
- **Version Comparison**: See what changed between releases
- **Migration Tools**: Update your research data automatically
- **Citation Generator**: Create proper academic references

### 3. Programmatic Access
- REST API with 30+ endpoints across 4 modules
- AI-powered natural language queries
- Python library for direct integration
- Bulk data export (JSON, CSV, YAML)
- Command-line tools
- Auto-generated API documentation

## Installation

```bash
# Clone the repository
git clone https://github.com/shandley/ICTV-git.git
cd ICTV-git

# Create virtual environment (recommended)
python3 -m venv ictv_api_env
source ictv_api_env/bin/activate  # On Windows: ictv_api_env\Scripts\activate

# Install API dependencies
pip install -r requirements_api.txt

# Build complete 20-year git repository
python scripts/complete_20_year_conversion.py

# Start REST API server
python scripts/run_api_server.py --dev
```

## Quick Example

```python
# Track a virus through history
from src.community_tools.taxonomy_browser import TaxonomyBrowser

browser = TaxonomyBrowser("output/git_taxonomy")
history = browser.get_species_history("Tobacco mosaic virus")

# Compare two versions
from src.community_tools.version_comparator import VersionComparator

comparator = VersionComparator("output/git_taxonomy")
changes = comparator.compare_versions("MSL37", "MSL38")
print(f"Species added: {len(changes['added'])}")
print(f"Species reclassified: {len(changes['reclassified'])}")
```

## Use Cases

### For Virologists
- Track how your virus has been classified over 20 years
- Understand the impact of major reorganizations
- Update legacy datasets to current taxonomy

### For Bioinformaticians
- Integrate taxonomy versioning into pipelines
- Access any version via REST API
- Ensure reproducible analyses

### For Database Maintainers
- Automated migration between versions
- Validation tools for data quality
- Complete audit trail

## Documentation Sections

1. **[Getting Started](getting-started.md)**
   - Installation guide
   - Basic usage tutorial
   - Common workflows

2. **[API Documentation](api_usage_examples.md)**
   - REST API endpoints
   - Authentication
   - Code examples

3. **[Data Management](migration_guide.md)**
   - Migration between versions
   - Validation procedures
   - Quality scoring

4. **[Development](../CONTRIBUTING.md)**
   - Contributing guidelines
   - Architecture overview
   - Testing procedures

## Key Discoveries

Our analysis of 20 years of ICTV data revealed:

- **1,383%** increase in viral species (1,950 → 28,911 in MSL23-MSL40)
- **7 distinct eras** of taxonomic evolution identified
- **Historic Caudovirales dissolution** (2019): 1,847+ species reclassified
- **COVID-19 response** (2020): Emergency taxonomy protocols documented
- **AI era** (2023-2024): Machine learning integration with 7,560 new species

## Support

- [GitHub Issues](https://github.com/shandley/ICTV-git/issues) - Bug reports and features
- [Discussions](https://github.com/shandley/ICTV-git/discussions) - Community support
- [ICTV Official](https://ictv.global) - Official taxonomy information

## Citation

If you use ICTV-git in your research, please cite:

```bibtex
@software{ictv-git,
  author = {Handley, Scott},
  title = {ICTV-git: Git-based Viral Taxonomy Management},
  year = {2024},
  url = {https://github.com/shandley/ICTV-git}
}
```

## License

This project is licensed under the MIT License. ICTV data is used under Creative Commons license.