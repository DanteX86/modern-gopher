# Test-Driven Development CLI for Modern Gopher

A comprehensive testing toolkit designed to support Test-Driven Development (TDD) workflow for the Modern Gopher project.

## Installation

The TDD CLI has been installed with the following tools:

- **pytest-watch** - Automatic test running on file changes
- **pytest-xdist** - Parallel test execution
- **pytest-sugar** - Beautiful test output with progress bars
- **pytest-clarity** - Enhanced assertion failure output

## Quick Start

```bash
# Run quick TDD feedback tests
./tdd quick

# Watch files and auto-run tests
./tdd watch

# Run all unit tests
./tdd test

# Run tests with coverage
./tdd test -c
```

## Available Commands

### Core Testing Commands

#### `./tdd quick`
Run a quick subset of tests for rapid TDD feedback.
- Excludes integration tests
- Stops on first failure (-x)
- Shows slowest 10 test durations
- Perfect for the red-green-refactor cycle

#### `./tdd watch [options]`
Watch files and automatically run tests when changes are detected.
```bash
./tdd watch                    # Watch all files
./tdd watch -p browser         # Watch and filter by pattern
./tdd watch -v                 # Verbose output
```

#### `./tdd test [options]`
Run tests with various configuration options.
```bash
./tdd test                     # Run all unit tests
./tdd test -c                  # Include coverage analysis
./tdd test -j                  # Run tests in parallel
./tdd test -f                  # Run only previously failed tests
./tdd test -v                  # Verbose output
./tdd test -i                  # Run integration tests
./tdd test -p pattern          # Filter tests by pattern
```

### Analysis Commands

#### `./tdd coverage`
Generate comprehensive test coverage reports.
- Terminal output with missing lines
- HTML report in `htmlcov/index.html`
- XML report for CI/CD integration

#### `./tdd lint`
Run all code quality checks:
- **Black** - Code formatting verification
- **isort** - Import sorting verification
- **flake8** - Style and error linting
- **mypy** - Type checking

#### `./tdd security`
Run security analysis:
- **bandit** - Security vulnerability scanning
- **safety** - Dependency vulnerability checking

### Code Maintenance

#### `./tdd fix`
Auto-fix code formatting issues:
- Format code with Black
- Sort imports with isort

### Test Management

#### `./tdd create <module>`
Create a new test file from template.
```bash
./tdd create auth              # Creates tests/test_auth.py
```

#### `./tdd file <path>`
Run tests for a specific file.
```bash
./tdd file tests/test_browser.py
```

#### `./tdd run <pattern>`
Run specific tests by name pattern.
```bash
./tdd run test_bookmarks       # Run all bookmark tests
./tdd run Browser              # Run all Browser class tests
```

#### `./tdd summary`
Show a summary of all available tests.

## TDD Workflow Integration

### Red-Green-Refactor Cycle

1. **Red Phase** - Write failing test:
   ```bash
   ./tdd create new_feature
   # Edit tests/test_new_feature.py
   ./tdd quick                  # Verify test fails
   ```

2. **Green Phase** - Make test pass:
   ```bash
   ./tdd watch -p new_feature   # Auto-run tests on save
   # Edit source code until tests pass
   ```

3. **Refactor Phase** - Improve code quality:
   ```bash
   ./tdd test -c                # Run with coverage
   ./tdd lint                   # Check code quality
   ./tdd fix                    # Auto-fix formatting
   ```

### Continuous Development

Start watch mode for continuous feedback:
```bash
./tdd watch
```

This will:
- Monitor all source files for changes
- Automatically run relevant tests
- Provide immediate feedback
- Stop on first failure for quick debugging

### Pre-Commit Workflow

Before committing code:
```bash
./tdd test -c                  # Full test suite with coverage
./tdd lint                     # Code quality checks
./tdd security                 # Security analysis
```

## Configuration

### Test Selection

The TDD CLI automatically excludes integration tests by default for faster feedback. Integration tests require network access and are slower.

```bash
# Unit tests only (default)
./tdd test

# Integration tests only
./tdd test -i
```

### Parallel Execution

Speed up test execution with parallel processing:
```bash
./tdd test -j                  # Auto-detect CPU cores
```

### Coverage Configuration

Coverage is configured in `pyproject.toml`:
- Source: `src/modern_gopher`
- Fail under: 80%
- Reports: Terminal + HTML + XML

## Advanced Features

### Test Creation Template

The `create` command generates a comprehensive test template with:
- Proper imports and structure
- Setup/teardown methods
- Placeholder tests
- Parametrized test examples
- Mock usage examples

### Pattern Matching

Use patterns to run specific test subsets:
```bash
./tdd test -p browser          # All browser-related tests
./tdd test -p "test_add"       # All tests with "test_add" in name
./tdd watch -p config          # Watch config-related tests only
```

### Performance Benchmarking

If `pytest-benchmark` is installed:
```bash
pip install pytest-benchmark
./tdd benchmark
```

## Output Features

### Enhanced Visual Feedback

- ✅ Success indicators with green checkmarks
- ❌ Error indicators with red X marks
- ⚠️ Warning indicators with yellow triangles
- ℹ️ Info indicators with blue information symbols
- Color-coded headers and progress bars

### Test Progress

- Real-time progress bars during test execution
- Test timing information
- Slowest test identification
- Clear failure summaries

## Error Handling

The TDD CLI provides robust error handling:
- Command not found errors
- Test execution failures
- File system permission issues
- Missing dependencies

Exit codes:
- `0` - Success
- `1` - Test failures or other errors

## Integration with Modern Gopher

### Test Structure

```
tests/
├── test_bookmarks.py      # Bookmark functionality
├── test_browser.py        # Browser interface
├── test_cli.py           # Command-line interface
├── test_client.py        # Gopher client
├── test_config.py        # Configuration system
├── test_html_renderer.py # HTML rendering
├── test_integration.py   # Network integration tests
├── test_keybindings.py   # Keyboard shortcuts
├── test_protocol.py      # Gopher protocol
├── test_sessions.py      # Session management
├── test_types.py         # Gopher item types
└── test_url_parsing.py   # URL parsing
```

### Current Test Statistics

- **260 total tests** (250 unit + 10 integration)
- **Comprehensive coverage** of all major components
- **Fast execution** - unit tests complete in ~2 seconds
- **Reliable** - tests pass consistently

## Troubleshooting

### Common Issues

1. **pytest-watch not found**
   ```bash
   pip install pytest-watch
   ```

2. **Permission denied**
   ```bash
   chmod +x tdd
   ```

3. **Tests not running**
   - Check you're in the project root directory
   - Verify virtual environment is activated
   - Ensure pytest is installed

### Debug Mode

For debugging test failures:
```bash
./tdd test -v --tb=long      # Detailed traceback
./tdd test -s                # Show print statements
./tdd test --pdb             # Drop into debugger on failure
```

## Best Practices

### TDD Workflow
1. Start with `./tdd watch` for continuous feedback
2. Use `./tdd quick` for rapid red-green-refactor cycles
3. Run `./tdd test -c` before commits
4. Use `./tdd create` for new features

### Test Organization
- One test file per module
- Clear, descriptive test names
- Use setup/teardown for test isolation
- Group related tests in classes

### Performance
- Keep unit tests fast (< 1 second each)
- Use mocks for external dependencies
- Reserve integration tests for end-to-end scenarios
- Run parallel tests for large test suites

---

*TDD CLI Documentation - Modern Gopher v1.2.0*

