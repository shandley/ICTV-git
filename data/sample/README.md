# Sample Dataset

This directory contains a small sample dataset for quick testing and demonstration purposes.

## Contents

- `sample_msl_data.csv` - A CSV file with 50 representative virus species from MSL38
- `sample_species/` - Directory with example YAML files in git taxonomy format

## Purpose

This sample data allows users to:
1. Test the tools without downloading the full MSL dataset
2. Run examples in under 1 minute
3. Understand the data format
4. Develop and test new features

## Usage

```python
# Use sample data for testing
from src.parsers.msl_parser import MSLParser

# Load sample CSV instead of full Excel
sample_data = pd.read_csv('data/sample/sample_msl_data.csv')

# Process as normal
for _, row in sample_data.iterrows():
    species = VirusSpecies(
        scientific_name=row['Species'],
        genus=row['Genus'],
        family=row['Family'],
        # ... etc
    )
```

## Creating Your Own Sample

To create a sample from any MSL file:

```bash
python scripts/create_sample_data.py data/MSL38.xlsx --size 50 --output data/sample/
```

This will randomly select 50 species while ensuring representation from different:
- Realms
- Genome types
- Host types
- Taxonomic families

## Full Dataset

To download the complete ICTV dataset:

```bash
python scripts/download_msl.py
```

This will download all MSL files (2005-2024) into the `data/` directory.