# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**nostr-tools** is a comprehensive Python library for building applications on the Nostr protocol. It provides async WebSocket communication, cryptographic operations (secp256k1), event handling, relay management, and relay capability testing (NIP-11, NIP-66). Built for Python 3.9+ with extensive type hints and test coverage.

## Development Commands

### Setup
```bash
# Install development dependencies
make install-dev

# Setup pre-commit hooks
pre-commit install
```

### Testing
```bash
# Run all tests with coverage
make test

# Run unit tests only (fast)
make test-unit

# Quick tests without coverage
make test-quick

# Run specific test
pytest tests/test_file.py::TestClass::test_method -v
```

### Code Quality
```bash
# Run all quality checks (format + lint + type check)
make check

# Format code with Ruff
make format

# Run linters (Ruff + MyPy)
make lint

# Type checking with MyPy
make type-check
```

### Security
```bash
# Run all security scans (bandit + safety + pip-audit)
make security

# Individual scans
make security-bandit
make security-safety
make security-audit
```

### Documentation
```bash
# Build documentation
make docs-build

# Build and serve locally at http://localhost:8000
make docs-serve
```

### Comprehensive Checks
```bash
# All CI checks (format + lint + type + security + test)
make check-ci

# All checks including docs and build
make check-all
```

## Architecture Overview

### Module Structure
```
src/nostr_tools/
├── core/              # Core protocol classes
│   ├── event.py       # Event creation, validation, signing
│   ├── filter.py      # Event filtering and queries
│   ├── relay.py       # Relay URL validation and configuration
│   ├── client.py      # WebSocket client for relay communication
│   └── relay_metadata.py  # NIP-11 and NIP-66 relay metadata
├── utils/             # Cryptographic and utility functions
│   └── utils.py       # Key generation, encoding, event signing
├── actions/           # High-level protocol operations
│   └── actions.py     # Event fetching, streaming, relay testing
└── exceptions/        # Custom exception hierarchy
    └── errors.py      # Domain-specific exceptions
```

### Core Classes

**Event** (`core/event.py`): Fundamental data structure representing Nostr events (text notes, metadata, etc.). Handles validation, signing, and serialization.

**Filter** (`core/filter.py`): Defines criteria for querying and subscribing to events. Supports filtering by kinds, authors, tags, time ranges, and limits.

**Relay** (`core/relay.py`): Represents a Nostr relay server. Validates WebSocket URLs and detects network type (clearnet/tor).

**Client** (`core/client.py`): Manages WebSocket connections to relays. Handles publishing, subscribing, and real-time event streaming. Supports Tor via SOCKS5 proxy.

**RelayMetadata** (`core/relay_metadata.py`): Contains NIP-11 (relay info) and NIP-66 (relay monitoring) metadata for relay capabilities.

### Key Utilities (`utils/utils.py`)

- `generate_keypair()` - Create new secp256k1 keypair
- `generate_event()` - Create and sign events (with optional PoW)
- `to_bech32()` / `to_hex()` - Convert between hex and bech32 (npub/nsec) formats
- `validate_keypair()` - Verify keypair validity
- `verify_sig()` - Verify event signatures

### High-Level Actions (`actions/actions.py`)

- `fetch_events()` - Retrieve stored events from relay
- `stream_events()` - Subscribe to real-time event stream
- `fetch_nip11()` - Get relay capabilities (NIP-11)
- `fetch_nip66()` - Get relay monitoring data (NIP-66)
- `check_connectivity()`, `check_readability()`, `check_writability()` - Test relay capabilities

### Exception Hierarchy

The library uses **custom exceptions** for core and actions modules, **standard exceptions** (ValueError, TypeError) for utils module to maintain independence.

Custom exception hierarchy:
- `NostrToolsError` (base)
  - `EventError` → `EventValidationError`
  - `FilterError` → `FilterValidationError`
  - `RelayError` → `RelayValidationError`
  - `ClientError` → `ClientValidationError`, `ClientConnectionError`, `ClientSubscriptionError`, `ClientPublicationError`
  - `RelayMetadataError` → `RelayMetadataValidationError`
  - `Nip11Error` → `Nip11ValidationError`
  - `Nip66Error` → `Nip66ValidationError`

**Important**: Use custom exceptions in core/actions modules, standard exceptions in utils module. All exceptions must be documented in docstrings.

## Code Standards

### Type Hints
All public APIs require type hints. Run `make type-check` to verify.

```python
def connect_to_relay(url: str, timeout: Optional[int] = None) -> Client:
    """Connect to a Nostr relay.

    Args:
        url: WebSocket URL of the relay
        timeout: Connection timeout in seconds

    Returns:
        Connected Client instance

    Raises:
        ClientConnectionError: If connection fails
    """
    ...
```

### Docstrings
Use Google-style docstrings with Args, Returns, Raises, and Example sections.

### Testing
- Minimum 80% coverage required (`--cov-fail-under=80`)
- Write tests for all new features
- Use `@pytest.mark.asyncio` for async tests
- Use `@pytest.mark.unit` for fast unit tests
- Test exception handling paths

### Formatting
- Ruff handles formatting (line length: 100)
- Run `make format` before committing
- Pre-commit hooks enforce style automatically

### Async/Await
The library is fully async. All relay communication uses `asyncio`. Client supports context manager:

```python
async with client:
    success = await client.publish(event)
```

## Pre-commit Hooks

Pre-commit hooks run automatically on commit and include:
- Ruff formatting and linting
- MyPy type checking
- Bandit security scanning
- Safety dependency scanning
- Trailing whitespace, YAML/TOML/JSON validation

Skip hooks only when necessary: `git commit --no-verify`

## Release Process

Version is managed by `setuptools-scm` from git tags. To release:

```bash
# 1. Full verification
make verify-all

# 2. Create git tag
git tag -a v1.2.1 -m "Release v1.2.1"
git push origin v1.2.1

# 3. Build and publish (automated via GitHub Actions)
# Workflow publishes to Test PyPI for pre-releases, production PyPI for stable releases
```

## Important Notes

- **Lazy loading**: The package uses lazy imports for runtime performance. Direct imports are used during Sphinx docs builds (detected via `_BUILDING_DOCS`).
- **Security**: Never commit private keys. Use environment variables for sensitive data. Security scans ignore known false positives (e.g., `GHSA-4xh5-x5gv-qwph`).
- **Python versions**: Supports Python 3.9-3.13. Test compatibility when using newer features.
- **Dependencies**: Core runtime deps are minimal (aiohttp, aiohttp-socks, secp256k1, bech32). Dev deps include pytest, ruff, mypy, sphinx, security tools.

## Common Tasks

### Adding a New Feature
1. Create feature branch: `git checkout -b feature/name`
2. Write code with type hints and docstrings
3. Add tests with 80%+ coverage
4. Run `make check-all` to verify
5. Update documentation if needed
6. Commit and create PR

### Running a Single Test
```bash
pytest tests/unit/test_client.py::TestClient::test_connect -v -s
```

### Debugging Test Failures
```bash
# Show full output
pytest -vv --tb=long

# Run without coverage for speed
make test-quick
```

### Updating Dependencies
```bash
# Update pre-commit hooks
make deps-update

# Check for security vulnerabilities
make security
```
