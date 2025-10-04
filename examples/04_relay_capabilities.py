#!/usr/bin/env python3
"""
Relay Capabilities Testing with nostr-tools
============================================

This example demonstrates:
- Testing relay connectivity
- Checking read/write capabilities
- Fetching NIP-11 relay information
- Collecting NIP-66 performance metrics
- Comprehensive relay metadata
- Comparing multiple relays

Learn how to discover and test relay capabilities!
"""

import asyncio

from nostr_tools import Client
from nostr_tools import Relay
from nostr_tools import check_connectivity
from nostr_tools import check_readability
from nostr_tools import check_writability
from nostr_tools import fetch_nip11
from nostr_tools import fetch_nip66
from nostr_tools import fetch_relay_metadata
from nostr_tools import generate_keypair


async def test_basic_connectivity():
    """Learn how to test basic relay connectivity."""
    print("=" * 60)
    print("1. BASIC CONNECTIVITY TESTING")
    print("=" * 60)

    test_relays = [
        "wss://relay.damus.io",
        "wss://relay.nostr.band",
        "wss://nos.lol",
    ]

    for relay_url in test_relays:
        print(f"\nTesting: {relay_url}")
        relay = Relay(relay_url)
        client = Client(relay, timeout=10)

        try:
            rtt_open, can_connect = await check_connectivity(client)

            if can_connect:
                print("  ✅ Connectable")
                print(f"  ⏱️  Connection time: {rtt_open}ms")
            else:
                print("  ❌ Cannot connect")

        except Exception as e:
            print(f"  ❌ Error: {e}")


async def test_read_capability():
    """Learn how to test relay read capability."""
    print("\n" + "=" * 60)
    print("2. READ CAPABILITY TESTING")
    print("=" * 60)

    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=10)

    try:
        async with client:
            print("\nTesting read capability...")

            rtt_read, can_read = await check_readability(client)

            if can_read:
                print("  ✅ Readable")
                print(f"  ⏱️  Read response time: {rtt_read}ms")
            else:
                print("  ❌ Cannot read")
                print("     (Relay might require authentication or payment)")

    except Exception as e:
        print(f"❌ Error: {e}")


async def test_write_capability():
    """Learn how to test relay write capability."""
    print("\n" + "=" * 60)
    print("3. WRITE CAPABILITY TESTING")
    print("=" * 60)

    private_key, public_key = generate_keypair()
    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=15)

    try:
        async with client:
            print("\nTesting write capability...")

            rtt_write, can_write = await check_writability(client, private_key, public_key)

            if can_write:
                print("  ✅ Writable")
                print(f"  ⏱️  Write response time: {rtt_write}ms")
            else:
                print("  ❌ Cannot write")
                print("     (Relay might require authentication, payment, or PoW)")

    except Exception as e:
        print(f"❌ Error: {e}")


async def fetch_relay_information():
    """Learn how to fetch NIP-11 relay information."""
    print("\n" + "=" * 60)
    print("4. NIP-11 RELAY INFORMATION")
    print("=" * 60)

    test_relays = [
        "wss://relay.damus.io",
        "wss://relay.nostr.band",
    ]

    for relay_url in test_relays:
        print(f"\n{relay_url}")
        relay = Relay(relay_url)
        client = Client(relay, timeout=10)

        try:
            nip11_data = await fetch_nip11(client)

            if nip11_data:
                print(f"  Name: {nip11_data.name or 'N/A'}")
                print(f"  Description: {nip11_data.description or 'N/A'}")
                print(f"  Contact: {nip11_data.contact or 'N/A'}")
                print(f"  Software: {nip11_data.software or 'N/A'} {nip11_data.version or ''}")

                if nip11_data.supported_nips:
                    print(f"  Supported NIPs: {nip11_data.supported_nips[:15]}...")

                if nip11_data.limitation:
                    print("  Limitations:")
                    for key, value in nip11_data.limitation.items():
                        print(f"    - {key}: {value}")
            else:
                print("  ❌ No NIP-11 information available")

        except Exception as e:
            print(f"  ❌ Error: {e}")


async def fetch_performance_metrics():
    """Learn how to fetch NIP-66 performance metrics."""
    print("\n" + "=" * 60)
    print("5. NIP-66 PERFORMANCE METRICS")
    print("=" * 60)

    private_key, public_key = generate_keypair()
    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=15)

    try:
        print(f"\nFetching comprehensive metrics for {relay.url}...")

        nip66_data = await fetch_nip66(client, private_key, public_key)

        if nip66_data:
            print("\n  Connection Capabilities:")
            print(f"    Openable: {'✅' if nip66_data.openable else '❌'}")
            print(f"    Readable: {'✅' if nip66_data.readable else '❌'}")
            print(f"    Writable: {'✅' if nip66_data.writable else '❌'}")

            print("\n  Performance Metrics:")
            if nip66_data.rtt_open:
                print(f"    Open RTT: {nip66_data.rtt_open}ms")
            if nip66_data.rtt_read:
                print(f"    Read RTT: {nip66_data.rtt_read}ms")
            if nip66_data.rtt_write:
                print(f"    Write RTT: {nip66_data.rtt_write}ms")
        else:
            print("  ❌ Could not fetch metrics")

    except Exception as e:
        print(f"❌ Error: {e}")


async def comprehensive_relay_metadata():
    """Learn how to fetch complete relay metadata."""
    print("\n" + "=" * 60)
    print("6. COMPREHENSIVE RELAY METADATA")
    print("=" * 60)

    private_key, public_key = generate_keypair()
    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=15)

    try:
        print(f"\nFetching complete metadata for {relay.url}...")
        print("(This combines NIP-11 and NIP-66 data)\n")

        metadata = await fetch_relay_metadata(client, private_key, public_key)

        # Show NIP-11 data
        if metadata.nip11:
            print("📋 NIP-11 Information:")
            print(f"  Name: {metadata.nip11.name or 'N/A'}")
            print(f"  Software: {metadata.nip11.software or 'N/A'}")
            if metadata.nip11.supported_nips:
                print(f"  Supported NIPs: {len(metadata.nip11.supported_nips)} NIPs")
        else:
            print("📋 NIP-11: Not available")

        # Show NIP-66 data
        if metadata.nip66:
            print("\n📊 NIP-66 Metrics:")
            print(
                f"  Capabilities: "
                f"{'R' if metadata.nip66.readable else '-'}"
                f"{'W' if metadata.nip66.writable else '-'}"
                f"{'O' if metadata.nip66.openable else '-'}"
            )
            print(f"  Open RTT: {metadata.nip66.rtt_open}ms")
            if metadata.nip66.rtt_read:
                print(f"  Read RTT: {metadata.nip66.rtt_read}ms")
            if metadata.nip66.rtt_write:
                print(f"  Write RTT: {metadata.nip66.rtt_write}ms")
        else:
            print("\n📊 NIP-66: Not available")

        print(f"\n  Generated at: {metadata.generated_at}")
        print(f"  Is valid: {'✅' if metadata.is_valid else '❌'}")

    except Exception as e:
        print(f"❌ Error: {e}")


async def compare_relays():
    """Learn how to compare multiple relays."""
    print("\n" + "=" * 60)
    print("7. COMPARING MULTIPLE RELAYS")
    print("=" * 60)

    private_key, public_key = generate_keypair()

    test_relays = [
        "wss://relay.damus.io",
        "wss://relay.nostr.band",
        "wss://nos.lol",
    ]

    print(f"\nComparing {len(test_relays)} relays...\n")
    print(f"{'Relay':<30} {'Open':>6} {'Read':>6} {'Write':>6}")
    print("-" * 60)

    for relay_url in test_relays:
        relay = Relay(relay_url)
        client = Client(relay, timeout=10)

        try:
            # Quick connectivity check
            rtt_open, openable = await check_connectivity(client)

            if openable:
                # Get read/write info
                async with client:
                    rtt_read, readable = await check_readability(client)
                    rtt_write, writable = await check_writability(client, private_key, public_key)

                open_str = f"{rtt_open}ms" if rtt_open else "N/A"
                read_str = f"{rtt_read}ms" if readable and rtt_read else "❌"
                write_str = f"{rtt_write}ms" if writable and rtt_write else "❌"

                print(f"{relay_url:<30} {open_str:>6} {read_str:>6} {write_str:>6}")
            else:
                print(f"{relay_url:<30} {'❌':>6} {'❌':>6} {'❌':>6}")

        except Exception:
            print(f"{relay_url:<30} {'ERR':>6} {'ERR':>6} {'ERR':>6}")


async def detect_relay_requirements():
    """Learn how to detect relay requirements from NIP-11."""
    print("\n" + "=" * 60)
    print("8. DETECTING RELAY REQUIREMENTS")
    print("=" * 60)

    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=10)

    try:
        nip11_data = await fetch_nip11(client)

        print(f"\nAnalyzing {relay.url} requirements...")

        if nip11_data and nip11_data.limitation:
            print("\n  Detected requirements:")

            limitations = nip11_data.limitation

            if "auth_required" in limitations and limitations["auth_required"]:
                print("    🔒 Authentication required (NIP-42)")

            if "payment_required" in limitations and limitations["payment_required"]:
                print("    💰 Payment required")

            if "restricted_writes" in limitations and limitations["restricted_writes"]:
                print("    ✍️  Restricted writes")

            if "min_pow_difficulty" in limitations:
                pow_difficulty = limitations["min_pow_difficulty"]
                print(f"    ⛏️  Minimum PoW difficulty: {pow_difficulty} bits")

            if "max_message_length" in limitations:
                max_length = limitations["max_message_length"]
                print(f"    📏 Max message length: {max_length} bytes")

            if "max_event_tags" in limitations:
                max_tags = limitations["max_event_tags"]
                print(f"    🏷️  Max event tags: {max_tags}")

            if not limitations:
                print("    ✅ No special requirements detected")
        else:
            print("  ℹ️  No NIP-11 limitations information available")

    except Exception as e:
        print(f"❌ Error: {e}")


async def main():
    """Run all relay capability examples."""
    await test_basic_connectivity()
    await test_read_capability()
    await test_write_capability()
    await fetch_relay_information()
    await fetch_performance_metrics()
    await comprehensive_relay_metadata()
    await compare_relays()
    await detect_relay_requirements()

    print("\n" + "=" * 60)
    print("✨ EXAMPLES COMPLETED!")
    print("=" * 60)
    print("\nYou now understand:")
    print("  ✓ How to test relay connectivity")
    print("  ✓ Checking read and write capabilities")
    print("  ✓ Fetching NIP-11 relay information")
    print("  ✓ Collecting NIP-66 performance metrics")
    print("  ✓ Comparing multiple relays")
    print("  ✓ Detecting relay requirements")
    print("\nNext: Check out 05_proof_of_work.py")


if __name__ == "__main__":
    asyncio.run(main())
