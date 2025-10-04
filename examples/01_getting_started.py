#!/usr/bin/env python3
"""
Getting Started with nostr-tools
=================================

This example covers the absolute basics:
- Generating key pairs
- Converting between hex and bech32 formats
- Connecting to a relay
- Creating your first event
- Basic relay communication

Run this first if you're new to nostr-tools!
"""

import asyncio

from nostr_tools import Client
from nostr_tools import ClientConnectionError
from nostr_tools import ClientPublicationError
from nostr_tools import Relay
from nostr_tools import generate_keypair
from nostr_tools import to_bech32
from nostr_tools import to_hex


async def generate_keys():
    """Learn how to generate and work with Nostr keys."""
    print("=" * 60)
    print("1. GENERATING NOSTR KEYS")
    print("=" * 60)

    # Generate a new key pair
    private_key, public_key = generate_keypair()

    print("\nHex Format:")
    print(f"  Private key: {private_key}")
    print(f"  Public key:  {public_key}")

    # Convert to Bech32 format (human-readable)
    nsec = to_bech32("nsec", private_key)
    npub = to_bech32("npub", public_key)

    print("\nBech32 Format:")
    print(f"  nsec: {nsec}")
    print(f"  npub: {npub}")

    # Convert back to hex
    hex_private = to_hex(nsec)
    hex_public = to_hex(npub)

    print("\nRound-trip conversion:")
    print(f"  Match: {private_key == hex_private and public_key == hex_public}")

    return private_key, public_key


async def connect_to_relay():
    """Learn how to connect to a Nostr relay."""
    print("\n" + "=" * 60)
    print("2. CONNECTING TO A RELAY")
    print("=" * 60)

    # Create a relay object
    relay = Relay("wss://relay.damus.io")

    print(f"\nRelay URL: {relay.url}")
    print(f"Network: {relay.network}")
    print(f"Is valid: {relay.is_valid}")

    # Create a client
    client = Client(relay, timeout=10)
    print(f"Client created with {client.timeout}s timeout")

    # Connect using context manager (recommended)
    try:
        async with client:
            print(f"Connected: {client.is_connected}")
            print("✅ Successfully connected to relay!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")

    return client


async def create_first_event(private_key, public_key):
    """Learn how to create your first Nostr event."""
    print("\n" + "=" * 60)
    print("3. CREATING YOUR FIRST EVENT")
    print("=" * 60)

    from nostr_tools import Event
    from nostr_tools import generate_event

    # Create a simple text note
    event_data = generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=1,  # Kind 1 = text note
        tags=[["t", "hello"], ["t", "nostr"]],  # Hashtags
        content="Hello Nostr! This is my first event with nostr-tools 🚀",
    )

    # Convert to Event object
    event = Event.from_dict(event_data)

    print("\nEvent created:")
    print(f"  ID: {event.id}")
    print(f"  Author: {event.pubkey[:16]}...")
    print(f"  Kind: {event.kind}")
    print(f"  Content: {event.content}")
    print(f"  Tags: {event.tags}")
    print(f"  Is valid: {event.is_valid}")

    # Show how to serialize
    event_dict = event.to_dict()
    print(f"\nEvent can be serialized to dict with {len(event_dict)} fields")

    return event


async def publish_event(private_key, public_key):
    """Learn how to publish an event to a relay."""
    print("\n" + "=" * 60)
    print("4. PUBLISHING AN EVENT")
    print("=" * 60)

    from nostr_tools import Event
    from nostr_tools import generate_event

    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=15)

    event_data = generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=1,
        tags=[["t", "nostr-tools"], ["t", "python"]],
        content="Testing nostr-tools library - getting started example",
    )

    event = Event.from_dict(event_data)

    try:
        async with client:
            print(f"Publishing event {event.id[:16]}...")
            await client.publish(event)

            print("✅ Event published successfully!")
            print(f"   View on explorers using ID: {event.id}")

    except ClientPublicationError as e:
        print(f"❌ Event rejected by relay: {e}")
    except ClientConnectionError as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def main():
    """Run all getting started examples."""
    print("\n" + "=" * 60)
    print("NOSTR-TOOLS GETTING STARTED GUIDE")
    print("=" * 60)

    # Step 1: Generate keys
    private_key, public_key = await generate_keys()

    # Step 2: Connect to relay
    await connect_to_relay()

    # Step 3: Create an event
    await create_first_event(private_key, public_key)

    # Step 4: Publish an event
    await publish_event(private_key, public_key)

    print("\n" + "=" * 60)
    print("✨ COMPLETED!")
    print("=" * 60)
    print("\nNext steps:")
    print("  - Check out 02_events_and_filters.py to learn about event types")
    print("  - Read 03_publishing_and_subscribing.py for subscription patterns")
    print("  - Explore 04_relay_capabilities.py to test relay features")


if __name__ == "__main__":
    asyncio.run(main())
