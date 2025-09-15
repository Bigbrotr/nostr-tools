# Nostr-Tools 🚀

[![PyPI Version](https://img.shields.io/pypi/v/nostr-tools.svg)](https://pypi.org/project/nostr-tools/)
[![Python Versions](https://img.shields.io/pypi/pyversions/nostr-tools.svg)](https://pypi.org/project/nostr-tools/)
[![License](https://img.shields.io/github/license/bigbrotr/nostr-tools.svg)](https://github.com/bigbrotr/nostr-tools/blob/main/LICENSE)
[![Test Status](https://github.com/bigbrotr/nostr-tools/workflows/Test/badge.svg)](https://github.com/bigbrotr/nostr-tools/actions)
[![Coverage](https://img.shields.io/codecov/c/github/bigbrotr/nostr-tools.svg)](https://codecov.io/gh/bigbrotr/nostr-tools)
[![Documentation](https://readthedocs.org/projects/nostr-tools/badge/?version=latest)](https://nostr-tools.readthedocs.io/en/latest/)

A comprehensive Python library for Nostr protocol interactions.

## ✨ Features

- 🔗 **Complete Nostr Protocol Implementation** - Full support for the Nostr specification
- 🔒 **Robust Cryptography** - Built-in secp256k1 signatures, key generation, and Bech32 encoding
- 🌐 **WebSocket Relay Management** - Efficient client with connection pooling and auto-reconnection
- 🔄 **Async/Await Support** - Fully asynchronous API for high-performance applications
- 📘 **Complete Type Hints** - Full type annotation coverage for excellent IDE support
- 🧪 **Comprehensive Testing** - Extensive test suite with 95%+ coverage
- 📖 **Rich Documentation** - Complete API documentation with examples

## 📦 Installation

```bash
pip install nostr-tools
```

For development with all optional dependencies:

```bash
pip install nostr-tools[all]
```

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from nostr_tools import Client, generate_keypair, Event

async def main():
    # Generate a new keypair
    private_key, public_key = generate_keypair()

    # Create a client
    client = Client()

    # Connect to a relay
    await client.connect("wss://relay.damus.io")

    # Create and publish an event
    event = Event(
        kind=1,
        content="Hello Nostr! 👋",
        public_key=public_key
    )

    # Sign and publish the event
    signed_event = event.sign(private_key)
    await client.publish(signed_event)

    # Subscribe to events
    filter_dict = {"kinds": [1], "limit": 10}
    async for event in client.subscribe(filter_dict):
        print(f"📧 {event.content}")

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Features

```python
from nostr_tools import (
    Client,
    Filter,
    fetch_events,
    check_connectivity,
    to_bech32
)

async def advanced_example():
    # Check relay connectivity
    is_connected = await check_connectivity("wss://relay.damus.io")
    print(f"Relay connectivity: {is_connected}")

    # Fetch events with complex filters
    events = await fetch_events(
        relay_urls=["wss://relay.damus.io", "wss://nos.lol"],
        filters=[
            Filter(
                kinds=[1],
                authors=["npub1..."],
                since=1640995200,  # Unix timestamp
                limit=50
            )
        ]
    )

    for event in events:
        # Convert keys to bech32 format
        npub = to_bech32(event.public_key, "npub")
        print(f"📝 {event.content} - from {npub}")

asyncio.run(advanced_example())
```

## 📚 Documentation

- **📖 Full Documentation**: [nostr-tools.readthedocs.io](https://nostr-tools.readthedocs.io/)
- **🔧 API Reference**: [API Documentation](https://nostr-tools.readthedocs.io/en/latest/api/)
- **💡 Examples**: [Example Gallery](https://github.com/bigbrotr/nostr-tools/tree/main/examples)
- **📋 Changelog**: [CHANGELOG.md](CHANGELOG.md)

## 🏗️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/bigbrotr/nostr-tools.git
cd nostr-tools

# Install with development dependencies
pip install -e .[dev]

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest

# Run all quality checks
make check
```

### Project Commands

```bash
# Code quality
make format          # Format code with Ruff
make lint           # Run linting checks
make type-check     # Run MyPy type checking

# Testing
make test           # Run all tests
make test-cov       # Run tests with coverage
make test-security  # Run security checks

# Building
make build          # Build distribution packages
make docs           # Build documentation
make clean          # Clean build artifacts
```

## 🔒 Security

Security is a top priority for nostr-tools:

- 🛡️ **Automated Security Scanning** - Bandit, Safety, and pip-audit in CI/CD
- 🔐 **Cryptographic Best Practices** - Secure key generation and signature verification
- 📊 **Dependency Monitoring** - Continuous monitoring for vulnerable dependencies
- 🧪 **Security Testing** - Dedicated security test suite

Report security vulnerabilities to: [security@bigbrotr.com](mailto:security@bigbrotr.com)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. **Fork & Clone** the repository
2. **Create a branch** for your feature/fix
3. **Make changes** with tests and documentation
4. **Run quality checks**: `make check`
5. **Submit a Pull Request**

All contributions are automatically tested for:

- ✅ Code quality (Ruff, MyPy)
- ✅ Test coverage (pytest)
- ✅ Security (Bandit, Safety)
- ✅ Documentation builds

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Nostr Protocol** - [nostr-protocol/nips](https://github.com/nostr-protocol/nips)
- **Python Packaging** - Following [PyPA best practices](https://packaging.python.org/)
- **Community** - Thanks to all contributors and the Nostr community

## 📞 Support

- **🐛 Issues**: [GitHub Issues](https://github.com/bigbrotr/nostr-tools/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/bigbrotr/nostr-tools/discussions)
- **📧 Email**: [hello@bigbrotr.com](mailto:hello@bigbrotr.com)

---

<div align="center">

**⚡ Built with ❤️ for the Nostr ecosystem**

[Documentation](https://nostr-tools.readthedocs.io/) •
[PyPI](https://pypi.org/project/nostr-tools/) •
[GitHub](https://github.com/bigbrotr/nostr-tools) •
[Issues](https://github.com/bigbrotr/nostr-tools/issues)

</div>
