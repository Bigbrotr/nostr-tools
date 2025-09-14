#!/usr/bin/env python3
"""
Basic usage example for nostr-tools library.

This example demonstrates:
- Key pair generation
- Creating and publishing events
- Subscribing to and fetching events
- Basic relay communication
"""

import asyncio
import time

from nostr_tools import Client
from nostr_tools import Event
from nostr_tools import Filter
from nostr_tools import Relay
from nostr_tools import generate_event
from nostr_tools import generate_keypair
from nostr_tools import to_bech32
from nostr_tools import to_hex


async def basic_example():
    """Demonstrate basic nostr-tools functionality."""
    print("🚀 Nostr Tools Basic Example\n")

    # Generate a new key pair
    print("1. Generating key pair...")
    private_key, public_key = generate_keypair()

    # Convert to Bech32 format
    nsec = to_bech32("nsec", private_key)
    npub = to_bech32("npub", public_key)

    print(f"   Private key (nsec): {nsec}")
    print(f"   Public key (npub): {npub}")
    print(f"   Hex private: {private_key}")
    print(f"   Hex public: {public_key}\n")

    # Create relay connection
    print("2. Connecting to relay...")
    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=10)

    print(f"   Relay: {relay.url}")
    print(f"   Network: {relay.network}\n")

    try:
        async with client:
            print("   ✅ Connected successfully!\n")

            # Create and publish an event
            print("3. Publishing a test event...")
            current_time = int(time.time())
            event_data = generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=1,  # Text note
                tags=[["t", "nostr"], ["t", "python"], ["t", "example"]],
                content=f"Hello Nostr! 👋 This is a test from nostr-tools at {current_time}",
                created_at=current_time,
            )

            event = Event.from_dict(event_data)
            print(f"   Event ID: {event.id}")
            print(f"   Content: {event.content}")

            # Publish the event
            success = await client.publish(event)
            print(f"   Published: {'✅ Success' if success else '❌ Failed'}\n")

            # Subscribe to recent events
            print("4. Fetching recent events...")
            filter = Filter(
                kinds=[1],  # Text notes only
                limit=5,  # Get last 5 events
                since=current_time - 3600,  # From last hour
            )

            events = []
            subscription_id = await client.subscribe(filter)
            print(f"   Subscription ID: {subscription_id}")

            async for event_message in client.listen_events(subscription_id):
                try:
                    received_event = Event.from_dict(event_message[2])
                    events.append(received_event)
                    print(f"   📨 Event {len(events)}: {received_event.content[:50]}...")

                    if len(events) >= 5:
                        break
                except Exception as e:
                    print(f"   ⚠️  Error processing event: {e}")
                    continue

            await client.unsubscribe(subscription_id)
            print(f"\n   Retrieved {len(events)} events total\n")

            # Display event details
            if events:
                print("5. Event details:")
                for i, evt in enumerate(events[:3], 1):
                    print(f"   Event {i}:")
                    print(f"     Author: {evt.pubkey[:16]}...")
                    print(f"     Kind: {evt.kind}")
                    print(f"     Created: {time.ctime(evt.created_at)}")
                    print(f"     Content: {evt.content[:80]}...")
                    if evt.tags:
                        tag_preview = [tag[0] for tag in evt.tags[:3]]
                        print(f"     Tags: {tag_preview}")
                    print()

    except Exception as e:
        print(f"   ❌ Error: {e}\n")


async def key_management_example():
    """Demonstrate key management features."""
    print("🔑 Key Management Example\n")

    # Generate multiple key pairs
    print("1. Generating multiple key pairs...")
    for i in range(3):
        private_key, public_key = generate_keypair()
        nsec = to_bech32("nsec", private_key)
        npub = to_bech32("npub", public_key)

        print(f"   Pair {i + 1}:")
        print(f"     nsec: {nsec}")
        print(f"     npub: {npub}")

    print("\n2. Converting between formats...")
    private_key, public_key = generate_keypair()

    # Hex to Bech32
    nsec = to_bech32("nsec", private_key)
    npub = to_bech32("npub", public_key)
    print(f"   Hex private: {private_key}")
    print(f"   Bech32 nsec: {nsec}")

    # Bech32 back to hex
    hex_private = to_hex(nsec)
    hex_public = to_hex(npub)
    print(f"   Back to hex private: {hex_private}")
    print(f"   Back to hex public: {hex_public}")

    # Verify conversion
    print(f"   Conversion correct: {private_key == hex_private and public_key == hex_public}")


async def filtering_example():
    """Demonstrate event filtering capabilities."""
    print("\n🔍 Event Filtering Example\n")

    relay = Relay("wss://relay.nostr.band")
    client = Client(relay, timeout=15)

    try:
        async with client:
            print("1. Filtering by kind (metadata events)...")
            metadata_filter = Filter(kinds=[0], limit=3)

            subscription_id = await client.subscribe(metadata_filter)
            metadata_events = []

            async for event_message in client.listen_events(subscription_id):
                try:
                    event = Event.from_dict(event_message[2])
                    metadata_events.append(event)

                    # Try to parse metadata
                    import json

                    try:
                        metadata = json.loads(event.content)
                        name = metadata.get("name", "Unknown")
                        about = metadata.get("about", "")[:50]
                        print(f"   👤 {name}: {about}...")
                    except Exception as e:
                        print(f"   📄 Metadata event from {event.pubkey[:16]}...: {e}")

                    if len(metadata_events) >= 3:
                        break
                except Exception as e:
                    print(f"   ❌ Error processing metadata event: {e}")
                    continue

            await client.unsubscribe(subscription_id)

            print("\n2. Filtering by tags...")
            # Filter for events with specific tags
            tag_filter = Filter(
                kinds=[1],
                t=["bitcoin"],  # Events tagged with #bitcoin
                limit=2,
            )

            subscription_id = await client.subscribe(tag_filter)
            tagged_events = []

            async for event_message in client.listen_events(subscription_id):
                try:
                    event = Event.from_dict(event_message[2])
                    tagged_events.append(event)
                    print(f"   🏷️  Bitcoin-tagged: {event.content[:60]}...")

                    if len(tagged_events) >= 2:
                        break
                except Exception:
                    continue

            await client.unsubscribe(subscription_id)

    except Exception as e:
        print(f"   ❌ Error: {e}")


async def main():
    """Run all examples."""
    await basic_example()
    await key_management_example()
    await filtering_example()

    print("\n✨ Examples completed!")
    print("\nNext steps:")
    print("- Check out more examples in the examples/ directory")
    print("- Read the full documentation in README.md")
    print("- Explore the API reference for advanced features")


if __name__ == "__main__":
    asyncio.run(main())
