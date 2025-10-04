# nostr-tools Release Notes

This directory contains detailed release notes for all versions of nostr-tools, providing comprehensive information about each release's features, changes, and migration guides.

## 📋 Available Releases

### Latest Releases

| Version | Release Date | Status | Release Notes | Key Features |
|---------|--------------|--------|---------------|--------------|
| [v1.2.0](v1.2.0.md) | 2025-01-15 | ✅ **Current & Only Supported** | Documentation & release management | Comprehensive docs, version consolidation, support policy |
| [v1.1.1](v1.1.1.md) | 2025-10-03 | ❌ End of Life | Documentation & build fixes | Sphinx improvements, setuptools fixes, development guide |
| [v1.1.0](v1.1.0.md) | 2025-10-03 | ❌ End of Life | Major refactoring & enhanced testing | RelayMetadata rewrite, test suite overhaul, exception system |
| [v1.0.0](v1.0.0.md) | 2025-09-15 | ❌ End of Life | First stable release | Complete Nostr protocol implementation, production-ready |

### Release Categories

#### 🎯 Current & Only Supported
- **[v1.2.0](v1.2.0.md)** - Documentation & release management
  - **✅ Only Supported Version** - v1.2.0 is the single supported version
  - Comprehensive release documentation for all versions
  - Professional release management with detailed migration guides
  - Clear version support policy and end-of-life timeline
  - Accurate documentation based on actual code analysis

#### 🎉 Major Releases (End of Life)
- **[v1.0.0](v1.0.0.md)** - First stable release with complete Nostr protocol implementation
  - Complete NIP-01 support with event management and WebSocket communication
  - Cryptographic operations with secp256k1 and bech32 encoding
  - Professional development infrastructure with comprehensive testing
  - Production-ready quality with 80%+ test coverage

#### 🔧 Minor Releases (End of Life)
- **[v1.1.0](v1.1.0.md)** - Major refactoring & enhanced testing
  - **⚠️ Breaking Changes**: Complete RelayMetadata rewrite from class-based to dataclass-based
  - Enhanced exception system with specific error types
  - Professional test suite rewrite with unit/integration separation
  - Comprehensive Makefile with 30+ development commands

#### 🐛 Patch Releases (End of Life)
- **[v1.1.1](v1.1.1.md)** - Documentation & build system fixes
  - Enhanced Sphinx configuration with custom autosummary templates
  - Setuptools version constraints for better twine compatibility
  - New DEVELOPMENT.md with 490+ lines of development documentation
  - Improved CI pipeline with better error handling

## 📖 How to Read Release Notes

Each release note includes:

- **Overview** - High-level summary of the release
- **What's New** - Detailed feature additions and improvements
- **Breaking Changes** - Any API changes that require code updates
- **Bug Fixes** - Issues resolved in this release
- **Security Updates** - Security-related changes and fixes
- **Dependencies** - Updated dependency versions
- **Migration Guide** - How to upgrade from previous versions
- **Technical Details** - Code examples and implementation details
- **Contributors** - People who contributed to this release

## ⚠️ Important Migration Notes

### v1.1.0 Breaking Changes
- **RelayMetadata API** - Complete rewrite from class-based to dataclass-based implementation
- **Exception System** - New base exception class `NostrToolsError` with specific exception types
- **Test Structure** - Moved from flat test structure to organized unit/integration separation

### v1.1.1 No Breaking Changes
- All existing APIs remain the same
- Documentation improvements are transparent
- Build system improvements are automatic
- No code changes required

## 🔄 Version Support Policy

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

## 🚀 Quick Links

- **[Latest Release](v1.1.1.md)** - Most recent release notes
- **[First Stable Release](v1.0.0.md)** - Initial production release
- **[Changelog](../CHANGELOG.md)** - Detailed changelog in main repository
- **[PyPI Package](https://pypi.org/project/nostr-tools/)** - Install from PyPI
- **[GitHub Repository](https://github.com/bigbrotr/nostr-tools)** - Source code and issues

## 📝 Contributing to Release Notes

When creating a new release:

1. Create a new markdown file: `vX.Y.Z.md`
2. Follow the established format and structure
3. Include all relevant changes and improvements
4. Update this README with the new release
5. Update the main CHANGELOG.md file

## 🔗 Related Documentation

- **[Main README](../README.md)** - Project overview and quick start
- **[Development Guide](../DEVELOPMENT.md)** - How to contribute
- **[API Documentation](https://bigbrotr.github.io/nostr-tools/)** - Complete API reference
- **[Examples](../examples/)** - Code examples and tutorials

---

**Last Updated**: October 2025  
**Maintained by**: [Bigbrotr](https://github.com/bigbrotr)
