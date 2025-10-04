#!/usr/bin/env python3
"""
Publishing and Subscribing with nostr-tools
============================================

This example demonstrates:
- Publishing events to relays
- Subscribing to event streams
- Listening for specific events
- Managing subscriptions
- Real-time event handling

Learn how to interact with Nostr relays in real-time!
"""

import asyncio

from nostr_tools import Client
from nostr_tools import ClientConnectionError
from nostr_tools import ClientPublicationError
from nostr_tools import Event
from nostr_tools import Filter
from nostr_tools import Relay
from nostr_tools import fetch_events
from nostr_tools import generate_event
from nostr_tools import generate_keypair


async def publish_events():
    """Learn how to publish events to relays."""
    print("=" * 60)
    print("1. PUBLISHING EVENTS")
    print("=" * 60)

    private_key, public_key = generate_keypair()
    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=15)

    import json

    published_count = 0

    try:
        async with client:
            # Publish a simple text note
            event1_data = generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=1,
                tags=[["t", "test"]],
                content="Hello from nostr-tools!",
            )
            event1 = Event.from_dict(event1_data)

            print("\nPublishing event 1...")
            try:
                await client.publish(event1)
                print("  Result: ✅ Accepted")
                published_count += 1
            except ClientPublicationError as e:
                print(f"  Result: ❌ Rejected - {e}")

            # Publish a metadata event
            metadata = {
                "name": "TestUser",
                "about": "Testing nostr-tools",
            }

            event2_data = generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=0,
                tags=[],
                content=json.dumps(metadata),
            )
            event2 = Event.from_dict(event2_data)

            print("\nPublishing event 2 (metadata)...")
            try:
                await client.publish(event2)
                print("  Result: ✅ Accepted")
                published_count += 1
            except ClientPublicationError as e:
                print(f"  Result: ❌ Rejected - {e}")

            print("\nPublishing summary:")
            print(f"  Total published: {published_count}/2")

    except ClientConnectionError as e:
        print(f"❌ Connection error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


async def subscribe_to_events():
    """Learn how to subscribe and listen to events."""
    print("\n" + "=" * 60)
    print("2. SUBSCRIBING TO EVENTS")
    print("=" * 60)

    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=15)

    try:
        async with client:
            # Create a filter for recent text notes
            event_filter = Filter(kinds=[1], limit=5)

            print("\nSubscribing to recent text notes...")
            subscription_id = await client.subscribe(event_filter)
            print(f"  Subscription ID: {subscription_id}")

            # Listen for events
            print("\nListening for events...")
            event_count = 0

            async for event_message in client.listen_events(subscription_id):
                try:
                    event = Event.from_dict(event_message[2])
                    event_count += 1

                    print(f"  Event {event_count}:")
                    print(f"    ID: {event.id[:16]}...")
                    print(f"    Author: {event.pubkey[:16]}...")
                    print(f"    Content: {event.content[:50]}...")

                    if event_count >= 5:
                        break

                except Exception as e:
                    print(f"    ⚠️ Error parsing event: {e}")
                    continue

            # Unsubscribe
            await client.unsubscribe(subscription_id)
            print(f"\n✅ Unsubscribed and received {event_count} events")

    except Exception as e:
        print(f"❌ Error: {e}")


async def multiple_subscriptions():
    """Learn how to manage multiple subscriptions."""
    print("\n" + "=" * 60)
    print("3. MULTIPLE SUBSCRIPTIONS")
    print("=" * 60)

    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=15)

    try:
        async with client:
            # Subscribe to different event types
            text_filter = Filter(kinds=[1], limit=3)
            metadata_filter = Filter(kinds=[0], limit=2)

            print("\nCreating multiple subscriptions...")
            sub_text = await client.subscribe(text_filter, "text-notes")
            sub_metadata = await client.subscribe(metadata_filter, "metadata")

            print(f"  Text subscription: {sub_text}")
            print(f"  Metadata subscription: {sub_metadata}")
            print(f"  Active subscriptions: {client.active_subscriptions}")

            # Listen to all messages
            print("\nListening to all subscriptions...")
            text_count = 0
            metadata_count = 0

            async for message in client.listen():
                if message[0] == "EVENT":
                    sub_id = message[1]
                    event_data = message[2]

                    try:
                        event = Event.from_dict(event_data)

                        if sub_id == sub_text:
                            text_count += 1
                            print(f"  📝 Text note {text_count}: {event.content[:40]}...")
                        elif sub_id == sub_metadata:
                            metadata_count += 1
                            print(f"  👤 Metadata {metadata_count}: from {event.pubkey[:16]}...")

                        # Break when we have enough events
                        if text_count >= 3 and metadata_count >= 2:
                            break

                    except Exception as e:
                        print(f"    ⚠️ Error: {e}")
                        continue

            # Clean up subscriptions
            await client.unsubscribe(sub_text)
            await client.unsubscribe(sub_metadata)

            print("\n✅ Received:")
            print(f"  Text notes: {text_count}")
            print(f"  Metadata events: {metadata_count}")

    except Exception as e:
        print(f"❌ Error: {e}")


async def fetch_vs_stream():
    """Learn the difference between fetching and streaming."""
    print("\n" + "=" * 60)
    print("4. FETCH vs STREAM")
    print("=" * 60)

    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=15)

    try:
        async with client:
            # FETCH: Get stored events and close
            print("\nA) FETCH (one-time retrieval):")
            filter_fetch = Filter(kinds=[1], limit=5)

            print("   Fetching events...")
            events = await fetch_events(client, filter_fetch)

            print(f"   ✅ Retrieved {len(events)} stored events")
            for i, event in enumerate(events[:3], 1):
                print(f"     {i}. {event.content[:40]}...")

            # STREAM: Continuous listening
            print("\nB) STREAM (continuous listening):")
            from nostr_tools import stream_events

            filter_stream = Filter(kinds=[1])

            print("   Streaming events (5 second limit)...")
            stream_count = 0
            import time

            start_time = time.time()

            async for event in stream_events(client, filter_stream):
                stream_count += 1
                elapsed = time.time() - start_time

                print(f"     {stream_count}. ({elapsed:.1f}s) {event.content[:40]}...")

                # Stop after 5 seconds or 5 events
                if elapsed > 5 or stream_count >= 5:
                    break

            print(f"   ✅ Streamed {stream_count} events in {elapsed:.1f}s")

    except Exception as e:
        print(f"❌ Error: {e}")


async def filter_by_author():
    """Learn how to filter events by specific authors."""
    print("\n" + "=" * 60)
    print("5. FILTERING BY AUTHOR")
    print("=" * 60)

    private_key, public_key = generate_keypair()
    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=15)

    try:
        async with client:
            # Publish an event
            print("\nPublishing test event...")
            event_data = generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=1,
                tags=[["t", "author-test"]],
                content="This is my test event",
            )
            event = Event.from_dict(event_data)
            try:
                await client.publish(event)
                print("  ✅ Event published")
            except ClientPublicationError as e:
                print(f"  ⚠️ Publish failed: {e}")

            # Filter by your pubkey
            print("\nFetching your events...")
            author_filter = Filter(kinds=[1], authors=[public_key], limit=10)

            your_events = await fetch_events(client, author_filter)

            print(f"  Found {len(your_events)} events from your pubkey")
            if your_events:
                print(f"  Latest: {your_events[0].content[:50]}...")

    except Exception as e:
        print(f"❌ Error: {e}")


async def filter_by_tags():
    """Learn how to filter events by tags."""
    print("\n" + "=" * 60)
    print("6. FILTERING BY TAGS")
    print("=" * 60)

    relay = Relay("wss://relay.nostr.band")
    client = Client(relay, timeout=15)

    try:
        async with client:
            # Filter by hashtag
            print("\nFetching events with #bitcoin hashtag...")
            tag_filter = Filter(kinds=[1], t=["bitcoin"], limit=3)

            events = await fetch_events(client, tag_filter)

            print(f"  Found {len(events)} events")
            for i, event in enumerate(events, 1):
                hashtags = event.get_tag_values("t")
                print(f"  {i}. Tags: {hashtags}")
                print(f"     Content: {event.content[:50]}...")

    except Exception as e:
        print(f"❌ Error: {e}")


async def handle_connection_lifecycle():
    """Learn about connection lifecycle management."""
    print("\n" + "=" * 60)
    print("7. CONNECTION LIFECYCLE")
    print("=" * 60)

    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=10)

    # Method 1: Context manager (recommended)
    print("\nMethod 1: Context manager")
    async with client:
        print(f"  Connected: {client.is_connected}")
    print(f"  After context: {client.is_connected}")

    # Method 2: Manual management
    print("\nMethod 2: Manual management")
    await client.connect()
    print(f"  Connected: {client.is_connected}")

    # Do some work...
    filter_obj = Filter(kinds=[1], limit=1)
    events = await fetch_events(client, filter_obj)
    print(f"  Fetched {len(events)} events")

    await client.disconnect()
    print(f"  After disconnect: {client.is_connected}")


async def main():
    """Run all publishing and subscribing examples."""
    await publish_events()
    await subscribe_to_events()
    await multiple_subscriptions()
    await fetch_vs_stream()
    await filter_by_author()
    await filter_by_tags()
    await handle_connection_lifecycle()

    print("\n" + "=" * 60)
    print("✨ EXAMPLES COMPLETED!")
    print("=" * 60)
    print("\nYou now understand:")
    print("  ✓ How to publish events to relays")
    print("  ✓ Subscribing and listening to events")
    print("  ✓ Managing multiple subscriptions")
    print("  ✓ Differences between fetch and stream")
    print("  ✓ Filtering by author and tags")
    print("\nNext: Check out 04_relay_capabilities.py")


if __name__ == "__main__":
    asyncio.run(main())
