# Contributing to nostr-tools

Thank you for your interest in contributing to nostr-tools! This document provides guidelines and information for contributors.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful, inclusive, and constructive in all interactions.

## Getting Started

### Development Environment Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/your-username/nostr-tools.git
   cd nostr-tools
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e .
   pip install pytest pytest-asyncio pytest-cov black flake8 mypy
   ```

4. **Verify Installation**
   ```bash
   python -m pytest
   ```

## Development Guidelines

### Code Style

We use the following tools to maintain code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking

Run these tools before submitting:

```bash
# Format code
black nostr_tools tests

# Check linting
flake8 nostr_tools tests

# Type checking
mypy nostr_tools
```

### Code Standards

1. **Type Hints**: All functions and methods must include type hints
2. **Docstrings**: All public functions, classes, and methods must have comprehensive docstrings
3. **Error Handling**: Proper exception handling with meaningful error messages
4. **Async/Await**: Use async/await for all I/O operations
5. **Testing**: All new features must include tests

### Project Structure

```
nostr_tools/
├── core/           # Core protocol components
│   ├── event.py    # Event representation and validation
│   ├── relay.py    # Relay configuration
│   ├── client.py   # WebSocket client
│   └── filter.py   # Event filtering
├── actions/        # High-level utility functions
├── utils/          # Utility functions
└── exceptions/     # Custom exceptions

tests/              # Test suite
docs/               # Documentation
```

## Types of Contributions

### Bug Reports

When reporting bugs, please include:

1. **Clear Description**: What happened vs. what you expected
2. **Reproduction Steps**: Minimal code example that reproduces the issue
3. **Environment**: Python version, OS, library version
4. **Error Messages**: Full traceback if applicable

**Bug Report Template:**
```markdown
**Description**: Brief description of the bug

**Steps to Reproduce**:
1. Step one
2. Step two
3. Step three

**Expected Behavior**: What should happen

**Actual Behavior**: What actually happens

**Environment**:
- Python version:
- OS:
- nostr-tools version:

**Additional Context**: Any other relevant information
```

### Feature Requests

For new features, please:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** and why it's valuable
3. **Provide examples** of how the feature would be used
4. **Consider implementation** if possible

### Code Contributions

#### Pull Request Process

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Follow code standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Test Your Changes**
   ```bash
   python -m pytest
   python -m pytest --cov=nostr_tools
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

#### Commit Message Guidelines

Use conventional commit format:

```
type(scope): description

- feat: new feature
- fix: bug fix
- docs: documentation changes
- style: formatting changes
- refactor: code refactoring
- test: adding tests
- chore: maintenance tasks
```

Examples:
```
feat(client): add authentication support
fix(event): handle escape sequences in content
docs(readme): update installation instructions
test(relay): add tests for Tor relay validation
```

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=nostr_tools

# Run specific test file
python -m pytest tests/test_event.py

# Run specific test
python -m pytest tests/test_event.py::TestEvent::test_event_creation
```

### Writing Tests

1. **Test Files**: Create test files in `tests/` directory
2. **Test Classes**: Group related tests in classes
3. **Async Tests**: Use `pytest.mark.asyncio` for async tests
4. **Fixtures**: Use pytest fixtures for common test data
5. **Coverage**: Aim for high test coverage on new code

**Test Example:**
```python
import pytest
from nostr_tools import Event, generate_keypair, generate_event

class TestEvent:
    def test_event_creation(self):
        """Test basic event creation and validation."""
        private_key, public_key = generate_keypair()
        event_data = generate_event(
            private_key, public_key, 1, [], "test content"
        )
        event = Event.from_dict(event_data)

        assert event.content == "test content"
        assert event.kind == 1
        assert len(event.id) == 64

    @pytest.mark.asyncio
    async def test_event_publishing(self):
        """Test event publishing to relay."""
        # Async test implementation
        pass
```

## Documentation

### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of the function.

    Longer description if needed, explaining the purpose,
    behavior, and any important details.

    Args:
        param1 (str): Description of parameter 1
        param2 (int): Description of parameter 2

    Returns:
        bool: Description of return value

    Raises:
        ValueError: When parameter is invalid
        TypeError: When parameter type is wrong

    Example:
        >>> result = example_function("test", 42)
        >>> print(result)
        True
    """
    # Implementation
    return True
```

### README Updates

When adding new features:

1. Update the feature list in README.md
2. Add usage examples
3. Update the API reference section
4. Add any new requirements or dependencies

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `setup.py` and `__init__.py`
2. Update `CHANGELOG.md` with new features and fixes
3. Ensure all tests pass
4. Update documentation
5. Create release PR
6. Tag release after merge
7. Publish to PyPI

## Community

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Email**: hello@bigbrotr.com for private inquiries

### Getting Help

If you need help with development:

1. Check existing documentation
2. Search through GitHub issues
3. Create a new issue with the "question" label
4. Join community discussions

## Recognition

Contributors will be recognized in:

- CHANGELOG.md for significant contributions
- README.md contributors section
- GitHub contributors list

## License

By contributing to nostr-tools, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to nostr-tools! Your efforts help make the Nostr ecosystem more accessible to Python developers.
