"""Advanced event fetching examples."""

import asyncio
from datetime import datetime, timedelta
from nostr_tools import Relay, fetch_events, fetch_events_from_multiple_relays, stream_events


async def fetch_by_author():
    """Fetch events by specific author."""
    relay = Relay("wss://relay.damus.io")

    # Fetch events from a specific author (Jack Dorsey's pubkey)
    jack_pubkey = "82341f882b6eabcd2ba7f1ef90aad961cf074af15b9ef44a09f9d2a8fbfbe6a2"

    events = await fetch_events(
        relay=relay,
        authors=[jack_pubkey],
        kinds=[1],  # Text notes
        limit=10
    )

    print(f"Fetched {len(events)} events from {jack_pubkey[:16]}...")
    for event in events:
        print(
            f"  {datetime.fromtimestamp(event.created_at)}: {event.content[:100]}...")


async def fetch_with_time_range():
    """Fetch events within a specific time range."""
    relay = Relay("wss://relay.damus.io")

    # Last 24 hours
    now = datetime.now()
    yesterday = now - timedelta(days=1)

    events = await fetch_events(
        relay=relay,
        kinds=[1],
        since=int(yesterday.timestamp()),
        until=int(now.timestamp()),
        limit=20
    )

    print(f"Fetched {len(events)} events from last 24 hours")
    for event in events:
        print(
            f"  {datetime.fromtimestamp(event.created_at)}: {event.content[:100]}...")


async def fetch_from_multiple_relays():
    """Fetch events from multiple relays concurrently."""
    relays = [
        Relay("wss://relay.damus.io"),
        Relay("wss://nos.lol"),
        Relay("wss://relay.snort.social"),
    ]

    filters = {
        "kinds": [1],
        "limit": 5
    }

    results = await fetch_events_from_multiple_relays(relays, filters)

    print("Results from multiple relays:")
    for relay_url, events in results.items():
        print(f"  {relay_url}: {len(events)} events")


async def stream_live_events():
    """Stream live events as they arrive."""
    relay = Relay("wss://relay.damus.io")

    filters = {
        "kinds": [1],  # Text notes
    }

    print("Streaming live events (press Ctrl+C to stop)...")
    try:
        count = 0
        async for event in stream_events(relay, filters):
            count += 1
            print(
                f"[{count}] New event from {event.pubkey[:16]}...: {event.content[:100]}...")

            if count >= 10:  # Stop after 10 events for demo
                break
    except KeyboardInterrupt:
        print("Stopped streaming")


async def fetch_with_tags():
    """Fetch events with specific tags."""
    relay = Relay("wss://relay.damus.io")

    # Fetch events that mention a specific pubkey
    mentioned_pubkey = "82341f882b6eabcd2ba7f1ef90aad961cf074af15b9ef44a09f9d2a8fbfbe6a2"

    events = await fetch_events(
        relay=relay,
        kinds=[1],
        tags={"p": [mentioned_pubkey]},  # 'p' tags mention users
        limit=10
    )

    print(
        f"Fetched {len(events)} events mentioning {mentioned_pubkey[:16]}...")
    for event in events:
        print(f"  From {event.pubkey[:16]}...: {event.content[:100]}...")


if __name__ == "__main__":
    print("=== Fetch by Author ===")
    asyncio.run(fetch_by_author())

    print("\n=== Fetch with Time Range ===")
    asyncio.run(fetch_with_time_range())

    print("\n=== Fetch from Multiple Relays ===")
    asyncio.run(fetch_from_multiple_relays())

    print("\n=== Fetch with Tags ===")
    asyncio.run(fetch_with_tags())

    print("\n=== Stream Live Events ===")
    asyncio.run(stream_live_events())
