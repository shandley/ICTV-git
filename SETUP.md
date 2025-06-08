# Development Environment Setup

## Prerequisites
- Python 3.8 or higher
- Git
- pip (Python package installer)

## Setting Up Virtual Environment

### macOS/Linux
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

### Windows
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .
```

## Verify Installation
```bash
# Check Python version
python --version

# Run tests
pytest

# Check code formatting
black --check src tests
flake8 src tests
```

## Deactivating Virtual Environment
```bash
deactivate
```

## Updating Dependencies
```bash
# Update all packages
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade pandas
```

## Common Issues

### macOS SSL Certificate Error
If you encounter SSL certificate errors when downloading data:
```bash
pip install --upgrade certifi
```

### Windows Long Path Support
Enable long path support in Windows if you encounter path length errors:
1. Open Group Policy Editor (gpedit.msc)
2. Navigate to: Computer Configuration > Administrative Templates > System > Filesystem
3. Enable "Enable Win32 long paths"

### Permission Errors
If you encounter permission errors:
```bash
# Use --user flag
pip install --user -r requirements.txt
```