# Changelog

All notable changes to ICTV-git will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Complete test suite for parsers, converters, comparators, and API
- Security policy for vulnerability reporting
- Development setup automation script
- Pre-commit hooks for code quality
- Modern Python packaging with pyproject.toml

## [1.0.0] - 2024-06-08

### Added
- Initial public release
- Complete MSL parser supporting 20 years of ICTV data (2005-2024)
- Git-based taxonomy structure with full version control
- Version comparison tools with fuzzy rename detection
- Interactive Streamlit-based taxonomy browser
- REST API with comprehensive endpoints
- Citation generator supporting multiple formats
- Sample dataset for quick testing
- Comprehensive documentation and examples
- GitHub Actions for CI/CD
- Professional repository structure

### Key Features
- Parse and convert all MSL files from MSL16 to MSL40
- Track 26,507 viral species across 20 years
- Identify reclassifications, restructures, and nomenclature changes
- Generate git-tracked citations for reproducible research
- Provide programmatic access via REST API
- Interactive web interface for exploring taxonomy evolution

### Research Findings
- 1,296.6% increase in viral species (1,898 → 26,507)
- 5× acceleration in discovery rate after 2015
- Peak discovery of 6,433 species in 2023
- Caudovirales order restructured, not abolished

## [0.1.0] - 2024-05-01 (Pre-release)

### Added
- Basic MSL parsing functionality
- Initial git conversion tools
- Prototype visualization scripts
- Core data structures

---

For detailed release notes, see the [GitHub Releases](https://github.com/shandley/ICTV-git/releases) page.