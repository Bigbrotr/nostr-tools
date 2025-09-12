# Contributing to nostr-tools

Thank you for your interest in contributing to nostr-tools! This guide provides comprehensive information for contributors, from first-time contributors to experienced developers. We welcome contributions of all kinds: bug reports, feature requests, documentation improvements, code contributions, and community engagement.

## 🎯 Quick Start for Contributors

```bash
# 1. Fork and clone the repository
git clone https://github.com/your-username/nostr-tools.git
cd nostr-tools

# 2. Set up development environment
make install-dev

# 3. Run pre-commit hooks
make pre-commit

# 4. Make your changes and test
make dev-check

# 5. Create pull request
git push origin feature/your-feature-name
```

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Development Guidelines](#development-guidelines)
- [Testing Strategy](#testing-strategy)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Release Process](#release-process)
- [Community](#community)

## 🤝 Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

### Our Pledge
We are committed to providing a welcoming and inclusive experience for everyone, regardless of age, body size, disability, ethnicity, sex characteristics, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards
- **Be Respectful**: Treat all community members with respect and kindness
- **Be Inclusive**: Welcome newcomers and help them feel comfortable
- **Be Constructive**: Provide helpful feedback and suggestions
- **Be Professional**: Maintain a professional tone in all interactions
- **Be Patient**: Remember that people have different levels of experience

### Unacceptable Behavior
- Harassment, trolling, or discriminatory language
- Personal attacks or insults
- Spam or off-topic discussions
- Sharing private information without consent
- Any behavior that would be inappropriate in a professional setting

### Enforcement
Violations of the Code of Conduct should be reported to hello@bigbrotr.com. All reports will be handled confidentially and promptly.

## 🛠️ Development Environment

### Prerequisites

- **Python 3.9+** (tested on 3.9, 3.10, 3.11, 3.12)
- **Git** for version control
- **Make** for build automation (optional but recommended)

### System Dependencies

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y build-essential pkg-config libffi-dev autoconf automake libtool
```

#### macOS
```bash
# Install Xcode command line tools
xcode-select --install

# Or using Homebrew
brew install autoconf automake libtool
```

#### Windows
```bash
# Using chocolatey
choco install visualstudio2019buildtools

# Or install Visual Studio Build Tools manually
```

### Setup Steps

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/your-username/nostr-tools.git
   cd nostr-tools
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   # Using make (recommended)
   make install-dev

   # Or manually
   pip install -e .[dev,test,security,docs]
   ```

4. **Set up Pre-commit Hooks**
   ```bash
   make pre-commit
   # This installs git hooks for automatic code quality checks
   ```

5. **Verify Installation**
   ```bash
   make dev-check
   # This runs formatting, linting, and unit tests
   ```

### Development Tools

We use the following tools to maintain high code quality:

- **[Ruff](https://github.com/astral-sh/ruff)**: Ultra-fast Python linter and formatter (replaces black, flake8, isort)
- **[MyPy](https://mypy.readthedocs.io/)**: Static type checking
- **[Pytest](https://pytest.org/)**: Testing framework with async support
- **[Pre-commit](https://pre-commit.com/)**: Git hooks for code quality
- **[Bandit](https://bandit.readthedocs.io/)**: Security vulnerability scanning

## 📁 Project Structure

```
nostr_tools/
├── core/                   # Core protocol components
│   ├── __init__.py        # Core exports
│   ├── client.py          # WebSocket client implementation
│   ├── event.py           # Event representation and validation
│   ├── filter.py          # Event filtering system
│   ├── relay.py           # Relay configuration and validation
│   └── relay_metadata.py  # Relay metadata management
├── actions/               # High-level action functions
│   ├── __init__.py       # Action exports
│   └── actions.py        # Event fetching, streaming, relay testing
├── utils/                 # Utility functions
│   ├── __init__.py       # Utility exports
│   └── utils.py          # Cryptographic, encoding, and helper functions
├── exceptions/            # Custom exceptions
│   ├── __init__.py       # Exception exports
│   └── errors.py         # RelayConnectionError and other exceptions
└── __init__.py           # Main package exports with lazy loading

tests/                     # Test suite
├── __init__.py           # Test configuration
├── conftest.py           # Pytest fixtures and configuration
├── test_basic.py         # Unit tests for core functionality
├── test_integration.py   # Integration tests with real relays
├── test_security.py      # Security and cryptographic tests
└── test_performance.py   # Performance benchmarks and regression tests

examples/                  # Example applications
├── basic_usage.py        # Fundamental operations and patterns
└── advanced_features.py  # Complex use cases and advanced features

docs/                      # Documentation (if added)
└── ...

.github/                   # GitHub configuration
├── workflows/
│   ├── ci.yml           # Continuous integration pipeline
│   └── publish.yml      # PyPI publishing workflow
└── ...

# Configuration files
pyproject.toml            # Project configuration and dependencies
Makefile                  # Development task automation
.pre-commit-config.yaml   # Pre-commit hook configuration
.gitignore               # Git ignore patterns
LICENSE                   # MIT license
README.md                 # Main documentation
CHANGELOG.md              # Version history and changes
CONTRIBUTING.md           # This file
SECURITY.md               # Security policy and reporting
MANIFEST.in               # Package distribution files
```

### Key Design Principles

1. **Separation of Concerns**: Core protocol logic separated from high-level actions
2. **Type Safety**: Complete type hints with runtime validation
3. **Async First**: All I/O operations use async/await patterns
4. **Error Handling**: Comprehensive error handling with specific exception types
5. **Testing**: Every component has corresponding tests
6. **Documentation**: All public APIs have comprehensive docstrings

## 📝 Development Guidelines

### Code Style and Standards

#### Python Code Style
We use **Ruff** for both linting and formatting, which provides a consistent and modern code style:

```bash
# Format code (replaces black)
make format

# Lint code (replaces flake8, isort, and others)
make lint

# Fix linting issues automatically
make lint-fix
```

#### Key Style Guidelines
- **Line Length**: 88 characters (black-compatible)
- **Imports**: Organized using isort rules integrated into Ruff
- **Strings**: Use double quotes for strings
- **Type Hints**: Required for all public functions and methods
- **Docstrings**: Google-style docstrings for all public APIs

#### Example Code Style
```python
"""Module docstring explaining the purpose."""

from typing import Any, Dict, List, Optional

from nostr_tools.core.event import Event


class ExampleClass:
    """
    Example class demonstrating code style.

    This class shows the expected format for documentation,
    type hints, and general code organization.

    Attributes:
        name (str): Name of the example
        value (Optional[int]): Optional integer value
    """

    def __init__(self, name: str, value: Optional[int] = None) -> None:
        """
        Initialize the example class.

        Args:
            name (str): The name for this example
            value (Optional[int]): Optional integer value

        Raises:
            ValueError: If name is empty
        """
        if not name:
            raise ValueError("name cannot be empty")

        self.name = name
        self.value = value

    def process_events(self, events: List[Event]) -> Dict[str, Any]:
        """
        Process a list of events and return summary statistics.

        Args:
            events (List[Event]): Events to process

        Returns:
            Dict[str, Any]: Summary statistics including count and types

        Example:
            >>> classifier = ExampleClass("test")
            >>> events = [event1, event2]
            >>> stats = classifier.process_events(events)
            >>> print(stats["count"])
            2
        """
        stats = {
            "count": len(events),
            "kinds": list({event.kind for event in events}),
            "average_content_length": (
                sum(len(event.content) for event in events) / len(events)
                if events else 0
            ),
        }
        return stats
```

### Type Hints and Validation

#### Required Type Annotations
All public functions must have complete type annotations:

```python
from typing import Any, Dict, List, Optional, Tuple, Union

# ✅ Good - complete type hints
def process_relay_metadata(
    relay_url: str,
    timeout: Optional[int] = None
) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Process relay metadata with proper types."""
    # Implementation...
    return True, {"name": "example"}

# ❌ Bad - missing type hints
def process_relay_metadata(relay_url, timeout=None):
    """Process relay metadata without types."""
    return True, {"name": "example"}
```

#### Runtime Validation
For critical functions, implement runtime type validation:

```python
def validate_event_data(data: Dict[str, Any]) -> None:
    """
    Validate event data structure.

    Args:
        data (Dict[str, Any]): Event data to validate

    Raises:
        TypeError: If data is not a dictionary
        KeyError: If required keys are missing
        ValueError: If values are invalid
    """
    if not isinstance(data, dict):
        raise TypeError(f"data must be a dict, not {type(data)}")

    required_keys = ["id", "pubkey", "created_at", "kind", "tags", "content", "sig"]
    for key in required_keys:
        if key not in data:
            raise KeyError(f"data must contain key '{key}'")

    # Additional validation...
```

### Error Handling Standards

#### Use Specific Exceptions
Create and use specific exception types for different error categories:

```python
from nostr_tools.exceptions import RelayConnectionError

# ✅ Good - specific exception
async def connect_to_relay(url: str) -> None:
    try:
        # Connection logic...
        pass
    except ConnectionRefusedError as e:
        raise RelayConnectionError(f"Failed to connect to {url}: {e}") from e

# ❌ Bad - generic exception
async def connect_to_relay(url: str) -> None:
    try:
        # Connection logic...
        pass
    except Exception as e:
        raise Exception(f"Something went wrong: {e}")
```

#### Comprehensive Error Information
Provide helpful error messages with context:

```python
def validate_private_key(private_key: str) -> None:
    """Validate private key format and content."""
    if not isinstance(private_key, str):
        raise TypeError(
            f"private_key must be a string, not {type(private_key).__name__}"
        )

    if len(private_key) != 64:
        raise ValueError(
            f"private_key must be exactly 64 characters, got {len(private_key)}"
        )

    try:
        int(private_key, 16)
    except ValueError as e:
        raise ValueError(
            f"private_key must be a valid hexadecimal string: {e}"
        ) from e
```

### Async Programming Guidelines

#### Always Use Async/Await
All I/O operations must use async/await patterns:

```python
# ✅ Good - proper async usage
async def fetch_relay_info(client: Client) -> Optional[Dict[str, Any]]:
    """Fetch relay information asynchronously."""
    try:
        async with client:
            return await client.fetch_nip11()
    except RelayConnectionError as e:
        logger.warning(f"Failed to fetch relay info: {e}")
        return None

# ❌ Bad - blocking I/O
def fetch_relay_info(client: Client) -> Optional[Dict[str, Any]]:
    """This would block the event loop."""
    # Blocking operations not allowed
```

#### Resource Management
Use async context managers for proper resource cleanup:

```python
# ✅ Good - proper resource management
async def process_events_from_relay(relay_url: str) -> List[Event]:
    """Process events with proper resource cleanup."""
    relay = Relay(relay_url)
    client = Client(relay)

    async with client:  # Automatically handles cleanup
        filter = Filter(kinds=[1], limit=10)
        return await fetch_events(client, filter)

# ❌ Bad - manual resource management
async def process_events_from_relay(relay_url: str) -> List[Event]:
    """Manual resource management is error-prone."""
    relay = Relay(relay_url)
    client = Client(relay)

    await client.connect()
    try:
        filter = Filter(kinds=[1], limit=10)
        return await fetch_events(client, filter)
    finally:
        await client.disconnect()  # Easy to forget or get wrong
```

## 🧪 Testing Strategy

### Test Categories and Organization

We maintain comprehensive test coverage across multiple categories:

#### Unit Tests (`pytest -m unit`)
- **Fast execution** (< 100ms per test)
- **No network dependencies**
- **Mock external services**
- **Test individual components in isolation**

```python
# Example unit test
def test_event_creation(sample_keypair):
    """Test Event object creation and validation."""
    private_key, public_key = sample_keypair
    event_data = generate_event(
        private_key, public_key, 1, [], "test content"
    )
    event = Event.from_dict(event_data)

    assert event.content == "test content"
    assert event.kind == 1
    assert len(event.id) == 64
    assert verify_sig(event.id, event.pubkey, event.sig)
```

#### Integration Tests (`pytest -m integration`)
- **Network-dependent** (require real Nostr relays)
- **Test component interactions**
- **May be slower** (network I/O)
- **Skip when NOSTR_SKIP_INTEGRATION=true**

```python
@pytest.mark.integration
@skip_integration
async def test_real_relay_connection(sample_client):
    """Test connection to a real Nostr relay."""
    try:
        async with sample_client:
            filter = Filter(kinds=[1], limit=1)
            events = await fetch_events(sample_client, filter)
            assert isinstance(events, list)
    except RelayConnectionError:
        pytest.skip("Test relay not accessible")
```

#### Security Tests (`pytest -m security`)
- **Cryptographic security validation**
- **Attack vector testing**
- **Input validation security**
- **Memory safety verification**

```python
@pytest.mark.security
def test_signature_security(sample_keypair):
    """Test that signatures are not reusable across different events."""
    private_key, public_key = sample_keypair

    # Create two different events
    event1_data = generate_event(private_key, public_key, 1, [], "content1")
    event2_data = generate_event(private_key, public_key, 1, [], "content2")

    # Signatures should be different
    assert event1_data["sig"] != event2_data["sig"]

    # Cross-validation should fail
    assert not verify_sig(event1_data["id"], public_key, event2_data["sig"])
    assert not verify_sig(event2_data["id"], public_key, event1_data["sig"])
```

#### Performance Tests (`pytest -m slow`)
- **Benchmark critical operations**
- **Performance regression detection**
- **Resource usage validation**
- **Scalability testing**

```python
@pytest.mark.slow
def test_key_generation_performance(performance_timer):
    """Test key generation performance meets requirements."""
    iterations = 100

    performance_timer.start()
    for _ in range(iterations):
        generate_keypair()
    performance_timer.stop()

    avg_time = performance_timer.elapsed / iterations
    # Should generate at least 10 keypairs per second
    assert avg_time < 0.1, f"Key generation too slow: {avg_time:.4f}s"
```

### Testing Commands

```bash
# Run all tests
make test

# Run specific test categories
make test-unit          # Fast unit tests only
make test-integration   # Integration tests with real relays
make test-security      # Security-focused tests
make test-performance   # Performance benchmarks

# Generate coverage report
make test-cov

# Run tests with specific markers
pytest -m "unit and not slow"
pytest -m "integration or security"

# Run specific test file
pytest tests/test_basic.py

# Run with verbose output
pytest -v

# Run with custom timeout for integration tests
NOSTR_TEST_TIMEOUT=30 pytest -m integration
```

### Writing Good Tests

#### Test Naming Convention
- Use descriptive names that explain what is being tested
- Follow the pattern `test_<component>_<behavior>_<expected_result>`

```python
# ✅ Good test names
def test_event_creation_with_valid_data_succeeds():
def test_relay_connection_with_invalid_url_raises_error():
def test_filter_validation_with_negative_limit_raises_ValueError():

# ❌ Poor test names
def test_event():
def test_connection():
def test_error():
```

#### Test Structure (Arrange, Act, Assert)
```python
def test_event_tag_filtering():
    """Test that events can be filtered by tag content."""
    # Arrange
    private_key, public_key = generate_keypair()
    event_data = generate_event(
        private_key, public_key, 1, [["t", "bitcoin"]], "Bitcoin content"
    )
    event = Event.from_dict(event_data)

    # Act
    has_bitcoin_tag = event.has_tag("t", "bitcoin")
    has_nostr_tag = event.has_tag("t", "nostr")

    # Assert
    assert has_bitcoin_tag is True
    assert has_nostr_tag is False
```

#### Use Fixtures for Common Setup
```python
# In conftest.py
@pytest.fixture
def sample_event_with_tags(sample_keypair):
    """Create a sample event with predefined tags."""
    private_key, public_key = sample_keypair
    tags = [["t", "nostr"], ["t", "bitcoin"], ["p", public_key]]
    event_data = generate_event(
        private_key, public_key, 1, tags, "Test content with tags"
    )
    return Event.from_dict(event_data)

# In test files
def test_tag_extraction(sample_event_with_tags):
    """Test extracting tag values from events."""
    event = sample_event_with_tags
    hashtags = event.get_tag_values("t")
    assert "nostr" in hashtags
    assert "bitcoin" in hashtags
```

## 📚 Documentation

### Docstring Standards

We use **Google-style docstrings** for all public APIs:

```python
def generate_event(
    private_key: str,
    public_key: str,
    kind: int,
    tags: List[List[str]],
    content: str,
    created_at: Optional[int] = None,
    target_difficulty: Optional[int] = None,
    timeout: int = 20,
) -> Dict[str, Any]:
    """
    Generate a signed Nostr event with optional proof-of-work.

    This function creates a complete Nostr event with proper ID calculation,
    signature generation, and optional proof-of-work nonce mining. The event
    follows NIP-01 specification for structure and validation.

    Args:
        private_key (str): Private key in hex format (64 characters)
        public_key (str): Public key in hex format (64 characters)
        kind (int): Event kind (0-65535) as defined by NIPs
        tags (List[List[str]]): List of event tags, each tag is a list of strings
        content (str): Event content (arbitrary string)
        created_at (Optional[int]): Unix timestamp (defaults to current time)
        target_difficulty (Optional[int]): Proof of work difficulty target (leading zero bits)
        timeout (int): Timeout for proof of work mining in seconds (default: 20)

    Returns:
        Dict[str, Any]: Complete signed event dictionary with keys:
                       id, pubkey, created_at, kind, tags, content, sig

    Raises:
        ValueError: If private_key or public_key format is invalid
        TypeError: If any argument has incorrect type
        TimeoutError: If proof-of-work mining times out (implicitly handled)

    Example:
        Basic event creation:

        >>> private_key, public_key = generate_keypair()
        >>> event = generate_event(
        ...     private_key, public_key, 1, [], "Hello Nostr!"
        ... )
        >>> len(event["id"])
        64

        Event with proof-of-work:

        >>> pow_event = generate_event(
        ...     private_key, public_key, 1, [], "PoW event",
        ...     target_difficulty=16, timeout=30
        ... )
        >>> # Check for nonce tag
        >>> nonce_tags = [tag for tag in pow_event["tags"] if tag[0] == "nonce"]
        >>> len(nonce_tags) > 0
        True

    Note:
        Proof-of-work mining may not complete within the timeout period for high
        difficulty targets. In such cases, the event is returned without the
        proof-of-work nonce tag.

        The generated event ID is deterministic based on the event content but
        signatures will vary due to cryptographic randomness in the signing process.
    """
```

#### Key Docstring Elements
1. **Summary Line**: Brief one-line description
2. **Detailed Description**: Comprehensive explanation of functionality
3. **Args Section**: Complete parameter documentation with types
4. **Returns Section**: Return value description with type information
5. **Raises Section**: All possible exceptions that may be raised
6. **Example Section**: Practical usage examples with expected output
7. **Note Section**: Important additional information and caveats

### README Updates

When adding new features, update the main README.md:

1. **Quick Start Section**: Add basic usage examples
2. **Features List**: Update the feature overview
3. **API Reference**: Add new functions/classes to the reference
4. **Examples**: Provide comprehensive usage examples

### Code Comments

Use comments sparingly and effectively:

```python
# ✅ Good - explains why, not what
def count_leading_zero_bits(hex_str: str) -> int:
    """Count leading zero bits for proof-of-work validation."""
    bits = 0
    for char in hex_str:
        val = int(char, 16)
        if val == 0:
            bits += 4  # Each hex char represents 4 bits
        else:
            # Stop at first non-zero and count its leading zeros
            bits += 4 - val.bit_length()
            break
    return bits

# ❌ Bad - explains what the code obviously does
def count_leading_zero_bits(hex_str: str) -> int:
    """Count leading zero bits for proof-of-work validation."""
    bits = 0  # Initialize counter
    for char in hex_str:  # Loop through each character
        val = int(char, 16)  # Convert hex char to int
        if val == 0:  # If character is zero
            bits += 4  # Add 4 bits
```

## 🔄 Pull Request Process

### Before Creating a Pull Request

1. **Fork and Branch**: Create a feature branch from `main`
   ```bash
   git checkout -b feature/descriptive-name
   ```

2. **Development**: Make your changes following our guidelines
   ```bash
   # Regular development workflow
   make dev-check  # Format, lint, and test
   ```

3. **Comprehensive Testing**: Ensure all tests pass
   ```bash
   make test        # All tests
   make test-cov    # With coverage report
   ```

4. **Documentation**: Update relevant documentation
   - Add/update docstrings for new/modified functions
   - Update README.md if needed
   - Add examples for new features

### Pull Request Guidelines

#### PR Title Format
Use conventional commit format for PR titles:

```
feat(core): add proof-of-work mining support
fix(client): resolve connection timeout handling
docs(readme): update installation instructions
test(security): add signature validation tests
refactor(utils): improve error handling consistency
```

#### PR Description Template
```markdown
## Description
Brief description of the changes and their purpose.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Integration tests pass (if applicable)
- [ ] Performance tests pass (if applicable)

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is documented (docstrings, comments)
- [ ] Changes are covered by tests
- [ ] No new warnings or errors introduced
- [ ] CHANGELOG.md updated (if applicable)

## Related Issues
Closes #123
Addresses #456

## Screenshots (if applicable)
Include any relevant screenshots or output samples.

## Additional Notes
Any additional information that reviewers should know.
```

#### Review Process

1. **Automated Checks**: All CI checks must pass
   - Code formatting and linting
   - Type checking
   - Security scans
   - Test suite (unit, integration, security)

2. **Manual Review**: Core maintainers will review for:
   - Code quality and adherence to guidelines
   - Test coverage and quality
   - Documentation completeness
   - API design consistency
   - Performance implications

3. **Approval Requirements**:
   - At least one approving review from a core maintainer
   - All CI checks passing
   - Conflicts resolved
   - Documentation updated

### Common Review Comments

#### Code Quality
- **Simplification**: "This logic can be simplified using..."
- **Error Handling**: "Consider adding error handling for..."
- **Performance**: "This operation could be optimized by..."
- **Testing**: "Please add tests for the error case where..."

#### Documentation
- **Missing Docstrings**: "Please add docstrings for public methods"
- **Examples**: "Consider adding usage examples to the docstring"
- **Type Hints**: "Missing type hint for return value"

## 🐛 Issue Guidelines

### Bug Reports

Use the bug report template to provide comprehensive information:

```markdown
**Bug Description**
A clear and concise description of what the bug is.

**Steps to Reproduce**
1. Create a client with relay "wss://example.com"
2. Attempt to connect using `async with client:`
3. Observe the error

**Expected Behavior**
Connection should succeed and allow event publishing.

**Actual Behavior**
Connection times out after 10 seconds with RelayConnectionError.

**Environment**
- OS: Ubuntu 22.04 LTS
- Python: 3.11.5
- nostr-tools version: 0.1.0
- Installation method: pip install

**Error Messages/Traceback**
```
Traceback (most recent call last):
  ...
RelayConnectionError: Failed to connect to wss://example.com: Connection timeout
```

**Additional Context**
- Works with other relays like relay.damus.io
- Network connection is stable
- Firewall allows WebSocket connections

**Possible Solution** (optional)
If you have any ideas about what might be causing the issue.
```

### Feature Requests

Provide detailed information about proposed features:

```markdown
**Feature Description**
A clear and concise description of the feature you'd like to see added.

**Use Case**
Describe the use case that this feature would enable or improve.

**Proposed API**
If you have ideas about the API design, include them here:

```python
# Example of proposed API
relay_pool = RelayPool(["wss://relay1.com", "wss://relay2.com"])
await relay_pool.publish_event(event)  # Publishes to all relays
```

**Alternatives Considered**
What alternative solutions or features have you considered?

**Additional Context**
Any other context, screenshots, or examples about the feature request.

**Implementation Notes** (optional)
If you have ideas about implementation approach.
```

### Issue Labels

We use labels to categorize and prioritize issues:

- **Type Labels**:
  - `bug`: Something isn't working correctly
  - `enhancement`: New feature or improvement
  - `documentation`: Documentation improvements
  - `performance`: Performance-related issues

- **Priority Labels**:
  - `priority:high`: Critical issues requiring immediate attention
  - `priority:medium`: Important issues for the next release
  - `priority:low`: Nice-to-have improvements

- **Component Labels**:
  - `core`: Core protocol components
  - `client`: WebSocket client functionality
  - `crypto`: Cryptographic operations
  - `tests`: Testing-related issues

- **Status Labels**:
  - `good first issue`: Suitable for new contributors
  - `help wanted`: Community assistance welcome
  - `needs investigation`: Requires further analysis

## 🚀 Release Process

### Versioning Strategy

We follow [Semantic Versioning (SemVer)](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes that require code modifications
- **MINOR** (0.X.0): New features that are backward compatible
- **PATCH** (0.0.X): Bug fixes that are backward compatible

### Release Timeline

- **Major Releases**: Every 6-12 months
- **Minor Releases**: Every 1-2 months
- **Patch Releases**: As needed for critical bug fixes

### Release Checklist

#### Pre-Release
- [ ] All tests passing on CI
- [ ] Documentation updated
- [ ] CHANGELOG.md updated with new features and fixes
- [ ] Version numbers updated in `pyproject.toml` and `__init__.py`
- [ ] Security audit completed
- [ ] Performance regression testing completed

#### Release Process
- [ ] Create release PR with version updates
- [ ] Merge release PR after approval
- [ ] Create and push Git tag
- [ ] GitHub Actions automatically publishes to PyPI
- [ ] Create GitHub release with changelog
- [ ] Announce release in community channels

#### Post-Release
- [ ] Monitor for any issues in the first 24 hours
- [ ] Update documentation sites
- [ ] Prepare patch release if critical issues discovered

### Breaking Changes

When introducing breaking changes:

1. **Deprecation Period**: Mark old API as deprecated in previous minor release
2. **Migration Guide**: Provide clear upgrade instructions
3. **Version Bump**: Increment major version number
4. **Communication**: Announce breaking changes prominently

Example deprecation warning:
```python
import warnings

def old_function():
    """Old function that will be removed."""
    warnings.warn(
        "old_function is deprecated and will be removed in v2.0.0. "
        "Use new_function instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # Implementation...
```

## 🌟 Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussion
- **Email**: hello@bigbrotr.com for general inquiries
- **Security**: security@bigbrotr.com for security-related matters

### Getting Help

1. **Check Documentation**: Start with README.md and docstrings
2. **Search Issues**: Look for similar problems or questions
3. **Create Issue**: Open a new issue with detailed information
4. **Community Discussion**: Engage in GitHub Discussions

### Recognition and Credits

Contributors are recognized in several ways:

- **CHANGELOG.md**: Significant contributions mentioned in release notes
- **GitHub Contributors**: Automatic recognition in repository statistics
- **Release Notes**: Major contributors highlighted in release announcements
- **Documentation**: Contributor acknowledgments in README.md

### Maintainer Responsibilities

Current maintainers commit to:

- **Timely Response**: Respond to issues and PRs within 1 week
- **Code Review**: Provide thorough and constructive feedback
- **Release Management**: Coordinate releases and maintain quality
- **Community Support**: Foster a welcoming and inclusive environment
- **Documentation**: Keep documentation accurate and up-to-date

### Becoming a Maintainer

Long-term contributors may be invited to become maintainers based on:

- **Consistent Contributions**: Regular, high-quality contributions over time
- **Code Quality**: Demonstrates understanding of project standards
- **Community Engagement**: Helps other contributors and users
- **Domain Expertise**: Shows deep understanding of the Nostr protocol
- **Reliability**: Consistently available and responsive

## 🎯 Contribution Areas

### High-Priority Areas

1. **NIP Implementation**: Help implement new Nostr Improvement Proposals
2. **Performance Optimization**: Improve cryptographic operation speed
3. **Documentation**: Enhance examples and API documentation
4. **Testing**: Expand test coverage, especially integration tests
5. **Security**: Security audits and vulnerability assessments

### Good First Issues

New contributors can start with:

- **Documentation Improvements**: Fix typos, add examples, clarify instructions
- **Test Coverage**: Add tests for existing functionality
- **Code Cleanup**: Refactor code for better readability
- **Example Applications**: Create new example use cases
- **Bug Fixes**: Resolve small, well-defined bugs

### Advanced Contributions

Experienced contributors can work on:

- **New NIP Support**: Implement support for additional Nostr NIPs
- **Performance Enhancements**: Optimize critical path operations
- **Architecture Improvements**: Enhance overall system design
- **Integration Features**: Add support for new relay types or protocols

## ❓ FAQ for Contributors

### Development Questions

**Q: How do I run tests locally?**
A: Use `make test` for all tests, or specific commands like `make test-unit` for faster unit tests only.

**Q: My code fails pre-commit hooks. How do I fix it?**
A: Run `make format` to format your code, then `make lint-fix` to automatically fix linting issues.

**Q: How do I test with real Nostr relays?**
A: Run `make test-integration` to run integration tests with real relays. Set `NOSTR_SKIP_INTEGRATION=false` if needed.

**Q: How do I add support for a new NIP?**
A: Start by creating an issue to discuss the implementation approach, then follow our development guidelines for adding new features.

### Process Questions

**Q: How long does code review take?**
A: We aim to provide initial feedback within 1 week. Complex changes may take longer for thorough review.

**Q: Can I work on multiple features at once?**
A: We recommend focusing on one feature per PR for easier review and testing.

**Q: How do I know if my contribution is needed?**
A: Check our GitHub issues for features marked as "help wanted" or "good first issue."

---

## 🙏 Thank You

Thank you for contributing to nostr-tools! Your efforts help build a more decentralized and open internet. Every contribution, whether it's a bug report, documentation improvement, or new feature, makes a difference.

**Remember**: Contributing to open source is a learning experience. Don't hesitate to ask questions, and don't worry about making mistakes. We're here to help you succeed and grow as a contributor.

---

*For the latest contribution guidelines and updates, always refer to the version in the main branch of the repository.*
