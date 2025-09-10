"""
Basic tests for the nostr-tools library.

These tests cover fundamental functionality without requiring
network connections or external dependencies.
"""

import pytest
import time
import json
from unittest.mock import Mock, patch

from nostr_tools import (
    Event, Relay, Filter, generate_keypair, generate_event,
    calc_event_id, verify_sig, to_bech32, to_hex, test_keypair
)


class TestKeyGeneration:
    """Test cryptographic key generation and validation."""
    
    def test_generate_keypair(self):
        """Test basic key pair generation."""
        private_key, public_key = generate_keypair()
        
        assert isinstance(private_key, str)
        assert isinstance(public_key, str)
        assert len(private_key) == 64
        assert len(public_key) == 64
        
        # Should be valid hex
        int(private_key, 16)
        int(public_key, 16)
    
    def test_keypair_uniqueness(self):
        """Test that generated key pairs are unique."""
        pairs = [generate_keypair() for _ in range(10)]
        private_keys = [pair[0] for pair in pairs]
        public_keys = [pair[1] for pair in pairs]
        
        # All keys should be unique
        assert len(set(private_keys)) == 10
        assert len(set(public_keys)) == 10
    
    def test_test_keypair_valid(self):
        """Test validation of valid key pairs."""
        private_key, public_key = generate_keypair()
        assert test_keypair(private_key, public_key) is True
    
    def test_test_keypair_invalid(self):
        """Test validation of invalid key pairs."""
        private_key1, public_key1 = generate_keypair()
        private_key2, public_key2 = generate_keypair()
        
        # Mismatched keys should fail
        assert test_keypair(private_key1, public_key2) is False
        assert test_keypair(private_key2, public_key1) is False
    
    def test_test_keypair_malformed(self):
        """Test validation with malformed keys."""
        assert test_keypair("invalid", "invalid") is False
        assert test_keypair("", "") is False
        assert test_keypair("x" * 63, "y" * 64) is False  # Wrong length


class TestBech32Encoding:
    """Test Bech32 encoding and decoding."""
    
    def test_hex_to_bech32_conversion(self):
        """Test conversion from hex to Bech32."""
        private_key, public_key = generate_keypair()
        
        nsec = to_bech32("nsec", private_key)
        npub = to_bech32("npub", public_key)
        
        assert isinstance(nsec, str)
        assert isinstance(npub, str)
        assert nsec.startswith("nsec1")
        assert npub.startswith("npub1")
    
    def test_bech32_to_hex_conversion(self):
        """Test conversion from Bech32 back to hex."""
        private_key, public_key = generate_keypair()
        
        nsec = to_bech32("nsec", private_key)
        npub = to_bech32("npub", public_key)
        
        hex_private = to_hex(nsec)
        hex_public = to_hex(npub)
        
        assert hex_private == private_key
        assert hex_public == public_key
    
    def test_bech32_roundtrip(self):
        """Test complete roundtrip conversion."""
        original_hex = "1234567890abcdef" * 4  # 64 char hex
        
        bech32_str = to_bech32("test", original_hex)
        converted_hex = to_hex(bech32_str)
        
        assert converted_hex == original_hex


class TestEventCreation:
    """Test Nostr event creation and validation."""
    
    def test_generate_event_basic(self):
        """Test basic event generation."""
        private_key, public_key = generate_keypair()
        
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="Hello Nostr!"
        )
        
        assert isinstance(event_data, dict)
        assert "id" in event_data
        assert "pubkey" in event_data
        assert "created_at" in event_data
        assert "kind" in event_data
        assert "tags" in event_data
        assert "content" in event_data
        assert "sig" in event_data
        
        assert event_data["pubkey"] == public_key
        assert event_data["kind"] == 1
        assert event_data["content"] == "Hello Nostr!"
        assert event_data["tags"] == []
    
    def test_generate_event_with_tags(self):
        """Test event generation with tags."""
        private_key, public_key = generate_keypair()
        
        tags = [["t", "nostr"], ["p", public_key]]
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=tags,
            content="Tagged event"
        )
        
        assert event_data["tags"] == tags
    
    def test_generate_event_custom_timestamp(self):
        """Test event generation with custom timestamp."""
        private_key, public_key = generate_keypair()
        custom_time = 1640995200  # Fixed timestamp
        
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="Timestamped event",
            created_at=custom_time
        )
        
        assert event_data["created_at"] == custom_time
    
    def test_event_id_calculation(self):
        """Test event ID calculation."""
        private_key, public_key = generate_keypair()
        created_at = int(time.time())
        kind = 1
        tags = [["t", "test"]]
        content = "Test content"
        
        # Calculate ID manually
        expected_id = calc_event_id(public_key, created_at, kind, tags, content)
        
        # Generate event
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=kind,
            tags=tags,
            content=content,
            created_at=created_at
        )
        
        assert event_data["id"] == expected_id
    
    def test_event_signature_verification(self):
        """Test event signature verification."""
        private_key, public_key = generate_keypair()
        
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="Signed event"
        )
        
        # Verify signature
        is_valid = verify_sig(
            event_data["id"],
            event_data["pubkey"],
            event_data["sig"]
        )
        
        assert is_valid is True


class TestEventClass:
    """Test the Event class functionality."""
    
    def test_event_from_dict(self):
        """Test creating Event from dictionary."""
        private_key, public_key = generate_keypair()
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[["t", "test"]],
            content="Test event"
        )
        
        event = Event.from_dict(event_data)
        
        assert event.id == event_data["id"]
        assert event.pubkey == event_data["pubkey"]
        assert event.created_at == event_data["created_at"]
        assert event.kind == event_data["kind"]
        assert event.tags == event_data["tags"]
        assert event.content == event_data["content"]
        assert event.sig == event_data["sig"]
    
    def test_event_to_dict(self):
        """Test converting Event to dictionary."""
        private_key, public_key = generate_keypair()
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="Test event"
        )
        
        event = Event.from_dict(event_data)
        converted_data = event.to_dict()
        
        assert converted_data == event_data
    
    def test_event_validation_invalid_id(self):
        """Test event validation with invalid ID."""
        private_key, public_key = generate_keypair()
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="Test event"
        )
        
        # Corrupt the ID
        event_data["id"] = "invalid_id"
        
        with pytest.raises(ValueError, match="id must be a 64-character hex string"):
            Event.from_dict(event_data)
    
    def test_event_validation_invalid_signature(self):
        """Test event validation with invalid signature."""
        private_key, public_key = generate_keypair()
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="Test event"
        )
        
        # Corrupt the signature
        event_data["sig"] = "x" * 128
        
        with pytest.raises(ValueError, match="sig is not a valid signature"):
            Event.from_dict(event_data)
    
    def test_event_get_tag_values(self):
        """Test getting tag values from event."""
        private_key, public_key = generate_keypair()
        tags = [
            ["t", "nostr", "bitcoin"],
            ["p", public_key],
            ["t", "python"]
        ]
        
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=tags,
            content="Tagged event"
        )
        
        event = Event.from_dict(event_data)
        
        # Get hashtags
        hashtags = event.get_tag_values("t")
        assert "nostr" in hashtags
        assert "bitcoin" in hashtags
        assert "python" in hashtags
        
        # Get mentioned pubkeys
        mentions = event.get_tag_values("p")
        assert public_key in mentions
    
    def test_event_has_tag(self):
        """Test checking if event has specific tags."""
        private_key, public_key = generate_keypair()
        tags = [
            ["t", "nostr"],
            ["p", public_key],
            ["e", "some_event_id"]
        ]
        
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=tags,
            content="Tagged event"
        )
        
        event = Event.from_dict(event_data)
        
        # Check tag existence
        assert event.has_tag("t") is True
        assert event.has_tag("p") is True
        assert event.has_tag("e") is True
        assert event.has_tag("r") is False
        
        # Check tag with specific value
        assert event.has_tag("t", "nostr") is True
        assert event.has_tag("t", "bitcoin") is False
        assert event.has_tag("p", public_key) is True


class TestRelay:
    """Test Relay class functionality."""
    
    def test_relay_creation_clearnet(self):
        """Test creating clearnet relay."""
        relay = Relay("wss://relay.example.com")
        
        assert relay.url == "wss://relay.example.com"
        assert relay.network == "clearnet"
    
    def test_relay_creation_tor(self):
        """Test creating Tor relay."""
        relay = Relay("wss://test1234567890abcdef.onion")
        
        assert relay.url == "wss://test1234567890abcdef.onion"
        assert relay.network == "tor"
    
    def test_relay_invalid_url(self):
        """Test relay creation with invalid URL."""
        with pytest.raises(ValueError, match="Invalid URL format"):
            Relay("not-a-valid-url")
    
    def test_relay_equality(self):
        """Test relay equality comparison."""
        relay1 = Relay("wss://relay.example.com")
        relay2 = Relay("wss://relay.example.com")
        relay3 = Relay("wss://other.example.com")
        
        assert relay1 == relay2
        assert relay1 != relay3
        assert relay2 != relay3
    
    def test_relay_hash(self):
        """Test relay hashing for use in sets/dicts."""
        relay1 = Relay("wss://relay.example.com")
        relay2 = Relay("wss://relay.example.com")
        relay3 = Relay("wss://other.example.com")
        
        relay_set = {relay1, relay2, relay3}
        assert len(relay_set) == 2  # relay1 and relay2 are the same
    
    def test_relay_from_dict(self):
        """Test creating relay from dictionary."""
        data = {"url": "wss://relay.example.com"}
        relay = Relay.from_dict(data)
        
        assert relay.url == "wss://relay.example.com"
        assert relay.network == "clearnet"
    
    def test_relay_to_dict(self):
        """Test converting relay to dictionary."""
        relay = Relay("wss://relay.example.com")
        data = relay.to_dict()
        
        expected = {
            "url": "wss://relay.example.com",
            "network": "clearnet"
        }
        
        assert data == expected


class TestFilter:
    """Test Filter class functionality."""
    
    def test_filter_creation_basic(self):
        """Test basic filter creation."""
        filter = Filter(kinds=[1], limit=10)
        
        assert filter.filter_dict["kinds"] == [1]
        assert filter.filter_dict["limit"] == 10
    
    def test_filter_creation_comprehensive(self):
        """Test comprehensive filter creation."""
        private_key, public_key = generate_keypair()
        
        filter = Filter(
            ids=["a" * 64],
            authors=[public_key],
            kinds=[0, 1],
            since=1640995200,
            until=1640995300,
            limit=50,
            t=["nostr", "bitcoin"],
            p=[public_key]
        )
        
        expected_dict = {
            "ids": ["a" * 64],
            "authors": [public_key],
            "kinds": [0, 1],
            "since": 1640995200,
            "until": 1640995300,
            "limit": 50,
            "#t": ["nostr", "bitcoin"],
            "#p": [public_key]
        }
        
        assert filter.filter_dict == expected_dict
    
    def test_filter_validation_invalid_ids(self):
        """Test filter validation with invalid IDs."""
        with pytest.raises(ValueError, match="All ids must be 64-character hexadecimal"):
            Filter(ids=["invalid_id"])
    
    def test_filter_validation_invalid_authors(self):
        """Test filter validation with invalid authors."""
        with pytest.raises(ValueError, match="All authors must be 64-character hexadecimal"):
            Filter(authors=["invalid_author"])
    
    def test_filter_validation_invalid_kinds(self):
        """Test filter validation with invalid kinds."""
        with pytest.raises(ValueError, match="All kinds must be integers between 0 and 65535"):
            Filter(kinds=[-1])
        
        with pytest.raises(ValueError, match="All kinds must be integers between 0 and 65535"):
            Filter(kinds=[65536])
    
    def test_filter_validation_invalid_time_range(self):
        """Test filter validation with invalid time range."""
        with pytest.raises(ValueError, match="since must be less than or equal to until"):
            Filter(since=2000, until=1000)
    
    def test_filter_equality(self):
        """Test filter equality comparison."""
        filter1 = Filter(kinds=[1], limit=10)
        filter2 = Filter(kinds=[1], limit=10)
        filter3 = Filter(kinds=[1], limit=20)
        
        assert filter1 == filter2
        assert filter1 != filter3
    
    def test_filter_from_dict(self):
        """Test creating filter from dictionary."""
        data = {
            "kinds": [1],
            "limit": 10,
            "t": ["nostr"]
        }
        
        filter = Filter.from_dict(data)
        assert filter.filter_dict["kinds"] == [1]
        assert filter.filter_dict["limit"] == 10
        assert filter.filter_dict["#t"] == ["nostr"]
    
    def test_filter_to_dict(self):
        """Test converting filter to dictionary."""
        filter = Filter(kinds=[1], limit=10, t=["nostr"])
        data = filter.to_dict()
        
        expected = {
            "kinds": [1],
            "limit": 10,
            "t": ["nostr"]
        }
        
        assert data == expected


if __name__ == "__main__":
    pytest.main([__file__])