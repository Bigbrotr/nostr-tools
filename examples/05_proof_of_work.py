#!/usr/bin/env python3
"""
Proof-of-Work Events with nostr-tools
======================================

This example demonstrates:
- Creating events with proof-of-work
- Understanding difficulty targets
- Mining events with different difficulties
- PoW validation and verification
- Using PoW for spam prevention

Learn how to create computationally expensive events!
"""

import asyncio
import time

from nostr_tools import Client
from nostr_tools import ClientPublicationError
from nostr_tools import Event
from nostr_tools import Relay
from nostr_tools import generate_event
from nostr_tools import generate_keypair


async def basic_proof_of_work():
    """Learn the basics of proof-of-work events."""
    print("=" * 60)
    print("1. BASIC PROOF-OF-WORK")
    print("=" * 60)

    private_key, public_key = generate_keypair()

    print("\nWhat is Proof-of-Work?")
    print("  PoW requires finding a nonce that makes the event ID")
    print("  start with a certain number of leading zero bits.")
    print("  Higher difficulty = more leading zeros = more computation")

    # Create event with minimal PoW
    print("\nCreating event with 8-bit PoW (easy)...")
    start_time = time.time()

    event_data = generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=1,
        tags=[],
        content="This event has proof-of-work!",
        target_difficulty=8,  # 8 bits of leading zeros
        timeout=20,
    )

    elapsed = time.time() - start_time
    event = Event.from_dict(event_data)

    print(f"  ✅ Mined in {elapsed:.2f} seconds")
    print(f"  Event ID: {event.id}")

    # Count leading zero bits
    leading_zeros = count_leading_zero_bits(event.id)
    print(f"  Leading zero bits: {leading_zeros}")

    # Check for nonce tag
    nonce_tags = [tag for tag in event.tags if tag[0] == "nonce"]
    if nonce_tags:
        print(f"  Nonce value: {nonce_tags[0][1]}")
        print(f"  Target difficulty: {nonce_tags[0][2]}")


def count_leading_zero_bits(hex_string):
    """Count leading zero bits in a hex string."""
    zero_bits = 0
    for char in hex_string:
        if char == "0":
            zero_bits += 4
        else:
            # Count bits in the first non-zero character
            value = int(char, 16)
            zero_bits += 4 - value.bit_length()
            break
    return zero_bits


async def mining_different_difficulties():
    """Learn how difficulty affects mining time."""
    print("\n" + "=" * 60)
    print("2. MINING DIFFERENT DIFFICULTIES")
    print("=" * 60)

    private_key, public_key = generate_keypair()

    difficulties = [8, 12, 16, 20]

    print("\nMining events with increasing difficulty...")
    print(f"{'Difficulty':>12} {'Time':>12} {'Leading Zeros':>15} {'Status':>10}")
    print("-" * 60)

    for difficulty in difficulties:
        start_time = time.time()

        try:
            event_data = generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=1,
                tags=[],
                content=f"PoW event with {difficulty}-bit difficulty",
                target_difficulty=difficulty,
                timeout=30,  # 30 second timeout
            )

            elapsed = time.time() - start_time
            event_id = event_data["id"]
            leading_zeros = count_leading_zero_bits(event_id)

            print(f"{difficulty:>12} {elapsed:>10.2f}s {leading_zeros:>15} {'✅':>10}")

        except TimeoutError:
            elapsed = time.time() - start_time
            print(f"{difficulty:>12} {elapsed:>10.2f}s {'timeout':>15} {'❌':>10}")
        except Exception as e:
            print(f"{difficulty:>12} {'error':>12} {str(e)[:13]:>15} {'❌':>10}")


async def pow_event_structure():
    """Learn about the structure of PoW events."""
    print("\n" + "=" * 60)
    print("3. POW EVENT STRUCTURE")
    print("=" * 60)

    private_key, public_key = generate_keypair()

    print("\nCreating PoW event...")
    event_data = generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=1,
        tags=[["t", "pow"]],
        content="Examining PoW event structure",
        target_difficulty=12,
        timeout=20,
    )

    event = Event.from_dict(event_data)

    print("\nEvent structure:")
    print("  Standard fields:")
    print(f"    - id: {event.id}")
    print(f"    - pubkey: {event.pubkey[:16]}...")
    print(f"    - kind: {event.kind}")
    print(f"    - created_at: {event.created_at}")

    print("\n  Tags:")
    for i, tag in enumerate(event.tags, 1):
        if tag[0] == "nonce":
            print(f"    {i}. nonce tag:")
            print(f"       - nonce value: {tag[1]}")
            print(f"       - target difficulty: {tag[2]}")
        else:
            print(f"    {i}. {tag[0]} tag: {tag[1]}")

    print(f"\n  Content: {event.content}")


async def publish_pow_event():
    """Learn how to publish PoW events to relays."""
    print("\n" + "=" * 60)
    print("4. PUBLISHING POW EVENTS")
    print("=" * 60)

    private_key, public_key = generate_keypair()
    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=20)

    try:
        print(f"\nCreating PoW event for {relay.url}...")
        print("(Some relays require or prefer PoW events)")

        # Create event with moderate PoW
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[["t", "pow"], ["t", "nostr-tools"]],
            content="Testing PoW event publication with nostr-tools",
            target_difficulty=16,
            timeout=30,
        )

        event = Event.from_dict(event_data)
        leading_zeros = count_leading_zero_bits(event.id)

        print("  ✅ Event mined")
        print(f"     ID: {event.id}")
        print(f"     Leading zeros: {leading_zeros} bits")

        # Publish to relay
        async with client:
            print("\nPublishing to relay...")
            try:
                await client.publish(event)
                print("  ✅ Event accepted by relay")
            except ClientPublicationError as e:
                print(f"  ❌ Event rejected (might need higher PoW): {e}")

    except TimeoutError:
        print("  ❌ Mining timed out (try lower difficulty)")
    except Exception as e:
        print(f"  ❌ Error: {e}")


async def pow_for_spam_prevention():
    """Learn how PoW helps prevent spam."""
    print("\n" + "=" * 60)
    print("5. POW FOR SPAM PREVENTION")
    print("=" * 60)

    print("\nWhy Proof-of-Work?")
    print("  - Makes bulk event creation computationally expensive")
    print("  - Increases cost of spam attacks")
    print("  - No central authority or payment required")
    print("  - Relay can set minimum PoW requirements")

    print("\nExample difficulty costs:")
    print("  8-bit:  ~instant (testing only)")
    print("  12-bit: ~0.1-1 seconds (light protection)")
    print("  16-bit: ~1-10 seconds (moderate protection)")
    print("  20-bit: ~10-100 seconds (strong protection)")
    print("  24-bit: ~minutes (very strong protection)")

    print("\nTypical relay requirements:")
    print("  - Public relays: 0-12 bits (or none)")
    print("  - Private relays: 16-20 bits")
    print("  - Spam-heavy relays: 20+ bits")


async def adaptive_pow():
    """Learn how to adapt PoW to relay requirements."""
    print("\n" + "=" * 60)
    print("6. ADAPTIVE POW")
    print("=" * 60)

    from nostr_tools import fetch_nip11

    private_key, public_key = generate_keypair()
    relay = Relay("wss://relay.damus.io")
    client = Client(relay, timeout=15)

    try:
        # Check relay requirements
        print("\nChecking relay PoW requirements...")
        nip11_data = await fetch_nip11(client)

        if nip11_data and nip11_data.limitation:
            min_pow = nip11_data.limitation.get("min_pow_difficulty", 0)
            print(f"  Relay requires: {min_pow} bits minimum")
        else:
            min_pow = 0
            print("  No PoW requirement detected")

        # Create event with appropriate PoW
        if min_pow > 0:
            print("\nCreating event with required PoW...")
            event_data = generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=1,
                tags=[],
                content="Adaptive PoW event",
                target_difficulty=min_pow,
                timeout=30,
            )

            event = Event.from_dict(event_data)
            print(f"  ✅ Event created with {min_pow}-bit PoW")

            # Verify it meets requirements
            leading_zeros = count_leading_zero_bits(event.id)
            if leading_zeros >= min_pow:
                print(f"  ✅ Meets relay requirements ({leading_zeros} >= {min_pow})")
            else:
                print(f"  ❌ Does not meet requirements ({leading_zeros} < {min_pow})")
        else:
            print("\n  ℹ️  Relay does not require PoW")

    except Exception as e:
        print(f"  ❌ Error: {e}")


async def pow_best_practices():
    """Learn best practices for using PoW."""
    print("\n" + "=" * 60)
    print("7. POW BEST PRACTICES")
    print("=" * 60)

    print("\nBest practices for PoW events:")

    print("\n  1. Check relay requirements first")
    print("     Use fetch_nip11() to detect min_pow_difficulty")

    print("\n  2. Set appropriate timeouts")
    print("     Higher difficulty needs longer timeout")
    print("     Use timeout parameter in generate_event()")

    print("\n  3. Handle timeouts gracefully")
    print("     Catch TimeoutError and retry with lower difficulty")

    print("\n  4. Balance UX and security")
    print("     16-bit: Good balance for most use cases")
    print("     20-bit: High security, noticeable delay")

    print("\n  5. Consider caching")
    print("     Mine events ahead of time for better UX")

    print("\n  6. Verify PoW in received events")
    print("     Check nonce tags and count leading zeros")

    print("\n  7. Use PoW for high-value events")
    print("     Metadata, contact lists, important announcements")


async def main():
    """Run all proof-of-work examples."""
    await basic_proof_of_work()
    await mining_different_difficulties()
    await pow_event_structure()
    await publish_pow_event()
    await pow_for_spam_prevention()
    await adaptive_pow()
    await pow_best_practices()

    print("\n" + "=" * 60)
    print("✨ EXAMPLES COMPLETED!")
    print("=" * 60)
    print("\nYou now understand:")
    print("  ✓ How proof-of-work events work")
    print("  ✓ Mining events with different difficulties")
    print("  ✓ PoW event structure and nonce tags")
    print("  ✓ Publishing PoW events to relays")
    print("  ✓ Using PoW for spam prevention")
    print("  ✓ Adapting PoW to relay requirements")
    print("\nNext: Check out 06_streaming_and_advanced.py")


if __name__ == "__main__":
    asyncio.run(main())
