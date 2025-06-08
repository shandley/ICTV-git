# Getting Started with ICTV-git

Welcome to ICTV-git! This guide will help you get up and running with the git-based viral taxonomy system.

## Prerequisites

Before you begin, ensure you have:
- Python 3.8 or higher
- Git installed on your system
- Basic familiarity with command line operations
- ~2GB of free disk space for the complete taxonomy data

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/shandley/ICTV-git.git
cd ICTV-git
```

### 2. Set Up Python Environment

We recommend using a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Download Taxonomy Data

You have two options:

**Option A: Download All Historical Data (Recommended)**
```bash
python scripts/download_msl.py
```
This downloads all MSL files from 2005-2024 (~500MB).

**Option B: Download Specific Versions**
```bash
python scripts/download_msl.py --versions MSL38 MSL37 MSL36
```

## Quick Start Tutorial

### Step 1: Convert MSL to Git Format

Convert an MSL Excel file to git-structured YAML files:

```bash
python scripts/convert_msl_to_git.py data/MSL38.xlsx
```

This creates a hierarchical directory structure in `output/git_taxonomy/MSL38/` with one YAML file per species.

### Step 2: Explore the Data

#### Using the Interactive Browser

Start the web interface:

```bash
streamlit run scripts/run_taxonomy_browser.py
```

Open your browser to http://localhost:8501 to:
- Browse the taxonomic tree
- Search for specific viruses
- View statistics and visualizations
- Compare versions

#### Using the REST API

Start the API server:

```bash
python scripts/run_taxonomy_api.py
```

The API will be available at http://localhost:8000 with documentation at http://localhost:8000/docs.

Example API calls:
```bash
# Get species information
curl http://localhost:8000/api/v1/species/MSL38/Tobacco%20mosaic%20virus

# Search for viruses
curl "http://localhost:8000/api/v1/search?q=coronavirus&version=MSL38"

# Compare versions
curl http://localhost:8000/api/v1/compare/MSL37/MSL38
```

### Step 3: Track Changes Between Versions

Compare any two MSL versions:

```bash
python -m src.community_tools.version_comparator output/git_taxonomy \
    --version1 MSL37 --version2 MSL38 --output comparison_report.json
```

This generates:
- JSON report with all changes
- Markdown summary for human reading
- Statistics on additions, removals, and reclassifications

### Step 4: Migrate Your Dataset

If you have research data using an older taxonomy version:

```python
from src.utils.migration_mapper import DatasetMigrator

# Initialize migrator
migrator = DatasetMigrator("output/git_taxonomy")

# Migrate your data
old_data = [
    {"virus": "Escherichia phage T4", "family": "Myoviridae"},
    # ... more entries
]

new_data = migrator.migrate_dataset(
    old_data, 
    from_version="MSL36", 
    to_version="MSL38"
)

# View migration report
print(migrator.get_migration_summary())
```

### Step 5: Generate Citations

Generate proper citations for reproducibility:

```python
from src.community_tools.citation_generator import CitationGenerator

generator = CitationGenerator("output/git_taxonomy")

# Cite a specific species
citation = generator.cite_species(
    "Severe acute respiratory syndrome-related coronavirus",
    "MSL38",
    format="bibtex"  # or "standard", "ris", "git"
)
print(citation)
```

## Common Use Cases

### 1. Finding What Happened to Your Virus

```python
# Check if Caudovirales still exists
from src.community_tools.taxonomy_browser import TaxonomyBrowser

browser = TaxonomyBrowser("output/git_taxonomy")
# Use the browser to track changes
```

### 2. Updating a Paper's Dataset

When reviewers ask you to update to the latest taxonomy:

1. Identify your current MSL version
2. Use the migration tools to update
3. Generate a citation for both versions
4. Document the changes in your methods

### 3. Analyzing Taxonomic Stability

```python
# Which families are most stable?
from src.utils.stability_analyzer import StabilityAnalyzer

analyzer = StabilityAnalyzer("output/git_taxonomy")
stability_report = analyzer.analyze_family_stability()
```

## Next Steps

Now that you have the basics working:

1. **Explore the Examples**: Check out the `examples/` directory for Jupyter notebooks
2. **Read the API Documentation**: See `docs/api_usage_examples.md`
3. **Learn About Migration**: Read `docs/migration_guide.md`
4. **Contribute**: See `CONTRIBUTING.md` to help improve the project

## Troubleshooting

### Common Issues

**ImportError when running scripts**
```bash
# Make sure you're in the project root and have installed requirements
cd /path/to/ICTV-git
pip install -r requirements.txt
```

**"MSL file not found" errors**
```bash
# Download the data first
python scripts/download_msl.py
```

**Port already in use (API or Browser)**
```bash
# Change the port
python scripts/run_taxonomy_api.py --port 8001
# or
streamlit run scripts/run_taxonomy_browser.py --server.port 8502
```

### Getting Help

- Check existing [GitHub Issues](https://github.com/shandley/ICTV-git/issues)
- Read the [FAQ](docs/faq.md)
- Open a new issue with the bug report template

## Video Tutorials

Coming soon:
- [ ] 5-minute quick start
- [ ] Deep dive into version comparison
- [ ] Migration workflow walkthrough
- [ ] API usage for developers

## Community

Join the discussion:
- GitHub Discussions (coming soon)
- Twitter: #ICTVgit
- Email list: (coming soon)

Happy exploring! 🦠