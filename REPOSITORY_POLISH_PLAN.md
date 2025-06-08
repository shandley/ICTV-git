# GitHub Repository Polish Plan for Community Release

## Overview
Transform the current development repository into a professional, community-ready resource that researchers can easily discover, understand, and use.

## 1. Repository Structure Optimization

### Current State
```
ICTV-git/
├── Various scripts and outputs mixed together
├── Development artifacts
├── Incomplete documentation
└── No clear entry point
```

### Target State
```
ICTV-git/
├── README.md                    # Compelling overview with quick start
├── INSTALL.md                   # Detailed installation guide
├── CITATION.cff                 # GitHub citation file
├── LICENSE                      # Already exists (MIT)
├── CONTRIBUTING.md              # Community contribution guide
├── CODE_OF_CONDUCT.md          # Community standards
├── .github/                     # GitHub-specific files
│   ├── workflows/              # CI/CD automation
│   ├── ISSUE_TEMPLATE/         # Bug report & feature templates
│   └── PULL_REQUEST_TEMPLATE.md
├── docs/                        # Comprehensive documentation
│   ├── getting-started.md      # New user guide
│   ├── api-reference.md        # API documentation
│   ├── tutorials/              # Step-by-step tutorials
│   └── examples/               # Example notebooks
├── src/                         # Clean source code
├── tests/                       # Unit tests
├── scripts/                     # User-facing scripts only
├── data/                        # Sample data (not full archive)
└── examples/                    # Example usage patterns
```

## 2. Professional README.md

### Structure
```markdown
# ICTV-git: Git-based Viral Taxonomy Management

<p align="center">
  <img src="docs/images/logo.png" width="400" alt="ICTV-git logo">
</p>

<p align="center">
  <a href="https://github.com/shandley/ICTV-git/actions"><img src="https://github.com/shandley/ICTV-git/workflows/tests/badge.svg" alt="Tests"></a>
  <a href="https://pypi.org/project/ictv-git/"><img src="https://img.shields.io/pypi/v/ictv-git.svg" alt="PyPI"></a>
  <a href="https://ictv-git.readthedocs.io/"><img src="https://readthedocs.org/projects/ictv-git/badge/?version=latest" alt="Documentation"></a>
  <a href="https://doi.org/10.5281/zenodo.XXXXXX"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXX.svg" alt="DOI"></a>
</p>

## 🦠 Revolutionizing Viral Taxonomy with Version Control

**ICTV-git** applies software version control principles to viral taxonomy, solving the reproducibility crisis in virology research. Track 20 years of taxonomic evolution, migrate datasets between versions, and explore viral diversity interactively.

### ✨ Key Features

- 📊 **Complete History**: 20 years of ICTV taxonomy (2005-2024) under git version control
- 🔄 **Automatic Migration**: Update datasets between any taxonomy versions
- 🌐 **Multiple Interfaces**: Web browser, REST API, Python library
- 📖 **Smart Citations**: Generate version-specific citations with git commits
- 🔍 **Semantic Diffs**: Understand what changed and why

### 🚀 Quick Start

```bash
# Install
pip install ictv-git

# Download taxonomy data
ictv-git download --all

# Start web interface
ictv-git browse

# Start API server
ictv-git api
```

### 📸 Screenshots

[Interactive taxonomy browser image]
[API documentation image]
[Version comparison visualization]

### 🎯 Use Cases

#### For Virologists
- Track how your virus classification changed over time
- Update old datasets to current taxonomy
- Generate proper citations for specific versions

#### For Bioinformaticians  
- Programmatic access via REST API
- Bulk download in multiple formats
- Version-controlled reproducible analyses

#### For Taxonomists
- Visualize reorganization patterns
- Compare proposal impacts
- Track nomenclature evolution

### 📚 Documentation

- [Getting Started Guide](docs/getting-started.md)
- [API Reference](docs/api-reference.md)
- [Migration Tutorial](docs/tutorials/dataset-migration.md)
- [Citation Guide](docs/tutorials/citations.md)

### 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### 📄 Citation

If you use ICTV-git in your research, please cite:

```bibtex
@software{ictv-git,
  author = {Handley, Scott},
  title = {ICTV-git: Git-based Viral Taxonomy Management},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/shandley/ICTV-git}
}
```

### 📊 Impact

- **26,507** virus species tracked
- **18** MSL versions preserved  
- **1,296%** growth documented
- **5x** discovery acceleration quantified

### 🔗 Links

- [ICTV Official Site](https://ictv.global)
- [Paper (in review)](link-to-preprint)
- [Online Demo](link-to-demo)
```

## 3. Installation & Setup Improvements

### Create setup.py Enhancement
```python
setup(
    name="ictv-git",
    version="1.0.0",
    description="Git-based viral taxonomy management system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Scott Handley",
    author_email="email@example.com",
    url="https://github.com/shandley/ICTV-git",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "pyyaml>=5.4",
        "openpyxl>=3.0.9",
        "xlrd>=2.0.1",
        "requests>=2.26.0",
        "click>=8.0.0",
        "tqdm>=4.62.0",
        "gitpython>=3.1.24",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "streamlit>=1.10.0",
        "plotly>=5.3.0",
        "matplotlib>=3.4.0",
        "seaborn>=0.11.0",
        "networkx>=2.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-cov>=2.12.0",
            "black>=21.9b0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "docs": [
            "sphinx>=4.2.0",
            "sphinx-rtd-theme>=1.0.0",
            "sphinx-autodoc-typehints>=1.12.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ictv-git=ictv_git.cli:main",
        ],
    },
)
```

### Create requirements.txt files
- `requirements.txt` - Core dependencies only
- `requirements-dev.txt` - Development dependencies
- `requirements-docs.txt` - Documentation building

## 4. Documentation Enhancement

### Create Sphinx Documentation
```
docs/
├── _static/
├── _templates/
├── conf.py
├── index.rst
├── installation.rst
├── quickstart.rst
├── api/
│   ├── parsers.rst
│   ├── converters.rst
│   └── community_tools.rst
├── tutorials/
│   ├── basic_usage.rst
│   ├── dataset_migration.rst
│   ├── api_examples.rst
│   └── citation_guide.rst
└── development/
    ├── contributing.rst
    └── architecture.rst
```

### Host on ReadTheDocs
- Connect GitHub repository
- Configure `.readthedocs.yml`
- Enable automatic builds

## 5. Example Notebooks

### Create Jupyter Notebooks
```
examples/
├── 01_getting_started.ipynb
├── 02_exploring_taxonomy.ipynb
├── 03_version_comparison.ipynb
├── 04_dataset_migration.ipynb
├── 05_api_usage.ipynb
├── 06_visualization_examples.ipynb
└── 07_research_applications.ipynb
```

### Include Binder Support
- Add `environment.yml` for Binder
- Create "Launch Binder" button in README

## 6. Testing & CI/CD

### GitHub Actions Workflows

#### `.github/workflows/tests.yml`
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10']
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
        pip install -e .
    - name: Run tests
      run: pytest tests/ --cov=src --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

#### `.github/workflows/docs.yml`
```yaml
name: Documentation
on:
  push:
    branches: [main]
jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build docs
      run: |
        pip install -r requirements-docs.txt
        cd docs && make html
```

## 7. Community Files

### CONTRIBUTING.md
```markdown
# Contributing to ICTV-git

We love your input! We want to make contributing as easy and transparent as possible.

## Development Process
1. Fork the repo
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Code Style
- Use Black for Python formatting
- Follow PEP 8
- Add type hints where possible
- Write docstrings for all functions

## Testing
- Add tests for new features
- Ensure all tests pass
- Maintain >80% code coverage
```

### CODE_OF_CONDUCT.md
- Use standard Contributor Covenant
- Establish welcoming community standards

### Issue Templates
```
.github/ISSUE_TEMPLATE/
├── bug_report.md
├── feature_request.md
└── question.md
```

## 8. Data Management

### Create Sample Dataset
```
data/
├── sample/
│   ├── MSL38_sample.xlsx  # 100 species subset
│   └── README.md          # Explains sample data
└── README.md              # Points to full data download
```

### Set up Git LFS
- Configure for large Excel files
- Add `.gitattributes` for proper handling

## 9. Package Distribution

### PyPI Release Preparation
1. Register package name on PyPI
2. Build distribution files
3. Upload to TestPyPI first
4. Create GitHub release workflow

### Conda Package
- Create conda-forge recipe
- Enable bioconda channel

## 10. Marketing & Discoverability

### GitHub Topics
Add relevant topics:
- `virology`
- `taxonomy`
- `bioinformatics`
- `git`
- `reproducible-research`
- `viral-genomics`

### Social Media Presence
- Create Twitter thread announcing release
- Post on relevant subreddits (r/bioinformatics, r/virology)
- Share in bioinformatics Slack/Discord communities

### Academic Presence
- Create Zenodo DOI
- Submit to bio.tools registry
- Add to ELIXIR registry
- Present at conferences

## Implementation Timeline

### Week 1: Core Polish
- [ ] Restructure repository
- [ ] Create professional README
- [ ] Set up CI/CD

### Week 2: Documentation
- [ ] Write comprehensive docs
- [ ] Create example notebooks
- [ ] Build API reference

### Week 3: Community Setup
- [ ] Add all community files
- [ ] Create issue templates
- [ ] Set up discussions

### Week 4: Release
- [ ] Final testing
- [ ] PyPI release
- [ ] Announcement campaign

## Success Metrics
- 100+ GitHub stars in first month
- 10+ forks for development
- 5+ community contributions
- Adoption by 3+ research groups
- Citation in 2+ preprints

This plan transforms the repository from a research project into a professional tool that the scientific community can confidently adopt and contribute to.