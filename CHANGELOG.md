# Changelog

All notable changes to nostr-tools will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2025-10-03

### Fixed

#### Documentation
- **Sphinx Build Compatibility** - Removed `-W` flag from docs-check to allow builds with dataclass duplicate warnings
- **Autosummary Template** - Added custom template with `:no-index:` directive to enable full autogeneration without errors
- **Dataclass Documentation** - Fixed duplicate object description warnings by filtering dataclass fields from autosummary stubs

#### Build & Distribution
- **Setuptools Version Constraint** - Constrained setuptools to `<75.0` to use Metadata-Version 2.1 for better twine compatibility
- **Package Metadata** - Fixed distribution check failures with older twine versions in CI environments

### Changed
- Documentation stubs now auto-generate cleanly without manual curation
- Improved CI pipeline reliability with better dependency version management

---

## [1.1.0] - 2025-10-03

### Added

#### Core Features
- **Enhanced Relay Metadata** - Separated NIP-11 and NIP-66 data structures for better organization
- **Improved Exception System** - Enhanced error handling with more specific exception types
- **Professional Development Infrastructure** - Comprehensive Makefile with 30+ development commands

#### Testing & Quality
- **Complete Test Suite Rewrite** - Professional test organization with 80%+ coverage
- **Enhanced Test Reliability** - Improved corrupted signature test stability
- **Security Scanning** - Added pip-audit with vulnerability ignore support

### Changed
- **Source Structure Refactoring** - Reorganized source code with dataclass-based relay metadata
- **Documentation Improvements** - Fixed inconsistencies and enhanced API documentation
- **CI/CD Pipeline** - Improved GitHub Actions workflow with better security scanning

### Fixed
- **Type Errors** - Resolved type checking issues across the codebase
- **Documentation Build** - Fixed Sphinx configuration and badge display
- **Codecov Integration** - Properly configured code coverage reporting

---

## [1.0.0] - 2025-09-15

### 🎉 First Stable Release

This is the first stable release of nostr-tools, a comprehensive Python library for building applications on the Nostr protocol.

### Added

#### Core Features
- **Complete Nostr Protocol Implementation** - Full support for NIP-01 basic protocol
- **Event Management** - Create, sign, verify, and serialize Nostr events
- **WebSocket Client** - Async WebSocket client with automatic reconnection
- **Relay Communication** - Connect to and interact with Nostr relays
- **Cryptographic Operations** - Key generation, signing, and verification using secp256k1
- **Event Filtering** - Advanced filtering with support for all NIP-01 filter attributes
- **Subscription Management** - Subscribe to events with multiple active subscriptions

#### Utilities
- **Key Management** - Generate and validate keypairs
- **Encoding/Decoding** - Bech32 encoding (npub, nsec) and hex conversion
- **Event ID Calculation** - Compute event IDs according to NIP-01
- **Proof of Work** - Generate events with configurable proof-of-work difficulty
- **URL Parsing** - Extract and validate WebSocket relay URLs
- **Relay Metadata** - Fetch and parse NIP-11 relay information documents

#### Developer Experience
- **Full Type Hints** - Complete type annotations for all public APIs
- **Async/Await Support** - Built on asyncio for concurrent operations
- **Context Managers** - Async context manager support for automatic cleanup
- **Comprehensive Documentation** - Detailed docstrings and usage examples
- **Error Handling** - Custom exceptions with descriptive error messages
- **Logging** - Structured logging throughout the library

#### Testing & Quality
- **Test Suite** - Comprehensive unit and integration tests
- **Code Coverage** - Over 80% test coverage
- **Type Checking** - MyPy strict mode compliance
- **Code Formatting** - Consistent formatting with Ruff
- **Security Scanning** - Automated security checks with Bandit, Safety, and pip-audit
- **Pre-commit Hooks** - Automated quality checks before commits

### Infrastructure
- **Modern Packaging** - PEP 517/518 compliant with pyproject.toml
- **CI/CD Pipeline** - GitHub Actions for testing and deployment
- **Documentation** - Sphinx documentation with Read the Docs integration
- **Distribution** - Automated PyPI releases on tag push
- **Development Tools** - Makefile with common development commands

### Security Features
- **Secure Random Generation** - Uses os.urandom() for cryptographic operations
- **Input Validation** - Comprehensive validation of all inputs
- **No Key Storage** - Private keys never stored or logged
- **Connection Security** - Supports secure WebSocket connections (wss://) with fallback
- **Enhanced Exception Handling** - Specific exception types for better error handling

### Supported Python Versions
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

### Dependencies
- secp256k1 (>=0.14.0) - Cryptographic operations
- bech32 (>=1.2.0) - Bech32 encoding/decoding
- aiohttp (>=3.9.0) - WebSocket client
- aiohttp-socks (>=0.8.0) - SOCKS proxy support

---

## Version Support Policy

### Supported Versions

| Version | Support Status | End of Support |
|---------|----------------|----------------|
| 1.1.x   | ✅ Active      | TBD            |
| 1.0.x   | ✅ Active      | TBD            |
| 0.x.x   | ❌ End of Life | 2025-09-14     |

### Support Timeline

- **Active Support**: Bug fixes, security updates, and new features
- **Security Support**: Security updates only
- **End of Life**: No further updates

We follow semantic versioning and maintain backward compatibility within major versions.

---

## Links

- [PyPI Package](https://pypi.org/project/nostr-tools/)
- [GitHub Repository](https://github.com/bigbrotr/nostr-tools)
- [Documentation](https://bigbrotr.github.io/nostr-tools/)
- [Issue Tracker](https://github.com/bigbrotr/nostr-tools/issues)
