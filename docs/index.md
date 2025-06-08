# ICTV-git Documentation

Welcome to the ICTV-git documentation! This project revolutionizes viral taxonomy management by applying git version control principles to the International Committee on Taxonomy of Viruses (ICTV) classification system.

## What is ICTV-git?

ICTV-git transforms static Excel-based taxonomy into a dynamic, versioned system that enables:

- 📊 **Historical Tracking**: Access any taxonomy version from 2005-2024
- 🔄 **Automated Migration**: Update datasets between incompatible versions
- 🔍 **Semantic Analysis**: Understand what changed and why
- 📖 **Proper Citations**: Generate version-specific references
- 🌐 **Multiple Interfaces**: Web browser, REST API, Python library

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
- REST API with 10+ endpoints
- Python library for direct integration
- Bulk data export (JSON, CSV, YAML)
- Command-line tools

## Installation

```bash
# Clone the repository
git clone https://github.com/shandley/ICTV-git.git
cd ICTV-git

# Install dependencies
pip install -r requirements.txt

# Download taxonomy data
python scripts/download_msl.py
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

- **1,296.6%** increase in viral species
- **5× acceleration** in discovery rate after 2015
- **Peak year**: 6,433 species added in 2023
- **Caudovirales**: Restructured, not abolished

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