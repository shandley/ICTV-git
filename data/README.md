# Data Directory Structure

This directory contains all data files for the ICTV-git project.

## Subdirectories

### raw/
Original MSL Excel files downloaded from ICTV. These files are not tracked by git due to size.

### processed/
Parsed and converted data in YAML/JSON format ready for git repository creation.

### cache/
Temporary storage for downloaded files and intermediate processing results.

## Note
Excel files in `raw/` are excluded from git tracking. To obtain MSL files:
1. Run the download script: `python scripts/download_msl.py`
2. Or manually download from https://ictv.global/msl