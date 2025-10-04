#!/usr/bin/env python3
"""
Streaming and Advanced Features with nostr-tools
=================================================

This example demonstrates:
- Real-time event streaming
- Multi-relay operations
- Error handling patterns
- Advanced filtering techniques
- Connection management
- Production-ready patterns

Learn advanced techniques for building robust Nostr applications!
"""

import asyncio
import time
from collections import Counter

from nostr_tools import Client
from nostr_tools import ClientConnectionError
from nostr_tools import Filter
from nostr_tools import Relay
from nostr_tools import check_connectivity
from nostr_tools import generate_keypair
from nostr_tools import stream_events


async def realtime_streaming():
    """Learn how to stream events in real-time."""
    print("=" * 60)
    print("1. REAL-TIME EVENT STREAMING")
    print("=" * 60)

    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=15)

    try:
        async with client:
            print("\nStreaming text notes for 15 seconds...")

            filter_obj = Filter(kinds=[1])  # Text notes
            event_count = 0
            start_time = time.time()

            async for event in stream_events(client, filter_obj):
                event_count += 1
                elapsed = time.time() - start_time

                print(f"  [{elapsed:>5.1f}s] Event {event_count}: {event.content[:50]}...")

                # Stop after 15 seconds or 10 events
                if elapsed > 15 or event_count >= 10:
                    break

            print(f"\n  ✅ Streamed {event_count} events")
            print(f"     Rate: {event_count / elapsed:.2f} events/second")

    except Exception as e:
        print(f"❌ Error: {e}")


async def multi_relay_operations():
    """Learn how to work with multiple relays."""
    print("\n" + "=" * 60)
    print("2. MULTI-RELAY OPERATIONS")
    print("=" * 60)

    relay_urls = [
        "wss://relay.damus.io",
        "wss://relay.nostr.band",
        "wss://nos.lol",
    ]

    print(f"\nTesting {len(relay_urls)} relays...")

    # Test all relays and collect working ones
    working_relays = []

    for url in relay_urls:
        relay = Relay(url)
        client = Client(relay, timeout=5)

        try:
            rtt, connectable = await check_connectivity(client)
            if connectable:
                print(f"  ✅ {url} ({rtt}ms)")
                working_relays.append((relay, rtt))
            else:
                print(f"  ❌ {url} (unreachable)")
        except Exception as e:
            print(f"  ❌ {url} ({e})")

    # Use fastest relay
    if working_relays:
        working_relays.sort(key=lambda x: x[1])  # Sort by RTT
        fastest_relay, fastest_rtt = working_relays[0]

        print(f"\n  Using fastest relay: {fastest_relay.url} ({fastest_rtt}ms)")

        # Fetch events from fastest relay
        client = Client(fastest_relay, timeout=10)
        async with client:
            from nostr_tools import fetch_events

            filter_obj = Filter(kinds=[1], limit=3)
            events = await fetch_events(client, filter_obj)
            print(f"  Fetched {len(events)} events")
    else:
        print("\n  ❌ No working relays found")


async def error_handling():
    """Learn proper error handling patterns."""
    print("\n" + "=" * 60)
    print("3. ERROR HANDLING PATTERNS")
    print("=" * 60)

    # 1. Handle invalid relay URLs
    print("\nA) Invalid relay URL:")
    try:
        relay = Relay("not-a-valid-url")
        print(f"  Created: {relay.url}")
    except ValueError:
        print("  ✅ Caught ValueError: URL validation failed")

    # 2. Handle connection failures
    print("\nB) Connection failure:")
    try:
        relay = Relay("wss://this-relay-does-not-exist.invalid")
        client = Client(relay, timeout=5)

        async with client:
            print("  This should not print")
    except ClientConnectionError as e:
        print(f"  ✅ Caught ClientConnectionError: {str(e)[:50]}...")

    # 3. Handle timeouts gracefully
    print("\nC) Timeout handling:")
    try:
        relay = Relay("wss://relay.damus.io")
        client = Client(relay, timeout=1)  # Very short timeout

        async with client:
            filter_obj = Filter(kinds=[1], limit=100)
            from nostr_tools import fetch_events

            events = await fetch_events(client, filter_obj)
            print(f"  Retrieved {len(events)} events despite short timeout")
    except asyncio.TimeoutError:
        print("  ✅ Caught TimeoutError: Handled gracefully")
    except Exception as e:
        print(f"  ℹ️  Other exception: {type(e).__name__}")

    # 4. Graceful degradation
    print("\nD) Graceful degradation:")
    relay_list = [
        "wss://invalid1.example.com",
        "wss://relay.damus.io",  # This should work
        "wss://relay.nostr.band",  # Backup
    ]

    for url in relay_list:
        try:
            relay = Relay(url)
            client = Client(relay, timeout=5)
            rtt, connectable = await check_connectivity(client)

            if connectable:
                print(f"  ✅ Connected to {url}")
                break
        except Exception:
            print(f"  ❌ Failed: {url}")
            continue
    else:
        print("  ⚠️  All relays failed (would use fallback)")


async def advanced_filtering():
    """Learn advanced filtering techniques."""
    print("\n" + "=" * 60)
    print("4. ADVANCED FILTERING")
    print("=" * 60)

    relay = Relay("wss://relay.nostr.band")
    client = Client(relay, timeout=15)

    try:
        async with client:
            from nostr_tools import fetch_events

            # Complex time-based filter
            print("\nA) Time window filtering:")
            one_day_ago = int(time.time()) - 86400
            two_days_ago = int(time.time()) - (86400 * 2)

            time_filter = Filter(
                kinds=[1],
                since=two_days_ago,
                until=one_day_ago,
                limit=5,
            )

            events = await fetch_events(client, time_filter)
            print(f"  Events from 1-2 days ago: {len(events)}")

            # Multiple tag filtering
            print("\nB) Multiple tag filtering:")
            tag_filter = Filter(
                kinds=[1],
                t=["bitcoin", "nostr"],  # Has #bitcoin OR #nostr
                limit=3,
            )

            events = await fetch_events(client, tag_filter)
            print(f"  Events with specified tags: {len(events)}")

            if events:
                for event in events[:2]:
                    tags = event.get_tag_values("t")
                    print(f"    - Tags: {tags}")

            # Multiple kind filtering
            print("\nC) Multiple kind filtering:")
            multi_kind_filter = Filter(
                kinds=[0, 1, 3],  # Metadata, text notes, contacts
                limit=6,
            )

            events = await fetch_events(client, multi_kind_filter)

            kind_counts = Counter(e.kind for e in events)
            print(f"  Retrieved {len(events)} events:")
            for kind, count in kind_counts.items():
                kind_name = {0: "metadata", 1: "text", 3: "contacts"}.get(kind, f"kind {kind}")
                print(f"    - {kind_name}: {count}")

    except Exception as e:
        print(f"❌ Error: {e}")


async def connection_pooling():
    """Learn about connection management."""
    print("\n" + "=" * 60)
    print("5. CONNECTION MANAGEMENT")
    print("=" * 60)

    relay = Relay("wss://relay.damus.io")

    # Pattern 1: Context manager (recommended)
    print("\nPattern 1: Context manager (recommended)")
    client1 = Client(relay, timeout=10)

    async with client1:
        print(f"  Connected: {client1.is_connected}")
        # Do work...
    print(f"  Disconnected: {not client1.is_connected}")

    # Pattern 2: Manual management
    print("\nPattern 2: Manual management")
    client2 = Client(relay, timeout=10)

    try:
        await client2.connect()
        print(f"  Connected: {client2.is_connected}")
        # Do work...
    finally:
        await client2.disconnect()
        print(f"  Disconnected: {not client2.is_connected}")

    # Pattern 3: Reusing connections
    print("\nPattern 3: Long-lived connection")
    client3 = Client(relay, timeout=10)

    async with client3:
        # Multiple operations with same connection
        from nostr_tools import fetch_events

        for i in range(3):
            filter_obj = Filter(kinds=[1], limit=1)
            events = await fetch_events(client3, filter_obj)
            print(f"  Operation {i + 1}: {len(events)} events")


async def batch_event_processing():
    """Learn how to process events in batches."""
    print("\n" + "=" * 60)
    print("6. BATCH EVENT PROCESSING")
    print("=" * 60)

    relay = Relay("wss://relay.nostr.band")
    client = Client(relay, timeout=15)

    try:
        async with client:
            from nostr_tools import fetch_events

            # Fetch large batch
            print("\nFetching batch of events...")
            filter_obj = Filter(kinds=[1], limit=20)

            events = await fetch_events(client, filter_obj)
            print(f"  Retrieved {len(events)} events")

            # Process in batches
            print("\n  Processing statistics:")

            # Analyze content lengths
            lengths = [len(e.content) for e in events]
            avg_length = sum(lengths) / len(lengths) if lengths else 0
            print(f"    Average content length: {avg_length:.0f} chars")

            # Count events with tags
            with_tags = sum(1 for e in events if e.tags)
            print(f"    Events with tags: {with_tags}/{len(events)}")

            # Count hashtag usage
            all_hashtags = []
            for event in events:
                if event.has_tag("t"):
                    all_hashtags.extend(event.get_tag_values("t"))

            if all_hashtags:
                top_tags = Counter(all_hashtags).most_common(5)
                print(f"    Top hashtags: {[tag for tag, _ in top_tags]}")

    except Exception as e:
        print(f"❌ Error: {e}")


async def production_patterns():
    """Learn production-ready patterns."""
    print("\n" + "=" * 60)
    print("7. PRODUCTION-READY PATTERNS")
    print("=" * 60)

    print("\nBest practices for production:")

    print("\n  1. Connection Management")
    print("     - Use context managers (async with)")
    print("     - Set appropriate timeouts")
    print("     - Handle disconnections gracefully")

    print("\n  2. Error Handling")
    print("     - Catch specific exceptions")
    print("     - Implement retry logic")
    print("     - Use graceful degradation")
    print("     - Log errors appropriately")

    print("\n  3. Multi-Relay Strategy")
    print("     - Test multiple relays")
    print("     - Use fastest/most reliable")
    print("     - Implement fallbacks")
    print("     - Cache relay performance")

    print("\n  4. Event Processing")
    print("     - Validate events before processing")
    print("     - Handle malformed events gracefully")
    print("     - Use batch processing for efficiency")
    print("     - Implement deduplication")

    print("\n  5. Performance")
    print("     - Reuse connections when possible")
    print("     - Use appropriate filter limits")
    print("     - Implement caching strategies")
    print("     - Monitor connection health")

    print("\n  6. Security")
    print("     - Validate relay URLs")
    print("     - Verify event signatures")
    print("     - Sanitize user input")
    print("     - Use secure key storage")


async def real_world_example():
    """A complete real-world example."""
    print("\n" + "=" * 60)
    print("8. REAL-WORLD EXAMPLE")
    print("=" * 60)

    print("\nBuilding a simple event monitor...")

    private_key, public_key = generate_keypair()

    # Configure relays with fallbacks
    relay_urls = [
        "wss://relay.damus.io",
        "wss://relay.nostr.band",
    ]

    # Find working relay
    working_relay = None
    for url in relay_urls:
        try:
            relay = Relay(url)
            client = Client(relay, timeout=5)
            rtt, connectable = await check_connectivity(client)

            if connectable:
                working_relay = relay
                print(f"  ✅ Connected to {url}")
                break
        except Exception:
            continue

    if not working_relay:
        print("  ❌ No relay available")
        return

    # Monitor events
    client = Client(working_relay, timeout=15)

    try:
        async with client:
            # Create monitoring filter
            filter_obj = Filter(
                kinds=[1],  # Text notes
                limit=5,  # Recent events
            )

            print("\n  Monitoring recent events...")

            from nostr_tools import fetch_events

            events = await fetch_events(client, filter_obj)

            print("\n  Summary:")
            print(f"    Total events: {len(events)}")

            if events:
                print("    Latest event:")
                latest = events[0]
                print(f"      Author: {latest.pubkey[:16]}...")
                print(f"      Content: {latest.content[:60]}...")

                if latest.tags:
                    print(f"      Tags: {len(latest.tags)}")

    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        print("  (Would retry with fallback relay)")


async def main():
    """Run all streaming and advanced examples."""
    await realtime_streaming()
    await multi_relay_operations()
    await error_handling()
    await advanced_filtering()
    await connection_pooling()
    await batch_event_processing()
    await production_patterns()
    await real_world_example()

    print("\n" + "=" * 60)
    print("✨ ALL EXAMPLES COMPLETED!")
    print("=" * 60)
    print("\nYou now understand:")
    print("  ✓ Real-time event streaming")
    print("  ✓ Multi-relay operations")
    print("  ✓ Error handling patterns")
    print("  ✓ Advanced filtering techniques")
    print("  ✓ Connection management")
    print("  ✓ Production-ready patterns")
    print("\nYou're ready to build robust Nostr applications!")
    print("\nFor more information:")
    print("  - Read the full documentation")
    print("  - Explore the API reference")
    print("  - Check out the source code")


if __name__ == "__main__":
    asyncio.run(main())
