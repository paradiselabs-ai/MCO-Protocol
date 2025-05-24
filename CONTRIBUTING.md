# Contributing to MCO Server

Thank you for your interest in contributing to MCO Server! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to foster an inclusive and respectful community.

## How to Contribute

### Reporting Bugs

If you find a bug in MCO Server, please report it by creating an issue in our GitHub repository. When filing a bug report, please include:

- A clear, descriptive title
- A detailed description of the issue
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Environment information (OS, Python version, etc.)
- Any relevant logs or error messages

### Suggesting Features

We welcome feature suggestions! To suggest a new feature:

1. Check existing issues to see if your feature has already been suggested
2. Create a new issue with the "feature request" label
3. Clearly describe the feature and its use case
4. Explain how it would benefit the project

### Pull Requests

We welcome pull requests for bug fixes, features, and improvements. To submit a pull request:

1. Fork the repository
2. Create a new branch for your changes
3. Make your changes
4. Add or update tests as necessary
5. Ensure all tests pass
6. Update documentation as needed
7. Submit a pull request

### Development Setup

To set up your development environment:

```bash
# Clone the repository
git clone https://github.com/mco-protocol/mco-server.git
cd mco-server

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## Coding Standards

- Follow PEP 8 style guidelines
- Write docstrings for all functions, classes, and modules
- Include type hints
- Write tests for new functionality
- Keep functions focused and modular

## Testing

- Write unit tests for all new functionality
- Ensure all tests pass before submitting a pull request
- Include integration tests for complex features

## Documentation

- Update documentation for any changes to the API
- Add examples for new features
- Keep the README and other documentation up to date

## Review Process

All pull requests will be reviewed by project maintainers. We may suggest changes or improvements before merging.

## License

By contributing to MCO Server, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
