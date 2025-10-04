#!/usr/bin/env python3
"""
Events and Filters in nostr-tools
==================================

This example demonstrates:
- Different event types (kinds)
- Creating various event structures
- Working with event tags
- Building filter criteria
- Validating events

Learn how to work with the core data structures of Nostr!
"""

import asyncio
import json
import time

from nostr_tools import Event
from nostr_tools import Filter
from nostr_tools import generate_event
from nostr_tools import generate_keypair


async def create_different_event_types():
    """Learn about different Nostr event kinds."""
    print("=" * 60)
    print("1. DIFFERENT EVENT TYPES (KINDS)")
    print("=" * 60)

    private_key, public_key = generate_keypair()

    # Kind 0: Metadata/Profile
    metadata_content = {
        "name": "Alice",
        "about": "Python developer exploring Nostr",
        "picture": "https://example.com/alice.jpg",
        "nip05": "alice@example.com",
        "website": "https://alice.dev",
    }

    metadata_event = generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=0,
        tags=[],
        content=json.dumps(metadata_content),
    )

    print("\nKind 0 - Metadata Event:")
    print(f"  ID: {metadata_event['id'][:16]}...")
    print(f"  Content: {metadata_content['name']} - {metadata_content['about']}")

    # Kind 1: Text Note
    text_event = generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=1,
        tags=[["t", "python"], ["t", "nostr"]],
        content="Just published my first Nostr app!",
    )

    print("\nKind 1 - Text Note:")
    print(f"  ID: {text_event['id'][:16]}...")
    print(f"  Content: {text_event['content']}")

    # Kind 3: Contact List
    contacts = [
        ["p", "abc" * 21 + "d", "wss://relay.damus.io", "friend"],
        ["p", "def" * 21 + "a", "wss://relay.nostr.band", "colleague"],
    ]

    contacts_event = generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=3,
        tags=contacts,
        content="",
    )

    print("\nKind 3 - Contact List:")
    print(f"  ID: {contacts_event['id'][:16]}...")
    print(f"  Contacts: {len(contacts_event['tags'])} entries")

    # Kind 7: Reaction
    original_note_id = text_event["id"]
    reaction_event = generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=7,
        tags=[
            ["e", original_note_id],
            ["p", public_key],
        ],
        content="🚀",  # Emoji reaction
    )

    print("\nKind 7 - Reaction:")
    print(f"  ID: {reaction_event['id'][:16]}...")
    print(f"  Reacting to: {original_note_id[:16]}...")
    print(f"  Reaction: {reaction_event['content']}")

    # Kind 5: Deletion
    deletion_event = generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=5,
        tags=[["e", text_event["id"]]],
        content="Changed my mind about this post",
    )

    print("\nKind 5 - Deletion Request:")
    print(f"  ID: {deletion_event['id'][:16]}...")
    print(f"  Deleting: {text_event['id'][:16]}...")


async def work_with_tags():
    """Learn how to work with event tags."""
    print("\n" + "=" * 60)
    print("2. WORKING WITH EVENT TAGS")
    print("=" * 60)

    private_key, public_key = generate_keypair()

    # Create event with various tags
    event_data = generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=1,
        tags=[
            ["t", "nostr"],  # Hashtag
            ["t", "python"],  # Another hashtag
            ["p", public_key, "wss://relay.damus.io", "mention"],  # Pubkey reference
            ["e", "a" * 64, "", "reply"],  # Event reference
            ["r", "https://github.com/nostr-protocol"],  # URL reference
        ],
        content="Check out the Nostr protocol! #nostr #python",
    )

    event = Event.from_dict(event_data)

    print("\nEvent tags breakdown:")
    for i, tag in enumerate(event.tags, 1):
        tag_name = tag[0]
        tag_value = tag[1][:16] + "..." if len(tag[1]) > 16 else tag[1]
        print(f"  Tag {i}: [{tag_name}] {tag_value}")

    # Use Event helper methods
    print("\nTag queries:")
    print(f"  Has 't' tags (hashtags): {event.has_tag('t')}")
    print(f"  Has 'p' tags (mentions): {event.has_tag('p')}")
    print(f"  Has 'a' tags: {event.has_tag('a')}")

    print("\nExtract tag values:")
    hashtags = event.get_tag_values("t")
    print(f"  Hashtags: {hashtags}")

    mentions = event.get_tag_values("p")
    print(f"  Mentioned pubkeys: {[m[:16] + '...' for m in mentions]}")

    referenced_events = event.get_tag_values("e")
    print(f"  Referenced events: {[e[:16] + '...' for e in referenced_events]}")

    urls = event.get_tag_values("r")
    print(f"  URLs: {urls}")


async def build_filters():
    """Learn how to create filter criteria."""
    print("\n" + "=" * 60)
    print("3. BUILDING FILTER CRITERIA")
    print("=" * 60)

    # Simple filter by kind
    filter1 = Filter(kinds=[1], limit=10)
    print("\nFilter 1 - Recent text notes:")
    print(f"  {filter1.subscription_filter}")

    # Filter by author
    author_pubkey = "abc" * 21 + "d"
    filter2 = Filter(kinds=[1], authors=[author_pubkey], limit=5)
    print("\nFilter 2 - Notes from specific author:")
    print(f"  {filter2.subscription_filter}")

    # Time-based filter
    one_hour_ago = int(time.time()) - 3600
    filter3 = Filter(
        kinds=[1],
        since=one_hour_ago,
        limit=20,
    )
    print("\nFilter 3 - Notes from last hour:")
    print(f"  {filter3.subscription_filter}")

    # Tag-based filter (replies to an event)
    event_id = "a" * 64
    filter4 = Filter(
        kinds=[1],
        e=[event_id],  # Using tag filter via kwargs
    )
    print("\nFilter 4 - Replies to specific event:")
    print(f"  {filter4.subscription_filter}")

    # Complex filter combining multiple criteria
    filter5 = Filter(
        kinds=[1, 7],  # Text notes and reactions
        t=["bitcoin", "nostr"],  # With specific hashtags
        since=one_hour_ago,
        until=int(time.time()),
        limit=50,
    )
    print("\nFilter 5 - Complex multi-criteria:")
    print(f"  {filter5.subscription_filter}")

    # Filter validation
    print("\n Filter validation:")
    print(f"  Filter 1 valid: {filter1.is_valid}")
    print(f"  Filter 5 valid: {filter5.is_valid}")


async def event_validation():
    """Learn about event validation."""
    print("\n" + "=" * 60)
    print("4. EVENT VALIDATION")
    print("=" * 60)

    private_key, public_key = generate_keypair()

    # Create a valid event
    valid_event_data = generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=1,
        tags=[["t", "test"]],
        content="This is a valid event",
    )

    valid_event = Event.from_dict(valid_event_data)

    print("\nValid event:")
    print(f"  Is valid: {valid_event.is_valid}")
    print(f"  ID: {valid_event.id}")
    print(f"  Signature: {valid_event.sig[:32]}...")

    # Demonstrate validation checks
    print("\nValidation checks performed:")
    print("  ✓ ID is 64-char lowercase hex")
    print("  ✓ Pubkey is 64-char lowercase hex")
    print("  ✓ Signature is 128-char lowercase hex")
    print("  ✓ Kind is in range 0-65535")
    print("  ✓ Created_at is non-negative")
    print("  ✓ No null bytes in content/tags")
    print("  ✓ ID matches computed event ID")
    print("  ✓ Signature is valid")

    # Try to create event with invalid kind
    try:
        invalid_data = {
            "id": "a" * 64,
            "pubkey": "b" * 64,
            "created_at": int(time.time()),
            "kind": 999999,  # Invalid - too large
            "tags": [],
            "content": "test",
            "sig": "c" * 128,
        }
        Event.from_dict(invalid_data)
    except Exception as e:
        print("\nInvalid event (kind too large):")
        print(f"  ❌ Validation error: {type(e).__name__}")


async def event_serialization():
    """Learn about event serialization."""
    print("\n" + "=" * 60)
    print("5. EVENT SERIALIZATION")
    print("=" * 60)

    private_key, public_key = generate_keypair()

    # Create event
    event_data = generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=1,
        tags=[["t", "serialization"]],
        content="Learning about event serialization",
    )

    event = Event.from_dict(event_data)

    # Serialize to dict
    event_dict = event.to_dict()
    print("\nSerialized to dict:")
    print(f"  Keys: {list(event_dict.keys())}")

    # Serialize to JSON
    event_json = json.dumps(event_dict)
    print(f"  JSON size: {len(event_json)} bytes")

    # Deserialize back
    loaded_dict = json.loads(event_json)
    loaded_event = Event.from_dict(loaded_dict)

    print("\nRound-trip serialization:")
    print(f"  Original ID: {event.id}")
    print(f"  Loaded ID:   {loaded_event.id}")
    print(f"  Match: {event.id == loaded_event.id}")


async def main():
    """Run all event and filter examples."""
    await create_different_event_types()
    await work_with_tags()
    await build_filters()
    await event_validation()
    await event_serialization()

    print("\n" + "=" * 60)
    print("✨ EXAMPLES COMPLETED!")
    print("=" * 60)
    print("\nYou now understand:")
    print("  ✓ Different event kinds and their purposes")
    print("  ✓ How to work with event tags")
    print("  ✓ Building filter criteria for queries")
    print("  ✓ Event validation and serialization")
    print("\nNext: Check out 03_publishing_and_subscribing.py")


if __name__ == "__main__":
    asyncio.run(main())
