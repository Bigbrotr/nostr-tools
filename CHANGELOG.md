# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-XX

### Added
- Initial release of nostr-tools Python library
- Core Nostr protocol implementation (NIP-01)
- Event creation, validation, and serialization
- WebSocket client for relay communication
- Support for both clearnet and Tor (.onion) relays
- Comprehensive event filtering system
- Cryptographic utilities (key generation, signing, verification)
- Proof-of-work mining for events (NIP-13)
- NIP-11 relay information document support
- High-level action functions for common operations
- Relay metadata and capability testing
- Bech32 encoding/decoding for keys and identifiers
- Full type hints for better development experience
- Comprehensive error handling with custom exceptions
- Support for SOCKS5 proxies for Tor relays
- Event streaming and real-time subscriptions
- Async/await API throughout the library

### Features
- **Event Management**
  - Create, sign, and verify Nostr events
  - Support for all standard event kinds
  - Tag-based filtering and event querying
  - Escape sequence handling for content and tags

- **Relay Communication**
  - WebSocket connections with automatic protocol detection
  - Subscription management with unique IDs
  - Event publishing with success confirmation
  - Connection timeout and error handling

- **Cryptographic Operations**
  - secp256k1 key pair generation
  - Schnorr signature creation and verification
  - Event ID calculation according to NIP-01
  - Proof-of-work mining with configurable difficulty

- **Network Support**
  - Clearnet relay connections
  - Tor relay support via SOCKS5 proxies
  - URL validation and normalization
  - Network type auto-detection

- **Developer Experience**
  - Complete type annotations
  - Comprehensive documentation
  - Example code and usage patterns
  - Async context managers for resource management

### Dependencies
- aiohttp 3.11.18+ (WebSocket and HTTP client)
- aiohttp-socks 0.10.1+ (SOCKS5 proxy support)
- bech32 1.2.0+ (Bech32 encoding/decoding)
- secp256k1 0.14.0+ (Elliptic curve cryptography)
- typing-extensions 4.0.0+ (Extended type hints)

### Requirements
- Python 3.8 or higher
- Support for asyncio

### Known Limitations
- Authentication (NIP-42) is partially implemented
- Some advanced NIPs are not yet supported
- Relay pool management is not included in this release
- Event deletion and modification features are not implemented

### Documentation
- Complete API reference
- Usage examples for all major features
- Configuration and setup instructions
- Error handling guidelines
- Contributing guidelines

## [Unreleased]

### Planned Features
- Relay pool management
- Event deletion and modification (NIP-09, NIP-16)
- Enhanced authentication support (NIP-42)
- Additional NIP implementations
- Performance optimizations
- Connection pooling and retry logic
- Event caching mechanisms

---

For the latest updates and detailed information about each release, visit the [GitHub releases page](https://github.com/bigbrotr/nostr-tools/releases).