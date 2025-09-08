# nostr-tools

A comprehensive Python library for interacting with the Nostr protocol. This library provides core components for building Nostr clients, including event handling, relay communication, cryptographic utilities, and WebSocket client functionality.

## Features

- 🔐 **Cryptographic Operations**: Event signing, verification, and key management
- 🌐 **Relay Communication**: WebSocket client for connecting to Nostr relays
- 📝 **Event Handling**: Create, validate, and manipulate Nostr events
- 🏷️ **Metadata Support**: Full NIP-11 relay metadata support
- 🧅 **Tor Support**: Built-in support for .onion relays via SOCKS5 proxy
- ⚡ **Async/Await**: Modern async Python for high-performance applications
- 🔍 **Event Fetching**: High-level utilities for querying events from relays
- ✅ **Validation**: Comprehensive validation for events, relays, and data

## Installation

```bash
pip install nostr-tools
```

## Quick Start

```python
import asyncio
from nostr_tools import Relay, fetch_events, generate_keypair, generate_event

async def main():
    # Connect to a relay
    relay = Relay("wss://relay.damus.io")
    
    # Fetch recent events
    events = await fetch_events(relay, kinds=[1], limit=10)
    print(f"Fetched {len(events)} events")
    
    # Generate a keypair
    private_key, public_key = generate_keypair()
    
    # Create and sign an event
    event_data = generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=1,
        tags=[],
        content="Hello, Nostr!"
    )
    print(f"Created event: {event_data['id']}")

asyncio.run(main())
```

## Core Components

### Events

```python
from nostr_tools import Event

# Create from dictionary
event = Event.from_dict({
    "id": "...",
    "pubkey": "...", 
    "created_at": 1234567890,
    "kind": 1,
    "tags": [],
    "content": "Hello, world!",
    "sig": "..."
})

# Access properties
print(event.content)
print(event.get_tag_values("p"))  # Get 'p' tag values
print(event.has_tag("e"))  # Check for 'e' tags
```

### Relays

```python
from nostr_tools import Relay

# Create relay
relay = Relay("wss://relay.damus.io")
print(f"Network: {relay.network}")  # "clearnet" or "tor"
print(f"Domain: {relay.domain}")

# Tor relay
tor_relay = Relay("wss://relay.onion")
print(f"Is Tor: {tor_relay.is_tor}")  # True
```

### WebSocket Client

```python
from nostr_tools import Client

async with Client(relay) as client:
    # Subscribe to events
    sub_id = await client.subscribe({"kinds": [1], "limit": 10})
    
    # Listen for events
    async for event in client.listen_for_events(sub_id):
        print(f"Received: {event.content}")
    
    # Unsubscribe
    await client.unsubscribe(sub_id)
```

### Event Fetching

```python
from nostr_tools import fetch_events, fetch_events_from_multiple_relays

# Fetch from single relay
events = await fetch_events(
    relay=relay,
    authors=["pubkey1", "pubkey2"],
    kinds=[1],
    limit=50
)

# Fetch from multiple relays
relays = [Relay("wss://relay1.com"), Relay("wss://relay2.com")]
results = await fetch_events_from_multiple_relays(relays, {"kinds": [1]})
```

### Cryptographic Utilities

```python
from nostr_tools import generate_keypair, generate_event, verify_sig

# Generate keypair
private_key, public_key = generate_keypair()

# Create signed event
event_data = generate_event(
    private_key=private_key,
    public_key=public_key,
    kind=1,
    tags=[["p", "pubkey"]],
    content="Hello, Nostr!"
)

# Verify signature
is_valid = verify_sig(event_data["id"], event_data["pubkey"], event_data["sig"])
```

## Advanced Usage

### Streaming Events

```python
from nostr_tools import stream_events

async for event in stream_events(relay, {"kinds": [1]}):
    print(f"Live event: {event.content}")
```

### Tor Support

```python
# For Tor relays, provide SOCKS5 proxy URL
tor_relay = Relay("wss://relay.onion")
events = await fetch_events(
    relay=tor_relay,
    kinds=[1],
    socks5_proxy_url="socks5://127.0.0.1:9050"
)
```

### Relay Metadata

```python
from nostr_tools import RelayMetadata

metadata = RelayMetadata(
    relay=relay,
    generated_at=int(time.time()),
    connection_success=True,
    readable=True,
    writable=True,
    name="My Relay",
    description="A test relay"
)

print(f"Relay is healthy: {metadata.is_healthy}")
print(f"Capabilities: {metadata.capabilities}")
```

## Error Handling

```python
from nostr_tools import EventValidationError, RelayConnectionError

try:
    events = await fetch_events(relay, kinds=[1])
except RelayConnectionError as e:
    print(f"Connection failed: {e}")
except EventValidationError as e:
    print(f"Invalid event: {e}")
```

## Examples

See the `examples/` directory for comprehensive usage examples:

- `basic_usage.py` - Core functionality demonstration
- `event_fetching.py` - Advanced event querying techniques  
- `relay_discovery.py` - Relay testing and discovery utilities

## Requirements

- Python 3.8+
- aiohttp
- aiohttp-socks (for Tor support)
- secp256k1
- bech32

## License

MIT License - see LICENSE file for details.