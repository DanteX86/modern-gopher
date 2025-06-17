# Contributing to Modern Gopher

Thank you for your interest in contributing to Modern Gopher! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Issue Reporting](#issue-reporting)

## Code of Conduct

This project follows a simple code of conduct:
- Be respectful and constructive
- Focus on what's best for the project and community
- Show empathy towards other contributors
- Welcome newcomers and help them get started

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A terminal/command line interface

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/modern-gopher.git
   cd modern-gopher
   ```

## Development Setup

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   # or if using older pip:
   pip install -r requirements.txt
   pip install pytest black flake8 isort mypy bandit safety
   ```

3. Verify the setup:
   ```bash
   make check
   ```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-new-feature` for new features
- `fix/resolve-issue-123` for bug fixes
- `docs/update-readme` for documentation
- `refactor/improve-caching` for refactoring

### Workflow

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes in small, logical commits

3. Write or update tests for your changes

4. Ensure all tests pass:
   ```bash
   make test
   ```

5. Check code style:
   ```bash
   make lint
   ```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run fast tests only (no network)
make test-fast

# Run with coverage
pytest --cov=src/modern_gopher --cov-report=html

# Run specific test file
pytest tests/test_protocol.py -v
```

### Test Categories

- **Unit Tests**: Fast tests with no external dependencies
- **Integration Tests**: Tests that require network access
- **Browser Tests**: Tests for the terminal browser functionality

### Writing Tests

- Write tests for all new functionality
- Use descriptive test names: `test_should_parse_gopher_url_with_port`
- Include both positive and negative test cases
- Mock external dependencies in unit tests
- Add integration tests for network functionality

## Code Style

### Python Style

This project follows PEP 8 with some modifications:

- Line length: 100 characters
- Use double quotes for strings
- Format with `black`
- Sort imports with `isort`

### Code Formatting

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Check style
flake8 src/ tests/ --max-line-length=100
```

### Type Hints

- Use type hints for all public functions
- Import types from `typing` module
- Use `Optional[T]` for optional parameters

### Documentation

- Write docstrings for all public functions and classes
- Use Google-style docstrings
- Include examples in docstrings when helpful
- Update README.md for user-facing changes

## Submitting Changes

### Pull Request Process

1. Ensure your branch is up to date:
   ```bash
   git checkout master
   git pull upstream master
   git checkout your-branch
   git rebase master
   ```

2. Push your branch:
   ```bash
   git push origin your-branch
   ```

3. Create a pull request on GitHub

### Pull Request Guidelines

- Use a clear, descriptive title
- Reference any related issues: "Fixes #123"
- Describe what changes you made and why
- Include screenshots for UI changes
- Ensure all CI checks pass

### Review Process

- All changes require review before merging
- Address reviewer feedback promptly
- Keep discussions constructive and focused
- Be open to suggestions and alternative approaches

## Issue Reporting

### Before Creating an Issue

- Search existing issues to avoid duplicates
- Try to reproduce the issue with the latest code
- Gather relevant information (OS, Python version, etc.)

### Bug Reports

Include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment information
- Error messages or logs

### Feature Requests

Include:
- Clear description of the proposed feature
- Use case and motivation
- Possible implementation approaches
- Any related issues or discussions

## Development Tools

### Makefile Commands

```bash
make help           # Show available commands
make test           # Run all tests
make test-fast      # Run fast tests only
make lint           # Check code style
make coverage       # Show test coverage
make demo           # Run browser demo
make check          # Run comprehensive checks
make clean          # Clean build artifacts
```

### Useful Development Commands

```bash
# Run the browser
python src/modern_gopher/cli.py browse gopher://gopher.floodgap.com

# Test configuration
python -c "from modern_gopher.config import get_config; print(get_config())"

# Test keybindings
python src/modern_gopher/cli.py keybindings list
```

## Getting Help

- Check the [README.md](README.md) for basic usage
- Look at existing issues and pull requests
- Ask questions in issue discussions
- Review the code and tests for examples

## Recognition

Contributors will be recognized in:
- The project's contributor list
- Release notes for significant contributions
- GitHub's contributor graphs and statistics

Thank you for contributing to Modern Gopher! 🎉

