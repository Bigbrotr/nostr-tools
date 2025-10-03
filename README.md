# nostr-tools 🚀

[![PyPI Version](https://img.shields.io/pypi/v/nostr-tools.svg)](https://pypi.org/project/nostr-tools/)
[![Python Versions](https://img.shields.io/pypi/pyversions/nostr-tools.svg)](https://pypi.org/project/nostr-tools/)
[![License](https://img.shields.io/github/license/bigbrotr/nostr-tools.svg)](https://github.com/bigbrotr/nostr-tools/blob/main/LICENSE)
[![CI Status](https://github.com/bigbrotr/nostr-tools/workflows/CI/badge.svg)](https://github.com/bigbrotr/nostr-tools/actions)
[![Coverage](https://img.shields.io/codecov/c/github/bigbrotr/nostr-tools.svg)](https://codecov.io/gh/bigbrotr/nostr-tools)
[![Downloads](https://static.pepy.tech/badge/nostr-tools)](https://pepy.tech/project/nostr-tools)

A comprehensive Python library for building applications on the Nostr protocol - featuring WebSocket communication, event handling, and cryptographic operations with full async support.

## ✨ Features

- 🔗 **Complete Nostr Protocol Implementation** - Full support for the core Nostr protocol specification
- 🔒 **Robust Cryptography** - Secure key generation, event signing, and signature verification using secp256k1
- 🌐 **WebSocket Relay Management** - Efficient async client with automatic connection handling
- 📡 **Event Subscription & Publishing** - Simple APIs for subscribing to and publishing Nostr events
- 🔍 **Advanced Filtering** - Powerful event filtering with support for all NIP-01 filter attributes
- 🎯 **Type Safety** - Full type hints for excellent IDE support and early error detection
- ⚡ **High Performance** - Built on asyncio for concurrent operations and optimal throughput
- 🧪 **Well Tested** - Comprehensive test suite with >80% code coverage
- 📚 **Extensively Documented** - Complete API documentation with practical examples

## 📦 Installation

Install the latest stable version from PyPI:

```bash
pip install nostr-tools
```

For development with all optional dependencies:

```bash
pip install "nostr-tools[dev]"
```

### Requirements

- Python 3.9 or higher
- Dependencies are automatically installed with pip

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from nostr_tools import Client, Event, Relay, generate_keypair

async def main():
    # Generate a new keypair
    private_key, public_key = generate_keypair()

    # Create a relay instance
    relay = Relay("wss://relay.damus.io")

    # Initialize the client
    client = Client(relay)

    # Connect to the relay
    await client.connect()

    # Create a text note event
    event = Event(
        kind=1,  # Text note
        content="Hello, Nostr! 👋",
        public_key=public_key
    )

    # Sign and publish the event
    event.sign(private_key)
    success = await client.publish(event)
    print(f"Event published: {success}")

    # Disconnect
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### Subscribing to Events

```python
import asyncio
from nostr_tools import Client, Filter, Relay

async def handle_events():
    relay = Relay("wss://relay.damus.io")
    client = Client(relay)

    await client.connect()

    # Create a filter for text notes
    event_filter = Filter(
        kinds=[1],  # Text notes
        limit=10    # Last 10 events
    )

    # Subscribe and process events
    subscription_id = await client.subscribe(event_filter)

    async for event_message in client.listen_events(subscription_id):
        event = Event.from_dict(event_message[2])
        print(f"📝 {event.content}")
        print(f"   by {event.public_key[:8]}...")

    await client.disconnect()

asyncio.run(handle_events())
```

### Using Multiple Relays

```python
import asyncio
from nostr_tools import Client, Event, Relay, generate_keypair

async def multi_relay_example():
    private_key, public_key = generate_keypair()

    # Define multiple relays
    relays = [
        "wss://relay.damus.io",
        "wss://nos.lol",
        "wss://relay.nostr.band"
    ]

    # Create event
    event = Event(
        kind=1,
        content="Broadcasting to multiple relays!",
        public_key=public_key
    )
    event.sign(private_key)

    # Publish to all relays
    results = []
    for relay_url in relays:
        relay = Relay(relay_url)
        client = Client(relay)

        try:
            await client.connect()
            success = await client.publish(event)
            results.append((relay_url, success))
            await client.disconnect()
        except Exception as e:
            results.append((relay_url, False))
            print(f"Failed to publish to {relay_url}: {e}")

    # Print results
    for relay_url, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {relay_url}")

asyncio.run(multi_relay_example())
```

## 📚 Documentation

### Core Components

#### **Event**
The fundamental data structure in Nostr:

```python
from nostr_tools import Event

# Create an event
event = Event(
    kind=1,              # Event kind (1 = text note)
    content="Hello!",    # Event content
    public_key=pub_key,  # Author's public key
    tags=[]             # Event tags
)

# Sign the event
event.sign(private_key)

# Verify signature
is_valid = event.verify()
```

#### **Client**
WebSocket client for relay communication:

```python
from nostr_tools import Client, Relay

relay = Relay("wss://relay.example.com")
client = Client(relay, timeout=30)

# Async context manager support
async with client as c:
    # Client automatically connects and disconnects
    await c.publish(event)
```

#### **Filter**
Event filtering for subscriptions:

```python
from nostr_tools import Filter

# Filter for specific event types
filter = Filter(
    kinds=[0, 1, 3],           # Profile, text note, contacts
    authors=["pubkey_hex"],    # Specific authors
    since=1640995200,          # Unix timestamp
    until=1672531200,          # Unix timestamp
    limit=100                  # Maximum events
)
```

### Advanced Features

#### **Relay Metadata**
Get relay information and capabilities:

```python
from nostr_tools import fetch_nip11, fetch_relay_metadata

# Fetch NIP-11 relay information
async with client:
    info = await fetch_nip11(client)
    print(f"Relay: {info.get('name')}")
    print(f"Software: {info.get('software')}")

    # Compute full relay metadata
    metadata = await fetch_relay_metadata(client, private_key, public_key)
    print(f"Readable: {metadata.readable}")
    print(f"Writable: {metadata.writable}")
```

#### **Proof of Work**
Generate events with proof-of-work:

```python
from nostr_tools import generate_event

# Generate event with PoW
event_dict = generate_event(
    private_key=private_key,
    public_key=public_key,
    kind=1,
    content="Important message",
    target_difficulty=20,  # Leading zero bits
    timeout=30            # Max time to mine
)
```

#### **Tor Support**
Connect through Tor for privacy:

```python
relay = Relay("wss://relay.onion", network="tor")
client = Client(
    relay,
    socks5_proxy_url="socks5://127.0.0.1:9050"
)
```

## 🏗️ Development

### Setting Up Development Environment

```bash
# Clone and setup
git clone https://github.com/bigbrotr/nostr-tools.git
cd nostr-tools
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
make install-dev

# Set up pre-commit hooks  
pre-commit install

# Verify setup
make info
```

**📖 For detailed development guide, see [DEVELOPMENT.md](DEVELOPMENT.md)**

### Quick Commands

```bash
# Run all quality checks
make check-all

# Run tests with coverage
make test

# Run specific test types
make test-unit        # Fast unit tests
make test-integration # Integration tests  
make test-benchmark   # Performance tests

# Security scans
make security

# Build documentation
make docs-serve
```

Run `make help` to see all available commands.

## 🔒 Security

### Security Features

- **Cryptographic Operations**: Uses `secp256k1` library for all cryptographic operations
- **Input Validation**: Comprehensive validation of all inputs and relay responses
- **Secure Random Generation**: Uses `os.urandom()` for key generation
- **No Private Key Storage**: Private keys are never stored or logged
- **Connection Security**: Supports secure WebSocket connections (wss://) with fallback to ws://
- **Automated Security Scanning**: Continuous security analysis with Bandit, Safety, and pip-audit

### Reporting Security Issues

Please report security vulnerabilities to **security@bigbrotr.com**. Do not file public issues for security vulnerabilities.

See [SECURITY.md](SECURITY.md) for complete security documentation and best practices.

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and quality checks (`make check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- The Nostr protocol creators and community
- Contributors and maintainers of this library
- The Python cryptography ecosystem

## 📞 Support

- **Documentation**: [Read the Docs](https://bigbrotr.github.io/nostr-tools/)
- **Issues**: [GitHub Issues](https://github.com/bigbrotr/nostr-tools/issues)
- **Discussions**: [GitHub Discussions](https://github.com/bigbrotr/nostr-tools/discussions)
- **Email**: hello@bigbrotr.com

## 📊 Project Status

This project is actively maintained and welcomes contributions. We follow semantic versioning and maintain backward compatibility within major versions.

---

<div align="center">

**Built with ❤️ for the Nostr ecosystem**

[PyPI](https://pypi.org/project/nostr-tools/) •
[Documentation](https://bigbrotr.github.io/nostr-tools/) •
[GitHub](https://github.com/bigbrotr/nostr-tools)

</div>
