# 🛠️ Development Guide

Complete guide for developing nostr-tools with professional quality standards.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Development Workflow](#development-workflow)
- [Quality Assurance](#quality-assurance)
- [Testing](#testing)
- [Security](#security)
- [Documentation](#documentation)
- [Release Process](#release-process)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Initial Setup

```bash
# 1. Clone the repository
git clone https://github.com/bigbrotr/nostr-tools.git
cd nostr-tools

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install development dependencies
make install-dev

# 4. Set up pre-commit hooks
pre-commit install

# 5. Verify installation
make info
```

### First Contribution

```bash
# 1. Create a feature branch
git checkout -b feature/your-feature

# 2. Make your changes
# Edit files...

# 3. Run quality checks
make check

# 4. Run tests
make test

# 5. Commit (pre-commit hooks run automatically)
git add .
git commit -m "feat: add your feature"

# 6. Push and create PR
git push origin feature/your-feature
```

## 🔄 Development Workflow

### Standard Development Cycle

```bash
# 1. Pull latest changes
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/amazing-feature

# 3. Develop with live checks
make test-watch  # Run tests on file changes

# 4. Before committing, run full checks
make check-all   # Format + Lint + Type + Security + Test + Docs
```

### Code Changes Checklist

- [ ] Code follows project style (Ruff formatted)
- [ ] Type hints added for all public APIs
- [ ] Tests written for new features
- [ ] Documentation updated
- [ ] Security implications considered
- [ ] All checks passing (`make check-all`)

## ✅ Quality Assurance

### Quick Quality Check

```bash
make check  # Format + Lint + Type check
```

### Full Quality Check

```bash
make check-all  # Everything including docs and build
```

### Individual Checks

```bash
# Code formatting
make format       # Auto-format code
make format-check # Check without changing

# Linting
make lint         # Run all linters
make lint-fix     # Auto-fix issues

# Type checking
make type-check   # MyPy static analysis
```

### Pre-commit Hooks

Pre-commit hooks run automatically on `git commit`:

```bash
# Run hooks manually
make pre-commit

# Update hooks to latest versions
make deps-update

# Skip hooks (not recommended)
git commit --no-verify
```

## 🧪 Testing

### Running Tests

```bash
# All tests with coverage
make test

# Quick test (no coverage)
make test-quick

# Watch mode (auto-rerun on changes)
make test-watch

# Coverage report
make test-cov  # Opens htmlcov/index.html
```

### Test Categories

```bash
# Unit tests only (fast)
make test-unit

# Integration tests (requires network)
make test-integration

# Performance benchmarks
make test-benchmark
```

### Writing Tests

Place tests in `tests/` directory:

```python
# tests/test_feature.py
import pytest
from nostr_tools import Feature

class TestFeature:
    """Test suite for Feature."""

    def test_basic_functionality(self):
        """Test basic feature works."""
        feature = Feature()
        assert feature.works() is True

    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test async feature works."""
        feature = Feature()
        result = await feature.async_works()
        assert result is True

    @pytest.mark.unit
    def test_unit_specific(self):
        """Unit test example."""
        pass

    @pytest.mark.integration
    async def test_integration_specific(self):
        """Integration test example."""
        pass
```

### Test Markers

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Tests requiring network
- `@pytest.mark.benchmark` - Performance tests

## 🔒 Security

### Security Scanning

```bash
# All security scans
make security

# Individual scans
make security-bandit  # Code security linter
make security-safety  # Known vulnerabilities
make security-audit   # Package audit
```

### Security Best Practices

1. **Never commit secrets**
   - Pre-commit hook detects private keys
   - Use environment variables for sensitive data

2. **Dependency security**
   - Regularly run `make security`
   - Review security reports in CI artifacts

3. **Code review**
   - All security-sensitive code requires review
   - Follow secure coding guidelines in SECURITY.md

## 📚 Documentation

### Building Documentation

```bash
# Build documentation
make docs-build

# Build and serve locally
make docs-serve  # http://localhost:8000

# Verify docs build (CI check)
make docs-check

# Open in browser
make docs-open

# Clean docs build
make docs-clean
```

### Writing Documentation

1. **Code documentation** - Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description.

    Detailed description of what this function does.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When invalid input
        TypeError: When wrong type

    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
    pass
```

2. **User documentation** - Update README.md and docs/

3. **API changes** - Update CHANGELOG.md

## 📦 Release Process

### Pre-release Checklist

```bash
# 1. Full verification
make verify-all

# 2. Version check
make version

# 3. Build and verify
make build-check
```

### Creating a Release

```bash
# 1. Update version in git tag
git tag -a v1.2.0 -m "Release v1.2.0"

# 2. Push tag
git push origin v1.2.0

# 3. Build package
make build

# 4. Test on Test PyPI
make publish-test

# 5. Publish to PyPI
make publish
```

## 🔧 Troubleshooting

### Common Issues

#### Pre-commit Hook Failures

```bash
# Update hooks
make deps-update

# Clear cache and retry
rm -rf ~/.cache/pre-commit
pre-commit clean
pre-commit run --all-files
```

#### Test Failures

```bash
# Run specific test
pytest tests/test_file.py::TestClass::test_method -v

# Show full output
pytest -vv --tb=long

# Run without coverage for faster iteration
make test-quick
```

#### Type Check Errors

```bash
# Show detailed errors
mypy src/nostr_tools --show-error-codes --pretty

# Ignore specific error (not recommended)
# type: ignore[error-code]
```

#### Import Errors

```bash
# Reinstall in development mode
pip install -e ".[dev]"

# Check installation
pip show nostr-tools
make info
```

#### Security Scan False Positives

Known issues are ignored in configuration:
- `GHSA-4xh5-x5gv-qwph` - pip vulnerability (build tool, not runtime)

To skip a specific issue, update `Makefile`:
```makefile
SECURITY_IGNORE := GHSA-xxx GHSA-yyy
```

### Build Issues

```bash
# Clean everything
make clean-all

# Rebuild from scratch
make build

# Check package integrity
make dist-check
```

### Getting Help

1. **Check documentation**
   - README.md
   - CONTRIBUTING.md
   - This file (DEVELOPMENT.md)

2. **Run diagnostics**
   ```bash
   make info        # Show environment info
   make version     # Show version
   python --version # Python version
   pip list         # Installed packages
   ```

3. **Ask for help**
   - GitHub Issues
   - Discussions
   - Email: hello@bigbrotr.com

## 📊 Makefile Commands Reference

### Setup
- `make install` - Install package
- `make install-dev` - Install with dev dependencies
- `make install-ci` - Install for CI

### Quality
- `make format` - Format code
- `make lint` - Run linters
- `make type-check` - Type checking
- `make check` - All quality checks

### Testing
- `make test` - All tests
- `make test-unit` - Unit tests
- `make test-integration` - Integration tests
- `make test-cov` - Coverage report

### Security
- `make security` - All security scans
- `make security-bandit` - Bandit scan
- `make security-safety` - Safety check
- `make security-audit` - pip-audit

### Documentation
- `make docs-build` - Build docs
- `make docs-serve` - Serve docs locally
- `make docs-check` - Verify docs

### Build & Release
- `make build` - Build package
- `make publish-test` - Publish to Test PyPI
- `make publish` - Publish to PyPI

### Utilities
- `make clean` - Clean build artifacts
- `make clean-all` - Deep clean
- `make version` - Show version
- `make info` - Show project info
- `make help` - Show all commands

## 🎯 Best Practices

1. **Always run checks before committing**
   ```bash
   make check-all
   ```

2. **Write tests for new features**
   - Aim for 80%+ coverage
   - Include edge cases

3. **Keep dependencies updated**
   ```bash
   make deps-update
   ```

4. **Document your code**
   - Clear docstrings
   - Update docs/

5. **Review security implications**
   ```bash
   make security
   ```

6. **Use meaningful commit messages**
   - Follow conventional commits
   - `feat:`, `fix:`, `docs:`, etc.

## 📝 Additional Resources

- [GitHub Actions CI](.github/workflows/ci.yml)
- [Pre-commit Config](.pre-commit-config.yaml)
- [Project Config](pyproject.toml)
- [Makefile](Makefile)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)

---

**Happy Coding! 🚀**
