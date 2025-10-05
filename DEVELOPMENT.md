# 🛠️ Development Guide

Complete guide for developing nostr-tools with professional quality standards.

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Development Workflow](#development-workflow)
- [Continuous Integration](#continuous-integration)
- [Quality Assurance](#quality-assurance)
- [Testing](#testing)
- [Security](#security)
- [Documentation](#documentation)
- [Release Process](#release-process)
- [Troubleshooting](#troubleshooting)
- [Makefile Commands Reference](#makefile-commands-reference)
- [Exception Handling](#exception-handling)
- [Best Practices](#best-practices)
- [Additional Resources](#additional-resources)

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** - The project supports Python 3.9, 3.10, 3.11, 3.12, and 3.13
- **Git** - For version control
- **Make** - For development automation (optional but recommended)

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

## 🤖 Continuous Integration

The project uses GitHub Actions for automated testing and quality assurance. The CI pipeline runs on every push and pull request to ensure code quality and reliability.

### CI Workflows

**Main CI Pipeline** (`.github/workflows/ci.yml`):
- **Pre-commit Checks** - Fast quality gates (formatting, linting, type checking)
- **Code Quality** - Comprehensive code analysis with Ruff and MyPy
- **Security Scanning** - Bandit, Safety, and pip-audit vulnerability scans
- **Testing** - Full test suite with coverage reporting
- **Documentation** - Build and verify documentation

**Documentation Pipeline** (`.github/workflows/docs.yml`):
- **Auto-deploy** - Builds and deploys documentation on main/develop branches
- **Version-specific** - Creates versioned documentation for releases

**Publishing Pipeline** (`.github/workflows/publish.yml`):
- **Test PyPI** - Automatic deployment to Test PyPI for pre-releases
- **Production PyPI** - Manual deployment to production PyPI for stable releases
- **Security** - Uses GitHub environments with proper permissions

### CI Environment

The CI runs on Ubuntu with Python 3.11 and includes:
- Cached dependencies for faster builds
- Parallel job execution for efficiency
- Comprehensive artifact collection
- Security scanning with known vulnerability exclusions

### Local CI Simulation

```bash
# Run the same checks as CI locally
make check-ci    # Format + Lint + Type + Security + Test
make check-all   # Full CI + Documentation + Build verification
```

### Modern Development Stack

The project uses a modern Python development stack:

**Code Quality:**
- **Ruff** - Ultra-fast Python linter and formatter (replaces Black, isort, flake8)
- **MyPy** - Static type checking with strict configuration
- **Pre-commit** - Git hooks for automated quality checks

**Testing:**
- **pytest** - Modern testing framework with async support
- **pytest-cov** - Coverage reporting with HTML output
- **pytest-xdist** - Parallel test execution for speed

**Security:**
- **Bandit** - Security vulnerability scanner
- **Safety** - Dependency vulnerability scanner
- **pip-audit** - Comprehensive package auditing

**Documentation:**
- **Sphinx** - Professional documentation generator
- **Furo theme** - Modern, clean documentation theme
- **Auto-generated API docs** - From docstrings and type hints

**Build & Release:**
- **setuptools-scm** - Git-based versioning
- **build** - Modern PEP 517 build tool
- **twine** - Secure PyPI uploads

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

Pre-commit hooks run automatically on `git commit` to ensure code quality:

```bash
# Run hooks manually
make pre-commit

# Update hooks to latest versions
make deps-update

# Skip hooks (not recommended)
git commit --no-verify
```

#### Pre-commit Configuration

The project uses a comprehensive pre-commit configuration (`.pre-commit-config.yaml`) that includes:

**Code Quality Hooks:**
- **Ruff** - Fast Python linter and formatter with auto-fix
- **MyPy** - Static type checking with strict configuration
- **General hooks** - Trailing whitespace, end-of-file, merge conflicts

**Security Hooks:**
- **Bandit** - Security vulnerability scanner for Python code
- **Safety** - Known vulnerability scanner for dependencies
- **pip-audit** - Package vulnerability scanner
- **Private key detection** - Prevents committing sensitive keys

**Documentation Hooks:**
- **Sphinx build verification** - Ensures documentation builds without errors
- **File hygiene** - YAML, TOML, JSON syntax validation

#### Pre-commit Features

- **Auto-fix enabled** - Many issues are automatically corrected
- **Fail-fast disabled** - All hooks run to show complete results
- **Exclusions configured** - Ignores build artifacts and generated files
- **CI integration** - Same hooks run in GitHub Actions
- **Weekly updates** - Hooks are automatically updated via pre-commit.ci

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

# Coverage report
make test-cov

# Quick tests (no coverage)
make test-quick
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
```

### Test Markers

- `@pytest.mark.unit` - Fast unit tests (no external dependencies)

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

#### Security Configuration

The security scanning is configured with:

- **Bandit** - Scans source code for security vulnerabilities with JSON reporting
- **Safety** - Checks dependencies against known vulnerability database
- **pip-audit** - Comprehensive package vulnerability scanning
- **Exclusions** - Known false positives are ignored (e.g., `GHSA-4xh5-x5gv-qwph`)
- **Coverage** - Scans all source files in `src/nostr_tools/`

#### Security Reports

Security reports are generated in various formats:
- **Bandit** - JSON report (`bandit-report.json`)
- **Safety** - Console output with vulnerability details
- **pip-audit** - Detailed package vulnerability information

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
git tag -a v1.2.1 -m "Release v1.2.1"

# 2. Push tag
git push origin v1.2.1

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

### Setup & Installation
- `make install` - Install package in production mode
- `make install-dev` - Install with all development dependencies
- `make install-ci` - Install for CI environment (test dependencies only)

### Code Quality
- `make format` - Format code with Ruff (auto-fix)
- `make format-check` - Check formatting without making changes
- `make lint` - Run all linters (Ruff + MyPy)
- `make lint-fix` - Run linters with auto-fix
- `make type-check` - Run MyPy static type checking
- `make check` - All quality checks (format + lint + type)

### Security
- `make security` - Run all security scans (bandit + safety + pip-audit)
- `make security-bandit` - Run Bandit security linter
- `make security-safety` - Run Safety dependency vulnerability scan
- `make security-audit` - Run pip-audit for package vulnerabilities

### Testing
- `make test` - Run all tests with coverage
- `make test-unit` - Run unit tests only (fast)
- `make test-cov` - Run tests and generate HTML coverage report
- `make test-quick` - Quick test run without coverage
- `make test-watch` - Run tests in watch mode (re-run on changes)

### Documentation
- `make docs-build` - Build documentation
- `make docs-serve` - Build and serve documentation locally
- `make docs-clean` - Clean documentation build files
- `make docs-check` - Build docs and verify (used in CI)
- `make docs-open` - Build and open documentation in browser

### Build & Release
- `make build` - Build source and wheel distributions
- `make build-check` - Build and verify package integrity
- `make dist-check` - Verify distribution packages with twine
- `make publish-test` - Upload to Test PyPI
- `make publish` - Upload to production PyPI

### Quality Assurance
- `make pre-commit` - Run pre-commit hooks on all files
- `make check` - Run all quality checks (format + lint + type)
- `make check-ci` - Run all CI checks (check + security + test)
- `make check-all` - Run comprehensive checks (check-ci + docs + build)
- `make verify-all` - Full verification before release

### Utilities
- `make clean` - Remove build artifacts and cache
- `make clean-all` - Deep clean (including venv, docs, coverage)
- `make version` - Show current version
- `make info` - Show project information
- `make deps-update` - Update pre-commit hooks
- `make help` - Show all commands

## ⚠️ Exception Handling

### Architecture Overview

The library follows a strict exception handling architecture that separates concerns between modules:

- **Utils Module**: Uses standard Python exceptions (`ValueError`, `TypeError`) for independence and reusability
- **Core & Actions Modules**: Use custom domain-specific exceptions for Nostr protocol operations

This design ensures that the `utils` module can be used independently without knowledge of the entire library, while `core` and `actions` modules provide rich, domain-specific error information.

### Custom Exceptions Hierarchy

The library defines 18 custom exceptions organized into base classes and specific implementations:

```
NostrToolsError (base)
├── Base Module Exceptions
│   ├── EventError                    # Base for event-related errors
│   ├── FilterError                   # Base for filter-related errors
│   ├── RelayError                    # Base for relay-related errors
│   ├── ClientError                   # Base for client-related errors
│   ├── RelayMetadataError            # Base for relay metadata errors
│   ├── Nip11Error                    # Base for NIP-11 errors
│   └── Nip66Error                    # Base for NIP-66 errors
└── Specific Exception Classes
    ├── EventValidationError          # Event validation failures
    ├── FilterValidationError         # Filter validation failures
    ├── RelayValidationError          # Relay validation failures
    ├── ClientValidationError         # Client configuration failures
    ├── ClientConnectionError         # WebSocket connection failures
    ├── ClientSubscriptionError       # Subscription operation failures
    ├── ClientPublicationError        # Event publishing failures
    ├── RelayMetadataValidationError  # Relay metadata validation failures
    ├── Nip11ValidationError          # NIP-11 relay info validation failures
    └── Nip66ValidationError          # NIP-66 relay monitoring validation failures
```

### Exception Usage by Module

#### Core Module Exceptions

**Client Class:**
- `ClientValidationError` - Invalid client configuration (timeout, relay type, proxy settings)

**RelayMetadata Classes:**
- `RelayMetadataValidationError` - Invalid relay metadata (relay type, timestamp)
- `Nip11ValidationError` - Invalid NIP-11 relay information (supported NIPs, limitations)
- `Nip66ValidationError` - Invalid NIP-66 relay monitoring data (RTT values, flags)

**Event Class:**
- `EventValidationError` - Invalid event structure, signature, or content

**Filter Class:**
- `FilterValidationError` - Invalid filter parameters or structure

**Relay Class:**
- `RelayValidationError` - Invalid relay URL or configuration

#### Client Operation Exceptions

**Client Operations:**
- `ClientConnectionError` - WebSocket connection failures
- `ClientSubscriptionError` - Subscription management failures
- `ClientPublicationError` - Event publishing failures

### When to Use What

**Use Custom Exceptions** (Core & Actions):
```python
from nostr_tools import ClientValidationError, Nip11ValidationError

class Client:
    def validate(self):
        if self.timeout < 0:
            raise ClientValidationError("timeout must be non-negative")
        if self.relay.network == "tor" and not self.socks5_proxy_url:
            raise ClientValidationError("socks5_proxy_url is required for Tor relays")

class Nip11:
    def validate(self):
        if not isinstance(self.supported_nips, list):
            raise Nip11ValidationError("supported_nips must be a list")
```

**Use Standard Exceptions** (Utils):
```python
def validate_keypair(sec: str, pub: str) -> bool:
    if len(sec) != 64:
        raise ValueError("Private key must be 64 hex characters")
    if not isinstance(pub, str):
        raise TypeError("Public key must be a string")
```

### Error Handling Best Practices

1. **Be specific** - Use the most specific exception type for the context
2. **Provide context** - Include helpful error messages with details
3. **Document exceptions** - List all raised exceptions in docstrings
4. **Catch appropriately** - Don't catch too broadly, let specific errors bubble up
5. **Test exception paths** - Include exception handling in your tests

```python
def process_event(event: Event) -> None:
    """Process a Nostr event.

    Args:
        event: The event to process

    Raises:
        EventValidationError: If event structure is invalid
        ClientConnectionError: If relay is unreachable
        ClientPublicationError: If event publishing fails
    """
    try:
        event.validate()
        # Process event...
    except EventValidationError as e:
        logger.error(f"Invalid event: {e}")
        raise  # Re-raise for caller to handle
    except ClientConnectionError as e:
        logger.error(f"Relay connection failed: {e}")
        # Handle connection issues...
```

### Exception Testing

All custom exceptions are thoroughly tested:

```python
def test_client_validation_error():
    """Test ClientValidationError exception."""
    with pytest.raises(ClientValidationError, match="timeout must be non-negative"):
        Client(relay=relay, timeout=-1)

def test_nip11_validation_error():
    """Test Nip11ValidationError exception."""
    with pytest.raises(Nip11ValidationError, match="supported_nips must be a list"):
        RelayMetadata.Nip11(supported_nips="not_a_list")
```

### Migration Guide

If you're updating code that previously used standard exceptions:

**Before:**
```python
# Old code using ValueError/TypeError
if timeout < 0:
    raise ValueError("timeout must be non-negative")
```

**After:**
```python
# New code using custom exceptions
if timeout < 0:
    raise ClientValidationError("timeout must be non-negative")
```

This provides better error specificity and follows the library's exception architecture.

## 🎯 Best Practices

1. **Always run checks before committing**
   ```bash
   make check-all
   ```

2. **Write tests for new features**
   - Aim for 80%+ coverage
   - Include edge cases
   - Test exception handling

3. **Keep dependencies updated**
   ```bash
   make deps-update
   ```

4. **Document your code**
   - Clear docstrings
   - Update docs/
   - Document raised exceptions

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
