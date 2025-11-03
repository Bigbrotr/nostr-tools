# nostr-tools Release Notes

This directory contains detailed release notes for all versions of nostr-tools, providing comprehensive information about each release's features, changes, and migration guides.

## 📋 Available Releases

### Current & Supported Versions

| Version | Release Date | Status | Release Notes | Key Features | Commit |
|---------|--------------|--------|---------------|--------------|--------|
| [v1.4.0](v1.4.0.md) | 2025-11-03 | ✅ **Current & Only Supported** | Filter validation enhancement | Non-negative integer support, zero value acceptance | TBD |

### End of Life Versions

| Version | Release Date | Status | Release Notes | Key Features | Commit |
|---------|--------------|--------|---------------|--------------|--------|
| [v1.3.0](v1.3.0.md) | 2025-11-02 | ❌ End of Life | Enhanced validation & documentation | is_valid properties, comprehensive validation, enhanced docs | `63cf17b` |
| [v1.2.1](v1.2.1.md) | 2025-10-05 | ❌ End of Life | Filter API enhancement | from_subscription_filter() method, comprehensive tests | `18637de` |
| [v1.2.0](v1.2.0.md) | 2025-10-04 | ❌ End of Life | Documentation & release management | Comprehensive docs, version consolidation, support policy | `02276d2` |
| [v1.1.1](v1.1.1.md) | 2025-10-03 | ❌ End of Life | Documentation & build fixes | Sphinx improvements, setuptools fixes, development guide | `7324fc5` |
| [v1.1.0](v1.1.0.md) | 2025-10-03 | ❌ End of Life | Major refactoring & enhanced testing | RelayMetadata rewrite, test suite overhaul, exception system | `6932dae` |
| [v1.0.0](v1.0.0.md) | 2025-09-15 | ❌ End of Life | First stable release | Complete Nostr protocol implementation, production-ready | `79d3dd6` |

## 🎯 Version Support Policy

### Supported Versions

| Version | Support Status | End of Support |
|---------|----------------|----------------|
| 1.4.0   | ✅ **Only Supported** | TBD            |
| 1.3.0   | ❌ End of Life | 2025-11-03     |
| 1.2.1   | ❌ End of Life | 2025-11-02     |
| 1.2.0   | ❌ End of Life | 2025-10-05     |
| 1.1.x   | ❌ End of Life | 2025-10-04     |
| 1.0.x   | ❌ End of Life | 2025-10-04     |
| 0.x.x   | ❌ End of Life | 2025-09-14     |

### Support Timeline

- **Active Support**: v1.4.0 only - bug fixes, security updates, and new features
- **End of Life**: All previous versions (v1.3.0, v1.2.1, v1.2.0, v1.1.x, v1.0.x, v0.x.x) - no further updates or support
- **Migration Required**: Users must upgrade to v1.4.0 for continued support

We follow semantic versioning and maintain backward compatibility within major versions.

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

### v1.4.0 - Current & Only Supported
- **No Breaking Changes** from v1.3.0
- All existing APIs remain the same
- Filter validation now accepts zero values for `since`, `until`, and `limit` fields
- Validation constraint updated from `> 0` to `>= 0` for better protocol compliance
- Error messages updated from "positive integer" to "non-negative integer"
- No code changes required for existing functionality

### v1.3.0 Breaking Changes (End of Life)
- **No Breaking Changes** from v1.2.1
- All existing APIs remain the same
- New `is_valid` properties added to Filter, Relay, Client, and RelayMetadata classes
- Enhanced validation methods with better error messages
- Comprehensive documentation improvements
- No code changes required for existing functionality

### v1.2.1 Breaking Changes (End of Life)
- **No Breaking Changes** from v1.2.0
- New `Filter.from_subscription_filter()` method is additive

### v1.1.0 Breaking Changes (End of Life)
- **RelayMetadata API** - Complete rewrite from class-based to dataclass-based implementation
- **Exception System** - New base exception class `NostrToolsError` with specific exception types
- **Test Structure** - Moved from flat test structure to organized unit/integration separation

### Migration Path

**Recommended Upgrade Path**
```bash
# Upgrade to v1.3.0 (latest and only supported version)
pip install --upgrade nostr-tools==1.3.0
```

**Migration Steps**
1. **Review Release Notes** - Check detailed release notes for your current version
2. **Update Dependencies** - Upgrade to v1.3.0
3. **Test Your Code** - Verify compatibility with new version
4. **Update Documentation** - Update your project documentation if needed

## 🚀 Quick Links

- **[Latest Release](v1.3.0.md)** - Current and only supported version
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

**Last Updated**: November 2, 2025
**Maintained by**: [Bigbrotr](https://github.com/bigbrotr)

**⚠️ Important**: Only v1.3.0 is currently supported. All previous versions are end-of-life as of November 2, 2025.
