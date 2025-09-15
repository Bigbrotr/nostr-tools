"""
Basic tests for the nostr-tools library.

These tests cover fundamental functionality without requiring
network connections or external dependencies.
"""

import time

import pytest

from nostr_tools import Client
from nostr_tools import Event
from nostr_tools import Filter
from nostr_tools import Relay
from nostr_tools import calc_event_id
from nostr_tools import find_websocket_relay_urls
from nostr_tools import generate_event
from nostr_tools import generate_keypair
from nostr_tools import parse_connection_response
from nostr_tools import parse_nip11_response
from nostr_tools import sanitize
from nostr_tools import to_bech32
from nostr_tools import to_hex
from nostr_tools import validate_keypair
from nostr_tools import verify_sig


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
        assert validate_keypair(private_key, public_key) is True

    def test_test_keypair_invalid(self):
        """Test validation of invalid key pairs."""
        private_key1, public_key1 = generate_keypair()
        private_key2, public_key2 = generate_keypair()

        # Mismatched keys should fail
        assert validate_keypair(private_key1, public_key2) is False
        assert validate_keypair(private_key2, public_key1) is False

    def test_test_keypair_malformed(self):
        """Test validation with malformed keys."""
        assert validate_keypair("invalid", "invalid") is False
        assert validate_keypair("", "") is False
        assert validate_keypair("x" * 63, "y" * 64) is False  # Wrong length

    def test_validate_keypair_exception_handling(self):
        """Test validate_keypair exception handling."""
        # Test non-hex characters
        assert validate_keypair("g" * 64, "h" * 64) is False

        # Test invalid lengths that would cause exceptions
        assert validate_keypair("a" * 65, "b" * 64) is False
        assert validate_keypair("a" * 64, "b" * 65) is False


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
        original_hex = "a" * 64  # 64 char hex

        bech32_str = to_bech32("test", original_hex)
        converted_hex = to_hex(bech32_str)

        assert converted_hex == original_hex

    def test_bech32_invalid_hex(self):
        """Test Bech32 encoding with invalid hex."""
        # Test invalid hex characters
        with pytest.raises(ValueError, match="non-hexadecimal number found"):
            to_bech32("test", "g" * 64)

    def test_bech32_conversion_failures(self):
        """Test Bech32 conversion failure cases."""
        # Test invalid Bech32 string
        result = to_hex("invalid_bech32")
        assert result == ""

        # Test Bech32 string that fails convertbits
        result = to_hex("test1invalid")
        assert result == ""


class TestURLDiscovery:
    """Test WebSocket URL discovery and validation."""

    def test_find_websocket_relay_urls_basic(self):
        """Test basic WebSocket URL discovery."""
        text = "Connect to wss://relay.damus.io for Nostr"
        urls = find_websocket_relay_urls(text)
        assert "wss://relay.damus.io" in urls

    def test_find_websocket_relay_urls_multiple(self):
        """Test finding multiple URLs."""
        text = "Use wss://relay1.com:443 or wss://relay2.com:8080"
        urls = find_websocket_relay_urls(text)
        assert len(urls) >= 2
        assert "wss://relay1.com:443" in urls
        assert "wss://relay2.com:8080" in urls

    def test_find_websocket_relay_urls_onion(self):
        """Test finding .onion URLs."""
        text = "Tor relay: wss://pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd.onion"
        urls = find_websocket_relay_urls(text)
        assert any(".onion" in url for url in urls)

    def test_find_websocket_relay_urls_invalid_port(self):
        """Test rejection of invalid port numbers."""
        text = "Invalid port: wss://relay.com:99999"
        urls = find_websocket_relay_urls(text)
        assert not any("99999" in url for url in urls)

    def test_find_websocket_relay_urls_invalid_onion(self):
        """Test rejection of invalid .onion addresses."""
        text = "Invalid onion: wss://short.onion"
        urls = find_websocket_relay_urls(text)
        assert not any("short.onion" in url for url in urls)

    def test_find_websocket_relay_urls_invalid_tld(self):
        """Test rejection of invalid TLDs."""
        text = "Invalid TLD: wss://relay.invalidtld"
        urls = find_websocket_relay_urls(text)
        assert not any("invalidtld" in url for url in urls)

    def test_find_websocket_relay_urls_normalization(self):
        """Test URL normalization to wss://."""
        text = "Use ws://relay.com (insecure)"
        urls = find_websocket_relay_urls(text)
        assert "wss://relay.com" in urls

    def test_find_websocket_relay_urls_path_handling(self):
        """Test URL path normalization."""
        text = "Relay with path: wss://relay.com/ and wss://relay2.com/path"
        urls = find_websocket_relay_urls(text)
        # Should normalize paths
        assert any(url.endswith("relay.com") for url in urls)
        assert any(url.endswith("/path") for url in urls)


class TestDataSanitization:
    """Test data sanitization functions."""

    def test_sanitize_string(self):
        """Test string sanitization."""
        dirty = "Hello\x00World"
        clean = sanitize(dirty)
        assert clean == "HelloWorld"
        assert "\x00" not in clean

    def test_sanitize_list(self):
        """Test list sanitization."""
        dirty = ["Hello\x00World", "Clean", "Another\x00Test"]
        clean = sanitize(dirty)
        assert clean == ["HelloWorld", "Clean", "AnotherTest"]
        assert all("\x00" not in item for item in clean)

    def test_sanitize_dict(self):
        """Test dictionary sanitization."""
        dirty = {
            "key\x00": "value\x00",
            "clean_key": "clean_value",
            "nested": {"inner\x00": "data\x00"},
        }
        clean = sanitize(dirty)

        # Check that null bytes are removed from keys and values
        assert "key" in clean
        assert "key\x00" not in clean
        assert clean["key"] == "value"
        assert clean["nested"]["inner"] == "data"

    def test_sanitize_mixed_structure(self):
        """Test sanitization of mixed data structures."""
        dirty = {
            "list": ["item\x001", "item\x002"],
            "dict": {"nested\x00": "value\x00"},
            "string": "test\x00string",
        }
        clean = sanitize(dirty)

        assert clean["list"] == ["item1", "item2"]
        assert clean["dict"]["nested"] == "value"
        assert clean["string"] == "teststring"

    def test_sanitize_non_string_types(self):
        """Test sanitization preserves non-string types."""
        data = {"number": 42, "boolean": True, "none": None, "list": [1, 2, 3]}
        clean = sanitize(data)
        assert clean == data  # Should be unchanged


class TestResponseParsing:
    """Test response parsing functions."""

    def test_parse_nip11_response_valid(self):
        """Test parsing valid NIP-11 response."""
        nip11_data = {
            "name": "Test Relay",
            "description": "A test relay",
            "pubkey": "a" * 64,
            "contact": "test@example.com",
            "supported_nips": [1, 2, 11],
            "software": "test-relay",
            "version": "1.0.0",
            "limitation": {"max_message_length": 16384, "auth_required": False},
        }

        result = parse_nip11_response(nip11_data)
        assert result["nip11_success"] is True
        assert result["name"] == "Test Relay"
        assert result["supported_nips"] == [1, 2, 11]
        assert result["limitation"]["max_message_length"] == 16384

    def test_parse_nip11_response_invalid_type(self):
        """Test parsing invalid NIP-11 response type."""
        result = parse_nip11_response("not a dict")
        assert result["nip11_success"] is False

    def test_parse_nip11_response_invalid_fields(self):
        """Test parsing NIP-11 with invalid field types."""
        nip11_data = {
            "name": 123,  # Should be string
            "supported_nips": "not a list",  # Should be list
            "limitation": "not a dict",  # Should be dict
        }

        result = parse_nip11_response(nip11_data)
        assert result["nip11_success"] is True
        assert result["name"] is None  # Invalid string becomes None
        assert result["supported_nips"] is None  # Invalid list becomes None
        assert result["limitation"] is None  # Invalid dict becomes None

    def test_parse_nip11_response_empty_data(self):
        """Test parsing empty NIP-11 response."""
        result = parse_nip11_response(None)
        assert result["nip11_success"] is False

    def test_parse_nip11_response_extra_fields(self):
        """Test parsing NIP-11 with extra fields."""
        nip11_data = {
            "name": "Test Relay",
            "custom_field": "custom_value",
            "another_field": {"nested": "data"},
        }

        result = parse_nip11_response(nip11_data)
        assert result["nip11_success"] is True
        assert result["extra_fields"]["custom_field"] == "custom_value"
        assert result["extra_fields"]["another_field"]["nested"] == "data"

    def test_parse_nip11_response_supported_nips_filtering(self):
        """Test filtering of supported_nips field."""
        nip11_data = {"name": "Test Relay", "supported_nips": [1, "2", 3, None, "invalid", 4]}

        result = parse_nip11_response(nip11_data)
        assert result["supported_nips"] == [1, "2", 3, "invalid", 4]  # None filtered out

    def test_parse_nip11_response_limitation_validation(self):
        """Test limitation field validation."""
        nip11_data = {
            "name": "Test Relay",
            "limitation": {
                "valid_key": "valid_value",
                123: "invalid_key",  # Non-string key
                "json_invalid": object(),  # Non-JSON-serializable value
            },
        }

        result = parse_nip11_response(nip11_data)
        assert "valid_key" in result["limitation"]
        assert 123 not in result["limitation"]
        assert "json_invalid" not in result["limitation"]

    def test_parse_connection_response_valid(self):
        """Test parsing valid connection response."""
        conn_data = {
            "connection_success": True,
            "rtt_open": 100,
            "rtt_read": 150,
            "rtt_write": 200,
            "openable": True,
            "writable": True,
            "readable": True,
        }

        result = parse_connection_response(conn_data)
        assert result["connection_success"] is True
        assert result["rtt_open"] == 100
        assert result["openable"] is True

    def test_parse_connection_response_invalid(self):
        """Test parsing invalid connection response."""
        result = parse_connection_response("not a dict")
        assert result["connection_success"] is False


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
            content="Hello Nostr!",
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
            content="Tagged event",
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
            created_at=custom_time,
        )

        assert event_data["created_at"] == custom_time

    def test_generate_event_pow_timeout(self):
        """Test event generation with proof-of-work timeout."""
        private_key, public_key = generate_keypair()

        # Use very high difficulty with short timeout to force timeout
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[["t", "test"]],
            content="PoW timeout test",
            target_difficulty=30,  # Very high difficulty
            timeout=1,  # Short timeout
        )

        # Should complete without nonce tag due to timeout
        assert isinstance(event_data, dict)
        assert event_data["content"] == "PoW timeout test"

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
            created_at=created_at,
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
            content="Signed event",
        )

        # Verify signature
        is_valid = verify_sig(event_data["id"], event_data["pubkey"], event_data["sig"])

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
            content="Test event",
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
            content="Test event",
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
            content="Test event",
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
            content="Test event",
        )

        # Corrupt the signature
        event_data["sig"] = "a" * 128

        with pytest.raises(ValueError, match="sig is not a valid signature"):
            Event.from_dict(event_data)

    def test_event_get_tag_values(self):
        """Test getting tag values from event."""
        private_key, public_key = generate_keypair()
        tags = [["t", "nostr", "bitcoin"], ["p", public_key], ["t", "python"]]

        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=tags,
            content="Tagged event",
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
        tags = [["t", "nostr"], ["p", public_key], ["e", "some_event_id"]]

        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=tags,
            content="Tagged event",
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
        relay = Relay("wss://pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd.onion")

        assert relay.url == "wss://pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd.onion"
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

        expected = {"url": "wss://relay.example.com", "network": "clearnet"}

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
        _, public_key = generate_keypair()

        filter = Filter(
            ids=["a" * 64],
            authors=[public_key],
            kinds=[0, 1],
            since=1640995200,
            until=1640995300,
            limit=50,
            t=["nostr", "bitcoin"],
            p=[public_key],
        )

        expected_dict = {
            "ids": ["a" * 64],
            "authors": [public_key],
            "kinds": [0, 1],
            "since": 1640995200,
            "until": 1640995300,
            "limit": 50,
            "#t": ["nostr", "bitcoin"],
            "#p": [public_key],
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
        data = {"kinds": [1], "limit": 10, "t": ["nostr"]}

        filter = Filter.from_dict(data)
        assert filter.filter_dict["kinds"] == [1]
        assert filter.filter_dict["limit"] == 10
        assert filter.filter_dict["#t"] == ["nostr"]

    def test_filter_to_dict(self):
        """Test converting filter to dictionary."""
        filter = Filter(kinds=[1], limit=10, t=["nostr"])
        data = filter.to_dict()

        expected = {"kinds": [1], "limit": 10, "t": ["nostr"]}

        assert data == expected


class TestClient:
    """Test Client class functionality."""

    def test_client_creation_clearnet(self, sample_relay):
        """Test creating client for clearnet relay."""
        client = Client(sample_relay, timeout=30)

        assert client.relay == sample_relay
        assert client.timeout == 30
        assert client.socks5_proxy_url is None
        assert not client.is_connected

    def test_client_creation_tor(self):
        """Test creating client for Tor relay."""
        tor_relay = Relay("wss://pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd.onion")
        socks5_url = "socks5://127.0.0.1:9050"

        client = Client(tor_relay, timeout=20, socks5_proxy_url=socks5_url)

        assert client.relay == tor_relay
        assert client.timeout == 20
        assert client.socks5_proxy_url == socks5_url

    def test_client_validation_invalid_relay(self):
        """Test client creation with invalid relay type."""
        with pytest.raises(TypeError, match="relay must be Relay"):
            Client("not_a_relay")

    def test_client_validation_invalid_timeout(self, sample_relay):
        """Test client creation with invalid timeout type."""
        with pytest.raises(TypeError, match="timeout must be int or None"):
            Client(sample_relay, timeout="invalid")

    def test_client_validation_invalid_socks5_url(self, sample_relay):
        """Test client creation with invalid SOCKS5 URL type."""
        with pytest.raises(TypeError, match="socks5_proxy_url must be str or None"):
            Client(sample_relay, socks5_proxy_url=123)

    def test_client_tor_without_proxy(self):
        """Test creating client for Tor relay without SOCKS5 proxy."""
        tor_relay = Relay("wss://pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd.onion")

        with pytest.raises(ValueError, match="socks5_proxy_url is required for Tor relays"):
            Client(tor_relay)

    async def test_client_connector_clearnet(self, sample_relay):
        """Test connector creation for clearnet relay."""
        client = Client(sample_relay)
        connector = client.connector()
        await connector.close()
        # Should return TCPConnector for clearnet
        from aiohttp import TCPConnector

        assert isinstance(connector, TCPConnector)

    async def test_client_connector_tor(self):
        """Test connector creation for Tor relay."""
        tor_relay = Relay("wss://pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd.onion")
        socks5_url = "socks5://127.0.0.1:9050"
        client = Client(tor_relay, socks5_proxy_url=socks5_url)
        connector = client.connector()
        await connector.close()
        # Should return ProxyConnector for Tor
        from aiohttp_socks import ProxyConnector

        assert isinstance(connector, ProxyConnector)

    def test_client_connector_tor_missing_proxy(self):
        """Test connector creation for Tor relay without proxy configured."""
        tor_relay = Relay("wss://pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd.onion")
        # Create client without proxy (should not raise here)
        client = Client.__new__(Client)  # Bypass validation
        client.relay = tor_relay
        client.socks5_proxy_url = None

        from nostr_tools import RelayConnectionError

        with pytest.raises(RelayConnectionError, match="SOCKS5 proxy URL required"):
            client.connector()

    async def test_client_session_creation(self, sample_relay):
        """Test session creation with custom connector."""
        client = Client(sample_relay)
        connector = client.connector()
        session = client.session(connector)
        await session.close()
        from aiohttp import ClientSession

        assert isinstance(session, ClientSession)

    async def test_client_session_auto_connector(self, sample_relay):
        """Test session creation with auto-detected connector."""
        client = Client(sample_relay)
        session = client.session()
        await session.close()
        from aiohttp import ClientSession

        assert isinstance(session, ClientSession)

    def test_client_active_subscriptions_empty(self, sample_relay):
        """Test active subscriptions when none exist."""
        client = Client(sample_relay)
        assert client.active_subscriptions == []

    def test_client_active_subscriptions_with_data(self, sample_relay):
        """Test active subscriptions with mock data."""
        client = Client(sample_relay)
        # Manually add subscription data for testing
        client._subscriptions = {
            "sub1": {"filter": None, "active": True},
            "sub2": {"filter": None, "active": False},
            "sub3": {"filter": None, "active": True},
        }

        active_subs = client.active_subscriptions
        assert len(active_subs) == 2
        assert "sub1" in active_subs
        assert "sub3" in active_subs
        assert "sub2" not in active_subs


if __name__ == "__main__":
    pytest.main([__file__])
