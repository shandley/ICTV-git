# MOCK DATA ARCHIVE

**⚠️ WARNING: This directory contains MOCK/SIMULATED data that violates our strict real-data-only policy.**

## Purpose

This archive contains all files that were moved from the research directory because they contained mock, simulated, or synthetic data rather than real ICTV analysis.

## What Was Archived

### Analysis Directories (All contained mock data)
- `discovery_bias/` - Mock discovery bias analysis
- `domain_architecture/` - Mock domain architecture analysis  
- `genome_architecture/` - Mock genome architecture analysis
- `growth_patterns/` - Mock growth pattern analysis
- `host_range_evolution/` - Mock host range analysis
- `phylogenetic_signal/` - Mock phylogenetic signal analysis
- `species_boundaries/` - Mock species boundary analysis

### Analyzer Results Directories (All contained mock results)
- `discoverybiasanalyzer/`
- `familysizeanalyzer/`
- `genomearchitectureanalyzer/`
- `growthpatternanalyzer/`
- `hostrangeevolutionanalyzer/`
- `phylogeneticsignalanalyzer/`
- `speciesboundaryanalyzer/`

### Family Size Analysis Mock Files
- `family_size_detailed_findings_MOCK.md` - Contained fake statistical analysis (p-values, effect sizes, specific family counts)
- `family_size_analysis_report_MOCK.txt` - Contained simulated family size data
- `family_size_analysis_figure.pdf` - Visualization based on mock data
- `family_size_analysis_figure.png` - Visualization based on mock data
- `optimal_family_size_figure.png` - Visualization based on mock data

## Why These Were Archived

### Strict Data Policy
The project adopted a **NO MOCK DATA** policy after discovering that multiple analyses contained simulated rather than real ICTV data. This policy states:

> **All analyses must use actual MSL Excel files from ICTV. No simulations, no mock data, no approximations.**

### Examples of Mock Data Found
- Fake statistical significance values (p < 0.01, Cohen's d = 1.4)
- Simulated family sizes (e.g., "Siphoviridae: 340 species")  
- Made-up stability analyses with invented family tracking
- Synthetic growth patterns and correlations
- Fabricated "optimal size ranges" without real data support

### Risk of Mock Data
- **Scientific integrity**: Mock results could be mistaken for real findings
- **Publication risk**: Fake statistics could end up in manuscripts
- **Reproducibility**: Mock analyses cannot be validated against real data
- **Credibility**: Discovery of mock data would undermine project validity

## Current Real Data Status

### What Remains in Active Research
- `family_size_analysis/basic_analysis.py` - Real analysis using documented ICTV statistics
- `family_size_analysis/REAL_DATA_FINDINGS.md` - Findings based exclusively on real data
- `family_size_analysis/results/family_size_analysis_basic.json` - Real ICTV growth statistics
- `family_size_analysis/results/family_size_analysis_summary.txt` - Real data summary

### Data Sources for Real Analysis
- ICTV published Master Species List (MSL) statistics (2005-2024)
- Official ICTV documentation and proposal records
- Cross-referenced with multiple ICTV publications

## Archive Policy

### Do NOT Use These Files
- All files in this archive contain mock data and should not be used for analysis
- Do not reference findings from these archived analyses
- Do not include visualizations or statistics from these files in any publication

### If Real Data Becomes Available
- Create new analyses from scratch using only real MSL data
- Do not attempt to "fix" or "update" the mock analyses
- Start with clean implementations that never touch mock data

### Future Researchers
- This archive serves as a cautionary example of the importance of data integrity
- Always verify data sources before beginning analysis
- Never mix real and simulated data

## Date Archived
June 9, 2025

## Archived By
Claude Code Assistant during data integrity cleanup

## Next Steps
1. Parse real MSL Excel files when technical capability allows
2. Re-implement analyses using only verified ICTV data
3. Generate genuine findings based on actual viral taxonomy data
4. Maintain strict separation between real and simulated data

---

**REMEMBER: Files in this archive contain MOCK DATA and should not be used for scientific analysis or publication.**