"""
Additional unit tests to boost code coverage to >95%.

This module provides focused tests for previously uncovered code paths.
"""

import time
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector

from nostr_tools import Client
from nostr_tools import Event
from nostr_tools import Filter
from nostr_tools import Relay
from nostr_tools import RelayMetadata
from nostr_tools import generate_event
from nostr_tools.actions.actions import check_connectivity
from nostr_tools.actions.actions import check_readability
from nostr_tools.actions.actions import check_writability
from nostr_tools.actions.actions import fetch_nip11
from nostr_tools.actions.actions import fetch_nip66
from nostr_tools.actions.actions import stream_events

# ============================================================================
# Client Coverage Tests
# ============================================================================


@pytest.mark.unit
class TestClientCoverage:
    """Tests to improve Client coverage."""

    @pytest.mark.asyncio
    async def test_client_connector_tcp(self, valid_relay: Relay) -> None:
        """Test TCP connector for clearnet relay."""
        from aiohttp import TCPConnector

        client = Client(relay=valid_relay)
        connector = client.connector()
        assert isinstance(connector, TCPConnector)
        await connector.close()

    @pytest.mark.asyncio
    async def test_client_connector_socks5(self) -> None:
        """Test SOCKS5 connector for Tor relay."""
        # Use a valid v3 onion address (exactly 56 chars, a-z2-7 only)
        tor_relay = Relay(
            url="wss://abcdefghijklmnopqrstuvwxyz234567abcdefghijklmnopqrstuvwx.onion"
        )
        client = Client(relay=tor_relay, socks5_proxy_url="socks5://localhost:9050")
        connector = client.connector()
        assert isinstance(connector, ProxyConnector)
        await connector.close()

    @pytest.mark.asyncio
    async def test_client_session_creation(self, valid_relay: Relay) -> None:
        """Test session creation."""
        client = Client(relay=valid_relay)
        session = client.session()
        assert isinstance(session, ClientSession)
        await session.close()

    @pytest.mark.asyncio
    async def test_client_session_with_custom_connector(self, valid_relay: Relay) -> None:
        """Test session with custom connector."""
        from aiohttp import TCPConnector

        client = Client(relay=valid_relay)
        connector = TCPConnector()
        session = client.session(connector)
        assert isinstance(session, ClientSession)
        await session.close()
        await connector.close()

    def test_client_is_connected_false(self, valid_relay: Relay) -> None:
        """Test is_connected when not connected."""
        client = Client(relay=valid_relay)
        assert client.is_connected is False

    def test_client_active_subscriptions_empty(self, valid_relay: Relay) -> None:
        """Test active_subscriptions when empty."""
        client = Client(relay=valid_relay)
        assert client.active_subscriptions == []

    def test_client_active_subscriptions_with_data(self, valid_relay: Relay) -> None:
        """Test active_subscriptions with subscriptions."""
        client = Client(relay=valid_relay)
        client._subscriptions = {"sub1": {"active": True}, "sub2": {"active": False}}
        active = client.active_subscriptions
        # Just check that it returns a list
        assert isinstance(active, list)

    @pytest.mark.asyncio
    async def test_client_disconnect_not_connected(self, valid_relay: Relay) -> None:
        """Test disconnect when not connected."""
        client = Client(relay=valid_relay)
        await client.disconnect()  # Should not raise

    @pytest.mark.asyncio
    async def test_client_unsubscribe_nonexistent(self, valid_relay: Relay) -> None:
        """Test unsubscribe from nonexistent subscription."""
        client = Client(relay=valid_relay)
        client._ws = AsyncMock()
        client._ws.closed = False
        await client.unsubscribe("nonexistent")  # Should not raise

    @pytest.mark.asyncio
    async def test_client_subscribe_auto_id(self, valid_filter: Filter) -> None:
        """Test subscribe generates subscription ID."""
        relay = Relay(url="wss://relay.example.com")
        client = Client(relay=relay)
        client._ws = AsyncMock()
        client._ws.closed = False
        client._ws.send_str = AsyncMock()

        sub_id = await client.subscribe(valid_filter)
        assert sub_id is not None
        assert len(sub_id) > 0


# ============================================================================
# Actions Coverage Tests
# ============================================================================


@pytest.mark.unit
class TestActionsCoverage:
    """Tests to improve Actions coverage."""

    @pytest.mark.asyncio
    async def test_check_connectivity_failure(self) -> None:
        """Test connectivity check failure."""
        relay = Relay(url="wss://relay.example.com")
        client = Client(relay=relay)

        # Mock connect to fail
        with patch.object(client, "connect", side_effect=Exception("Connection failed")):
            rtt, connected = await check_connectivity(client)

        assert connected is False
        assert rtt is None

    @pytest.mark.asyncio
    async def test_check_readability_failure(self) -> None:
        """Test readability check failure."""
        relay = Relay(url="wss://relay.example.com")
        client = Client(relay=relay)
        client._ws = AsyncMock()
        client._ws.closed = False

        # Mock subscribe to fail
        with patch.object(client, "subscribe", side_effect=Exception("Subscribe failed")):
            rtt, readable = await check_readability(client)

        assert readable is False
        assert rtt is None

    @pytest.mark.asyncio
    async def test_check_writability_failure(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test writability check failure."""
        relay = Relay(url="wss://relay.example.com")
        client = Client(relay=relay)
        client._ws = AsyncMock()
        client._ws.closed = False

        # Mock publish to fail
        with patch.object(client, "publish", side_effect=Exception("Publish failed")):
            rtt, writable = await check_writability(client, valid_private_key, valid_public_key)

        assert writable is False
        assert rtt is None

    @pytest.mark.asyncio
    async def test_fetch_nip11_http_fallback(self) -> None:
        """Test NIP-11 fetch with HTTP fallback."""
        relay = Relay(url="wss://relay.example.com")
        client = Client(relay=relay)

        # Mock to return None (simulating both protocols failing)
        mock_response = AsyncMock()
        mock_response.status = 404

        mock_session = AsyncMock()
        mock_session.get = MagicMock()
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.get.return_value.__aexit__ = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        with patch.object(client, "session", return_value=mock_session):
            nip11 = await fetch_nip11(client)

        # Should return None when both fail
        assert nip11 is None

    @pytest.mark.asyncio
    async def test_fetch_nip66_not_openable(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test NIP-66 when relay is not openable."""
        relay = Relay(url="wss://relay.example.com")
        client = Client(relay=relay)

        # Mock connectivity to return False
        with patch("nostr_tools.actions.actions.check_connectivity", return_value=(None, False)):
            nip66 = await fetch_nip66(client, valid_private_key, valid_public_key)

        assert nip66 is None

    @pytest.mark.asyncio
    async def test_stream_events_yields_events(
        self, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test stream_events yields events."""
        relay = Relay(url="wss://relay.example.com")
        client = Client(relay=relay)
        filter = Filter(kinds=[1])

        # Create a test event
        event_dict = generate_event(valid_private_key, valid_public_key, 1, [], "test")
        event = Event.from_dict(event_dict)

        # Mock listen_events to yield test event
        async def mock_listen_events(sub_id: str):
            yield ["EVENT", sub_id, event.to_dict()]

        client._ws = AsyncMock()
        client._ws.closed = False

        with patch.object(client, "listen_events", mock_listen_events):
            events = []
            async for evt in stream_events(client, filter):
                events.append(evt)
                break  # Only get first event

        assert len(events) == 1
        assert events[0].id == event.id


# ============================================================================
# RelayMetadata Coverage Tests
# ============================================================================


@pytest.mark.unit
class TestRelayMetadataCoverage:
    """Tests to improve RelayMetadata coverage."""

    def test_nip11_with_none_values(self) -> None:
        """Test Nip11 with all None values."""
        nip11 = RelayMetadata.Nip11()
        assert nip11.name is None
        assert nip11.description is None
        assert nip11.is_valid is True

    def test_nip66_with_false_flags(self) -> None:
        """Test Nip66 with all flags False."""
        nip66 = RelayMetadata.Nip66(
            openable=False,
            readable=False,
            writable=False,
        )
        assert nip66.openable is False
        assert nip66.rtt_open is None
        assert nip66.rtt_read is None
        assert nip66.rtt_write is None

    def test_relay_metadata_minimal(self, valid_relay: Relay) -> None:
        """Test RelayMetadata with minimal data."""
        metadata = RelayMetadata(
            relay=valid_relay,
            generated_at=int(time.time()),
        )
        assert metadata.nip11 is None
        assert metadata.nip66 is None
        assert metadata.is_valid is True


# ============================================================================
# Utils Coverage Tests
# ============================================================================


@pytest.mark.unit
class TestUtilsCoverage:
    """Tests to improve utils coverage."""

    def test_to_bech32_with_prefix_variations(self) -> None:
        """Test to_bech32 with different prefixes."""
        from nostr_tools import to_bech32

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
        from nostr_tools import find_ws_urls

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
        from nostr_tools import sanitize

        # Test with empty structures
        assert sanitize([]) == []
        assert sanitize({}) == {}
        assert sanitize("") == ""

        # Test with nested null bytes
        nested = {"a": ["test\x00", {"b": "value\x00"}]}
        result = sanitize(nested)
        assert "\x00" not in str(result)
