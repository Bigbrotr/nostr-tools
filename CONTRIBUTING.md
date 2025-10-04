# Contributing to nostr-tools

Thank you for your interest in contributing to nostr-tools! We welcome contributions from everyone and are grateful for even the smallest fixes or features.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Security Issues](#security-issues)
- [Community](#community)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and considerate in all interactions. We expect all contributors to:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- A GitHub account
- Basic knowledge of the Nostr protocol

### First-Time Contributors

Looking for a good first issue? Check out issues labeled with [`good first issue`](https://github.com/bigbrotr/nostr-tools/labels/good%20first%20issue) or [`help wanted`](https://github.com/bigbrotr/nostr-tools/labels/help%20wanted).

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/nostr-tools.git
cd nostr-tools
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

### 4. Set Up Pre-commit Hooks

```bash
pre-commit install
```

### 5. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

## How to Contribute

### Types of Contributions

#### 🐛 Bug Reports
- Search existing issues first to avoid duplicates
- Include Python version, OS, and dependency versions
- Provide minimal reproducible example
- Include full error messages and stack traces

#### ✨ Feature Requests
- Check if the feature has been requested before
- Explain the use case and benefits
- Consider if it aligns with project goals
- Be willing to implement it yourself

#### 📝 Documentation
- Fix typos or clarify existing documentation
- Add examples or tutorials
- Improve API documentation
- Translate documentation

#### 💻 Code Contributions
- Fix bugs
- Implement new features
- Improve performance
- Refactor code for better maintainability

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

```python
# Good: Descriptive variable names
relay_url = "wss://relay.example.com"
event_filter = Filter(kinds=[1], limit=10)

# Bad: Single letter variables (except in loops)
r = "wss://relay.example.com"
f = Filter(kinds=[1], limit=10)
```

### Code Formatting

We use Ruff for formatting and linting:

```bash
# Format code
make format

# Check linting
make lint
```

### Type Hints

All public APIs must have type hints:

```python
from typing import Optional, List

def connect_to_relay(
    url: str,
    timeout: Optional[int] = None
) -> Client:
    """Connect to a Nostr relay.

    Args:
        url: WebSocket URL of the relay
        timeout: Connection timeout in seconds

    Returns:
        Connected Client instance

    Raises:
        RelayConnectionError: If connection fails
    """
    ...
```

### Docstrings

Use Google-style docstrings:

```python
def process_event(event: Event) -> bool:
    """Process a Nostr event.

    Validates and stores the event in the local database.

    Args:
        event: The Event instance to process

    Returns:
        True if processing succeeded, False otherwise

    Raises:
        ValidationError: If event validation fails
        DatabaseError: If storage fails

    Example:
        >>> event = Event(kind=1, content="Hello")
        >>> success = process_event(event)
        >>> print(f"Processed: {success}")
    """
    ...
```

## Testing Guidelines

### Writing Tests

All new features must include tests:

```python
# tests/test_feature.py
import pytest
from nostr_tools import YourFeature

class TestYourFeature:
    """Test suite for YourFeature."""

    def test_basic_functionality(self):
        """Test basic feature functionality."""
        feature = YourFeature()
        result = feature.do_something()
        assert result == expected_value

    @pytest.mark.asyncio
    async def test_async_functionality(self):
        """Test async feature functionality."""
        feature = YourFeature()
        result = await feature.do_async()
        assert result == expected_value

    def test_error_handling(self):
        """Test error handling."""
        feature = YourFeature()
        with pytest.raises(ValueError):
            feature.do_something_invalid()
```

### Running Tests

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run with coverage
make test-cov

# Run quick tests (no coverage)
make test-quick
```

### Test Coverage

We maintain high test coverage:
- **Minimum**: 80% overall coverage
- **Target**: 90% for new features
- **Critical paths**: 100% coverage

## Documentation

### Code Documentation

All public APIs must be documented:

```python
def process_event(event: Event) -> bool:
    """Process a Nostr event.

    Validates and stores the event in the local database.

    Args:
        event: The Event instance to process

    Returns:
        True if processing succeeded, False otherwise

    Raises:
        EventValidationError: If event validation fails
        DatabaseError: If storage fails

    Example:
        >>> event = Event(kind=1, content="Hello")
        >>> success = process_event(event)
        >>> print(f"Processed: {success}")
    """
    ...
```

### User Documentation

- Update README.md for user-facing changes
- Add examples for new features
- Update API documentation in docs/

## Submitting Changes

### Before Submitting

1. **Run all checks**:
   ```bash
   make check-all
   ```

2. **Ensure tests pass**:
   ```bash
   make test
   ```

3. **Check coverage**:
   ```bash
   make test-cov
   ```

### Pull Request Process

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Write code following our standards
   - Add tests for new functionality
   - Update documentation

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request**:
   - Use the PR template
   - Describe your changes clearly
   - Link any related issues

### Pull Request Guidelines

- **Title**: Use conventional commit format
- **Description**: Explain what and why
- **Tests**: Ensure all tests pass
- **Documentation**: Update docs if needed
- **Breaking changes**: Clearly mark them

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

**Examples:**
```
feat(client): add connection retry logic
fix(event): resolve signature validation issue
docs(readme): update installation instructions
```

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

1. **Environment**:
   - Python version
   - Operating system
   - nostr-tools version
   - Dependencies versions

2. **Reproduction**:
   - Minimal code example
   - Expected behavior
   - Actual behavior
   - Error messages and stack traces

3. **Additional Info**:
   - Screenshots (if applicable)
   - Related issues
   - Workarounds (if any)

### Feature Requests

For feature requests:

1. **Check existing issues** first
2. **Describe the use case** clearly
3. **Explain the benefits** to users
4. **Consider implementation** complexity
5. **Be willing to contribute** if possible

## Security Issues

**Do not report security vulnerabilities publicly.**

Report security issues privately to: **security@bigbrotr.com**

See [SECURITY.md](SECURITY.md) for our security policy.

## Community

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and ideas
- **Email**: hello@bigbrotr.com for general inquiries

### Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Recognition

Contributors are recognized in:
- Release notes
- GitHub contributors list
- Project documentation

## Development Resources

### Useful Commands

```bash
# Development setup
make install-dev
make pre-commit

# Quality checks
make check          # Format + lint + type
make check-ci       # + security + test
make check-all      # + docs + build

# Testing
make test           # All tests with coverage
make test-unit      # Unit tests only
make test-quick     # Fast tests without coverage

# Documentation
make docs-build     # Build documentation
make docs-serve     # Serve locally

# Security
make security       # All security scans
```

### IDE Setup

**VS Code**:
- Install Python extension
- Configure Ruff for formatting
- Enable MyPy type checking
- Install pre-commit extension

**PyCharm**:
- Configure external tools for Ruff
- Enable type checking
- Set up pre-commit integration

### Debugging

```bash
# Run with debug output
PYTHONPATH=. python -m pytest tests/ -v -s

# Run specific test with debugging
python -m pytest tests/unit/test_client.py::TestClient::test_connect -v -s

# Profile performance
python -m pytest tests/ --durations=10
```

## Thank You! 🙏

Thank you for contributing to nostr-tools! Your contributions help make the Nostr ecosystem better for everyone.

Every contribution, no matter how small, is valuable and appreciated.

---

**Questions?** Open an issue or contact us at hello@bigbrotr.com
