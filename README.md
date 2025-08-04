# BigBrotr

A comprehensive Python library for NOSTR protocol and relay management with PostgreSQL backend.

## Features

- **Complete NOSTR Protocol Support**: Event creation, validation, and signature verification
- **PostgreSQL Integration**: Efficient database operations with transaction support
- **Relay Management**: WebSocket URL validation, network detection (clearnet/Tor), and metadata tracking
- **Cryptographic Operations**: Schnorr signatures, keypair generation, and Bech32 encoding
- **Proof of Work**: Configurable difficulty PoW generation for events
- **Batch Operations**: Efficient bulk insertions for high-throughput scenarios
- **Comprehensive Validation**: Type checking and input sanitization throughout

## Installation

### From PyPI (when published)
```bash
pip install bigbrotr
```

### From Source
```bash
git clone https://github.com/Bigbrotr/bigbrotr.git
cd bigbrotr
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/Bigbrotr/bigbrotr.git
cd bigbrotr
pip install -e .[dev]
```

## Quick Start

### Basic Usage

```python
from bigbrotr import Bigbrotr, Event, Relay
import time

# Initialize database connection
db = Bigbrotr(
    host="localhost",
    port=5432,
    user="your_user",
    password="your_password",
    dbname="bigbrotr_db"
)

# Connect to database
db.connect()

# Create a relay
relay = Relay("wss://relay.damus.io")
print(f"Relay: {relay.url}, Network: {relay.network}")

# Insert relay
db.insert_relay(relay)

# Create an event (you'll need valid NOSTR event data)
event_data = {
    "id": "a1b2c3d4e5f6" + "0" * 52,  # 64 char hex
    "pubkey": "1234567890abcdef" + "0" * 48,  # 64 char hex  
    "created_at": int(time.time()),
    "kind": 1,
    "tags": [["t", "bigbrotr"], ["t", "nostr"]],
    "content": "Hello from BigBrotr!",
    "sig": "abcdef123456" + "0" * 116  # 128 char hex
}

# Note: This example uses dummy data. In practice, you'd generate
# valid events with proper signatures using the utils functions.

try:
    event = Event.from_dict(event_data)
    db.insert_event(event, relay)
    print("Event inserted successfully!")
except Exception as e:
    print(f"Error: {e}")

# Close connection
db.close()
```

### Working with Valid Events

```python
from bigbrotr import utils
import time

# Generate a keypair
private_key, public_key = utils.generate_nostr_keypair()
print(f"Private key: {private_key}")
print(f"Public key: {public_key}")

# Generate a valid event
event_dict = utils.generate_event(
    sec=private_key,
    pub=public_key,
    kind=1,
    tags=[["t", "bigbrotr"]],
    content="This is a valid NOSTR event!",
    created_at=int(time.time())
)

# Create Event object
event = Event.from_dict(event_dict)
print(f"Generated event ID: {event.id}")

# Convert keys to bech32 format
nsec = utils.to_bech32("nsec", private_key)
npub = utils.to_bech32("npub", public_key)
print(f"nsec: {nsec}")
print(f"npub: {npub}")
```

### Batch Operations

```python
# Insert multiple events efficiently
events = []
for i in range(100):
    event_dict = utils.generate_event(
        sec=private_key,
        pub=public_key,
        kind=1,
        tags=[["t", f"batch_{i}"]],
        content=f"Batch event {i}",
    )
    events.append(Event.from_dict(event_dict))

# Batch insert
db.insert_event_batch(events, relay)
print(f"Inserted {len(events)} events in batch")
```

### Relay Metadata

```python
from bigbrotr import RelayMetadata
import time

# Create relay metadata
metadata = RelayMetadata(
    relay=relay,
    generated_at=int(time.time()),
    connection_success=True,
    nip11_success=True,
    openable=True,
    readable=True,
    writable=True,
    rtt_open=150,
    rtt_read=200,
    rtt_write=250,
    name="Example Relay",
    description="A test NOSTR relay",
    supported_nips=[1, 2, 9, 11, 12, 15, 16, 20, 22],
    software="nostr-relay",
    version="1.0.0"
)

# Insert metadata
db.insert_relay_metadata(metadata)
```

## Database Schema

The library expects the following PostgreSQL functions to exist:
- `insert_event(...)` - Insert a single event
- `insert_relay(...)` - Insert a single relay  
- `insert_relay_metadata(...)` - Insert relay metadata
- `delete_orphan_events()` - Clean up orphaned events

You'll need to create these functions in your PostgreSQL database according to your schema design.

## API Reference

### Classes

#### `Bigbrotr`
Main database interface class.

**Methods:**
- `connect()` - Establish database connection
- `close()` - Close database connection
- `execute(query, args)` - Execute SQL query
- `insert_event(event, relay, seen_at)` - Insert single event
- `insert_event_batch(events, relay, seen_at)` - Insert multiple events
- `insert_relay(relay, inserted_at)` - Insert single relay
- `insert_relay_batch(relays, inserted_at)` - Insert multiple relays
- `insert_relay_metadata(metadata)` - Insert relay metadata
- `delete_orphan_events()` - Clean up orphaned events

#### `Event`
Represents a NOSTR event with validation.

**Attributes:**
- `id` - Event ID (64-char hex)
- `pubkey` - Author's public key (64-char hex)
- `created_at` - Unix timestamp
- `kind` - Event kind (0-65535)
- `tags` - List of tag arrays
- `content` - Event content string
- `sig` - Event signature (128-char hex)

#### `Relay`
Represents a NOSTR relay.

**Attributes:**
- `url` - WebSocket URL
- `network` - "clearnet" or "tor"

#### `RelayMetadata`
Comprehensive relay metadata and performance tracking.

### Utility Functions

#### `utils.generate_nostr_keypair()`
Generate a new NOSTR keypair.

#### `utils.generate_event(sec, pub, kind, tags, content, ...)`
Generate a valid NOSTR event with optional Proof of Work.

#### `utils.verify_sig(event_id, pubkey, sig)`
Verify an event signature.

#### `utils.to_bech32(prefix, hex_str)` / `utils.to_hex(bech32_str)`
Convert between hex and bech32 formats.

#### `utils.find_websoket_relay_urls(text)`
Extract WebSocket relay URLs from text.

## Configuration

### Environment Variables

You can set database connection parameters via environment variables:

```bash
export BIGBROTR_DB_HOST=localhost
export BIGBROTR_DB_PORT=5432
export BIGBROTR_DB_USER=your_user
export BIGBROTR_DB_PASSWORD=your_password
export BIGBROTR_DB_NAME=bigbrotr_db
```

## Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=bigbrotr

# Run linting
flake8 src/
black --check src/
mypy src/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [NOSTR Protocol](https://github.com/nostr-protocol/nostr) - The decentralized social network protocol
- [secp256k1](https://github.com/bitcoin-core/secp256k1) - Cryptographic library
- [PostgreSQL](https://www.postgresql.org/) - Database system

## Support

- Create an [issue](https://github.com/Bigbrotr/bigbrotr/issues) for bug reports
- Start a [discussion](https://github.com/Bigbrotr/bigbrotr/discussions) for questions
- Check the [documentation](https://bigbrotr.readthedocs.io/) for detailed guides

## Changelog

### v0.1.0