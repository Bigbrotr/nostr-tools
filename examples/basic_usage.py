"""Basic usage examples for nostr-tools."""

import asyncio
from nostr_tools import Relay, Event, fetch_events, generate_keypair, generate_event


async def basic_example():
    """Basic example showing core functionality."""

    # Create a relay connection
    relay = Relay("wss://relay.damus.io")
    print(f"Created relay: {relay}")
    print(f"Network type: {relay.network}")
    print(f"Is Tor: {relay.is_tor}")

    # Fetch some recent events
    print("\nFetching recent events...")
    events = await fetch_events(relay, kinds=[1], limit=5)
    print(f"Fetched {len(events)} events")

    for event in events:
        print(f"Event {event.id[:16]}... by {event.pubkey[:16]}...")
        print(f"  Kind: {event.kind}")
        print(f"  Content: {event.content[:100]}...")
        print(f"  Created: {event.created_at}")
        print()

    # Generate a new keypair
    private_key, public_key = generate_keypair()
    print(f"Generated keypair:")
    print(f"  Private: {private_key}")
    print(f"  Public: {public_key}")

    # Create and sign an event
    event_data = generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=1,
        tags=[],
        content="Hello, Nostr! This is a test event from nostr-tools."
    )

    event = Event.from_dict(event_data)
    print(f"\nCreated event: {event}")
    print(f"Event ID: {event.id}")
    print(f"Content: {event.content}")


if __name__ == "__main__":
    asyncio.run(basic_example())
