# nostr-tools

A comprehensive Python library for interacting with the Nostr protocol. This library provides high-level and low-level APIs for connecting to Nostr relays, publishing and subscribing to events, and managing cryptographic operations.

[![Python Version](https://img.shields.io/pypi/pyversions/nostr-tools.svg)](https://pypi.org/project/nostr-tools/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/nostr-tools.svg)](https://pypi.org/project/nostr-tools/)

## Features

- **Complete Nostr Protocol Support**: Full implementation of NIP-01 and related NIPs
- **Async/Await API**: Modern Python async support for high-performance applications
- **Relay Management**: Connect to multiple relays with automatic failover
- **Event Handling**: Create, sign, verify, and filter Nostr events
- **Cryptographic Operations**: Built-in key generation, signing, and verification
- **Tor Support**: Connect to .onion relays through SOCKS5 proxies
- **Proof of Work**: Optional proof-of-work mining for events
- **Type Safety**: Full type hints for better development experience
- **Comprehensive Testing**: Extensive test suite for reliability

## Installation

```bash
pip install nostr-tools
```

### Development Installation

```bash
git clone https://github.com/bigbrotr/nostr-tools.git
cd nostr-tools
pip install -e .
```

## Quick Start

### Basic Usage

```python
import asyncio
from nostr_tools import Client, Relay, Filter, generate_keypair, generate_event

async def main():
    # Generate a new key pair
    private_key, public_key = generate_keypair()
    
    # Create a relay connection
    relay = Relay("wss://relay.damus.io")
    client = Client(relay)
    
    # Connect and publish an event
    async with client:
        # Create and publish a text note
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="Hello Nostr! 🚀"
        )
        
        from nostr_tools import Event
        event = Event.from_dict(event_data)
        success = await client.publish(event)
        print(f"Event published: {success}")
        
        # Subscribe to events
        filter = Filter(kinds=[1], limit=10)
        events = []
        
        subscription_id = await client.subscribe(filter)
        async for event_message in client.listen_events(subscription_id):
            event = Event.event_handler(event_message[2])
            events.append(event)
            if len(events) >= 10:
                break
        
        await client.unsubscribe(subscription_id)
        print(f"Retrieved {len(events)} events")

# Run the example
asyncio.run(main())
```

### High-Level Actions

```python
import asyncio
from nostr_tools import Client, Relay, Filter, generate_keypair
from nostr_tools import fetch_events, compute_relay_metadata

async def advanced_example():
    private_key, public_key = generate_keypair()
    relay = Relay("wss://relay.nostr.band")
    client = Client(relay)
    
    # Test relay capabilities
    metadata = await compute_relay_metadata(client, private_key, public_key)
    print(f"Relay readable: {metadata.readable}")
    print(f"Relay writable: {metadata.writable}")
    print(f"Relay software: {metadata.software}")
    
    # Fetch events with high-level API
    async with client:
        filter = Filter(kinds=[1], limit=5)
        events = await fetch_events(client, filter)
        
        for event in events:
            print(f"Event from {event.pubkey[:8]}...: {event.content[:50]}...")

asyncio.run(advanced_example())
```

## Core Components

### Events

Events are the fundamental data structure in Nostr:

```python
from nostr_tools import Event, generate_event, generate_keypair

# Generate keys
private_key, public_key = generate_keypair()

# Create an event
event_data = generate_event(
    private_key=private_key,
    public_key=public_key,
    kind=1,  # Text note
    tags=[["t", "nostr"], ["t", "python"]],  # Hashtags
    content="Building with nostr-tools!"
)

# Create Event object
event = Event.from_dict(event_data)

# Verify event
print(f"Event ID: {event.id}")
print(f"Valid signature: {event.sig}")
```

### Filters

Filters define what events to retrieve from relays:

```python
from nostr_tools import Filter

# Filter for recent text notes
filter = Filter(
    kinds=[1],        # Text notes
    since=1640995200, # Events since timestamp
    limit=50,         # Maximum 50 events
    t=["nostr"]      # Events with #nostr hashtag
)

# Filter for specific authors
authors_filter = Filter(
    authors=["pubkey1...", "pubkey2..."],
    kinds=[0, 1],  # Metadata and text notes
    limit=20
)
```

### Relays

Manage connections to Nostr relays:

```python
from nostr_tools import Relay, Client

# Clearnet relay
relay1 = Relay("wss://relay.damus.io")
client1 = Client(relay1)

# Tor relay (requires SOCKS5 proxy)
relay2 = Relay("wss://example.onion")
client2 = Client(relay2, socks5_proxy_url="socks5://127.0.0.1:9050")

print(f"Relay network: {relay1.network}")  # "clearnet"
print(f"Relay network: {relay2.network}")  # "tor"
```

## Advanced Features

### Proof of Work

Generate events with proof-of-work for spam prevention:

```python
from nostr_tools import generate_event, generate_keypair

private_key, public_key = generate_keypair()

# Generate event with proof of work (16 leading zero bits)
event_data = generate_event(
    private_key=private_key,
    public_key=public_key,
    kind=1,
    tags=[],
    content="This event has proof of work!",
    target_difficulty=16,  # 16 leading zero bits
    timeout=30  # 30 second timeout
)

print(f"Event ID starts with zeros: {event_data['id']}")
```

### Key Management

```python
from nostr_tools import generate_keypair, test_keypair, to_bech32, to_hex

# Generate new keys
private_key, public_key = generate_keypair()

# Verify key pair
is_valid = test_keypair(private_key, public_key)
print(f"Key pair valid: {is_valid}")

# Convert to Bech32 format
nsec = to_bech32("nsec", private_key)  # Secret key
npub = to_bech32("npub", public_key)   # Public key

print(f"nsec: {nsec}")
print(f"npub: {npub}")

# Convert back to hex
hex_private = to_hex(nsec)
hex_public = to_hex(npub)
```

### Relay Metadata

Get comprehensive information about relays:

```python
import asyncio
from nostr_tools import Client, Relay, compute_relay_metadata, generate_keypair

async def analyze_relay():
    private_key, public_key = generate_keypair()
    relay = Relay("wss://relay.nostr.band")
    client = Client(relay)
    
    metadata = await compute_relay_metadata(client, private_key, public_key)
    
    print(f"Name: {metadata.name}")
    print(f"Description: {metadata.description}")
    print(f"Software: {metadata.software} {metadata.version}")
    print(f"Supported NIPs: {metadata.supported_nips}")
    print(f"Read latency: {metadata.rtt_read}ms")
    print(f"Write latency: {metadata.rtt_write}ms")
    print(f"Limitations: {metadata.limitation}")

asyncio.run(analyze_relay())
```

### Event Streaming

Stream events in real-time:

```python
import asyncio
from nostr_tools import Client, Relay, Filter, stream_events

async def stream_realtime():
    relay = Relay("wss://relay.damus.io")
    client = Client(relay)
    
    async with client:
        # Stream all new text notes
        filter = Filter(kinds=[1])
        
        async for event in stream_events(client, filter):
            print(f"New event: {event.content[:100]}...")
            # Process events in real-time

# Note: This will run indefinitely
# asyncio.run(stream_realtime())
```

## Error Handling

The library provides specific exceptions for better error handling:

```python
import asyncio
from nostr_tools import Client, Relay, RelayConnectionError

async def handle_errors():
    relay = Relay("wss://invalid-relay.example.com")
    client = Client(relay, timeout=5)
    
    try:
        async with client:
            print("Connected successfully")
    except RelayConnectionError as e:
        print(f"Connection failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

asyncio.run(handle_errors())
```

## Configuration

### Timeout Settings

```python
from nostr_tools import Client, Relay

relay = Relay("wss://relay.example.com")

# Set custom timeout (default: 10 seconds)
client = Client(relay, timeout=30)
```

### Proxy Configuration

For Tor relays or privacy:

```python
from nostr_tools import Client, Relay

# Tor relay
tor_relay = Relay("wss://example.onion")
client = Client(
    tor_relay, 
    socks5_proxy_url="socks5://127.0.0.1:9050"
)

# Use proxy for clearnet relay (optional)
clearnet_relay = Relay("wss://relay.example.com")
client = Client(
    clearnet_relay,
    socks5_proxy_url="socks5://proxy.example.com:1080"
)
```

## API Reference

### Core Classes

- **Event**: Represents a Nostr event with validation and serialization
- **Relay**: Represents a Nostr relay with URL validation
- **RelayMetadata**: Comprehensive relay information and capabilities
- **Client**: WebSocket client for relay communication
- **Filter**: Event filtering for subscriptions

### Utility Functions

- **generate_keypair()**: Generate new secp256k1 key pairs
- **generate_event()**: Create signed events with optional proof-of-work
- **test_keypair()**: Validate that a private/public key pair matches
- **verify_sig()**: Verify event signatures using Schnorr verification
- **calc_event_id()**: Calculate event IDs according to NIP-01 specification
- **sig_event_id()**: Create Schnorr signatures for event IDs
- **to_bech32()** / **to_hex()**: Convert between hex and Bech32 formats
- **find_websocket_relay_urls()**: Extract and validate WebSocket relay URLs from text
- **sanitize()**: Remove null bytes and clean data structures recursively
- **TLDS**: List of valid top-level domains for URL validation
- **URI_GENERIC_REGEX**: Comprehensive URI regex pattern following RFC 3986
- **parse_nip11_response()**: Parse and validate NIP-11 relay information responses
- **parse_connection_response()**: Parse relay connection test results

### Action Functions

- **fetch_events()**: Retrieve stored events matching filters
- **stream_events()**: Stream events in real-time
- **compute_relay_metadata()**: Analyze relay capabilities and generate comprehensive metadata
- **fetch_nip11()**: Get NIP-11 relay information document
- **fetch_connection()**: Perform complete connection capability analysis with metrics
- **check_connectivity()**: Test basic relay connectivity and measure connection time
- **check_readability()**: Test event subscription capability and measure response time
- **check_writability()**: Test event publishing capability and measure response time

## Protocol Support

This library implements the following Nostr Improvement Proposals (NIPs):

- **NIP-01**: Basic protocol flow description
- **NIP-11**: Relay information document
- **NIP-13**: Proof of work
- **NIP-42**: Authentication of clients to relays (partial)

## Requirements

- Python 3.8+
- aiohttp 3.11.18+
- aiohttp-socks 0.10.1+
- bech32 1.2.0+
- secp256k1 0.14.0+

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
git clone https://github.com/bigbrotr/nostr-tools.git
cd nostr-tools
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
pip install pytest pytest-asyncio
python -m pytest
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=nostr_tools

# Run specific test file
python -m pytest tests/test_event.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- GitHub Issues: [https://github.com/bigbrotr/nostr-tools/issues](https://github.com/bigbrotr/nostr-tools/issues)
- Email: hello@bigbrotr.com

## Acknowledgments

- The Nostr protocol developers and community
- The Python cryptography and networking library maintainers
- All contributors to this project

---

**Note**: This library is in active development. While we strive for stability, the API may change between versions. Please pin to specific versions in production applications.