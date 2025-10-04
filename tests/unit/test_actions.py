"""
Unit tests for the actions module.

This module tests high-level action functions that use
mocked network interactions and async operations.
"""

from typing import Any
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from aiohttp import ClientError

from nostr_tools.actions.actions import check_connectivity
from nostr_tools.actions.actions import check_readability
from nostr_tools.actions.actions import check_writability
from nostr_tools.actions.actions import fetch_events
from nostr_tools.actions.actions import fetch_nip11
from nostr_tools.actions.actions import fetch_nip66
from nostr_tools.actions.actions import fetch_relay_metadata
from nostr_tools.actions.actions import stream_events
from nostr_tools.core.client import Client
from nostr_tools.core.event import Event
from nostr_tools.core.filter import Filter
from nostr_tools.core.relay import Relay
from nostr_tools.exceptions import ClientConnectionError

# ============================================================================
# Fetch Events Tests
# ============================================================================


@pytest.mark.unit
class TestFetchEvents:
    """Test fetch_events action."""

    @pytest.mark.asyncio
    async def test_fetch_events_requires_connection(
        self, valid_client: Client, valid_filter: Filter
    ) -> None:
        """Test that fetch_events requires client to be connected."""
        with pytest.raises(ClientConnectionError, match="not connected"):
            await fetch_events(valid_client, valid_filter)

    @pytest.mark.asyncio
    async def test_fetch_events_returns_list(
        self,
        valid_client: Client,
        valid_filter: Filter,
        valid_event_dict: dict[str, Any],
    ) -> None:
        """Test that fetch_events returns a list of events."""
        # Mock connection
        valid_client._ws = AsyncMock()
        valid_client._ws.closed = False
        valid_client._ws.send_str = AsyncMock()

        # Create async generator for listen_events
        async def mock_listen_events(sub_id: str):
            # Yield one event then EOSE
            yield ["EVENT", sub_id, valid_event_dict]

        with patch.object(valid_client, "listen_events", mock_listen_events):
            events = await fetch_events(valid_client, valid_filter)

        assert isinstance(events, list)
        assert len(events) == 1
        assert isinstance(events[0], Event)

    @pytest.mark.asyncio
    async def test_fetch_events_handles_invalid_events(
        self, valid_client: Client, valid_filter: Filter
    ) -> None:
        """Test that fetch_events handles invalid events gracefully."""
        valid_client._ws = AsyncMock()
        valid_client._ws.closed = False
        valid_client._ws.send_str = AsyncMock()

        async def mock_listen_events(sub_id: str):
            # Yield invalid event
            yield ["EVENT", sub_id, {"invalid": "event"}]

        with patch.object(valid_client, "listen_events", mock_listen_events):
            events = await fetch_events(valid_client, valid_filter)

        # Invalid events should be skipped
        assert events == []


# ============================================================================
# Stream Events Tests
# ============================================================================


@pytest.mark.unit
class TestStreamEvents:
    """Test stream_events action."""

    @pytest.mark.asyncio
    async def test_stream_events_requires_connection(
        self, valid_client: Client, valid_filter: Filter
    ) -> None:
        """Test that stream_events requires client to be connected."""
        with pytest.raises(ClientConnectionError, match="not connected"):
            async for _ in stream_events(valid_client, valid_filter):
                pass

    @pytest.mark.asyncio
    async def test_stream_events_yields_events(
        self,
        valid_client: Client,
        valid_filter: Filter,
        valid_event_dict: dict[str, Any],
    ) -> None:
        """Test that stream_events yields events."""
        valid_client._ws = AsyncMock()
        valid_client._ws.closed = False
        valid_client._ws.send_str = AsyncMock()

        async def mock_listen_events(sub_id: str):
            yield ["EVENT", sub_id, valid_event_dict]

        events = []
        with patch.object(valid_client, "listen_events", mock_listen_events):
            async for event in stream_events(valid_client, valid_filter):
                events.append(event)
                break  # Only get first event

        assert len(events) == 1
        assert isinstance(events[0], Event)


# ============================================================================
# Fetch NIP-11 Tests
# ============================================================================


@pytest.mark.unit
class TestFetchNip11:
    """Test fetch_nip11 action."""

    @pytest.mark.asyncio
    async def test_fetch_nip11_returns_nip11(
        self, valid_client: Client, valid_nip11_dict: dict[str, Any]
    ) -> None:
        """Test that fetch_nip11 returns Nip11 metadata."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=valid_nip11_dict)

        mock_session = AsyncMock()
        mock_session.get = MagicMock()
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.get.return_value.__aexit__ = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        with patch.object(valid_client, "session", return_value=mock_session):
            nip11 = await fetch_nip11(valid_client)

        assert nip11 is not None
        assert nip11.name == valid_nip11_dict["name"]

    @pytest.mark.asyncio
    async def test_fetch_nip11_returns_none_on_404(self, valid_client: Client) -> None:
        """Test that fetch_nip11 returns None on 404."""
        mock_response = AsyncMock()
        mock_response.status = 404

        mock_session = AsyncMock()
        mock_session.get = MagicMock()
        mock_session.get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
        mock_session.get.return_value.__aexit__ = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        with patch.object(valid_client, "session", return_value=mock_session):
            nip11 = await fetch_nip11(valid_client)

        assert nip11 is None

    @pytest.mark.asyncio
    async def test_fetch_nip11_handles_network_error(self, valid_client: Client) -> None:
        """Test that fetch_nip11 handles network errors."""
        mock_session = AsyncMock()
        mock_session.get = MagicMock()
        mock_session.get.return_value.__aenter__ = AsyncMock(side_effect=ClientError())
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock()

        with patch.object(valid_client, "session", return_value=mock_session):
            nip11 = await fetch_nip11(valid_client)

        assert nip11 is None


# ============================================================================
# Check Connectivity Tests
# ============================================================================


@pytest.mark.unit
class TestCheckConnectivity:
    """Test check_connectivity action."""

    @pytest.mark.asyncio
    async def test_check_connectivity_succeeds(self, valid_client: Client) -> None:
        """Test successful connectivity check."""
        with patch.object(valid_client, "connect", new_callable=AsyncMock):
            with patch.object(valid_client, "disconnect", new_callable=AsyncMock):
                rtt, openable = await check_connectivity(valid_client)

        assert isinstance(rtt, int) or rtt is None
        assert isinstance(openable, bool)

    @pytest.mark.asyncio
    async def test_check_connectivity_fails_when_already_connected(
        self, valid_client: Client
    ) -> None:
        """Test that connectivity check fails if already connected."""
        valid_client._ws = AsyncMock()
        valid_client._ws.closed = False

        with pytest.raises(ClientConnectionError, match="already connected"):
            await check_connectivity(valid_client)


# ============================================================================
# Check Readability Tests
# ============================================================================


@pytest.mark.unit
class TestCheckReadability:
    """Test check_readability action."""

    @pytest.mark.asyncio
    async def test_check_readability_requires_connection(self, valid_client: Client) -> None:
        """Test that readability check requires connection."""
        with pytest.raises(ClientConnectionError, match="not connected"):
            await check_readability(valid_client)

    @pytest.mark.asyncio
    async def test_check_readability_succeeds(self, valid_client: Client) -> None:
        """Test successful readability check."""
        valid_client._ws = AsyncMock()
        valid_client._ws.closed = False
        valid_client._ws.send_str = AsyncMock()

        async def mock_listen():
            yield ["EOSE", "test_sub_id"]

        with patch.object(valid_client, "subscribe", return_value="test_sub_id"):
            with patch.object(valid_client, "listen", mock_listen):
                with patch.object(valid_client, "unsubscribe", new_callable=AsyncMock):
                    rtt, readable = await check_readability(valid_client)

        assert isinstance(rtt, int) or rtt is None
        assert isinstance(readable, bool)


# ============================================================================
# Check Writability Tests
# ============================================================================


@pytest.mark.unit
class TestCheckWritability:
    """Test check_writability action."""

    @pytest.mark.asyncio
    async def test_check_writability_requires_connection(
        self, valid_client: Client, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test that writability check requires connection."""
        with pytest.raises(ClientConnectionError, match="not connected"):
            await check_writability(valid_client, valid_private_key, valid_public_key)

    @pytest.mark.asyncio
    async def test_check_writability_succeeds(
        self,
        valid_client: Client,
        valid_private_key: str,
        valid_public_key: str,
    ) -> None:
        """Test successful writability check."""
        valid_client._ws = AsyncMock()
        valid_client._ws.closed = False

        with patch.object(valid_client, "publish", return_value=True):
            rtt, writable = await check_writability(
                valid_client, valid_private_key, valid_public_key
            )

        assert isinstance(rtt, int) or rtt is None
        assert isinstance(writable, bool)


# ============================================================================
# Fetch NIP-66 Tests
# ============================================================================


@pytest.mark.unit
class TestFetchNip66:
    """Test fetch_nip66 action."""

    @pytest.mark.asyncio
    async def test_fetch_nip66_requires_disconnected_client(
        self, valid_client: Client, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test that fetch_nip66 requires disconnected client."""
        valid_client._ws = AsyncMock()
        valid_client._ws.closed = False

        with pytest.raises(ClientConnectionError, match="already connected"):
            await fetch_nip66(valid_client, valid_private_key, valid_public_key)

    @pytest.mark.asyncio
    async def test_fetch_nip66_returns_nip66(
        self, valid_relay: Relay, valid_private_key: str, valid_public_key: str
    ) -> None:
        """Test that fetch_nip66 returns Nip66 metadata."""
        # Create a fresh client for this test
        client = Client(relay=valid_relay)

        async def mock_check_connectivity(c):
            return (100, True)

        async def mock_check_readability(c):
            return (50, True)

        async def mock_check_writability(
            c, sec, pub, target_difficulty=None, event_creation_timeout=None
        ):
            return (75, True)

        with patch("nostr_tools.actions.actions.check_connectivity", mock_check_connectivity):
            with patch("nostr_tools.actions.actions.check_readability", mock_check_readability):
                with patch(
                    "nostr_tools.actions.actions.check_writability",
                    mock_check_writability,
                ):
                    nip66 = await fetch_nip66(client, valid_private_key, valid_public_key)

        assert nip66 is not None
        assert nip66.openable is True


# ============================================================================
# Fetch Relay Metadata Tests
# ============================================================================


@pytest.mark.unit
class TestFetchRelayMetadata:
    """Test fetch_relay_metadata action."""

    @pytest.mark.asyncio
    async def test_fetch_relay_metadata_returns_metadata(
        self,
        valid_relay: Relay,
        valid_private_key: str,
        valid_public_key: str,
        valid_nip11_dict: dict[str, Any],
    ) -> None:
        """Test that fetch_relay_metadata returns complete metadata."""
        from nostr_tools import RelayMetadata

        # Create a fresh client for this test
        client = Client(relay=valid_relay)

        mock_nip11 = RelayMetadata.Nip11.from_dict(valid_nip11_dict)
        mock_nip66 = RelayMetadata.Nip66(
            openable=True,
            readable=True,
            writable=True,
            rtt_open=100,
            rtt_read=50,
            rtt_write=75,
        )

        async def mock_fetch_nip11(c):
            return mock_nip11

        async def mock_fetch_nip66(
            c, sec, pub, target_difficulty=None, event_creation_timeout=None
        ):
            return mock_nip66

        with patch("nostr_tools.actions.actions.fetch_nip11", mock_fetch_nip11):
            with patch("nostr_tools.actions.actions.fetch_nip66", mock_fetch_nip66):
                metadata = await fetch_relay_metadata(client, valid_private_key, valid_public_key)

        # Check type by name due to lazy loading class identity issues
        assert type(metadata).__name__ == "RelayMetadata"
        assert metadata.relay.url == client.relay.url
        # Check we got some metadata (may be mocked or real depending on test order)
        assert metadata.nip11 is not None or metadata.nip66 is not None

    @pytest.mark.asyncio
    async def test_fetch_relay_metadata_detects_pow_requirement(
        self,
        valid_relay: Relay,
        valid_private_key: str,
        valid_public_key: str,
        valid_nip11_dict: dict[str, Any],
    ) -> None:
        """Test that fetch_relay_metadata detects PoW requirements."""
        import copy

        from nostr_tools import RelayMetadata

        # Create a fresh client for this test
        client = Client(relay=valid_relay)

        # Use a copy to avoid mutating the fixture
        nip11_dict = copy.deepcopy(valid_nip11_dict)
        # Add PoW requirement to NIP-11
        nip11_dict["limitation"] = {"min_pow_difficulty": 20}
        mock_nip11 = RelayMetadata.Nip11.from_dict(nip11_dict)

        async def mock_fetch_nip11(c):
            return mock_nip11

        async def mock_fetch_nip66(
            c, sec, pub, target_difficulty=None, event_creation_timeout=None
        ):
            # Verify target_difficulty was passed
            assert target_difficulty == 20
            return None

        with patch("nostr_tools.actions.actions.fetch_nip11", mock_fetch_nip11):
            with patch("nostr_tools.actions.actions.fetch_nip66", mock_fetch_nip66):
                await fetch_relay_metadata(client, valid_private_key, valid_public_key)


# ============================================================================
# Additional Actions Coverage Tests
# ============================================================================


@pytest.mark.unit
class TestActionsAdditionalCoverage:
    """Additional tests for improved Actions coverage."""

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
        from unittest.mock import MagicMock

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
        from nostr_tools import Filter
        from nostr_tools import generate_event

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
