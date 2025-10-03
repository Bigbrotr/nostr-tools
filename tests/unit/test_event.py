"""
Unit tests for the Event class.

This module tests all functionality of the Event class including:
- Event creation and validation
- Type checking and validation rules
- Signature verification
- Event ID calculation
- Dictionary conversion
- Edge cases and error handling
"""

import json
import time
from typing import Any

import pytest

from nostr_tools import calc_event_id
from nostr_tools import generate_event
from nostr_tools import verify_sig
from nostr_tools.core.event import Event

# ============================================================================
# Event Creation Tests
# ============================================================================


@pytest.mark.unit
class TestEventCreation:
    """Test Event instance creation."""

    def test_create_valid_event(self, valid_event_dict: dict[str, Any]) -> None:
        """Test creating a valid event from dictionary."""
        event = Event.from_dict(valid_event_dict)
        assert isinstance(event, Event)
        assert event.id == valid_event_dict["id"]
        assert event.pubkey == valid_event_dict["pubkey"]
        assert event.kind == valid_event_dict["kind"]
        assert event.content == valid_event_dict["content"]

    def test_create_event_with_all_fields(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test event creation with all possible fields."""
        created_at = int(time.time())
        tags = [["e", "event_id"], ["p", "pubkey"], ["t", "tag"]]
        content = "Test content with special chars: 日本語 émojis 🚀"

        event_dict = generate_event(
            valid_private_key, valid_public_key, 1, tags, content, created_at
        )
        event = Event.from_dict(event_dict)

        assert event.created_at == created_at
        assert event.tags == tags
        assert event.content == content

    def test_event_post_init_normalization(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test that event __post_init__ normalizes hex strings to lowercase."""
        event_dict = generate_event(valid_private_key, valid_public_key, 1, [], "test")
        # Modify to uppercase
        event_dict["id"] = event_dict["id"].upper()
        event_dict["pubkey"] = event_dict["pubkey"].upper()
        event_dict["sig"] = event_dict["sig"].upper()

        event = Event.from_dict(event_dict)

        # Should be normalized to lowercase
        assert event.id.islower()
        assert event.pubkey.islower()
        assert event.sig.islower()

    def test_event_escape_sequence_handling(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test that escape sequences in content and tags are properly handled."""
        # Create event with escaped content
        content_with_escapes = r"Line1\nLine2\tTabbed\"Quoted\""
        tags_with_escapes = [[r"tag\nwith\tescape"]]

        event_dict = generate_event(
            valid_private_key, valid_public_key, 1, tags_with_escapes, content_with_escapes
        )
        event = Event.from_dict(event_dict)

        # Event should handle escape sequences
        assert isinstance(event.content, str)
        assert isinstance(event.tags, list)


# ============================================================================
# Event Validation Tests
# ============================================================================


@pytest.mark.unit
class TestEventValidation:
    """Test Event validation logic."""

    def test_valid_event_passes_validation(self, valid_event: Event) -> None:
        """Test that a valid event passes validation."""
        valid_event.validate()  # Should not raise
        assert valid_event.is_valid

    def test_invalid_id_length_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that invalid ID length raises ValueError."""
        valid_event_dict["id"] = "a" * 63  # Wrong length
        with pytest.raises(ValueError, match="id must be a 64-character hex string"):
            Event.from_dict(valid_event_dict)

    def test_invalid_id_chars_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that invalid ID characters raise ValueError."""
        valid_event_dict["id"] = "g" * 64  # Invalid hex char
        with pytest.raises(ValueError, match="id must be a 64-character hex string"):
            Event.from_dict(valid_event_dict)

    def test_invalid_pubkey_length_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that invalid pubkey length raises ValueError."""
        valid_event_dict["pubkey"] = "a" * 63
        with pytest.raises(ValueError, match="pubkey must be a 64-character hex string"):
            Event.from_dict(valid_event_dict)

    def test_invalid_pubkey_chars_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that invalid pubkey characters raise ValueError."""
        valid_event_dict["pubkey"] = "Z" * 64  # Invalid hex char
        with pytest.raises(ValueError, match="pubkey must be a 64-character hex string"):
            Event.from_dict(valid_event_dict)

    def test_invalid_signature_length_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that invalid signature length raises ValueError."""
        valid_event_dict["sig"] = "a" * 127
        with pytest.raises(ValueError, match="sig must be a 128-character hex string"):
            Event.from_dict(valid_event_dict)

    def test_invalid_signature_chars_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that invalid signature characters raise ValueError."""
        valid_event_dict["sig"] = "X" * 128  # Invalid hex char
        with pytest.raises(ValueError, match="sig must be a 128-character hex string"):
            Event.from_dict(valid_event_dict)

    def test_negative_created_at_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that negative created_at raises ValueError."""
        valid_event_dict["created_at"] = -1
        with pytest.raises(ValueError, match="created_at must be a non-negative integer"):
            Event.from_dict(valid_event_dict)

    def test_invalid_kind_below_range_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that kind below valid range raises ValueError."""
        valid_event_dict["kind"] = -1
        with pytest.raises(ValueError, match="kind must be between 0 and 65535"):
            Event.from_dict(valid_event_dict)

    def test_invalid_kind_above_range_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that kind above valid range raises ValueError."""
        valid_event_dict["kind"] = 65536
        with pytest.raises(ValueError, match="kind must be between 0 and 65535"):
            Event.from_dict(valid_event_dict)

    def test_null_character_in_content_raises_error(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test that null characters in content raise ValueError."""
        # Create event with null character in content
        event_dict = generate_event(valid_private_key, valid_public_key, 1, [], "test")
        event_dict["content"] = "test\x00content"
        # ID and signature are now invalid due to changed content
        with pytest.raises(ValueError):
            Event.from_dict(event_dict)

    def test_null_character_in_tags_raises_error(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test that null characters in tags raise ValueError."""
        # Create event with null character in tags
        event_dict = generate_event(valid_private_key, valid_public_key, 1, [], "test")
        event_dict["tags"] = [["test\x00tag"]]
        # ID and signature are now invalid due to changed tags
        with pytest.raises(ValueError):
            Event.from_dict(event_dict)

    def test_wrong_event_id_raises_error(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test that incorrect event ID raises ValueError."""
        event_dict = generate_event(valid_private_key, valid_public_key, 1, [], "test")
        event_dict["id"] = "a" * 64  # Wrong ID
        with pytest.raises(ValueError, match="id does not match the computed event id"):
            Event.from_dict(event_dict)

    def test_invalid_signature_raises_error(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test that invalid signature raises ValueError."""
        event_dict = generate_event(valid_private_key, valid_public_key, 1, [], "test")
        event_dict["sig"] = "a" * 128  # Wrong signature
        with pytest.raises(ValueError, match="sig is not a valid signature for the event"):
            Event.from_dict(event_dict)


# ============================================================================
# Event Type Validation Tests
# ============================================================================


@pytest.mark.unit
class TestEventTypeValidation:
    """Test Event type validation."""

    def test_non_string_id_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that non-string ID raises error."""
        valid_event_dict["id"] = 123
        with pytest.raises((TypeError, AttributeError)):  # .lower() will fail on int
            Event.from_dict(valid_event_dict)

    def test_non_string_pubkey_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that non-string pubkey raises error."""
        valid_event_dict["pubkey"] = 123
        with pytest.raises((TypeError, AttributeError)):  # .lower() will fail on int
            Event.from_dict(valid_event_dict)

    def test_non_int_created_at_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that non-integer created_at raises TypeError."""
        valid_event_dict["created_at"] = "not_an_int"
        with pytest.raises(TypeError, match="created_at must be int"):
            Event.from_dict(valid_event_dict)

    def test_non_int_kind_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that non-integer kind raises TypeError."""
        valid_event_dict["kind"] = "not_an_int"
        with pytest.raises(TypeError, match="kind must be int"):
            Event.from_dict(valid_event_dict)

    def test_non_list_tags_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that non-list tags raises TypeError."""
        valid_event_dict["tags"] = "not_a_list"
        with pytest.raises(TypeError, match="tags must be list"):
            Event.from_dict(valid_event_dict)

    def test_non_string_content_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that non-string content raises TypeError."""
        valid_event_dict["content"] = 123
        with pytest.raises(TypeError, match="content must be str"):
            Event.from_dict(valid_event_dict)

    def test_non_string_sig_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that non-string signature raises error."""
        valid_event_dict["sig"] = 123
        with pytest.raises((TypeError, AttributeError)):  # .lower() will fail on int
            Event.from_dict(valid_event_dict)

    def test_empty_tag_list_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that empty tag lists raise TypeError."""
        valid_event_dict["tags"] = [[]]  # Empty tag
        with pytest.raises(TypeError, match="tags must be a list of lists"):
            Event.from_dict(valid_event_dict)

    def test_non_string_tag_elements_raises_error(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that non-string tag elements raise TypeError."""
        valid_event_dict["tags"] = [[1, 2, 3]]  # Non-string elements
        with pytest.raises(TypeError, match="tags must be a list of lists"):
            Event.from_dict(valid_event_dict)


# ============================================================================
# Event Property Tests
# ============================================================================


@pytest.mark.unit
class TestEventProperties:
    """Test Event properties."""

    def test_is_valid_property_returns_true_for_valid_event(self, valid_event: Event) -> None:
        """Test that is_valid returns True for valid events."""
        assert valid_event.is_valid is True

    def test_is_valid_property_returns_false_for_invalid_event(self, valid_event: Event) -> None:
        """Test that is_valid returns False for invalid events."""
        # Corrupt the event
        valid_event.id = "invalid_id"
        assert valid_event.is_valid is False


# ============================================================================
# Event Dictionary Conversion Tests
# ============================================================================


@pytest.mark.unit
class TestEventDictionaryConversion:
    """Test Event dictionary conversion."""

    def test_from_dict_creates_event(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that from_dict creates an Event instance."""
        event = Event.from_dict(valid_event_dict)
        assert isinstance(event, Event)

    def test_from_dict_with_non_dict_raises_error(self) -> None:
        """Test that from_dict with non-dict raises TypeError."""
        with pytest.raises(TypeError, match="data must be a dict"):
            Event.from_dict("not_a_dict")  # type: ignore

    def test_from_dict_with_missing_keys_raises_error(self) -> None:
        """Test that from_dict with missing keys raises KeyError."""
        with pytest.raises(KeyError):
            Event.from_dict({})

    def test_to_dict_returns_dict(self, valid_event: Event) -> None:
        """Test that to_dict returns a dictionary."""
        event_dict = valid_event.to_dict()
        assert isinstance(event_dict, dict)

    def test_to_dict_contains_all_fields(self, valid_event: Event) -> None:
        """Test that to_dict contains all event fields."""
        event_dict = valid_event.to_dict()
        assert "id" in event_dict
        assert "pubkey" in event_dict
        assert "created_at" in event_dict
        assert "kind" in event_dict
        assert "tags" in event_dict
        assert "content" in event_dict
        assert "sig" in event_dict

    def test_round_trip_conversion(self, valid_event_dict: dict[str, Any]) -> None:
        """Test that Event can be converted to dict and back."""
        event1 = Event.from_dict(valid_event_dict)
        event_dict = event1.to_dict()
        event2 = Event.from_dict(event_dict)

        assert event1.id == event2.id
        assert event1.pubkey == event2.pubkey
        assert event1.created_at == event2.created_at
        assert event1.kind == event2.kind
        assert event1.tags == event2.tags
        assert event1.content == event2.content
        assert event1.sig == event2.sig


# ============================================================================
# Event ID and Signature Tests
# ============================================================================


@pytest.mark.unit
class TestEventIdAndSignature:
    """Test Event ID calculation and signature verification."""

    def test_event_id_matches_calculated_id(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test that event ID matches the calculated ID."""
        event_dict = generate_event(valid_private_key, valid_public_key, 1, [], "test")
        event = Event.from_dict(event_dict)

        calculated_id = calc_event_id(
            event.pubkey, event.created_at, event.kind, event.tags, event.content
        )
        assert event.id == calculated_id

    def test_event_signature_is_valid(self, valid_private_key: str, valid_public_key: str) -> None:
        """Test that event signature is valid."""
        event_dict = generate_event(valid_private_key, valid_public_key, 1, [], "test")
        event = Event.from_dict(event_dict)

        assert verify_sig(event.id, event.pubkey, event.sig) is True

    def test_different_content_produces_different_id(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test that different content produces different event IDs."""
        event_dict1 = generate_event(valid_private_key, valid_public_key, 1, [], "content1")
        event_dict2 = generate_event(valid_private_key, valid_public_key, 1, [], "content2")

        event1 = Event.from_dict(event_dict1)
        event2 = Event.from_dict(event_dict2)

        assert event1.id != event2.id


# ============================================================================
# Event Edge Cases Tests
# ============================================================================


@pytest.mark.unit
class TestEventEdgeCases:
    """Test Event edge cases and special scenarios."""

    def test_event_with_empty_content(self, valid_private_key: str, valid_public_key: str) -> None:
        """Test that events with empty content are valid."""
        event_dict = generate_event(valid_private_key, valid_public_key, 1, [], "")
        event = Event.from_dict(event_dict)
        assert event.content == ""
        assert event.is_valid

    def test_event_with_empty_tags(self, valid_private_key: str, valid_public_key: str) -> None:
        """Test that events with empty tags are valid."""
        event_dict = generate_event(valid_private_key, valid_public_key, 1, [], "test")
        event = Event.from_dict(event_dict)
        assert event.tags == []
        assert event.is_valid

    def test_event_with_complex_tags(self, valid_private_key: str, valid_public_key: str) -> None:
        """Test events with complex tag structures."""
        tags = [
            ["e", "event_id", "relay_url", "marker"],
            ["p", "pubkey", "relay_url"],
            ["a", "kind:pubkey:d-identifier"],
            ["t", "hashtag"],
        ]
        event_dict = generate_event(valid_private_key, valid_public_key, 1, tags, "test")
        event = Event.from_dict(event_dict)
        assert event.tags == tags
        assert event.is_valid

    def test_event_with_unicode_content(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test events with Unicode content."""
        content = "Hello 世界 🌍 Привет مرحبا"
        event_dict = generate_event(valid_private_key, valid_public_key, 1, [], content)
        event = Event.from_dict(event_dict)
        assert event.content == content
        assert event.is_valid

    def test_event_with_max_kind_value(self, valid_private_key: str, valid_public_key: str) -> None:
        """Test events with maximum kind value."""
        event_dict = generate_event(valid_private_key, valid_public_key, 65535, [], "test")
        event = Event.from_dict(event_dict)
        assert event.kind == 65535
        assert event.is_valid

    def test_event_with_min_kind_value(self, valid_private_key: str, valid_public_key: str) -> None:
        """Test events with minimum kind value."""
        event_dict = generate_event(valid_private_key, valid_public_key, 0, [], "test")
        event = Event.from_dict(event_dict)
        assert event.kind == 0
        assert event.is_valid

    def test_event_with_very_long_content(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test events with very long content."""
        content = "a" * 100000  # 100KB content
        event_dict = generate_event(valid_private_key, valid_public_key, 1, [], content)
        event = Event.from_dict(event_dict)
        assert len(event.content) == 100000
        assert event.is_valid

    def test_event_with_json_content(self, valid_private_key: str, valid_public_key: str) -> None:
        """Test events with JSON content."""
        content_obj = {"key": "value", "nested": {"data": 123}}
        content = json.dumps(content_obj)
        event_dict = generate_event(valid_private_key, valid_public_key, 1, [], content)
        event = Event.from_dict(event_dict)
        assert event.content == content
        assert event.is_valid
        # Verify JSON can be parsed back
        parsed = json.loads(event.content)
        assert parsed == content_obj
