#!/usr/bin/env python3
"""
Advanced features example for nostr-tools library.

This example demonstrates:
- Relay metadata and capability testing
- Proof-of-work event creation
- Event streaming
- High-level action functions
- Error handling patterns
"""

import asyncio
import json
import time

from nostr_tools import Client
from nostr_tools import Event
from nostr_tools import Filter
from nostr_tools import Relay
from nostr_tools import RelayConnectionError
from nostr_tools import check_connectivity
from nostr_tools import fetch_events
from nostr_tools import fetch_nip11
from nostr_tools import fetch_relay_metadata
from nostr_tools import generate_event
from nostr_tools import generate_keypair
from nostr_tools import stream_events


async def relay_testing_example():
    """Demonstrate comprehensive relay testing."""
    print("🔍 Relay Testing Example\n")

    # Test multiple relays
    test_relays = [
        "wss://relay.damus.io",
        "wss://relay.nostr.band",
        "wss://nos.lol",
        "wss://relay.snort.social",
    ]

    private_key, public_key = generate_keypair()

    for relay_url in test_relays:
        print(f"Testing relay: {relay_url}")
        relay = Relay(relay_url)
        client = Client(relay, timeout=10)

        try:
            # Get comprehensive metadata
            metadata = await fetch_relay_metadata(client, private_key, public_key)

            print("  📊 Results:")
            print(f"    NIP-66: {'✅' if metadata.nip66_success else '❌'}")
            print(f"    NIP-11: {'✅' if metadata.nip11_success else '❌'}")

            if metadata.nip66_success:
                print(f"    Open RTT: {metadata.rtt_open}ms")
                if metadata.rtt_read:
                    print(f"    Read RTT: {metadata.rtt_read}ms")
                if metadata.rtt_write:
                    print(f"    Write RTT: {metadata.rtt_write}ms")

            if metadata.nip11_success:
                print(f"    Name: {metadata.name or 'N/A'}")
                print(f"    Software: {metadata.software or 'N/A'} {metadata.version or ''}")
                if metadata.supported_nips:
                    print(f"    NIPs: {metadata.supported_nips[:10]}...")  # First 10 NIPs
                if metadata.limitation:
                    print(f"    Limitations: {json.dumps(metadata.limitation, indent=6)}")

        except Exception as e:
            print(f"  ❌ Error testing relay: {e}")

        print()


async def proof_of_work_example():
    """Demonstrate proof-of-work event creation."""
    print("⛏️  Proof of Work Example\n")

    private_key, public_key = generate_keypair()

    # Create events with different difficulties
    difficulties = [8, 12, 16]

    for difficulty in difficulties:
        print(f"Mining event with {difficulty} leading zero bits...")
        start_time = time.time()

        try:
            event_data = generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=1,
                tags=[],
                content=f"This event has {difficulty} bits of proof-of-work! ⛏️",
                target_difficulty=difficulty,
                timeout=20,  # 20 second timeout
            )

            mine_time = time.time() - start_time
            event_id = event_data["id"]

            # Count leading zeros in event ID
            leading_zeros = 0
            for char in event_id:
                if char == "0":
                    leading_zeros += 4
                else:
                    leading_zeros += 4 - int(char, 16).bit_length()
                    break

            print(f"  ✅ Mined in {mine_time:.2f}s")
            print(f"  Event ID: {event_id}")
            print(f"  Leading zero bits: {leading_zeros}")

            # Check for nonce tag
            event = Event.from_dict(event_data)
            nonce_tags = [tag for tag in event.tags if tag[0] == "nonce"]
            if nonce_tags:
                print(f"  Nonce: {nonce_tags[0][1]}")

        except Exception as e:
            print(f"  ❌ Mining failed: {e}")

        print()


async def streaming_example():
    """Demonstrate real-time event streaming."""
    print("📡 Event Streaming Example\n")

    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=15)

    try:
        async with client:
            print("Streaming events for 30 seconds...")

            # Stream all text notes
            filter = Filter(kinds=[1])
            event_count = 0
            start_time = time.time()

            async for event in stream_events(client, filter):
                event_count += 1
                elapsed = time.time() - start_time

                print(f"  📨 Event {event_count} ({elapsed:.1f}s): {event.content[:60]}...")

                # Show some event details
                if event_count % 5 == 0:
                    print(f"    Author: {event.pubkey[:16]}...")
                    print(f"    Tags: {len(event.tags)} tags")
                    if event.tags:
                        tag_types = list({tag[0] for tag in event.tags if tag})
                        print(f"    Tag types: {tag_types[:5]}")

                # Stop after 30 seconds or 20 events
                if elapsed > 30 or event_count >= 20:
                    break

            print(f"\n  Received {event_count} events in {elapsed:.1f} seconds")
            print(f"  Rate: {event_count / elapsed:.1f} events/second")

    except Exception as e:
        print(f"  ❌ Streaming error: {e}")


async def high_level_actions_example():
    """Demonstrate high-level action functions."""
    print("🎯 High-Level Actions Example\n")

    relay = Relay("wss://relay.nostr.band")
    client = Client(relay, timeout=15)

    try:
        async with client:
            print("1. Fetching recent metadata events...")

            # Fetch user metadata events
            metadata_filter = Filter(kinds=[0], limit=5)
            metadata_events = await fetch_events(client, metadata_filter)

            print(f"   Retrieved {len(metadata_events)} metadata events")

            for i, event in enumerate(metadata_events[:3], 1):
                try:
                    metadata = json.loads(event.content)
                    name = metadata.get("name", "Unknown")
                    display_name = metadata.get("display_name", name)
                    print(f"   {i}. {display_name} ({event.pubkey[:16]}...)")
                except Exception as e:
                    print(f"   {i}. Invalid metadata ({event.pubkey[:16]}...): {e}")

            print("\n2. Fetching recent text notes...")

            # Fetch recent text notes with specific tags
            notes_filter = Filter(
                kinds=[1],
                since=int(time.time()) - 3600,  # Last hour
                limit=10,
            )

            text_events = await fetch_events(client, notes_filter)
            print(f"   Retrieved {len(text_events)} text notes from the last hour")

            # Analyze content
            if text_events:
                total_length = sum(len(event.content) for event in text_events)
                avg_length = total_length / len(text_events)
                print(f"   Average content length: {avg_length:.1f} characters")

                # Find events with hashtags
                tagged_events = [event for event in text_events if event.has_tag("t")]
                print(f"   Events with hashtags: {len(tagged_events)}")

                # Show popular hashtags
                all_hashtags = []
                for event in tagged_events:
                    hashtags = event.get_tag_values("t")
                    all_hashtags.extend(hashtags)

                if all_hashtags:
                    from collections import Counter

                    popular_tags = Counter(all_hashtags).most_common(5)
                    print(f"   Popular hashtags: {[tag for tag, count in popular_tags]}")

    except Exception as e:
        print(f"  ❌ Error: {e}")


async def error_handling_example():
    """Demonstrate proper error handling patterns."""
    print("🚨 Error Handling Example\n")

    # Test connection to invalid relay
    print("1. Testing invalid relay...")
    try:
        invalid_relay = Relay("wss://this-relay-does-not-exist.invalid")
        client = Client(invalid_relay, timeout=5)

        async with client:
            print("   This should not print")
    except RelayConnectionError as e:
        print(f"   ✅ Caught RelayConnectionError: {e}")
    except Exception as e:
        print(f"   ⚠️  Unexpected error: {e}")

    # Test malformed relay URL
    print("\n2. Testing malformed relay URL...")
    try:
        Relay("not-a-valid-url")
    except ValueError as e:
        print(f"   ✅ Caught ValueError: {e}")
    except Exception as e:
        print(f"   ⚠️  Unexpected error: {e}")

    # Test timeout handling
    print("\n3. Testing timeout handling...")
    try:
        relay = Relay("wss://relay.damus.io")
        client = Client(relay, timeout=1)  # Very short timeout

        async with client:
            # Try to fetch many events quickly
            filter = Filter(kinds=[1], limit=100)
            events = await fetch_events(client, filter)
            print(f"   Retrieved {len(events)} events despite short timeout")
    except RelayConnectionError as e:
        print(f"   ⚠️  Timeout occurred: {e}")
    except Exception as e:
        print(f"   ⚠️  Other error: {e}")

    # Test graceful degradation
    print("\n4. Testing graceful degradation...")
    relay_list = [
        "wss://invalid1.example.com",
        "wss://invalid2.example.com",
        "wss://relay.damus.io",  # This should work
        "wss://relay.nostr.band",  # Backup
    ]

    for relay_url in relay_list:
        try:
            relay = Relay(relay_url)
            client = Client(relay, timeout=5)

            # Test basic connectivity
            rtt_open, openable = await check_connectivity(client)
            if openable:
                print(f"   ✅ Successfully connected to {relay_url}")
                print(f"   Connection time: {rtt_open}ms")
                break
            else:
                print(f"   ❌ Failed to connect to {relay_url}")
        except Exception as e:
            print(f"   ❌ Error with {relay_url}: {e}")
    else:
        print("   ⚠️  All relays failed!")


async def nip11_exploration_example():
    """Demonstrate NIP-11 relay information exploration."""
    print("📋 NIP-11 Relay Information Example\n")

    test_relays = ["wss://relay.damus.io", "wss://relay.nostr.band", "wss://nos.lol"]

    for relay_url in test_relays:
        print(f"Exploring {relay_url}...")
        relay = Relay(relay_url)
        client = Client(relay, timeout=10)

        try:
            # Fetch NIP-11 information
            nip11_data = await fetch_nip11(client)

            if nip11_data:
                print("  📄 NIP-11 Information:")
                print(f"    Name: {nip11_data.get('name', 'N/A')}")
                print(f"    Description: {nip11_data.get('description', 'N/A')[:100]}...")
                print(f"    Contact: {nip11_data.get('contact', 'N/A')}")
                print(
                    f"    Software: {nip11_data.get('software', 'N/A')} {nip11_data.get('version', '')}"
                )

                if "supported_nips" in nip11_data:
                    nips = nip11_data["supported_nips"]
                    print(f"    Supported NIPs: {nips[:15]}{'...' if len(nips) > 15 else ''}")

                if "limitation" in nip11_data:
                    limitations = nip11_data["limitation"]
                    print("    Limitations:")
                    for key, value in limitations.items():
                        print(f"      {key}: {value}")

                # Check for interesting features
                features = []
                if nip11_data.get("fees"):
                    features.append("Paid relay")
                if limitations.get("auth_required"):
                    features.append("Auth required")
                if limitations.get("payment_required"):
                    features.append("Payment required")
                if limitations.get("restricted_writes"):
                    features.append("Restricted writes")

                if features:
                    print(f"    Special features: {', '.join(features)}")
            else:
                print("  ❌ No NIP-11 information available")

        except Exception as e:
            print(f"  ❌ Error fetching NIP-11: {e}")

        print()


async def custom_event_types_example():
    """Demonstrate working with different event types."""
    print("📝 Custom Event Types Example\n")

    private_key, public_key = generate_keypair()
    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=10)

    try:
        async with client:
            print("1. Creating different event types...")

            # Metadata event (kind 0)
            metadata = {
                "name": "NostrTools Demo",
                "about": "Testing the nostr-tools Python library",
                "picture": "",
                "nip05": "",
            }

            metadata_event_data = generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=0,
                tags=[],
                content=json.dumps(metadata),
            )

            print("   📄 Created metadata event")

            # Text note with mentions and hashtags (kind 1)
            text_event_data = generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=1,
                tags=[
                    ["t", "nostr"],
                    ["t", "python"],
                    ["t", "demo"],
                    ["p", public_key, "", "mention"],
                ],
                content="Hello #nostr! This is a test of the nostr-tools Python library 🐍",
            )

            print("   💬 Created text note with tags")

            # Reaction event (kind 7)
            reaction_event_data = generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=7,
                tags=[["e", text_event_data["id"]], ["p", public_key]],
                content="🚀",
            )

            print("   👍 Created reaction event")

            # Deletion event (kind 5)
            deletion_event_data = generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=5,
                tags=[["e", text_event_data["id"]]],
                content="Deleting test event",
            )

            print("   🗑️  Created deletion event")

            print("\n2. Event validation...")

            # Validate all events
            events_to_validate = [
                ("Metadata", metadata_event_data),
                ("Text note", text_event_data),
                ("Reaction", reaction_event_data),
                ("Deletion", deletion_event_data),
            ]

            for name, event_data in events_to_validate:
                try:
                    event = Event.from_dict(event_data)
                    print(f"   ✅ {name} event is valid")
                    print(f"      ID: {event.id}")
                    print(f"      Kind: {event.kind}")
                    print(f"      Tags: {len(event.tags)}")
                except Exception as e:
                    print(f"   ❌ {name} event is invalid: {e}")

            print("\n3. Publishing events...")

            # Publish the text note only (as an example)
            text_event = Event.from_dict(text_event_data)
            success = await client.publish(text_event)
            print(f"   Text note published: {'✅' if success else '❌'}")

    except Exception as e:
        print(f"  ❌ Error: {e}")


async def main():
    """Run all advanced examples."""
    print("🚀 Nostr Tools Advanced Features\n")

    await relay_testing_example()
    await proof_of_work_example()
    await streaming_example()
    await high_level_actions_example()
    await error_handling_example()
    await nip11_exploration_example()
    await custom_event_types_example()

    print("✨ Advanced examples completed!")
    print("\nThese examples show the full power of nostr-tools.")
    print("You can now build sophisticated Nostr applications!")


if __name__ == "__main__":
    asyncio.run(main())
