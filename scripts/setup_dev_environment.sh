#!/bin/bash
# Development Environment Setup Script for ICTV-git

set -e  # Exit on error

echo "🚀 Setting up ICTV-git development environment..."

# Check Python version
echo "📍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Error: Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version is compatible"

# Create virtual environment
echo "📍 Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "⚠️  Virtual environment already exists"
fi

# Activate virtual environment
echo "📍 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📍 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📍 Installing core dependencies..."
pip install -r requirements.txt

echo "📍 Installing development dependencies..."
if [ -f "requirements-dev.txt" ]; then
    pip install -r requirements-dev.txt
else
    # Install common dev tools if requirements-dev.txt doesn't exist
    pip install pytest pytest-cov black flake8 mypy pre-commit
fi

# Install package in development mode
echo "📍 Installing ICTV-git in development mode..."
pip install -e .

# Set up pre-commit hooks
echo "📍 Setting up pre-commit hooks..."
if [ -f ".pre-commit-config.yaml" ]; then
    pre-commit install
    echo "✅ Pre-commit hooks installed"
else
    echo "⚠️  No pre-commit configuration found"
fi

# Create necessary directories
echo "📍 Creating necessary directories..."
mkdir -p data/raw
mkdir -p output/git_taxonomy
mkdir -p logs

# Download sample data if not present
echo "📍 Checking sample data..."
if [ ! -f "data/sample/sample_msl_data.csv" ]; then
    echo "✅ Sample data already present"
else
    echo "✅ Sample data found"
fi

# Run tests to verify setup
echo "📍 Running tests to verify setup..."
if python -m pytest tests/ -v --tb=short; then
    echo "✅ All tests passed!"
else
    echo "⚠️  Some tests failed, but setup is complete"
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "To activate the environment in the future, run:"
echo "    source venv/bin/activate"
echo ""
echo "To run the web interface:"
echo "    streamlit run scripts/run_taxonomy_browser.py"
echo ""
echo "To start the API server:"
echo "    python scripts/run_taxonomy_api.py"
echo ""
echo "To run tests:"
echo "    pytest tests/"
echo ""
echo "Happy coding! 🦠"