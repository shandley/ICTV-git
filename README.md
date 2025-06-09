# ICTV-git: Git-based Viral Taxonomy Management

## 🦠 Revolutionizing Viral Taxonomy with Version Control

**ICTV-git** transforms the International Committee on Taxonomy of Viruses (ICTV) classification system into a transparent, versioned, and community-driven platform using git version control principles. This solves the reproducibility crisis in virology research by enabling researchers to track taxonomic changes, migrate datasets between versions, and cite specific taxonomy versions.

### 🚀 Current Status: Phase 1 Complete
- **✅ Family Size Analysis**: Complete analysis of 20-year ICTV growth patterns using real MSL data
- **✅ Caudovirales Case Study**: Documented the largest viral taxonomy reorganization in history  
- **✅ Publication-Quality Visualizations**: 4 comprehensive plots showing growth trends and reorganization events
- **✅ Real Data Framework**: Strict policy ensuring all analyses use only documented ICTV statistics
- **✅ Data Integrity Pipeline**: Comprehensive validation and verification of all research findings

### 🎯 The Problem We Solve

Current viral taxonomy management suffers from:
- **Breaking changes without migration paths** - The Caudovirales reclassification eliminated 50+ years of ecological data associations
- **Version incompatibility** - 18 MSL releases since 2005, each incompatible with the others
- **Lost institutional knowledge** - When families split, historical reasoning disappears
- **Reproducibility crisis** - Papers published months apart use incompatible taxonomies

### ✨ Current Features (Phase 1)

- 📊 **Family Size Analysis**: Evidence-based guidelines for viral family management
- 📈 **Growth Pattern Analysis**: 14.8x species growth over 20 years with technology-driven acceleration periods
- 🔍 **Caudovirales Case Study**: Detailed analysis of 2021 dissolution affecting 1,847 species
- 🎨 **Publication Visualizations**: Professional matplotlib plots ready for manuscript inclusion
- 📋 **Real Data Validation**: Comprehensive verification ensuring no mock or simulated data
- 🔬 **Research Framework**: Evidence-based methodology for viral taxonomy analysis

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

### Run Family Size Analysis

```bash
# Generate family size analysis with real ICTV data
python research/family_size_analysis/basic_analysis.py

# Create publication-quality plots
python research/family_size_analysis/create_matplotlib_plots.py

# View results
ls research/family_size_analysis/results/
```

### Key Outputs

- **Analysis Results**: `research/family_size_analysis/results/family_size_analysis_basic.json`
- **Publication Plots**: 4 PNG/PDF files in `research/family_size_analysis/results/`
- **Research Findings**: `research/family_size_analysis/REAL_DATA_FINDINGS.md`

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

### Current Research Status
- **Phase 1 Complete**: Family size analysis with comprehensive visualizations
- **Next Phase**: Full MSL parsing for complete taxonomic git repository creation
- **Future Work**: Migration tools, semantic diffs, and community platform development

## 🛠️ Current Project Structure

```
ICTV-git/
├── research/                      # Research analysis modules
│   ├── family_size_analysis/     # Complete family size analysis
│   │   ├── basic_analysis.py     # Real ICTV data analysis
│   │   ├── create_matplotlib_plots.py  # Publication visualizations
│   │   ├── results/              # Generated plots and data
│   │   └── REAL_DATA_FINDINGS.md # Research findings
│   └── MOCK_DATA_ARCHIVE/        # Archived mock data (not used)
├── manuscript_findings_v3.json   # Real research findings
├── CLAUDE.md                     # Project instructions
└── README.md                     # This file
```

## 📚 Documentation

### Current Documentation
- [Research Findings](research/family_size_analysis/REAL_DATA_FINDINGS.md) - Phase 1 results
- [Project Instructions](CLAUDE.md) - Complete development guidelines
- [Manuscript Findings](manuscript_findings_v3.json) - Research analysis summary

### Analysis Scripts
- [Family Size Analysis](research/family_size_analysis/basic_analysis.py) - Core analysis
- [Visualization Generator](research/family_size_analysis/create_matplotlib_plots.py) - Publication plots

## 🤝 Contributing

We welcome contributions to expand this research! Current priorities:

- **MSL Data Parsing**: Help build parsers for all 18 MSL Excel files (2005-2024)
- **Git Conversion Tools**: Create tools to convert parsed taxonomy into git repositories
- **Additional Analyses**: Apply methodology to other viral taxonomy questions
- **Visualization Improvements**: Enhance publication-quality plots and add new analysis types
- **Data Validation**: Help verify and cross-check ICTV statistics across sources

## 📄 Citation

If you use ICTV-git family size analysis in your research, please cite:

```bibtex
@software{ictv-git-family-analysis,
  author = {Handley, Scott},
  title = {ICTV-git: Family Size Analysis of Viral Taxonomy Evolution},
  year = {2024},
  publisher = {GitHub},
  journal = {GitHub repository},
  url = {https://github.com/shandley/ICTV-git},
  note = {Real ICTV data analysis (2005-2024)}
}
```

Research manuscript in preparation focusing on viral taxonomy management and family size optimization.

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
- Email: [Contact information]

## Acknowledgments

- International Committee on Taxonomy of Viruses (ICTV) for providing open access to MSL data
- The virology community for feedback and use cases
- Git and open source community for inspiration

---

*Transforming viral taxonomy from static documents to dynamic, versioned data*