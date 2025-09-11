# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-10

### Added
- Initial release of nostr-tools Python library
- **Core Nostr Protocol Implementation**
  - Complete NIP-01 support (basic protocol flow)
  - Event creation, validation, and serialization
  - Schnorr signature verification and creation
  - Event ID calculation according to specification

- **WebSocket Client**
  - Async WebSocket client for relay communication
  - Support for both clearnet and Tor (.onion) relays
  - SOCKS5 proxy support for Tor connections
  - Connection timeout and error handling
  - Subscription management with unique IDs

- **Event Management**
  - Event class with full validation
  - Support for all standard event kinds (0, 1, 3, 5, 7, etc.)
  - Tag-based filtering and querying
  - Escape sequence handling for content and tags
  - Event streaming and real-time subscriptions

- **Cryptographic Operations**
  - secp256k1 key pair generation
  - Schnorr signature creation and verification
  - Proof-of-work mining with configurable difficulty (NIP-13)
  - Key pair validation and testing

- **Relay Operations**
  - NIP-11 relay information document support
  - Relay metadata and capability testing
  - Connection performance metrics (RTT)
  - Readability and writability testing

- **Encoding Utilities**
  - Bech32 encoding/decoding for keys (nsec, npub)
  - Hex to Bech32 conversion and vice versa
  - URL validation and normalization

- **High-Level Actions**
  - `fetch_events()` - Retrieve stored events
  - `stream_events()` - Real-time event streaming
  - `compute_relay_metadata()` - Comprehensive relay analysis
  - `check_connectivity()` - Test relay connectivity
  - `check_readability()` - Test event subscription capability
  - `check_writability()` - Test event publishing capability

- **Developer Experience**
  - Complete type annotations throughout
  - Comprehensive error handling with custom exceptions
  - Async context managers for resource management
  - Extensive documentation and examples

### Dependencies
- **aiohttp 3.11.18** - WebSocket and HTTP client
- **aiohttp-socks 0.10.1** - SOCKS5 proxy support for Tor
- **bech32 1.2.0** - Bech32 encoding/decoding
- **secp256k1 0.14.0** - Elliptic curve cryptography
- **typing-extensions >=4.0.0** - Extended type hints (Python <3.10)

### Platform Support
- **Python 3.9+** - Full support for Python 3.9 through 3.12
- **Operating Systems** - Linux, macOS, Windows
- **Architecture** - x86_64, ARM64

### NIPs Implemented
- **NIP-01** - Basic protocol flow description
- **NIP-11** - Relay information document
- **NIP-13** - Proof of work
- **NIP-42** - Authentication (partial support)

### Examples and Documentation
- Basic usage examples
- Advanced features demonstration
- Comprehensive API documentation
- Security guidelines and best practices
- Contributing guidelines

### Known Limitations
- Authentication (NIP-42) is partially implemented
- Some advanced NIPs are not yet supported
- Relay pool management is not included
- Event deletion requires manual implementation

---

## [Unreleased]

### Planned for v0.2.0
- Enhanced NIP-42 authentication support
- Relay pool management with failover
- Event deletion and modification (NIP-09, NIP-16)
- Additional NIP implementations
- Performance optimizations
- Connection pooling and retry logic

### Planned for Future Releases
- Event caching mechanisms
- Advanced filtering capabilities
- Bulk operations support
- WebSocket compression
- Enhanced Tor support
- Plugin system for custom NIPs

---

For the latest updates and detailed information about each release, visit the [GitHub releases page](https://github.com/bigbrotr/nostr-tools/releases).