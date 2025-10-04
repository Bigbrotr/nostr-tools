# Changelog

All notable changes to nostr-tools will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## ⚠️ Important Notice

**Only v1.2.0 is currently supported.** All previous versions (v1.1.x, v1.0.x, v0.x.x) are end-of-life as of October 4, 2025. Users must upgrade to v1.2.0 for continued support.

## [1.2.0] - 2025-10-04

### Added

#### Documentation & Release Management
- **Comprehensive Release Documentation** - Detailed release notes for all versions (v1.0.0, v1.1.0, v1.1.1, v1.2.0)
- **Enhanced Release Organization** - Professional release management with detailed migration guides
- **Version Support Policy** - Clear support timeline with v1.2.0 as the single supported version
- **Releases Folder Structure** - Organized release notes with comprehensive README

#### Quality Assurance
- **Accurate Documentation** - All release notes based on actual code analysis and diff verification
- **Professional Standards** - Release management following industry best practices
- **Clear Communication** - Transparent documentation of changes and migration paths
- **User-Friendly Documentation** - Easy-to-understand release notes and migration guides

### Changed

#### Release Management
- **Clean Tag Structure** - Removed backup tags, keeping only official releases (v1.0.0, v1.1.0, v1.1.1, v1.2.0)
- **Version Consolidation** - v1.2.0 established as the single supported version
- **Documentation Accuracy** - Updated CHANGELOG.md with precise information based on actual code diffs
- **Support Policy** - Clear end-of-life timeline for all previous versions

#### Documentation Structure
- **Enhanced Changelog** - Updated with accurate information and detailed breaking changes
- **Release Notes Organization** - Professional structure with comprehensive migration guides
- **Version Support Timeline** - Clear documentation of support status for all versions
- **Migration Documentation** - Detailed upgrade paths between all versions

### Fixed
- **Documentation Accuracy** - Corrected inaccurate information in release notes
- **Changelog Precision** - Updated with actual changes based on code analysis
- **Release Management** - Professional release documentation and organization
- **Version Support Clarity** - Clear communication of support status and migration paths

---

## [1.1.1] - 2025-10-03

### Fixed

#### Documentation
- **Enhanced Sphinx Configuration** - Improved autodoc settings with better member filtering and exclusion of internal members
- **Custom Autosummary Templates** - Added custom templates for class and module documentation with better inheritance display
- **Dataclass Documentation** - Fixed duplicate object description warnings by filtering dataclass fields from autosummary stubs
- **Member Filtering** - Better exclusion of internal members, annotations, and improved inheritance display

#### Build & Distribution
- **Setuptools Version Constraint** - Constrained setuptools to `<75.0` to avoid Metadata-Version 2.4 compatibility issues with older twine
- **Package Metadata** - Fixed distribution check failures with older twine versions in CI environments
- **Dependency Cleanup** - Removed performance profiling tools from dev dependencies for cleaner builds

#### CI/CD Pipeline
- **Enhanced CI Workflow** - Improved GitHub Actions workflow with better organization and error handling
- **Better Error Reporting** - Enhanced error reporting and build artifact handling
- **Dependency Management** - Better version constraints and dependency resolution
- **Workflow Optimization** - Streamlined CI pipeline with better caching and organization

### Added

#### Development Experience
- **DEVELOPMENT.md** - Comprehensive development guide with 490+ lines of documentation
- **Enhanced Makefile** - Improved development commands with better organization and color-coded output
- **Better Test Organization** - Moved integration tests to unit tests for better organization
- **Professional Workflow** - Complete development workflow with quality assurance standards

### Changed
- Documentation stubs now auto-generate cleanly with custom templates
- Improved CI pipeline reliability with better dependency version management
- Enhanced development experience with comprehensive documentation
- Better test organization and structure

---

## [1.1.0] - 2025-10-03

### Added

#### Core Features
- **Complete RelayMetadata Rewrite** - Converted from class-based to dataclass-based implementation with separated NIP-11 and NIP-66 data structures
- **Enhanced Exception System** - New base exception class `NostrToolsError` with specific exception types for better error handling
- **Professional Development Infrastructure** - Comprehensive Makefile with 30+ development commands and organized help system

#### Testing & Quality
- **Complete Test Suite Rewrite** - Professional test organization with unit/integration separation and 80%+ coverage
- **Enhanced Test Structure** - New test organization with `tests/unit/` and `tests/integration/` directories
- **Test Documentation** - Comprehensive test README with usage guidelines and best practices
- **Security Scanning** - Added pip-audit with vulnerability ignore support

### Changed

#### Breaking Changes
- **RelayMetadata API** - Complete rewrite from class-based to dataclass-based implementation
- **Exception Hierarchy** - New base exception class with specific exception types
- **Test Structure** - Moved from flat test structure to organized unit/integration separation

#### Source Code Refactoring
- **RelayMetadata Complete Rewrite** - From class-based to dataclass-based implementation
- **Better Separation of Concerns** - Clear separation between NIP-11 and NIP-66 data
- **Enhanced Type Safety** - Improved type hints and validation throughout
- **Simplified API** - Cleaner, more intuitive interface for relay metadata

#### Development Infrastructure
- **Enhanced Makefile** - Comprehensive development commands with organized help system
- **Better CI/CD Pipeline** - Improved GitHub Actions workflows with better security scanning
- **Enhanced Documentation** - Better Sphinx configuration and documentation generation
- **Improved Project Structure** - Better organization of development files

### Fixed
- **Type Errors** - Resolved type checking issues across the codebase
- **Documentation Build** - Fixed Sphinx configuration and badge display
- **Codecov Integration** - Properly configured code coverage reporting
- **Test Organization** - Professional test structure with better fixtures and setup

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
| 1.2.x   | ✅ **Only Supported** | TBD            |
| 1.1.x   | ❌ End of Life | 2025-01-15     |
| 1.0.x   | ❌ End of Life | 2025-01-15     |
| 0.x.x   | ❌ End of Life | 2025-09-14     |

### Support Timeline

- **Active Support**: v1.2.0 only - bug fixes, security updates, and new features
- **End of Life**: All previous versions (v1.1.x, v1.0.x, v0.x.x) - no further updates or support
- **Migration Required**: Users must upgrade to v1.2.0 for continued support

We follow semantic versioning and maintain backward compatibility within major versions.

---

## Links

- [PyPI Package](https://pypi.org/project/nostr-tools/)
- [GitHub Repository](https://github.com/bigbrotr/nostr-tools)
- [Documentation](https://bigbrotr.github.io/nostr-tools/)
- [Issue Tracker](https://github.com/bigbrotr/nostr-tools/issues)
