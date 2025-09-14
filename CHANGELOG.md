# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive project restructure and modernization
- Complete CI/CD pipeline with GitHub Actions
- Automated documentation generation with Sphinx
- Pre-commit hooks for code quality enforcement
- Security scanning with Bandit, Safety, and pip-audit
- Type checking with MyPy
- Code formatting and linting with Ruff
- Coverage reporting with pytest-cov
- ReadTheDocs integration
- GitHub Pages documentation deployment

### Changed
- Updated pyproject.toml to follow modern Python packaging standards
- Restructured project to use src-layout
- Enhanced package metadata and dependencies
- Improved development workflow with Makefile commands

### Fixed
- Package name consistency (nostr-tools → nostr_tools)
- Import path corrections
- Dependency version constraints
- Configuration file syntax and formatting

## [0.1.0] - 2024-XX-XX

### Added
- Initial release of nostr-tools
- Core Nostr protocol implementation
- WebSocket relay client with async/await support
- Cryptographic utilities (secp256k1, bech32)
- Event creation, signing, and verification
- Relay connection management
- Filter-based event subscription
- NIP-11 relay metadata support
- Complete type annotations

### Core Features
- `Client` class for relay interactions
- `Event` class for Nostr events
- `Relay` class for connection management
- `Filter` class for event filtering
- Utility functions for key management and encoding
- High-level action functions for common operations

### Developer Experience
- Comprehensive test suite
- Type hints throughout codebase
- Detailed docstrings
- Example implementations
- Error handling and logging

---

## Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Types
- **🚀 Major Release**: Breaking changes, new architecture
- **✨ Minor Release**: New features, enhancements
- **🐛 Patch Release**: Bug fixes, security updates
- **🔧 Pre-release**: Alpha/Beta/RC versions

### Automatic Releases
Releases are automatically created when:
1. A tag matching `v*.*.*` is pushed
2. GitHub Actions build and test the release
3. Distributions are published to PyPI
4. GitHub Release is created with changelog
5. Documentation is updated

### Manual Release Process
```bash
# 1. Update version and changelog
git add CHANGELOG.md
git commit -m "chore: prepare release v1.2.3"

# 2. Create and push tag
git tag v1.2.3
git push origin v1.2.3

# 3. GitHub Actions handles the rest!
```