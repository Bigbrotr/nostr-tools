# nostr-tools

A comprehensive Python library for interacting with the Nostr protocol. This library provides high-level and low-level APIs for connecting to Nostr relays, publishing and subscribing to events, and managing cryptographic operations.

[![Python Version](https://img.shields.io/pypi/pyversions/nostr-tools.svg)](https://pypi.org/project/nostr-tools/)
[![PyPI Version](https://img.shields.io/pypi/v/nostr-tools.svg)](https://pypi.org/project/nostr-tools/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI Status](https://github.com/bigbrotr/nostr-tools/workflows/CI/badge.svg)](https://github.com/bigbrotr/nostr-tools/actions)
[![Coverage](https://codecov.io/gh/bigbrotr/nostr-tools/branch/main/graph/badge.svg)](https://codecov.io/gh/bigbrotr/nostr-tools)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://github.com/bigbrotr/nostr-tools#readme)

## 🚀 Features

- **Complete Nostr Protocol Support**: Full implementation of NIP-01 and related NIPs
- **Async/Await API**: Modern Python async support for high-performance applications
- **Advanced Relay Management**: Connect to multiple relays with automatic failover and comprehensive metadata analysis
- **Event Handling**: Create, sign, verify, and filter Nostr events with full validation
- **Cryptographic Operations**: Built-in key generation, Schnorr signatures, and proof-of-work mining
- **Tor Support**: Connect to .onion relays through SOCKS5 proxies with proper network detection
- **Type Safety**: Complete type hints and runtime validation for better development experience
- **Performance Optimized**: Efficient cryptographic operations and connection management
- **Comprehensive Testing**: Extensive test suite covering unit, integration, security, and performance tests

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install nostr-tools
```

### Development Installation

```bash
git clone https://github.com/bigbrotr/nostr-tools.git
cd nostr-tools
pip install -e .

# With all development dependencies
pip install -e .[dev,test,security,docs]
```

### System Requirements

- **Python**: 3.9+ (tested on 3.9, 3.10, 3.11, 3.12)
- **Operating Systems**: Linux, macOS, Windows
- **Architecture**: x86_64, ARM64

## 🏃 Quick Start

### Basic Usage

```python
import asyncio
from nostr_tools import Client, Relay, Filter, generate_keypair, generate_event, Event

async def main():
    # Generate a new key pair
    private_key, public_key = generate_keypair()
    print(f"Generated keypair - Public: {public_key[:16]}...")

    # Create a relay connection
    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=10)

    async with client:
        # Create and publish a text note
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,  # Text note
            tags=[["t", "nostr"], ["t", "python"]],
            content="Hello Nostr! 🚀 Built with nostr-tools"
        )

        event = Event.from_dict(event_data)
        success = await client.publish(event)
        print(f"Event published: {'✅' if success else '❌'}")

        # Subscribe to recent events
        filter = Filter(kinds=[1], limit=5)
        subscription_id = await client.subscribe(filter)

        print("Recent events:")
        event_count = 0
        async for event_message in client.listen_events(subscription_id):
            event = Event.from_dict(event_message[2])
            print(f"  📨 {event.content[:60]}...")
            event_count += 1
            if event_count >= 5:
                break

        await client.unsubscribe(subscription_id)

if __name__ == "__main__":
    asyncio.run(main())
```

### High-Level API

```python
import asyncio
from nostr_tools import (
    Client, Relay, Filter, generate_keypair,
    fetch_events, compute_relay_metadata, stream_events
)

async def advanced_example():
    private_key, public_key = generate_keypair()
    relay = Relay("wss://relay.nostr.band")
    client = Client(relay)

    # Test relay capabilities comprehensively
    metadata = await compute_relay_metadata(client, private_key, public_key)
    print(f"🔍 Relay Analysis:")
    print(f"  Name: {metadata.name or 'Unknown'}")
    print(f"  Software: {metadata.software} {metadata.version or ''}")
    print(f"  Readable: {'✅' if metadata.readable else '❌'}")
    print(f"  Writable: {'✅' if metadata.writable else '❌'}")
    print(f"  RTT: {metadata.rtt_open}ms open, {metadata.rtt_read or 'N/A'}ms read")

    if metadata.supported_nips:
        print(f"  Supported NIPs: {metadata.supported_nips[:10]}...")

    # Fetch events with high-level API
    async with client:
        filter = Filter(kinds=[1], limit=10)
        events = await fetch_events(client, filter)

        print(f"\n📄 Retrieved {len(events)} events:")
        for i, event in enumerate(events[:3], 1):
            print(f"  {i}. {event.content[:50]}...")
            if event.tags:
                hashtags = [tag[1] for tag in event.tags if tag[0] == 't']
                if hashtags:
                    print(f"     Tags: {hashtags[:3]}")

asyncio.run(advanced_example())
```

## 🔧 Core Components

### Event System

Events are the fundamental data structure in Nostr with comprehensive validation:

```python
from nostr_tools import Event, generate_event, generate_keypair, verify_sig

# Generate keys and create an event
private_key, public_key = generate_keypair()

event_data = generate_event(
    private_key=private_key,
    public_key=public_key,
    kind=1,  # Text note
    tags=[
        ["t", "nostr"],       # Hashtag
        ["p", public_key],    # Mention
        ["e", "event_id"]     # Reply reference
    ],
    content="Building the decentralized web with Nostr! #nostr"
)

# Create and validate Event object
event = Event.from_dict(event_data)
print(f"Event ID: {event.id}")
print(f"Valid: {verify_sig(event.id, event.pubkey, event.sig)}")

# Event introspection
hashtags = event.get_tag_values("t")  # Get all hashtags
has_mention = event.has_tag("p", public_key)  # Check for specific mention
print(f"Hashtags: {hashtags}")
print(f"Has self-mention: {has_mention}")
```

### Advanced Filtering

Create sophisticated filters for event queries:

```python
from nostr_tools import Filter
import time

# Complex filter with multiple criteria
filter = Filter(
    kinds=[0, 1, 3],                    # Metadata, text notes, contacts
    authors=["author1...", "author2..."], # Specific authors
    since=int(time.time()) - 3600,      # Last hour
    until=int(time.time()),             # Until now
    limit=50,                           # Maximum 50 events
    t=["bitcoin", "nostr"],             # Events tagged with these hashtags
    p=[public_key],                     # Events mentioning this pubkey
    e=["event_id"]                      # Replies to specific event
)

# Time-based filters
recent_filter = Filter(
    kinds=[1],
    since=int(time.time()) - 86400,  # Last 24 hours
    limit=100
)

# Author-specific filters
author_filter = Filter(
    authors=[public_key],
    kinds=[0, 1],  # Metadata and text notes
    limit=20
)
```

### Relay Management

Advanced relay connection and metadata analysis:

```python
from nostr_tools import Relay, Client, compute_relay_metadata, check_connectivity

# Support for different network types
clearnet_relay = Relay("wss://relay.damus.io")
tor_relay = Relay("wss://example.onion")

print(f"Clearnet relay: {clearnet_relay.network}")  # "clearnet"
print(f"Tor relay: {tor_relay.network}")           # "tor"

# Tor relay with SOCKS5 proxy
tor_client = Client(
    tor_relay,
    socks5_proxy_url="socks5://127.0.0.1:9050",
    timeout=30
)

# Comprehensive relay testing
async def test_relay(relay_url):
    relay = Relay(relay_url)
    client = Client(relay, timeout=15)

    try:
        # Quick connectivity test
        rtt_open, openable = await check_connectivity(client)
        if not openable:
            print(f"❌ {relay_url} - Not accessible")
            return

        # Full metadata analysis
        metadata = await compute_relay_metadata(client, private_key, public_key)
        print(f"✅ {relay_url}")
        print(f"   Connection: {rtt_open}ms")
        print(f"   Read/Write: {metadata.readable}/{metadata.writable}")

        if metadata.limitation:
            limits = metadata.limitation
            print(f"   Limits: {limits.get('max_message_length', 'N/A')} chars, "
                  f"{limits.get('max_subscriptions', 'N/A')} subs")

    except Exception as e:
        print(f"❌ {relay_url} - Error: {e}")

# Test multiple relays
relays_to_test = [
    "wss://relay.damus.io",
    "wss://relay.nostr.band",
    "wss://nos.lol"
]

for relay_url in relays_to_test:
    await test_relay(relay_url)
```

## 🔐 Cryptographic Features

### Key Management

```python
from nostr_tools import (
    generate_keypair, validate_keypair,
    to_bech32, to_hex
)

# Generate secure key pairs
private_key, public_key = generate_keypair()

# Validate key pair integrity
is_valid = validate_keypair(private_key, public_key)
print(f"Key pair valid: {is_valid}")

# Convert to Bech32 format for user display
nsec = to_bech32("nsec", private_key)  # Private key (keep secret!)
npub = to_bech32("npub", public_key)   # Public key (share freely)

print(f"🔒 Private (nsec): {nsec}")
print(f"🔑 Public (npub): {npub}")

# Convert back to hex for protocol use
hex_private = to_hex(nsec)
hex_public = to_hex(npub)

# Verify roundtrip conversion
assert private_key == hex_private
assert public_key == hex_public
```

### Proof of Work

Generate events with computational proof-of-work for spam prevention:

```python
from nostr_tools import generate_event
import time

# Generate event with proof of work
start_time = time.time()
event_data = generate_event(
    private_key=private_key,
    public_key=public_key,
    kind=1,
    tags=[],
    content="This event required computational work to create! ⛏️",
    target_difficulty=16,  # 16 leading zero bits
    timeout=30            # 30 second timeout
)

mining_time = time.time() - start_time
event = Event.from_dict(event_data)

print(f"⛏️ Mining completed in {mining_time:.2f} seconds")
print(f"Event ID: {event.id}")

# Check for proof-of-work nonce
nonce_tags = [tag for tag in event.tags if tag[0] == "nonce"]
if nonce_tags:
    nonce_value, difficulty = nonce_tags[0][1], nonce_tags[0][2]
    print(f"Nonce: {nonce_value}, Target difficulty: {difficulty}")

    # Count actual leading zeros
    leading_zeros = 0
    for char in event.id:
        if char == '0':
            leading_zeros += 4
        else:
            leading_zeros += 4 - int(char, 16).bit_length()
            break

    print(f"Achieved difficulty: {leading_zeros} leading zero bits")
```

## 📡 Real-time Event Streaming

Stream events as they arrive from relays:

```python
from nostr_tools import stream_events
import asyncio

async def stream_realtime():
    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=30)

    async with client:
        # Stream all new text notes
        filter = Filter(kinds=[1])

        print("🔴 Streaming live events (Ctrl+C to stop)...")
        event_count = 0

        try:
            async for event in stream_events(client, filter):
                event_count += 1
                timestamp = time.strftime('%H:%M:%S', time.localtime(event.created_at))
                print(f"[{timestamp}] {event.content[:80]}...")

                # Show hashtags if present
                hashtags = event.get_tag_values("t")
                if hashtags:
                    print(f"         Tags: #{', #'.join(hashtags[:3])}")

                # Throttle output
                if event_count % 10 == 0:
                    print(f"--- Processed {event_count} events ---")

        except KeyboardInterrupt:
            print(f"\n🛑 Stream stopped. Processed {event_count} events total.")

# Run stream (will continue until interrupted)
# asyncio.run(stream_realtime())
```

## 🎯 Advanced Examples

### Multi-Relay Event Publishing

```python
async def publish_to_multiple_relays():
    private_key, public_key = generate_keypair()

    relays = [
        "wss://relay.damus.io",
        "wss://relay.nostr.band",
        "wss://nos.lol"
    ]

    event_data = generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=1,
        tags=[["t", "multi-relay"], ["t", "nostr-tools"]],
        content="Broadcasting to multiple relays simultaneously! 📡"
    )

    event = Event.from_dict(event_data)
    results = {}

    # Publish to all relays concurrently
    async def publish_to_relay(relay_url):
        try:
            relay = Relay(relay_url)
            client = Client(relay, timeout=10)
            async with client:
                success = await client.publish(event)
                return relay_url, success
        except Exception as e:
            return relay_url, f"Error: {e}"

    tasks = [publish_to_relay(url) for url in relays]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    print("📤 Publishing results:")
    for relay_url, result in results:
        status = "✅ Success" if result is True else f"❌ {result}"
        print(f"  {relay_url}: {status}")

await publish_to_multiple_relays()
```

### Event Analytics

```python
async def analyze_relay_content():
    relay = Relay("wss://relay.nostr.band")
    client = Client(relay)

    async with client:
        # Fetch recent events for analysis
        filter = Filter(
            kinds=[1],  # Text notes only
            since=int(time.time()) - 3600,  # Last hour
            limit=100
        )

        events = await fetch_events(client, filter)
        print(f"📊 Analyzing {len(events)} recent events...\n")

        # Content analysis
        total_chars = sum(len(event.content) for event in events)
        avg_length = total_chars / len(events) if events else 0

        # Tag analysis
        all_hashtags = []
        mentions = set()

        for event in events:
            all_hashtags.extend(event.get_tag_values("t"))
            mentions.update(event.get_tag_values("p"))

        # Popular hashtags
        from collections import Counter
        popular_hashtags = Counter(all_hashtags).most_common(10)

        # Time distribution
        hours = {}
        for event in events:
            hour = time.strftime('%H', time.localtime(event.created_at))
            hours[hour] = hours.get(hour, 0) + 1

        print("📈 Analysis Results:")
        print(f"  Average content length: {avg_length:.1f} characters")
        print(f"  Unique authors: {len(set(e.pubkey for e in events))}")
        print(f"  Total mentions: {len(mentions)}")
        print(f"  Events with hashtags: {len([e for e in events if e.has_tag('t')])}")

        if popular_hashtags:
            print(f"  Popular hashtags:")
            for tag, count in popular_hashtags[:5]:
                print(f"    #{tag}: {count} times")

        print(f"  Most active hours: {sorted(hours.items(), key=lambda x: x[1], reverse=True)[:3]}")

await analyze_relay_content()
```

## ⚠️ Error Handling

Robust error handling for network operations:

```python
from nostr_tools import RelayConnectionError
import asyncio

async def resilient_connection():
    relay_urls = [
        "wss://primary-relay.example.com",
        "wss://backup-relay.example.com",
        "wss://relay.damus.io"  # Known working relay
    ]

    for relay_url in relay_urls:
        try:
            relay = Relay(relay_url)
            client = Client(relay, timeout=10)

            async with client:
                print(f"✅ Connected to {relay_url}")

                # Test basic functionality
                filter = Filter(kinds=[1], limit=1)
                events = await fetch_events(client, filter)
                print(f"   Retrieved {len(events)} test events")

                # Success - use this relay
                return client

        except RelayConnectionError as e:
            print(f"❌ Failed to connect to {relay_url}: {e}")
            continue
        except Exception as e:
            print(f"⚠️ Unexpected error with {relay_url}: {e}")
            continue

    raise Exception("All relays failed to connect")

# Usage with proper error handling
try:
    client = await resilient_connection()
    # Use the working client...
except Exception as e:
    print(f"🚨 No relays available: {e}")
```

## 🧪 Testing

The library includes comprehensive test coverage:

```bash
# Run all tests
make test

# Run only fast unit tests
make test-unit

# Run integration tests (requires network)
make test-integration

# Run security-focused tests
make test-security

# Run performance benchmarks
make test-performance

# Generate coverage report
make test-cov
```

### Test Categories

- **Unit Tests**: Fast tests for individual components
- **Integration Tests**: Network-dependent tests with real relays
- **Security Tests**: Cryptographic security and vulnerability tests
- **Performance Tests**: Benchmarks and performance regression detection

## 🔧 Development

### Setting up Development Environment

```bash
# Clone repository
git clone https://github.com/bigbrotr/nostr-tools.git
cd nostr-tools

# Install in development mode with all dependencies
make install-dev

# Install pre-commit hooks
make pre-commit

# Run development checks
make dev-check
```

### Code Quality Tools

```bash
# Format code
make format

# Run linting
make lint

# Type checking
make type-check

# Security scan
make security-scan

# Full quality check
make check-all
```

## 📊 Protocol Support

This library implements the following Nostr Improvement Proposals (NIPs):

| NIP | Status | Description |
|-----|--------|-------------|
| [NIP-01](https://github.com/nostr-protocol/nips/blob/master/01.md) | ✅ Complete | Basic protocol flow description |
| [NIP-11](https://github.com/nostr-protocol/nips/blob/master/11.md) | ✅ Complete | Relay information document |
| [NIP-13](https://github.com/nostr-protocol/nips/blob/master/13.md) | ✅ Complete | Proof of work |
| [NIP-42](https://github.com/nostr-protocol/nips/blob/master/42.md) | 🔄 Partial | Authentication of clients to relays |

### Roadmap

Planned for future releases:

- **NIP-09**: Event deletion
- **NIP-16**: Event treatment
- **NIP-19**: Bech32-encoded entities
- **NIP-26**: Delegated event signing
- **NIP-28**: Public chat
- Enhanced relay pool management
- Event caching mechanisms
- Performance optimizations

## 🔒 Security

Security is a top priority for nostr-tools:

- **Cryptographic Security**: Uses industry-standard secp256k1 and Schnorr signatures
- **Secure Random Generation**: Utilizes `os.urandom()` for entropy
- **Input Validation**: Comprehensive validation of all inputs and data structures
- **Memory Safety**: Proper cleanup of sensitive data
- **Network Security**: Support for secure WebSocket connections and Tor

### Security Best Practices

```python
import os
from nostr_tools import generate_keypair

# 🔒 Secure key storage (example - use proper key management in production)
private_key, public_key = generate_keypair()

# DON'T: Store keys in plaintext
# with open('key.txt', 'w') as f: f.write(private_key)

# DO: Use environment variables or encrypted storage
os.environ['NOSTR_PRIVATE_KEY'] = private_key

# DO: Use secure WebSocket connections
relay = Relay("wss://relay.example.com")  # WSS, not WS

# DO: Validate all external inputs
def safe_event_handler(event_data):
    try:
        event = Event.from_dict(event_data)
        # Process validated event
    except (ValueError, TypeError) as e:
        print(f"Invalid event rejected: {e}")
```

Report security vulnerabilities to: **security@bigbrotr.com**

## 🚀 Performance

nostr-tools is optimized for high-performance applications:

- **Async I/O**: Non-blocking network operations
- **Connection Pooling**: Efficient WebSocket connection management  
- **Batch Operations**: Support for bulk event processing
- **Memory Efficient**: Minimal memory overhead and proper garbage collection
- **Cryptographic Optimization**: Fast elliptic curve operations

### Benchmarks

Typical performance on modern hardware:

- **Key Generation**: 1,000+ keypairs/second
- **Event Signing**: 2,000+ events/second  
- **Signature Verification**: 5,000+ verifications/second
- **Event Creation**: 10,000+ events/second
- **Connection Establishment**: <100ms to most relays

## 📄 API Reference

### Core Classes

- **[Event](nostr_tools/core/event.py)**: Nostr event representation with validation
- **[Relay](nostr_tools/core/relay.py)**: Relay configuration and network detection
- **[RelayMetadata](nostr_tools/core/relay_metadata.py)**: Comprehensive relay information
- **[Client](nostr_tools/core/client.py)**: WebSocket client for relay communication  
- **[Filter](nostr_tools/core/filter.py)**: Event filtering for subscriptions

### Utility Functions

- **Key Management**: `generate_keypair()`, `validate_keypair()`, `to_bech32()`, `to_hex()`
- **Event Operations**: `generate_event()`, `calc_event_id()`, `verify_sig()`
- **Network**: `find_websocket_relay_urls()`, `sanitize()`
- **High-level Actions**: `fetch_events()`, `stream_events()`, `compute_relay_metadata()`

### Error Handling

- **RelayConnectionError**: Connection and communication errors

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Start for Contributors

```bash
# Setup development environment
git clone https://github.com/bigbrotr/nostr-tools.git
cd nostr-tools
make install-dev

# Make changes and test
make dev-check

# Submit pull request
git push origin feature/your-feature
```

## 📋 Requirements

### Runtime Dependencies

- **Python**: 3.9+
- **aiohttp**: 3.8.0+ (WebSocket client)
- **aiohttp-socks**: 0.8.0+ (SOCKS5 proxy support)
- **bech32**: 1.2.0+ (Address encoding)
- **secp256k1**: 0.14.0+ (Elliptic curve cryptography)

### Development Dependencies

- **pytest**: 7.0.0+ (Testing framework)
- **ruff**: 0.8.4 (Linting and formatting)
- **mypy**: 1.0.0+ (Type checking)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💬 Support

- **GitHub Issues**: [Report bugs and request features](https://github.com/bigbrotr/nostr-tools/issues)
- **Discussions**: [Community discussion](https://github.com/bigbrotr/nostr-tools/discussions)  
- **Email**: hello@bigbrotr.com
- **Security**: security@bigbrotr.com

## 🙏 Acknowledgments

- The [Nostr protocol](https://github.com/nostr-protocol/nips) developers and community
- Python cryptography and networking library maintainers
- All contributors to this project
- The decentralized social media movement

---

**Built with ❤️ for the decentralized web**

*nostr-tools is actively maintained and continuously improved. Star the repository to stay updated with the latest features and improvements!*
