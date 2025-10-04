# nostr-tools Examples

Welcome to the **nostr-tools** examples directory! This collection of examples will guide you through all the features of the library, from basic concepts to advanced patterns.

## 📚 Example Files

The examples are organized in a progressive learning path. Start from the beginning and work your way through:

### 1️⃣ Getting Started
**File:** `01_getting_started.py`

Your first steps with nostr-tools:
- Generating and managing key pairs
- Converting between hex and bech32 formats
- Connecting to Nostr relays
- Creating your first event
- Publishing events

**Start here if you're new to nostr-tools!**

### 2️⃣ Events and Filters
**File:** `02_events_and_filters.py`

Understanding Nostr's core data structures:
- Different event types (kinds 0, 1, 3, 5, 7, etc.)
- Working with event tags
- Creating filter criteria
- Event validation and serialization
- Tag manipulation and queries

### 3️⃣ Publishing and Subscribing
**File:** `03_publishing_and_subscribing.py`

Real-time communication with relays:
- Publishing events to relays
- Subscribing to event streams
- Managing multiple subscriptions
- Fetch vs. stream patterns
- Filtering by author and tags
- Connection lifecycle management

### 4️⃣ Relay Capabilities
**File:** `04_relay_capabilities.py`

Testing and discovering relay features:
- Testing basic connectivity
- Checking read/write capabilities
- Fetching NIP-11 relay information
- Collecting NIP-66 performance metrics
- Comparing multiple relays
- Detecting relay requirements

### 5️⃣ Proof-of-Work
**File:** `05_proof_of_work.py`

Creating computationally expensive events:
- Understanding proof-of-work basics
- Mining events with different difficulties
- PoW event structure and nonce tags
- Publishing PoW events
- Spam prevention strategies
- Adapting to relay PoW requirements

### 6️⃣ Streaming and Advanced
**File:** `06_streaming_and_advanced.py`

Production-ready patterns and techniques:
- Real-time event streaming
- Multi-relay operations
- Error handling patterns
- Advanced filtering techniques
- Connection management
- Batch event processing
- Production best practices

## 🚀 Running the Examples

Each example file is standalone and can be run directly:

```bash
# Navigate to the examples directory
cd examples

# Run any example
python 01_getting_started.py
python 02_events_and_filters.py
python 03_publishing_and_subscribing.py
# ... and so on
```

Or use the full path:
```bash
python examples/01_getting_started.py
```

## 📋 Prerequisites

Make sure you have nostr-tools installed:

```bash
pip install nostr-tools
```

Or install from source:
```bash
pip install -e .
```

## 💡 Learning Path

We recommend following this learning path:

1. **Beginner** (30 minutes)
   - `01_getting_started.py` - Learn the basics
   - `02_events_and_filters.py` - Understand data structures

2. **Intermediate** (1 hour)
   - `03_publishing_and_subscribing.py` - Real-time communication
   - `04_relay_capabilities.py` - Testing relays

3. **Advanced** (1-2 hours)
   - `05_proof_of_work.py` - PoW events
   - `06_streaming_and_advanced.py` - Production patterns

## 🎯 Quick Reference

### Creating a Client and Publishing
```python
from nostr_tools import Client, Relay, generate_event, generate_keypair, Event

# Generate keys
private_key, public_key = generate_keypair()

# Create client
relay = Relay("wss://relay.damus.io")
client = Client(relay, timeout=10)

# Publish event
async with client:
    event_data = generate_event(
        private_key, public_key,
        kind=1, tags=[], content="Hello Nostr!"
    )
    event = Event.from_dict(event_data)
    success = await client.publish(event)
```

### Subscribing to Events
```python
from nostr_tools import Filter, fetch_events

async with client:
    filter_obj = Filter(kinds=[1], limit=10)
    events = await fetch_events(client, filter_obj)

    for event in events:
        print(event.content)
```

### Testing Relay Capabilities
```python
from nostr_tools import check_connectivity, fetch_relay_metadata

# Quick connectivity test
rtt, connectable = await check_connectivity(client)

# Comprehensive metadata
metadata = await fetch_relay_metadata(client, private_key, public_key)
print(f"Readable: {metadata.nip66.readable if metadata.nip66 else 'Unknown'}")
```

## 📖 Additional Resources

- **Documentation**: Check the main README.md for full API documentation
- **API Reference**: See the `/docs` directory for detailed API documentation
- **Source Code**: Explore `/src/nostr_tools` for implementation details
- **Tests**: See `/tests` for more usage examples

## 🤝 Contributing

Found an issue with the examples? Have an idea for a new example?

1. Open an issue describing the problem or suggestion
2. Submit a pull request with improvements
3. Share your own examples with the community!

## 📝 License

These examples are part of nostr-tools and are released under the same license as the main project.

---

**Happy coding!** 🎉

For questions or support, please open an issue on GitHub.
