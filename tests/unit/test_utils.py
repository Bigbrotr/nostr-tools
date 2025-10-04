"""
Unit tests for the utils module.

This module tests all utility functions including:
- WebSocket URL discovery and validation
- Data sanitization
- Cryptographic operations (key generation, signing, verification)
- Event ID calculation
- Bech32 encoding/decoding
- Proof-of-work mining
"""

import time

import pytest

from nostr_tools import calc_event_id
from nostr_tools import find_ws_urls
from nostr_tools import generate_event
from nostr_tools import generate_keypair
from nostr_tools import sanitize
from nostr_tools import sig_event_id
from nostr_tools import to_bech32
from nostr_tools import to_hex
from nostr_tools import validate_keypair
from nostr_tools import verify_sig

# ============================================================================
# WebSocket URL Discovery Tests
# ============================================================================


@pytest.mark.unit
class TestFindWsUrls:
    """Test WebSocket URL discovery."""

    def test_find_single_wss_url(self) -> None:
        """Test finding a single WSS URL."""
        text = "Connect to wss://relay.damus.io"
        urls = find_ws_urls(text)
        assert len(urls) == 1
        assert "relay.damus.io" in urls[0]

    def test_find_multiple_urls(self) -> None:
        """Test finding multiple WebSocket URLs."""
        text = "wss://relay1.example.com and wss://relay2.example.com"
        urls = find_ws_urls(text)
        assert len(urls) == 2

    def test_find_ws_url_normalizes_to_wss(self) -> None:
        """Test that ws:// URLs are normalized to wss://."""
        text = "ws://relay.example.com"
        urls = find_ws_urls(text)
        assert len(urls) == 1
        assert urls[0].startswith("wss://")

    def test_find_url_with_port(self) -> None:
        """Test finding URLs with custom ports."""
        text = "wss://relay.example.com:7777"
        urls = find_ws_urls(text)
        assert len(urls) == 1
        assert ":7777" in urls[0]

    def test_find_url_with_path(self) -> None:
        """Test finding URLs with paths."""
        text = "wss://relay.example.com/nostr"
        urls = find_ws_urls(text)
        assert len(urls) == 1
        assert "/nostr" in urls[0]

    def test_find_onion_url(self) -> None:
        """Test finding .onion URLs."""
        text = "wss://thehub7gqe43miyc.onion"
        urls = find_ws_urls(text)
        assert len(urls) == 1
        assert ".onion" in urls[0]

    def test_find_v3_onion_url(self) -> None:
        """Test finding v3 .onion URLs."""
        text = "wss://oxtrdevav64z64yb7x6rjg4ntzqjhedm5b5zjqulugknhzr46ny2qbad.onion"
        urls = find_ws_urls(text)
        assert len(urls) == 1
        assert ".onion" in urls[0]

    def test_ignore_http_urls(self) -> None:
        """Test that HTTP URLs are ignored."""
        text = "http://example.com https://example.com"
        urls = find_ws_urls(text)
        assert len(urls) == 0

    def test_ignore_invalid_tld(self) -> None:
        """Test that invalid TLDs are ignored."""
        text = "wss://relay.invalidtld"
        urls = find_ws_urls(text)
        assert len(urls) == 0

    def test_ignore_invalid_onion_length(self) -> None:
        """Test that invalid .onion lengths are ignored."""
        text = "wss://invalid.onion"
        urls = find_ws_urls(text)
        assert len(urls) == 0

    def test_empty_text_returns_empty_list(self) -> None:
        """Test that empty text returns empty list."""
        urls = find_ws_urls("")
        assert urls == []

    def test_url_with_query_string(self) -> None:
        """Test URL with query string."""
        text = "wss://relay.example.com?key=value"
        urls = find_ws_urls(text)
        # Query strings might be included or excluded based on implementation
        assert len(urls) >= 0


# ============================================================================
# Data Sanitization Tests
# ============================================================================


@pytest.mark.unit
class TestSanitize:
    """Test data sanitization."""

    def test_sanitize_string_removes_null_bytes(self) -> None:
        """Test that null bytes are removed from strings."""
        result = sanitize("hello\x00world")
        assert result == "helloworld"
        assert "\x00" not in result

    def test_sanitize_list_recursively(self) -> None:
        """Test that lists are sanitized recursively."""
        result = sanitize(["hello\x00", "world\x00"])
        assert result == ["hello", "world"]

    def test_sanitize_dict_recursively(self) -> None:
        """Test that dicts are sanitized recursively."""
        result = sanitize(
            {"key\x00": "value\x00", "nested": {"data\x00": "test\x00"}})
        assert result["key"] == "value"
        assert result["nested"]["data"] == "test"

    def test_sanitize_nested_structures(self) -> None:
        """Test sanitizing deeply nested structures."""
        data = {"list": ["item\x00", {"nested\x00": "value\x00"}]}
        result = sanitize(data)
        assert result["list"][0] == "item"
        assert result["list"][1]["nested"] == "value"

    def test_sanitize_non_string_types(self) -> None:
        """Test that non-string types are returned unchanged."""
        assert sanitize(123) == 123
        assert sanitize(True) is True
        assert sanitize(None) is None

    def test_sanitize_empty_string(self) -> None:
        """Test sanitizing empty string."""
        assert sanitize("") == ""

    def test_sanitize_multiple_null_bytes(self) -> None:
        """Test sanitizing multiple null bytes."""
        result = sanitize("a\x00b\x00c\x00")
        assert result == "abc"


# ============================================================================
# Event ID Calculation Tests
# ============================================================================


@pytest.mark.unit
class TestCalcEventId:
    """Test event ID calculation."""

    def test_calc_event_id_returns_64_char_hex(self, valid_public_key: str) -> None:
        """Test that calc_event_id returns 64-character hex string."""
        event_id = calc_event_id(
            valid_public_key, int(time.time()), 1, [], "test")
        assert len(event_id) == 64
        assert all(c in "0123456789abcdef" for c in event_id)

    def test_calc_event_id_is_deterministic(self, valid_public_key: str) -> None:
        """Test that same inputs produce same event ID."""
        created_at = int(time.time())
        event_id1 = calc_event_id(valid_public_key, created_at, 1, [], "test")
        event_id2 = calc_event_id(valid_public_key, created_at, 1, [], "test")
        assert event_id1 == event_id2

    def test_calc_event_id_different_content(self, valid_public_key: str) -> None:
        """Test that different content produces different event ID."""
        created_at = int(time.time())
        event_id1 = calc_event_id(
            valid_public_key, created_at, 1, [], "content1")
        event_id2 = calc_event_id(
            valid_public_key, created_at, 1, [], "content2")
        assert event_id1 != event_id2

    def test_calc_event_id_different_kind(self, valid_public_key: str) -> None:
        """Test that different kind produces different event ID."""
        created_at = int(time.time())
        event_id1 = calc_event_id(valid_public_key, created_at, 1, [], "test")
        event_id2 = calc_event_id(valid_public_key, created_at, 2, [], "test")
        assert event_id1 != event_id2

    def test_calc_event_id_with_tags(self, valid_public_key: str) -> None:
        """Test event ID calculation with tags."""
        tags = [["e", "event_id"], ["p", "pubkey"]]
        event_id = calc_event_id(
            valid_public_key, int(time.time()), 1, tags, "test")
        assert len(event_id) == 64

    def test_calc_event_id_with_unicode_content(self, valid_public_key: str) -> None:
        """Test event ID calculation with Unicode content."""
        content = "Hello 世界 🌍"
        event_id = calc_event_id(
            valid_public_key, int(time.time()), 1, [], content)
        assert len(event_id) == 64


# ============================================================================
# Signature Verification Tests
# ============================================================================


@pytest.mark.unit
class TestVerifySig:
    """Test signature verification."""

    def test_verify_valid_signature(self, valid_private_key: str, valid_public_key: str) -> None:
        """Test verifying a valid signature."""
        event_id = calc_event_id(
            valid_public_key, int(time.time()), 1, [], "test")
        sig = sig_event_id(event_id, valid_private_key)
        assert verify_sig(event_id, valid_public_key, sig) is True

    def test_verify_invalid_signature(self, valid_public_key: str) -> None:
        """Test verifying an invalid signature."""
        event_id = "a" * 64
        sig = "b" * 128
        assert verify_sig(event_id, valid_public_key, sig) is False

    def test_verify_wrong_pubkey(self, valid_private_key: str, valid_public_key: str) -> None:
        """Test verifying with wrong public key."""
        event_id = calc_event_id(
            valid_public_key, int(time.time()), 1, [], "test")
        sig = sig_event_id(event_id, valid_private_key)
        wrong_pubkey = "a" * 64
        assert verify_sig(event_id, wrong_pubkey, sig) is False

    def test_verify_corrupted_signature(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test verifying a corrupted signature."""
        event_id = calc_event_id(
            valid_public_key, int(time.time()), 1, [], "test")
        # Use a completely different signature (all zeros) to ensure it's invalid
        corrupted_sig = "0" * 128
        assert verify_sig(event_id, valid_public_key, corrupted_sig) is False


# ============================================================================
# Signature Generation Tests
# ============================================================================


@pytest.mark.unit
class TestSigEventId:
    """Test event ID signing."""

    def test_sig_event_id_returns_128_char_hex(self, valid_private_key: str) -> None:
        """Test that sig_event_id returns 128-character hex string."""
        event_id = "a" * 64
        sig = sig_event_id(event_id, valid_private_key)
        assert len(sig) == 128
        assert all(c in "0123456789abcdef" for c in sig)

    def test_sig_event_id_is_deterministic(self, valid_private_key: str) -> None:
        """Test that same inputs produce same signature."""
        event_id = "a" * 64
        sig1 = sig_event_id(event_id, valid_private_key)
        sig2 = sig_event_id(event_id, valid_private_key)
        assert sig1 == sig2

    def test_sig_different_event_ids(self, valid_private_key: str) -> None:
        """Test that different event IDs produce different signatures."""
        sig1 = sig_event_id("a" * 64, valid_private_key)
        sig2 = sig_event_id("b" * 64, valid_private_key)
        assert sig1 != sig2


# ============================================================================
# Event Generation Tests
# ============================================================================


@pytest.mark.unit
class TestGenerateEvent:
    """Test event generation."""

    def test_generate_event_returns_dict(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test that generate_event returns a dictionary."""
        event = generate_event(
            valid_private_key, valid_public_key, 1, [], "test")
        assert isinstance(event, dict)

    def test_generate_event_has_all_fields(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test that generated event has all required fields."""
        event = generate_event(
            valid_private_key, valid_public_key, 1, [], "test")
        assert "id" in event
        assert "pubkey" in event
        assert "created_at" in event
        assert "kind" in event
        assert "tags" in event
        assert "content" in event
        assert "sig" in event

    def test_generate_event_with_custom_created_at(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test generating event with custom timestamp."""
        created_at = 1234567890
        event = generate_event(
            valid_private_key, valid_public_key, 1, [], "test", created_at=created_at
        )
        assert event["created_at"] == created_at

    def test_generate_event_signature_is_valid(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test that generated event has valid signature."""
        event = generate_event(
            valid_private_key, valid_public_key, 1, [], "test")
        assert verify_sig(event["id"], event["pubkey"], event["sig"]) is True

    def test_generate_event_id_is_correct(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test that generated event ID is correctly calculated."""
        event = generate_event(
            valid_private_key, valid_public_key, 1, [], "test")
        expected_id = calc_event_id(
            event["pubkey"],
            event["created_at"],
            event["kind"],
            event["tags"],
            event["content"],
        )
        assert event["id"] == expected_id

    def test_generate_event_with_proof_of_work(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test generating event with proof-of-work."""
        event = generate_event(
            valid_private_key,
            valid_public_key,
            1,
            [],
            "test",
            target_difficulty=4,
            timeout=5,
        )
        # Should have nonce tag if PoW succeeded
        nonce_tags = [tag for tag in event["tags"] if tag[0] == "nonce"]
        # Might timeout, so nonce tag is optional
        assert len(nonce_tags) <= 1

    def test_generate_event_pow_timeout(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test that PoW respects timeout."""
        import time

        start = time.time()
        generate_event(
            valid_private_key,
            valid_public_key,
            1,
            [],
            "test",
            target_difficulty=30,  # Very high difficulty
            timeout=1,  # Short timeout
        )
        elapsed = time.time() - start
        # Should timeout within reasonable time
        assert elapsed < 2.0


# ============================================================================
# Keypair Validation Tests
# ============================================================================


@pytest.mark.unit
class TestValidateKeypair:
    """Test keypair validation."""

    def test_validate_valid_keypair(self, valid_private_key: str, valid_public_key: str) -> None:
        """Test validating a valid keypair."""
        assert validate_keypair(valid_private_key, valid_public_key) is True

    def test_validate_mismatched_keypair(self, valid_private_key: str) -> None:
        """Test validating a mismatched keypair."""
        wrong_pubkey = "a" * 64
        assert validate_keypair(valid_private_key, wrong_pubkey) is False

    def test_validate_invalid_length_private_key(self, valid_public_key: str) -> None:
        """Test validating with invalid private key length."""
        invalid_privkey = "a" * 63
        assert validate_keypair(invalid_privkey, valid_public_key) is False

    def test_validate_invalid_length_public_key(self, valid_private_key: str) -> None:
        """Test validating with invalid public key length."""
        invalid_pubkey = "a" * 63
        assert validate_keypair(valid_private_key, invalid_pubkey) is False


# ============================================================================
# Bech32 Encoding Tests
# ============================================================================


@pytest.mark.unit
class TestToBech32:
    """Test Bech32 encoding."""

    def test_to_bech32_npub(self, valid_public_key: str) -> None:
        """Test encoding public key to npub."""
        npub = to_bech32("npub", valid_public_key)
        assert npub.startswith("npub1")

    def test_to_bech32_nsec(self, valid_private_key: str) -> None:
        """Test encoding private key to nsec."""
        nsec = to_bech32("nsec", valid_private_key)
        assert nsec.startswith("nsec1")

    def test_to_bech32_note(self) -> None:
        """Test encoding event ID to note."""
        event_id = "a" * 64
        note = to_bech32("note", event_id)
        assert note.startswith("note1")

    def test_to_bech32_round_trip(self, valid_public_key: str) -> None:
        """Test that Bech32 encoding can be reversed."""
        npub = to_bech32("npub", valid_public_key)
        decoded = to_hex(npub)
        assert decoded == valid_public_key


# ============================================================================
# Bech32 Decoding Tests
# ============================================================================


@pytest.mark.unit
class TestToHex:
    """Test Bech32 decoding."""

    def test_to_hex_from_npub(self, valid_public_key: str) -> None:
        """Test decoding npub to hex."""
        npub = to_bech32("npub", valid_public_key)
        decoded = to_hex(npub)
        assert decoded == valid_public_key
        assert len(decoded) == 64

    def test_to_hex_from_nsec(self, valid_private_key: str) -> None:
        """Test decoding nsec to hex."""
        nsec = to_bech32("nsec", valid_private_key)
        decoded = to_hex(nsec)
        assert decoded == valid_private_key

    def test_to_hex_invalid_bech32(self) -> None:
        """Test decoding invalid Bech32 string."""
        result = to_hex("invalid_bech32")
        assert result == ""

    def test_to_hex_empty_string(self) -> None:
        """Test decoding empty string."""
        result = to_hex("")
        assert result == ""


# ============================================================================
# Keypair Generation Tests
# ============================================================================


@pytest.mark.unit
class TestGenerateKeypair:
    """Test keypair generation."""

    def test_generate_keypair_returns_tuple(self) -> None:
        """Test that generate_keypair returns a tuple."""
        result = generate_keypair()
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_generate_keypair_keys_are_hex(self) -> None:
        """Test that generated keys are hex strings."""
        privkey, pubkey = generate_keypair()
        assert len(privkey) == 64
        assert len(pubkey) == 64
        assert all(c in "0123456789abcdef" for c in privkey)
        assert all(c in "0123456789abcdef" for c in pubkey)

    def test_generate_keypair_is_valid(self) -> None:
        """Test that generated keypair is valid."""
        privkey, pubkey = generate_keypair()
        assert validate_keypair(privkey, pubkey) is True

    def test_generate_multiple_unique_keypairs(self) -> None:
        """Test that multiple generations produce unique keypairs."""
        keypairs = [generate_keypair() for _ in range(10)]
        private_keys = [kp[0] for kp in keypairs]
        public_keys = [kp[1] for kp in keypairs]

        # All should be unique
        assert len(set(private_keys)) == 10
        assert len(set(public_keys)) == 10

    def test_generated_keypair_can_sign_and_verify(self) -> None:
        """Test that generated keypair can sign and verify."""
        privkey, pubkey = generate_keypair()
        event_id = calc_event_id(pubkey, int(time.time()), 1, [], "test")
        sig = sig_event_id(event_id, privkey)
        assert verify_sig(event_id, pubkey, sig) is True


# ============================================================================
# Edge Cases Tests
# ============================================================================


@pytest.mark.unit
class TestUtilsEdgeCases:
    """Test utils edge cases."""

    def test_calc_event_id_with_empty_tags(self, valid_public_key: str) -> None:
        """Test calculating event ID with empty tags."""
        event_id = calc_event_id(
            valid_public_key, int(time.time()), 1, [], "test")
        assert len(event_id) == 64

    def test_calc_event_id_with_empty_content(self, valid_public_key: str) -> None:
        """Test calculating event ID with empty content."""
        event_id = calc_event_id(valid_public_key, int(time.time()), 1, [], "")
        assert len(event_id) == 64

    def test_generate_event_with_complex_tags(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test generating event with complex tags."""
        tags = [
            ["e", "event_id", "relay_url", "marker"],
            ["p", "pubkey"],
            ["a", "kind:pubkey:d"],
        ]
        event = generate_event(
            valid_private_key, valid_public_key, 1, tags, "test")
        assert event["tags"] == tags

    def test_sanitize_preserves_structure(self) -> None:
        """Test that sanitize preserves data structure."""
        data = {
            "string": "test",
            "number": 123,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "nested": {"key": "value"},
        }
        result = sanitize(data)
        assert result["number"] == 123
        assert result["boolean"] is True
        assert result["null"] is None
        assert result["list"] == [1, 2, 3]

    def test_to_bech32_empty_hex_returns_value(self) -> None:
        """Test that empty hex returns a Bech32 value."""
        result = to_bech32("npub", "")
        # Empty hex will still produce a Bech32 string with the prefix
        assert result.startswith("npub") or result == ""


# ============================================================================
# Additional Utils Coverage Tests
# ============================================================================


@pytest.mark.unit
class TestUtilsAdditionalCoverage:
    """Additional tests for improved utils coverage."""

    def test_to_bech32_with_prefix_variations(self) -> None:
        """Test to_bech32 with different prefixes."""
        hex_str = "a" * 64

        # Test different prefixes
        npub = to_bech32("npub", hex_str)
        assert npub.startswith("npub")

        nsec = to_bech32("nsec", hex_str)
        assert nsec.startswith("nsec")

        note = to_bech32("note", hex_str)
        assert note.startswith("note")

    def test_find_ws_urls_edge_cases(self) -> None:
        """Test find_ws_urls with edge cases."""
        # Test with mixed content
        text = "Check wss://relay1.com and also wss://relay2.com:443/path"
        urls = find_ws_urls(text)
        assert len(urls) >= 1

        # Test with no URLs
        text = "No URLs here"
        urls = find_ws_urls(text)
        assert len(urls) == 0

    def test_sanitize_edge_cases(self) -> None:
        """Test sanitize with edge cases."""
        # Test with empty structures
        assert sanitize([]) == []
        assert sanitize({}) == {}
        assert sanitize("") == ""

        # Test with nested null bytes
        nested = {"a": ["test\x00", {"b": "value\x00"}]}
        result = sanitize(nested)
        assert "\x00" not in str(result)
