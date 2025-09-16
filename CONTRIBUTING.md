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
        """Test error
