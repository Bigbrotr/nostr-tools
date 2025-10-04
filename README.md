# nostr-tools

[![PyPI Version](https://img.shields.io/pypi/v/nostr-tools.svg)](https://pypi.org/project/nostr-tools/)
[![Python Versions](https://img.shields.io/pypi/pyversions/nostr-tools.svg)](https://pypi.org/project/nostr-tools/)
[![License](https://img.shields.io/github/license/bigbrotr/nostr-tools.svg)](https://github.com/bigbrotr/nostr-tools/blob/main/LICENSE)
[![CI Status](https://github.com/bigbrotr/nostr-tools/workflows/CI/badge.svg)](https://github.com/bigbrotr/nostr-tools/actions)
[![Coverage](https://img.shields.io/codecov/c/github/bigbrotr/nostr-tools.svg)](https://codecov.io/gh/bigbrotr/nostr-tools)
[![Downloads](https://static.pepy.tech/badge/nostr-tools)](https://pepy.tech/project/nostr-tools)

**A comprehensive, production-ready Python library for building applications on the Nostr protocol.**

nostr-tools provides a complete implementation of the Nostr protocol with an elegant async API, featuring robust WebSocket communication, cryptographic operations, event handling, and relay management. Built with modern Python best practices and extensive test coverage.

## Features ✨

### Core Protocol
- 🔗 **Complete NIP-01 Implementation** - Full support for the core Nostr protocol specification
- 📡 **Event System** - Create, validate, sign, and verify all event types (kinds 0-65535)
- 🔍 **Advanced Filtering** - Powerful event filtering with support for time ranges, tags, authors, and kinds
- 🏷️ **Tag Management** - Rich tag support with helper methods for common operations

### Networking & Relays
- 🌐 **WebSocket Client** - Efficient async client with automatic connection handling and reconnection
- 🔄 **Real-time Streaming** - Subscribe to events and receive updates in real-time
- 📊 **Relay Testing** - Comprehensive relay capability testing (NIP-11, NIP-66)
- 🌍 **Multi-relay Support** - Connect to multiple relays simultaneously with fallback strategies
- 🧅 **Tor Support** - Built-in SOCKS5 proxy support for Tor hidden services

### Cryptography & Security
- 🔒 **Robust Cryptography** - Secure key generation and event signing using secp256k1
- 🔑 **Key Management** - Generate, validate, and convert keys between hex and bech32 formats
- ⛏️ **Proof-of-Work** - Create events with configurable difficulty for spam prevention
- ✅ **Signature Verification** - Automatic signature and event ID validation

### Developer Experience
- ⚡ **Async/Await** - Built on asyncio for high-performance concurrent operations
- 🎯 **Type Safety** - Complete type hints with mypy validation for IDE support
- 📚 **Comprehensive Docs** - Detailed documentation with practical examples
- 🧪 **Well Tested** - Extensive test suite with >80% code coverage
- 🛡️ **Production Ready** - Battle-tested error handling and connection management

## Installation 📦

### From PyPI (Recommended)

```bash
pip install nostr-tools
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/bigbrotr/nostr-tools.git
cd nostr-tools

# Install with development dependencies
pip install -e ".[dev]"

# Setup pre-commit hooks
pre-commit install
```

### Requirements

- **Python:** 3.9 or higher
- **Dependencies:** Automatically installed
  - `aiohttp` - Async HTTP client/server
  - `aiohttp-socks` - SOCKS proxy support
  - `secp256k1` - Cryptographic operations
  - `bech32` - Bech32 encoding/decoding

## Quick Start 🚀

### Generate Keys and Connect

```python
import asyncio
from nostr_tools import Client, Relay, generate_keypair, to_bech32

async def main():
    # Generate a new keypair
    private_key, public_key = generate_keypair()
    print(f"Your npub: {to_bech32('npub', public_key)}")

    # Create and connect to a relay
    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=10)

    async with client:
        print(f"✅ Connected to {relay.url}")

asyncio.run(main())
```

### Publish an Event

```python
import asyncio
from nostr_tools import Client, Event, Relay, generate_event, generate_keypair

async def publish_note():
    private_key, public_key = generate_keypair()

    # Create a text note
    event_data = generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=1,  # Text note
        tags=[["t", "nostr"], ["t", "python"]],
        content="Hello Nostr! 👋 This is my first event with nostr-tools!"
    )

    event = Event.from_dict(event_data)

    # Publish to relay
    relay = Relay("wss://relay.damus.io")
    client = Client(relay)

    async with client:
        success = await client.publish(event)
        print(f"{'✅' if success else '❌'} Event published: {event.id}")

asyncio.run(publish_note())
```

### Subscribe to Events

```python
import asyncio
from nostr_tools import Client, Filter, Relay, fetch_events

async def get_recent_notes():
    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=15)

    async with client:
        # Create a filter for recent text notes
        filter_obj = Filter(kinds=[1], limit=10)

        # Fetch stored events
        events = await fetch_events(client, filter_obj)

        print(f"Retrieved {len(events)} events:")
        for event in events:
            print(f"  📝 {event.content[:60]}...")
            print(f"     by {event.pubkey[:16]}...")

asyncio.run(get_recent_notes())
```

### Stream Events in Real-Time

```python
import asyncio
from nostr_tools import Client, Filter, Relay, stream_events

async def stream_notes():
    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=15)

    async with client:
        filter_obj = Filter(kinds=[1])  # All text notes

        print("Streaming events (Ctrl+C to stop)...")
        async for event in stream_events(client, filter_obj):
            print(f"📨 {event.content[:50]}...")

asyncio.run(stream_notes())
```

## Core Components 📚

### Event - The Fundamental Data Structure

Events are the core data structure in Nostr. They can represent text notes, metadata, contacts, and more.

```python
from nostr_tools import Event, generate_event, generate_keypair

private_key, public_key = generate_keypair()

# Create and sign an event
event_data = generate_event(
    private_key=private_key,
    public_key=public_key,
    kind=1,  # Text note
    tags=[
        ["e", "event_id_to_reply_to"],  # Reply reference
        ["p", "pubkey_to_mention"],      # Mention
        ["t", "nostr"],                  # Hashtag
    ],
    content="This is a reply with mentions and hashtags!"
)

event = Event.from_dict(event_data)

# Access event properties
print(f"ID: {event.id}")
print(f"Author: {event.pubkey}")
print(f"Content: {event.content}")
print(f"Valid: {event.is_valid}")

# Work with tags
if event.has_tag("t"):
    hashtags = event.get_tag_values("t")
    print(f"Hashtags: {hashtags}")

# Serialize for storage or transmission
event_dict = event.to_dict()
```

### Client - WebSocket Communication

The Client handles all WebSocket communication with Nostr relays.

```python
from nostr_tools import Client, Relay

# Create a client
relay = Relay("wss://relay.damus.io")
client = Client(relay, timeout=10)

# Method 1: Context manager (recommended)
async with client:
    # Client automatically connects and disconnects
    success = await client.publish(event)

# Method 2: Manual connection management
await client.connect()
try:
    success = await client.publish(event)
finally:
    await client.disconnect()

# Check connection status
print(f"Connected: {client.is_connected}")

# View active subscriptions
print(f"Active: {client.active_subscriptions}")
```

### Filter - Query Events

Filters define criteria for querying and subscribing to events.

```python
from nostr_tools import Filter
import time

# Simple filter
filter1 = Filter(kinds=[1], limit=10)

# Filter by author
filter2 = Filter(
    kinds=[1],
    authors=["pubkey_hex"],
    limit=20
)

# Time-based filter
one_hour_ago = int(time.time()) - 3600
filter3 = Filter(
    kinds=[1],
    since=one_hour_ago,
    until=int(time.time()),
    limit=50
)

# Tag-based filter (replies to an event)
filter4 = Filter(
    kinds=[1],
    e=["event_id"],  # Events that reference this event ID
)

# Complex filter with multiple criteria
filter5 = Filter(
    kinds=[1, 6, 7],  # Text notes, reposts, reactions
    authors=["pubkey1", "pubkey2"],
    t=["bitcoin", "nostr"],  # With specific hashtags
    since=one_hour_ago,
    limit=100
)

# Use with client
async with client:
    events = await fetch_events(client, filter5)
```

### Relay - Connection Configuration

Relays represent Nostr relay servers and handle URL validation.

```python
from nostr_tools import Relay

# Create relay with automatic network detection
relay1 = Relay("wss://relay.damus.io")
print(f"Network: {relay1.network}")  # "clearnet"

# Tor relay
relay2 = Relay("wss://relay.onion")
print(f"Network: {relay2.network}")  # "tor"

# Validation
print(f"Valid: {relay1.is_valid}")

# Serialization
relay_dict = relay1.to_dict()
relay_restored = Relay.from_dict(relay_dict)
```

## Advanced Features 🔧

### Relay Capabilities Testing

Discover what a relay supports before using it.

```python
from nostr_tools import (
    Client, Relay,
    check_connectivity,
    check_readability,
    check_writability,
    fetch_nip11,
    fetch_relay_metadata,
    generate_keypair
)

relay = Relay("wss://relay.damus.io")
client = Client(relay, timeout=10)
private_key, public_key = generate_keypair()

# Quick connectivity test
rtt_open, can_connect = await check_connectivity(client)
print(f"Connectable: {can_connect} (RTT: {rtt_open}ms)")

# Test read capability
async with client:
    rtt_read, can_read = await check_readability(client)
    print(f"Readable: {can_read} (RTT: {rtt_read}ms)")

    # Test write capability
    rtt_write, can_write = await check_writability(
        client, private_key, public_key
    )
    print(f"Writable: {can_write} (RTT: {rtt_write}ms)")

# Get NIP-11 information
nip11_info = await fetch_nip11(client)
if nip11_info:
    print(f"Name: {nip11_info.name}")
    print(f"Software: {nip11_info.software}")
    print(f"Supported NIPs: {nip11_info.supported_nips}")

# Get comprehensive metadata
metadata = await fetch_relay_metadata(client, private_key, public_key)
print(f"NIP-66 available: {metadata.nip66 is not None}")
print(f"NIP-11 available: {metadata.nip11 is not None}")
```

### Proof-of-Work Events

Create events with computational proof to prevent spam.

```python
from nostr_tools import generate_event, generate_keypair, Event

private_key, public_key = generate_keypair()

# Generate event with 16-bit proof-of-work
event_data = generate_event(
    private_key=private_key,
    public_key=public_key,
    kind=1,
    tags=[],
    content="This event required computational work to create!",
    target_difficulty=16,  # Leading zero bits
    timeout=30  # Maximum mining time in seconds
)

event = Event.from_dict(event_data)

# Check the nonce tag
nonce_tags = [tag for tag in event.tags if tag[0] == "nonce"]
if nonce_tags:
    print(f"Nonce: {nonce_tags[0][1]}")
    print(f"Target: {nonce_tags[0][2]}")

# Count leading zeros in event ID
leading_zeros = sum(4 if c == '0' else 4 - int(c, 16).bit_length()
                   for c in event.id[:1])
print(f"Achieved difficulty: {leading_zeros} bits")
```

### Key Management

Generate and convert keys between formats.

```python
from nostr_tools import generate_keypair, to_bech32, to_hex, validate_keypair

# Generate new keypair
private_key, public_key = generate_keypair()

# Convert to bech32 format
nsec = to_bech32("nsec", private_key)  # Private key
npub = to_bech32("npub", public_key)   # Public key

print(f"Private (nsec): {nsec}")
print(f"Public (npub): {npub}")

# Convert back to hex
hex_private = to_hex(nsec)
hex_public = to_hex(npub)

# Validate keypair
is_valid = validate_keypair(private_key, public_key)
print(f"Keypair valid: {is_valid}")
```

### Multi-Relay Operations

Work with multiple relays for redundancy and reach.

```python
from nostr_tools import Relay, Client, check_connectivity

relay_urls = [
    "wss://relay.damus.io",
    "wss://relay.nostr.band",
    "wss://nos.lol",
]

# Test all relays
working_relays = []
for url in relay_urls:
    relay = Relay(url)
    client = Client(relay, timeout=5)

    try:
        rtt, connectable = await check_connectivity(client)
        if connectable:
            working_relays.append((relay, rtt))
            print(f"✅ {url} ({rtt}ms)")
    except Exception as e:
        print(f"❌ {url}: {e}")

# Sort by speed and use fastest
working_relays.sort(key=lambda x: x[1])
if working_relays:
    fastest_relay, rtt = working_relays[0]
    print(f"\nUsing fastest: {fastest_relay.url}")
```

### Tor Hidden Service Support

Connect to Tor relays for enhanced privacy.

```python
from nostr_tools import Relay, Client

# Create Tor relay with SOCKS5 proxy
tor_relay = Relay("wss://some-relay.onion")
client = Client(
    relay=tor_relay,
    socks5_proxy_url="socks5://127.0.0.1:9050",
    timeout=30  # Tor is slower
)

async with client:
    print(f"Connected via Tor: {client.is_connected}")
    # Use normally...
```

## Examples 📖

The [`examples/`](https://github.com/bigbrotr/nostr-tools/tree/main/examples) directory contains comprehensive, runnable examples:

- **[01_getting_started.py](https://github.com/bigbrotr/nostr-tools/blob/main/examples/01_getting_started.py)** - Key generation, basic connection, first events
- **[02_events_and_filters.py](https://github.com/bigbrotr/nostr-tools/blob/main/examples/02_events_and_filters.py)** - Event types, tags, filtering, validation
- **[03_publishing_and_subscribing.py](https://github.com/bigbrotr/nostr-tools/blob/main/examples/03_publishing_and_subscribing.py)** - Publishing, subscribing, real-time patterns
- **[04_relay_capabilities.py](https://github.com/bigbrotr/nostr-tools/blob/main/examples/04_relay_capabilities.py)** - Testing relays, NIP-11/66, capabilities
- **[05_proof_of_work.py](https://github.com/bigbrotr/nostr-tools/blob/main/examples/05_proof_of_work.py)** - PoW events, mining, difficulty management
- **[06_streaming_and_advanced.py](https://github.com/bigbrotr/nostr-tools/blob/main/examples/06_streaming_and_advanced.py)** - Streaming, multi-relay, production patterns

Run any example:
```bash
python examples/01_getting_started.py
```

For more details, see the [Examples README](https://github.com/bigbrotr/nostr-tools/blob/main/examples/README.md).

## Development 🏗️

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/bigbrotr/nostr-tools.git
cd nostr-tools

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
make install-dev

# Setup pre-commit hooks
pre-commit install

# Verify setup
make info
```

### Development Commands

```bash
# Run all checks (lint, format, type check, tests)
make check-all

# Run tests
make test          # With coverage
make test-unit     # Unit tests only
make test-quick    # Fast tests without coverage

# Code quality
make lint          # Run ruff linter
make format        # Format code with ruff
make type-check    # Run mypy type checker

# Security
make security      # Run all security checks
make security-bandit # Security linting
make security-safety # Dependency vulnerability scan

# Documentation
make docs-build    # Build documentation
make docs-serve    # Build and serve locally

# Cleanup
make clean         # Remove build artifacts
make clean-all     # Deep clean including caches
```

See the [Development Guide](https://github.com/bigbrotr/nostr-tools/blob/main/DEVELOPMENT.md) for detailed information.

## Security 🔒

### Security Features

- **Secure Key Generation** - Uses `os.urandom()` for cryptographically secure random numbers
- **No Private Key Storage** - Private keys never logged or persisted by the library
- **Input Validation** - Comprehensive validation of all inputs and relay data
- **Signature Verification** - Automatic verification of all received events
- **Type Safety** - Full type hints prevent common programming errors
- **Dependency Security** - Regular automated security scanning with Bandit, Safety, and pip-audit

### Best Practices

1. **Never commit private keys** - Use environment variables or secure vaults
2. **Validate relay URLs** - Always validate URLs before connecting
3. **Use secure connections** - Prefer `wss://` over `ws://`
4. **Handle errors gracefully** - Implement proper error handling and timeouts
5. **Verify event signatures** - Always verify events from untrusted sources
6. **Keep dependencies updated** - Regularly update to get security patches

### Reporting Security Issues

**Do not file public issues for security vulnerabilities.**

Report security issues privately to: **security@bigbrotr.com**

See [SECURITY.md](https://github.com/bigbrotr/nostr-tools/blob/main/SECURITY.md) for our security policy and disclosure process.

## Contributing 🤝

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Test** your changes (`make check-all`)
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to the branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

Please read our [Contributing Guide](https://github.com/bigbrotr/nostr-tools/blob/main/CONTRIBUTING.md) for detailed guidelines.

### Code of Conduct

This project follows a Code of Conduct. By participating, you agree to uphold this code. Report unacceptable behavior to hello@bigbrotr.com.

## License 📄

This project is licensed under the **MIT License** - see the [LICENSE](https://github.com/bigbrotr/nostr-tools/blob/main/LICENSE) file for details.

## Acknowledgments 🙏

- **Nostr Protocol** - Thanks to [fiatjaf](https://github.com/fiatjaf) and the [Nostr community](https://github.com/nostr-protocol)
- **Contributors** - All [contributors](https://github.com/bigbrotr/nostr-tools/graphs/contributors) to this project
- **Dependencies** - The amazing Python ecosystem:
  - [aiohttp](https://github.com/aio-libs/aiohttp) - Async HTTP client/server framework
  - [aiohttp-socks](https://github.com/romis2012/aiohttp-socks) - SOCKS proxy support for aiohttp
  - [secp256k1](https://github.com/ludbb/secp256k1-py) - Python bindings for Bitcoin's secp256k1 library
  - [bech32](https://github.com/sipa/bech32) - Bech32 encoding/decoding implementation

## Support & Resources 📞

- 📚 **Documentation** - [Full API Documentation](https://bigbrotr.github.io/nostr-tools/)
- 🐛 **Issues & Discussions** - [GitHub Issues](https://github.com/bigbrotr/nostr-tools/issues)
- 📧 **Email** - hello@bigbrotr.com
- 🔗 **Nostr Protocol** - [nostr.com](https://nostr.com/) | [NIPs Repository](https://github.com/nostr-protocol/nips)

## Project Status 📊

**Status:** ✅ Active Development & Maintenance

This project is actively maintained and welcomes contributions. We follow:
- **Semantic Versioning** (SemVer)
- **Backward Compatibility** within major versions
- **Regular Updates** with new features and bug fixes
- **Security First** approach with automated scanning

---

<div align="center">

**Built with ❤️ for the Nostr ecosystem**

[Documentation](https://bigbrotr.github.io/nostr-tools/) •
[PyPI](https://pypi.org/project/nostr-tools/) •
[GitHub](https://github.com/bigbrotr/nostr-tools) •
[Examples](https://github.com/bigbrotr/nostr-tools/tree/main/examples)

⭐ [Star us on GitHub](https://github.com/bigbrotr/nostr-tools) if you find this useful!

</div>
