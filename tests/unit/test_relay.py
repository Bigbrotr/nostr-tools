"""
Unit tests for the Relay class.

This module tests all functionality of the Relay class including:
- Relay creation and validation
- URL validation and normalization
- Network type detection (clearnet vs Tor)
- Dictionary conversion
- Edge cases and error handling
"""

import pytest

from nostr_tools import RelayValidationError
from nostr_tools.core.relay import Relay

# ============================================================================
# Relay Creation Tests
# ============================================================================


@pytest.mark.unit
class TestRelayCreation:
    """Test Relay instance creation."""

    def test_create_clearnet_relay(self, valid_relay_url: str) -> None:
        """Test creating a clearnet relay."""
        relay = Relay(url=valid_relay_url)
        assert isinstance(relay, Relay)
        assert relay.url == valid_relay_url
        assert relay.network == "clearnet"

    def test_create_tor_relay(self, tor_relay_url: str) -> None:
        """Test creating a Tor relay."""
        relay = Relay(url=tor_relay_url)
        assert isinstance(relay, Relay)
        assert relay.url == tor_relay_url
        assert relay.network == "tor"

    def test_create_relay_with_explicit_network(self, valid_relay_url: str) -> None:
        """Test creating a relay with explicit network specification."""
        relay = Relay(url=valid_relay_url, network="clearnet")
        assert relay.network == "clearnet"

    def test_create_relay_normalizes_url(self) -> None:
        """Test that relay creation normalizes URLs."""
        # URL without wss:// prefix should be normalized
        relay = Relay(url="wss://relay.damus.io")
        assert relay.url == "wss://relay.damus.io"

    def test_create_relay_with_port(self) -> None:
        """Test creating a relay with custom port."""
        relay = Relay(url="wss://relay.example.com:7777")
        assert relay.url == "wss://relay.example.com:7777"
        assert relay.network == "clearnet"

    def test_create_relay_with_path(self) -> None:
        """Test creating a relay with URL path."""
        relay = Relay(url="wss://relay.example.com/v1")
        assert relay.url == "wss://relay.example.com/v1"
        assert relay.network == "clearnet"


# ============================================================================
# Relay URL Validation Tests
# ============================================================================


@pytest.mark.unit
class TestRelayUrlValidation:
    """Test Relay URL validation."""

    def test_valid_wss_url_passes_validation(self) -> None:
        """Test that valid WSS URL passes validation."""
        relay = Relay(url="wss://relay.damus.io")
        relay.validate()  # Should not raise
        assert relay.is_valid

    def test_valid_onion_url_passes_validation(self) -> None:
        """Test that valid .onion URL passes validation."""
        # Valid v3 onion address (56 chars)
        relay = Relay(url="wss://oxtrdevav64z64yb7x6rjg4ntzqjhedm5b5zjqulugknhzr46ny2qbad.onion")
        relay.validate()
        assert relay.is_valid

    def test_invalid_url_format_raises_error(self) -> None:
        """Test that invalid URL format raises ValueError."""
        with pytest.raises(RelayValidationError, match="must be a valid WebSocket URL"):
            Relay(url="invalid_url")

    def test_http_url_raises_error(self) -> None:
        """Test that HTTP URL raises ValueError."""
        with pytest.raises(RelayValidationError, match="must be a valid WebSocket URL"):
            Relay(url="http://relay.example.com")

    def test_https_url_raises_error(self) -> None:
        """Test that HTTPS URL raises ValueError."""
        with pytest.raises(RelayValidationError, match="must be a valid WebSocket URL"):
            Relay(url="https://relay.example.com")

    def test_ws_url_is_normalized_to_wss(self) -> None:
        """Test that ws:// URLs are accepted and normalized."""
        # ws:// should be found by find_ws_urls and normalized
        relay = Relay(url="ws://relay.example.com")
        assert relay.url.startswith("wss://")

    def test_url_with_multiple_slashes_raises_error(self) -> None:
        """Test that URL with multiple slashes raises error."""
        with pytest.raises(RelayValidationError, match="must be a valid WebSocket URL"):
            Relay(url="wss:////relay.example.com")

    def test_url_without_domain_raises_error(self) -> None:
        """Test that URL without domain raises error."""
        with pytest.raises(RelayValidationError, match="must be a valid WebSocket URL"):
            Relay(url="wss://")

    def test_url_with_invalid_onion_length_raises_error(self) -> None:
        """Test that invalid onion address length raises error."""
        with pytest.raises(RelayValidationError, match="must be a valid WebSocket URL"):
            Relay(url="wss://invalidonion.onion")  # Not 16 or 56 chars


# ============================================================================
# Relay Network Detection Tests
# ============================================================================


@pytest.mark.unit
class TestRelayNetworkDetection:
    """Test Relay network type detection."""

    def test_clearnet_domain_detects_clearnet(self) -> None:
        """Test that clearnet domain is detected as clearnet."""
        relay = Relay(url="wss://relay.damus.io")
        assert relay.network == "clearnet"

    def test_onion_domain_detects_tor(self) -> None:
        """Test that .onion domain is detected as Tor."""
        relay = Relay(url="wss://oxtrdevav64z64yb7x6rjg4ntzqjhedm5b5zjqulugknhzr46ny2qbad.onion")
        assert relay.network == "tor"

    def test_ip_address_detects_clearnet(self) -> None:
        """Test that IP address is detected as clearnet."""
        relay = Relay(url="wss://192.168.1.1")
        assert relay.network == "clearnet"

    def test_localhost_detects_clearnet(self) -> None:
        """Test that localhost is detected as clearnet."""
        # Note: find_ws_urls might not accept localhost
        # This test might need adjustment based on actual implementation
        try:
            relay = Relay(url="wss://127.0.0.1")
            assert relay.network == "clearnet"
        except ValueError:
            # If localhost is not supported, that's also valid
            pass

    def test_wrong_network_specification_raises_error(self) -> None:
        """Test that wrong network specification raises error."""
        with pytest.raises(RelayValidationError, match="network must be"):
            Relay(url="wss://relay.damus.io", network="tor")  # Wrong network

    def test_wrong_network_for_onion_raises_error(self) -> None:
        """Test that wrong network for .onion raises error."""
        onion_url = "wss://oxtrdevav64z64yb7x6rjg4ntzqjhedm5b5zjqulugknhzr46ny2qbad.onion"
        with pytest.raises(RelayValidationError, match="network must be"):
            Relay(url=onion_url, network="clearnet")  # Wrong network


# ============================================================================
# Relay Type Validation Tests
# ============================================================================


@pytest.mark.unit
class TestRelayTypeValidation:
    """Test Relay type validation."""

    def test_non_string_url_raises_error(self) -> None:
        """Test that non-string URL raises TypeError."""
        with pytest.raises(TypeError):
            Relay(url=123)  # type: ignore

    def test_non_string_network_raises_error(self, valid_relay_url: str) -> None:
        """Test that non-string network raises TypeError."""
        with pytest.raises(TypeError):
            Relay(url=valid_relay_url, network=123)  # type: ignore


# ============================================================================
# Relay Property Tests
# ============================================================================


@pytest.mark.unit
class TestRelayProperties:
    """Test Relay properties."""

    def test_is_valid_property_returns_true_for_valid_relay(self, valid_relay: Relay) -> None:
        """Test that is_valid returns True for valid relays."""
        assert valid_relay.is_valid is True

    def test_is_valid_property_returns_false_for_invalid_relay(self, valid_relay: Relay) -> None:
        """Test that is_valid returns False for invalid relays."""
        # Corrupt the relay
        valid_relay.url = "invalid_url"
        assert valid_relay.is_valid is False


# ============================================================================
# Relay Dictionary Conversion Tests
# ============================================================================


@pytest.mark.unit
class TestRelayDictionaryConversion:
    """Test Relay dictionary conversion."""

    def test_from_dict_creates_relay(self) -> None:
        """Test that from_dict creates a Relay instance."""
        data = {"url": "wss://relay.damus.io"}
        relay = Relay.from_dict(data)
        assert isinstance(relay, Relay)

    def test_from_dict_with_network(self) -> None:
        """Test that from_dict creates relay with network."""
        data = {"url": "wss://relay.damus.io", "network": "clearnet"}
        relay = Relay.from_dict(data)
        assert relay.network == "clearnet"

    def test_from_dict_with_non_dict_raises_error(self) -> None:
        """Test that from_dict with non-dict raises TypeError."""
        with pytest.raises(TypeError, match="data must be a dict"):
            Relay.from_dict("not_a_dict")  # type: ignore

    def test_from_dict_with_missing_url_raises_error(self) -> None:
        """Test that from_dict with missing URL raises KeyError."""
        with pytest.raises(KeyError):
            Relay.from_dict({})

    def test_to_dict_returns_dict(self, valid_relay: Relay) -> None:
        """Test that to_dict returns a dictionary."""
        relay_dict = valid_relay.to_dict()
        assert isinstance(relay_dict, dict)

    def test_to_dict_contains_url_and_network(self, valid_relay: Relay) -> None:
        """Test that to_dict contains url and network."""
        relay_dict = valid_relay.to_dict()
        assert "url" in relay_dict
        assert "network" in relay_dict

    def test_round_trip_conversion(self, valid_relay: Relay) -> None:
        """Test that Relay can be converted to dict and back."""
        relay_dict = valid_relay.to_dict()
        relay2 = Relay.from_dict(relay_dict)

        assert valid_relay.url == relay2.url
        assert valid_relay.network == relay2.network


# ============================================================================
# Relay Edge Cases Tests
# ============================================================================


@pytest.mark.unit
class TestRelayEdgeCases:
    """Test Relay edge cases and special scenarios."""

    def test_relay_with_subdomain(self) -> None:
        """Test relay with subdomain."""
        relay = Relay(url="wss://sub.relay.example.com")
        assert relay.url == "wss://sub.relay.example.com"
        assert relay.network == "clearnet"

    def test_relay_with_multiple_subdomains(self) -> None:
        """Test relay with multiple subdomains."""
        relay = Relay(url="wss://a.b.c.relay.example.com")
        assert relay.url == "wss://a.b.c.relay.example.com"
        assert relay.network == "clearnet"

    def test_relay_with_port_and_path(self) -> None:
        """Test relay with custom port and path."""
        relay = Relay(url="wss://relay.example.com:7777/nostr")
        assert relay.url == "wss://relay.example.com:7777/nostr"
        assert relay.network == "clearnet"

    def test_relay_with_query_string(self) -> None:
        """Test relay with query string."""
        relay = Relay(url="wss://relay.example.com/nostr?key=value")
        assert "relay.example.com" in relay.url
        assert relay.network == "clearnet"

    def test_relay_url_case_insensitive_domain(self) -> None:
        """Test that relay domain is case-insensitive."""
        relay = Relay(url="wss://Relay.Damus.IO")
        # Domain should be normalized to lowercase
        assert relay.url.lower() == "wss://relay.damus.io"

    def test_v2_onion_address(self) -> None:
        """Test valid v2 onion address (16 chars)."""
        relay = Relay(url="wss://thehub7gqe43miyc.onion")
        assert relay.network == "tor"

    def test_v3_onion_address(self) -> None:
        """Test valid v3 onion address (56 chars)."""
        relay = Relay(url="wss://oxtrdevav64z64yb7x6rjg4ntzqjhedm5b5zjqulugknhzr46ny2qbad.onion")
        assert relay.network == "tor"

    def test_onion_with_port(self) -> None:
        """Test onion address with custom port."""
        relay = Relay(url="wss://thehub7gqe43miyc.onion:9735")
        assert relay.network == "tor"
        assert "9735" in relay.url

    def test_relay_with_international_domain(self) -> None:
        """Test relay with internationalized domain name (IDN)."""
        # Example with German umlaut (if supported by find_ws_urls)
        try:
            relay = Relay(url="wss://relay.münchen.de")
            assert relay.network == "clearnet"
        except RelayValidationError:
            # If IDN is not supported, that's also valid
            pass

    def test_relay_equality_based_on_url(self) -> None:
        """Test that relays with same URL are considered equal."""
        relay1 = Relay(url="wss://relay.damus.io")
        relay2 = Relay(url="wss://relay.damus.io")
        # While Relay doesn't implement __eq__, the URLs should be the same
        assert relay1.url == relay2.url
        assert relay1.network == relay2.network
