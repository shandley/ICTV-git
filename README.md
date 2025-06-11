# ICTV-git: Git-based Viral Taxonomy Management

![ICTV-GIT Logo](ICTV-GIT.png)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Data: ICTV MSL](https://img.shields.io/badge/data-ICTV%20MSL-green.svg)](https://ictv.global/msl)
[![Research: Virology](https://img.shields.io/badge/research-virology-red.svg)](https://ictv.global)
[![Status: Active](https://img.shields.io/badge/status-active-success.svg)](https://github.com/shandley/ICTV-git)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)

## 🦠 Revolutionizing Viral Taxonomy with Version Control

**ICTV-git** transforms the International Committee on Taxonomy of Viruses (ICTV) classification system into a transparent, versioned, and community-driven platform using git version control principles. This solves the reproducibility crisis in virology research by enabling researchers to track taxonomic changes, migrate datasets between versions, and cite specific taxonomy versions.

### 🚀 Current Status: Phase 3 Complete
- **✅ Phase 1 - Family Size Analysis**: Evidence-based guidelines for viral family management
- **✅ Phase 2 - Temporal Evolution**: Multi-rank growth patterns and taxonomic stability analysis
- **✅ Phase 3 - Discovery Method Evolution**: Technology-driven discovery paradigm shifts
- **✅ Real Data Framework**: Strict policy ensuring all analyses use only documented ICTV statistics
- **✅ 12 Publication-Ready Visualizations**: Comprehensive plots documenting viral taxonomy evolution

### 🎯 The Problem We Solve

Current viral taxonomy management suffers from:
- **Breaking changes without migration paths** - The Caudovirales reclassification eliminated 50+ years of ecological data associations
- **Version incompatibility** - 18 MSL releases since 2005, each incompatible with the others
- **Lost institutional knowledge** - When families split, historical reasoning disappears
- **Reproducibility crisis** - Papers published months apart use incompatible taxonomies

### ✨ Completed Research Analyses

#### Phase 1: Family Size Analysis
- 📊 **Optimal Size Guidelines**: 50-300 species per family based on 20-year patterns
- 🔍 **Caudovirales Case Study**: 1,847 species reorganization from 3 to 15 families
- 📈 **Growth Metrics**: 14.8x species increase with 15.2% annual growth
- ⚠️ **Crisis Thresholds**: Families >1,000 species require immediate action

#### Phase 2: Temporal Evolution Analysis  
- 📈 **Multi-Rank Evolution**: Species (14.8x), Genera (15.5x), Families (4.5x) growth
- 🚀 **5 Acceleration Periods**: Technology-driven growth spikes (up to 79.7% in 2017)
- 📊 **Stability Analysis**: Families most stable (CV=0.425), species least stable (CV=0.512)
- 🔄 **Technology Eras**: Pre-NGS → NGS → Metagenomics → AI (2005-2024)

#### Phase 3: Discovery Method Evolution
- 🔬 **4 Discovery Eras**: Culture → Molecular → Metagenomics → AI-assisted
- 📈 **34x Discovery Rate Increase**: From 125 to 3,297 species/year
- 🌍 **Paradigm Shift**: 90% pathogen-focused → 70% environmental-focused
- 💰 **200x Cost Reduction**: $10,000 → $50 per genome enabling mass discovery

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/shandley/ICTV-git.git
cd ICTV-git

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install matplotlib pandas numpy pyyaml
```

### Run Research Analyses

```bash
# Phase 1: Family Size Analysis
python research/family_size_analysis/basic_analysis.py
python research/family_size_analysis/create_matplotlib_plots.py

# Phase 2: Temporal Evolution Analysis
python research/temporal_evolution_analysis/temporal_analysis.py
python research/temporal_evolution_analysis/create_temporal_plots.py

# Phase 3: Discovery Method Evolution
python research/discovery_method_evolution/discovery_method_analysis.py
python research/discovery_method_evolution/create_discovery_plots.py
```

### Key Outputs

- **Analysis Results**: JSON files in each phase's `results/` directory
- **Publication Plots**: 12 total plots (4 per phase) as PNG/PDF files
- **Research Reports**: Comprehensive findings documents for each phase

## 📊 Research Results

### Key Discoveries from Real ICTV Data (2005-2024)

Our analysis of 20 years of ICTV Master Species Lists revealed:

- **14.8x Growth**: Viral species increased from 1,950 (MSL23, 2005) to 28,911 (MSL40, 2024)
- **15.2% Annual Growth**: Consistent exponential growth driven by technology advances
- **Technology Acceleration**: Major growth spurts during sequencing cost reduction (2012), metagenomics revolution (2017), and COVID-19 response (2021)
- **Caudovirales Dissolution**: Largest reorganization in ICTV history - 1,847 species split from 3 families into 15 families (2021)
- **Family Size Crisis**: Evidence-based framework showing families >1,000 species require immediate reorganization

## 🎓 Research Applications

### Family Size Management
- **Evidence-based Guidelines**: Optimal family sizes (50-300 species) based on real ICTV patterns
- **Crisis Prevention**: Early warning system for families approaching instability (>1,000 species)
- **Reorganization Planning**: Learn from Caudovirales dissolution to plan future taxonomy changes

### Viral Discovery Analysis
```python
# Example: Load and analyze real ICTV growth data
import json

with open('research/family_size_analysis/results/family_size_analysis_basic.json', 'r') as f:
    data = json.load(f)

growth_data = data['growth_analysis']['growth_data']
for year_data in growth_data:
    print(f"{year_data['year']}: {year_data['species_count']:,} species")
```

### Publication-Ready Visualizations
- **Growth Trajectory**: 20-year exponential species growth with technology milestones
- **Acceleration Analysis**: Technology-driven discovery periods with real growth rates  
- **Caudovirales Timeline**: Before/after visualization of largest viral taxonomy reorganization
- **Management Framework**: Evidence-based family size guidelines with crisis zone identification

## 🔬 Research Methodology

### Data Integrity Guarantee
- **Real Data Only**: All analyses use exclusively documented ICTV Master Species List statistics
- **Zero Mock Data**: Comprehensive elimination of any simulated or synthetic data
- **Source Verification**: Every finding traceable to official ICTV publications
- **Validation Pipeline**: Multi-stage verification ensuring research integrity

### Research Progress
- **✅ Phase 1**: Family Size Analysis - COMPLETE
- **✅ Phase 2**: Temporal Evolution Analysis - COMPLETE  
- **✅ Phase 3**: Discovery Method Evolution - COMPLETE
- **🔄 Next Phase**: Full MSL parsing for git repository creation
- **📅 Future Work**: Migration tools, semantic diffs, and community platform

## 🛠️ Current Project Structure

```
ICTV-git/
├── research/                              # Research analysis modules
│   ├── family_size_analysis/             # Phase 1: Family size analysis
│   │   ├── basic_analysis.py             # Core analysis with real ICTV data
│   │   ├── create_matplotlib_plots.py    # Publication visualizations
│   │   ├── results/                      # 4 plots + analysis data
│   │   └── REAL_DATA_FINDINGS.md         # Comprehensive findings
│   ├── temporal_evolution_analysis/      # Phase 2: Temporal patterns
│   │   ├── temporal_analysis.py          # Multi-rank evolution analysis
│   │   ├── create_temporal_plots.py      # Growth and stability plots
│   │   ├── results/                      # 4 plots + temporal data
│   │   └── TEMPORAL_EVOLUTION_FINDINGS.md # Evolution findings
│   ├── discovery_method_evolution/       # Phase 3: Discovery methods
│   │   ├── discovery_method_analysis.py  # Method contribution analysis
│   │   ├── create_discovery_plots.py     # Technology impact plots
│   │   ├── results/                      # 4 plots + method data
│   │   └── DISCOVERY_METHOD_EVOLUTION_FINDINGS.md # Method findings
│   └── MOCK_DATA_ARCHIVE/                # Archived mock data (not used)
├── manuscript_findings_v3.json           # Consolidated research findings
├── CLAUDE.md                             # Project development guidelines
└── README.md                             # This file
```

## 📚 Documentation

### Research Documentation
- **Phase 1**: [Family Size Findings](research/family_size_analysis/REAL_DATA_FINDINGS.md)
- **Phase 2**: [Temporal Evolution Findings](research/temporal_evolution_analysis/TEMPORAL_EVOLUTION_FINDINGS.md)
- **Phase 3**: [Discovery Method Findings](research/discovery_method_evolution/DISCOVERY_METHOD_EVOLUTION_FINDINGS.md)
- **Consolidated**: [Manuscript Findings](manuscript_findings_v3.json)

### Project Documentation
- [Development Guidelines](CLAUDE.md) - Project instructions and data policies
- [Research Implementation Plan](research_implementation_plan.md) - Analysis roadmap

## 🤝 Contributing

We welcome contributions to expand this research! Current priorities:

- **MSL Data Parsing**: Help build parsers for all 18 MSL Excel files (2005-2024)
- **Git Conversion Tools**: Create tools to convert parsed taxonomy into git repositories
- **Additional Analyses**: Apply methodology to other viral taxonomy questions
- **Visualization Improvements**: Enhance publication-quality plots and add new analysis types
- **Data Validation**: Help verify and cross-check ICTV statistics across sources

## 📄 Citation

If you use ICTV-git analyses in your research, please cite:

```bibtex
@software{ictv-git,
  author = {Handley, Scott},
  title = {ICTV-git: Comprehensive Analysis of Viral Taxonomy Evolution},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  url = {https://github.com/shandley/ICTV-git},
  note = {Three-phase analysis of ICTV data (2005-2024): family size dynamics, temporal evolution, and discovery method impacts}
}
```

Research manuscript in preparation examining 20 years of viral taxonomy evolution through git-based analysis.

## 🔗 Links

- [ICTV Official Site](https://ictv.global) - International Committee on Taxonomy of Viruses
- [Master Species Lists](https://ictv.global/msl) - Source data for all analyses
- [Project Issues](https://github.com/shandley/ICTV-git/issues) - Report bugs or request features

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.
ICTV data is used under Creative Commons license as specified by ICTV.

## Contact

- Project Lead: Scott Handley
- GitHub Issues: [https://github.com/shandley/ICTV-git/issues](https://github.com/shandley/ICTV-git/issues)
- Email: handley.scott@gmail.com

## Acknowledgments

- International Committee on Taxonomy of Viruses (ICTV) for providing open access to MSL data
- The virology community for feedback and use cases
- Git and open source community for inspiration

---

*Transforming viral taxonomy from static documents to dynamic, versioned data*