# Contributing to ICTV-git

First off, thank you for considering contributing to ICTV-git! It's people like you that make ICTV-git such a great tool for the virology community.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [project email].

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When you create a bug report, please include as many details as possible:

**Bug Report Template:**
- **Description**: Clear and concise description of the bug
- **Steps to Reproduce**: 
  1. Go to '...'
  2. Run command '....'
  3. See error
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**:
  - OS: [e.g., Ubuntu 20.04]
  - Python version: [e.g., 3.8.10]
  - ICTV-git version/commit: [e.g., v1.0.0 or commit hash]
- **Additional Context**: Any other relevant information

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Use Case**: Explain why this enhancement would be useful
- **Proposed Solution**: Describe the solution you'd like
- **Alternatives**: Describe alternatives you've considered
- **Additional Context**: Add any other context or screenshots

### Your First Code Contribution

Unsure where to begin? You can start by looking through these issues:

- Issues labeled `good first issue` - should only require a few lines of code
- Issues labeled `help wanted` - more involved but still accessible

### Pull Requests

1. **Fork the Repository** and create your branch from `main`
2. **Set Up Development Environment**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/ICTV-git.git
   cd ICTV-git
   pip install -r requirements-dev.txt
   pip install -e .
   ```

3. **Make Your Changes**:
   - Write code that follows our style guidelines
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

4. **Commit Your Changes**:
   ```bash
   git add .
   git commit -m "Add clear, descriptive commit message"
   ```
   
   Commit message guidelines:
   - Use present tense ("Add feature" not "Added feature")
   - Limit first line to 72 characters
   - Reference issues and pull requests liberally

5. **Push to Your Fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Submit a Pull Request**:
   - Fill in the PR template
   - Link any relevant issues
   - Request review from maintainers

## Development Process

### Code Style

- Follow PEP 8 for Python code
- Use Black for code formatting: `black src/ tests/`
- Use type hints where possible
- Write descriptive variable names

### Testing

- Write tests for all new functionality
- Ensure test coverage remains above 80%
- Run tests before submitting PR:
  ```bash
  pytest tests/
  pytest tests/ --cov=src --cov-report=html
  ```

### Documentation

- Update docstrings for new functions/classes
- Update README.md if adding new features
- Add examples to documentation when helpful
- Use Google-style docstrings:
  ```python
  def function(param1: str, param2: int) -> bool:
      """Brief description of function.
      
      More detailed description if needed.
      
      Args:
          param1: Description of param1
          param2: Description of param2
          
      Returns:
          Description of return value
          
      Raises:
          ValueError: When invalid input provided
      """
  ```

## Project Structure

Understanding the project structure helps you know where to make changes:

```
ICTV-git/
├── src/                    # Main package code
│   ├── parsers/           # MSL file parsing
│   ├── converters/        # Data conversion tools
│   ├── utils/             # Utility functions
│   └── community_tools/   # Web/API interfaces
├── tests/                 # Test files (mirror src/ structure)
├── scripts/               # Standalone scripts
├── docs/                  # Documentation
└── examples/              # Example usage notebooks
```

## Areas Where We Need Help

### High Priority
- **Testing**: Increase test coverage, especially edge cases
- **Documentation**: Improve API documentation and tutorials
- **Performance**: Optimize large dataset operations
- **Visualization**: Enhance interactive visualizations

### Research Applications
- Integration with bioinformatics pipelines
- New analysis methods for taxonomy evolution
- Machine learning applications
- Cross-database synchronization

### Community Tools
- GUI improvements for non-technical users
- Additional export formats
- Integration with existing tools (BLAST, etc.)
- Mobile-friendly interfaces

## Recognition

Contributors will be:
- Listed in AUTHORS.md file
- Acknowledged in publications
- Credited in release notes
- Invited to contribute to manuscripts (significant contributions)

## Questions?

Feel free to:
- Open an issue for discussion
- Contact maintainers directly
- Join our community discussions

Thank you for contributing to better viral taxonomy management!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.