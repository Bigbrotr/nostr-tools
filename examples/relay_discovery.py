"""Relay discovery and testing examples."""

import asyncio
from nostr_tools import Relay, NostrWebSocketClient
from nostr_tools.utils.network import find_websocket_relay_urls, is_valid_websocket_url


async def test_relay_connectivity():
    """Test connectivity to various relays."""
    relay_urls = [
        "wss://relay.damus.io",
        "wss://nos.lol",
        "wss://relay.snort.social",
        "wss://relay.nostr.band",
        "wss://relay.current.fyi",
    ]

    print("Testing relay connectivity...")

    for url in relay_urls:
        try:
            relay = Relay(url)

            async with NostrWebSocketClient(relay, timeout=5) as client:
                if client.is_connected:
                    print(f"✅ {url} - Connected successfully")

                    # Test basic subscription
                    sub_id = await client.subscribe({"kinds": [1], "limit": 1})
                    print(f"   Subscription {sub_id} created")

                    # Listen for one event or timeout
                    found_event = False
                    async for event in client.listen_for_events(sub_id):
                        print(f"   Received event {event.id[:16]}...")
                        found_event = True
                        break

                    if not found_event:
                        print("   No events received (relay might be empty)")

                    await client.unsubscribe(sub_id)
                else:
                    print(f"❌ {url} - Failed to connect")

        except Exception as e:
            print(f"❌ {url} - Error: {e}")

        print()


def discover_relay_urls_in_text():
    """Discover relay URLs in text content."""
    sample_text = """
    Check out these Nostr relays:
    - wss://relay.damus.io
    - wss://nos.lol:443
    - ws://localhost:8080
    - wss://relay.example.com/path
    - wss://3g2upl4pq6kufc4m.onion (Tor relay)
    - Not a relay: https://example.com
    - Invalid: ftp://relay.com
    """

    print("Discovering WebSocket relay URLs in text:")
    print(f"Sample text:\n{sample_text}")

    urls = find_websocket_relay_urls(sample_text)
    print(f"\nFound {len(urls)} relay URLs:")
    for url in urls:
        print(f"  - {url}")
        print(f"    Valid: {is_valid_websocket_url(url)}")


async def test_relay_capabilities():
    """Test relay capabilities (read/write)."""
    relay = Relay("wss://relay.damus.io")

    async with NostrWebSocketClient(relay) as client:
        print(f"Testing capabilities of {relay.url}")

        # Test read capability
        print("Testing read capability...")
        try:
            sub_id = await client.subscribe({"kinds": [1], "limit": 1})
            print("✅ Read capability: Working")
            await client.unsubscribe(sub_id)
        except Exception as e:
            print(f"❌ Read capability: Failed - {e}")

        # Note: Write testing would require a valid event with proper signature
        # This is just a demonstration of the structure
        print("✅ Write testing would require a signed event")


def analyze_relay_urls():
    """Analyze different types of relay URLs."""
    test_urls = [
        "wss://relay.damus.io",
        "wss://nos.lol:443",
        "ws://localhost:8080",
        "wss://relay.example.com/path",
        "wss://3g2upl4pq6kufc4m.onion",  # Tor relay
        "wss://relay.nostr.band",
        "invalid-url",
        "https://not-a-websocket.com",
    ]

    print("Analyzing relay URLs:")
    for url in test_urls:
        try:
            relay = Relay(url)
            print(f"✅ {url}")
            print(f"   Network: {relay.network}")
            print(f"   Domain: {relay.domain}")
            print(f"   Is Tor: {relay.is_tor}")
            print(f"   Is Clearnet: {relay.is_clearnet}")
        except Exception as e:
            print(f"❌ {url} - Invalid: {e}")
        print()


if __name__ == "__main__":
    print("=== Relay URL Discovery ===")
    discover_relay_urls_in_text()

    print("\n=== Relay URL Analysis ===")
    analyze_relay_urls()

    print("\n=== Relay Connectivity Test ===")
    asyncio.run(test_relay_connectivity())

    print("\n=== Relay Capabilities Test ===")
    asyncio.run(test_relay_capabilities())
