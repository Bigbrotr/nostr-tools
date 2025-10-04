"""
Unit tests for the Client class.

This module tests all functionality of the Client class including:
- Client creation and validation
- WebSocket connection management
- Event subscription and publishing
- Message sending and receiving
- Error handling
- Async context management
"""

from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest

from nostr_tools.core.client import Client
from nostr_tools.core.event import Event
from nostr_tools.core.filter import Filter
from nostr_tools.core.relay import Relay
from nostr_tools.exceptions import ClientValidationError
from nostr_tools.exceptions import ClientConnectionError
from nostr_tools.exceptions import ClientSubscriptionError

# ============================================================================
# Client Creation Tests
# ============================================================================


@pytest.mark.unit
class TestClientCreation:
    """Test Client instance creation."""

    def test_create_clearnet_client(self, valid_relay: Relay) -> None:
        """Test creating a client for clearnet relay."""
        client = Client(relay=valid_relay, timeout=10)
        assert isinstance(client, Client)
        assert client.relay == valid_relay
        assert client.timeout == 10
        assert client.socks5_proxy_url is None

    def test_create_tor_client(self, tor_relay: Relay, socks5_proxy_url: str) -> None:
        """Test creating a client for Tor relay."""
        client = Client(relay=tor_relay, timeout=10,
                        socks5_proxy_url=socks5_proxy_url)
        assert isinstance(client, Client)
        assert client.relay == tor_relay
        assert client.socks5_proxy_url == socks5_proxy_url

    def test_create_client_with_default_timeout(self, valid_relay: Relay) -> None:
        """Test creating a client with default timeout."""
        client = Client(relay=valid_relay)
        assert client.timeout == 10

    def test_create_client_with_no_timeout(self, valid_relay: Relay) -> None:
        """Test creating a client with no timeout."""
        client = Client(relay=valid_relay, timeout=None)
        assert client.timeout is None


# ============================================================================
# Client Validation Tests
# ============================================================================


@pytest.mark.unit
class TestClientValidation:
    """Test Client validation logic."""

    def test_valid_client_passes_validation(self, valid_client: Client) -> None:
        """Test that a valid client passes validation."""
        valid_client.validate()  # Should not raise
        assert valid_client.is_valid

    def test_negative_timeout_raises_error(self, valid_relay: Relay) -> None:
        """Test that negative timeout raises ClientValidationError."""
        with pytest.raises(ClientValidationError, match="timeout must be non-negative"):
            Client(relay=valid_relay, timeout=-1)

    def test_tor_relay_without_proxy_raises_error(self, tor_relay: Relay) -> None:
        """Test that Tor relay without proxy URL raises ClientValidationError."""
        with pytest.raises(ClientValidationError, match="socks5_proxy_url is required for Tor relays"):
            Client(relay=tor_relay)

    def test_tor_relay_with_proxy_is_valid(self, tor_relay: Relay, socks5_proxy_url: str) -> None:
        """Test that Tor relay with proxy URL is valid."""
        client = Client(relay=tor_relay, socks5_proxy_url=socks5_proxy_url)
        assert client.is_valid


# ============================================================================
# Client Type Validation Tests
# ============================================================================


@pytest.mark.unit
class TestClientTypeValidation:
    """Test Client type validation."""

    def test_non_relay_relay_raises_error(self) -> None:
        """Test that non-Relay relay raises ClientValidationError."""
        with pytest.raises(ClientValidationError):
            Client(relay="not_a_relay")  # type: ignore

    def test_non_int_timeout_raises_error(self, valid_relay: Relay) -> None:
        """Test that non-integer timeout raises ClientValidationError."""
        with pytest.raises(ClientValidationError):
            Client(relay=valid_relay, timeout="not_an_int")  # type: ignore

    def test_non_string_socks5_proxy_url_raises_error(self, tor_relay: Relay) -> None:
        """Test that non-string socks5_proxy_url raises ClientValidationError."""
        with pytest.raises(ClientValidationError):
            Client(relay=tor_relay, socks5_proxy_url=123)  # type: ignore


# ============================================================================
# Client Dictionary Conversion Tests
# ============================================================================


@pytest.mark.unit
class TestClientDictionaryConversion:
    """Test Client dictionary conversion."""

    def test_from_dict_creates_client(self) -> None:
        """Test that from_dict creates a Client instance."""
        data = {
            "relay": {"url": "wss://relay.damus.io"},
            "timeout": 10,
        }
        client = Client.from_dict(data)
        assert isinstance(client, Client)

    def test_from_dict_with_socks5_proxy(self) -> None:
        """Test that from_dict creates client with socks5_proxy_url."""
        data = {
            "relay": {
                "url": "wss://oxtrdevav64z64yb7x6rjg4ntzqjhedm5b5zjqulugknhzr46ny2qbad.onion"
            },
            "timeout": 10,
            "socks5_proxy_url": "socks5://localhost:9050",
        }
        client = Client.from_dict(data)
        assert client.socks5_proxy_url == "socks5://localhost:9050"

    def test_from_dict_with_non_dict_raises_error(self) -> None:
        """Test that from_dict with non-dict raises TypeError."""
        with pytest.raises(TypeError, match="data must be a dict"):
            Client.from_dict("not_a_dict")  # type: ignore

    def test_to_dict_returns_dict(self, valid_client: Client) -> None:
        """Test that to_dict returns a dictionary."""
        client_dict = valid_client.to_dict()
        assert isinstance(client_dict, dict)

    def test_to_dict_contains_all_fields(self, valid_client: Client) -> None:
        """Test that to_dict contains all client fields."""
        client_dict = valid_client.to_dict()
        assert "relay" in client_dict
        assert "timeout" in client_dict
        assert "socks5_proxy_url" in client_dict

    def test_round_trip_conversion(self, valid_client: Client) -> None:
        """Test that Client can be converted to dict and back."""
        client_dict = valid_client.to_dict()
        client2 = Client.from_dict(client_dict)

        assert valid_client.relay.url == client2.relay.url
        assert valid_client.timeout == client2.timeout
        assert valid_client.socks5_proxy_url == client2.socks5_proxy_url


# ============================================================================
# Client Connection Tests
# ============================================================================


@pytest.mark.unit
class TestClientConnection:
    """Test Client connection management."""

    @pytest.mark.asyncio
    async def test_connector_returns_tcp_for_clearnet(self, valid_client: Client) -> None:
        """Test that connector returns TCPConnector for clearnet."""
        from aiohttp import TCPConnector

        connector = valid_client.connector()
        assert isinstance(connector, TCPConnector)

    @pytest.mark.asyncio
    async def test_connector_returns_proxy_for_tor(self, tor_client: Client) -> None:
        """Test that connector returns ProxyConnector for Tor."""
        from aiohttp_socks import ProxyConnector

        connector = tor_client.connector()
        assert isinstance(connector, ProxyConnector)

    @pytest.mark.asyncio
    async def test_connector_raises_error_for_tor_without_proxy(self, tor_relay: Relay) -> None:
        """Test that connector raises error for Tor without proxy."""
        # Create client that bypasses validation
        client = Client.__new__(Client)
        client.relay = tor_relay
        client.socks5_proxy_url = None
        client.timeout = 10

        with pytest.raises(ClientConnectionError, match="SOCKS5 proxy URL required"):
            client.connector()

    @pytest.mark.asyncio
    async def test_session_creates_session(self, valid_client: Client) -> None:
        """Test that session creates a ClientSession."""
        from aiohttp import ClientSession

        session = valid_client.session()
        assert isinstance(session, ClientSession)
        await session.close()

    @pytest.mark.asyncio
    async def test_is_connected_returns_false_initially(self, valid_client: Client) -> None:
        """Test that is_connected returns False initially."""
        assert valid_client.is_connected is False

    @pytest.mark.asyncio
    async def test_active_subscriptions_empty_initially(self, valid_client: Client) -> None:
        """Test that active_subscriptions is empty initially."""
        assert valid_client.active_subscriptions == []


# ============================================================================
# Client Message Sending Tests
# ============================================================================


@pytest.mark.unit
class TestClientMessageSending:
    """Test Client message sending."""

    @pytest.mark.asyncio
    async def test_send_message_requires_connection(self, valid_relay: Relay) -> None:
        """Test that send_message requires connection."""
        # Create a fresh client that's not connected
        client = Client(relay=valid_relay)
        with pytest.raises(ClientConnectionError):
            await client.send_message(["TEST"])

    @pytest.mark.asyncio
    async def test_send_message_validates_type(self, valid_client: Client) -> None:
        """Test that send_message validates message type."""
        # Mock websocket connection
        valid_client._ws = AsyncMock()
        valid_client._ws.closed = False

        with pytest.raises(TypeError, match="message must be a list"):
            await valid_client.send_message("not_a_list")  # type: ignore


# ============================================================================
# Client Subscription Tests
# ============================================================================


@pytest.mark.unit
class TestClientSubscription:
    """Test Client subscription management."""

    @pytest.mark.asyncio
    async def test_subscribe_validates_filter_type(self, valid_client: Client) -> None:
        """Test that subscribe validates filter type."""
        valid_client._ws = AsyncMock()
        valid_client._ws.closed = False

        with pytest.raises(TypeError, match="filter must be Filter"):
            await valid_client.subscribe("not_a_filter")  # type: ignore

    @pytest.mark.asyncio
    async def test_subscribe_returns_subscription_id(
        self, valid_client: Client, valid_filter: Filter
    ) -> None:
        """Test that subscribe returns a subscription ID."""
        valid_client._ws = AsyncMock()
        valid_client._ws.closed = False
        valid_client._ws.send_str = AsyncMock()

        sub_id = await valid_client.subscribe(valid_filter)
        assert isinstance(sub_id, str)
        assert len(sub_id) > 0

    @pytest.mark.asyncio
    async def test_subscribe_uses_custom_id(
        self, valid_client: Client, valid_filter: Filter
    ) -> None:
        """Test that subscribe uses custom subscription ID."""
        valid_client._ws = AsyncMock()
        valid_client._ws.closed = False
        valid_client._ws.send_str = AsyncMock()

        custom_id = "custom_sub_id"
        sub_id = await valid_client.subscribe(valid_filter, custom_id)
        assert sub_id == custom_id

    @pytest.mark.asyncio
    async def test_unsubscribe_validates_type(self, valid_client: Client) -> None:
        """Test that unsubscribe validates subscription_id type."""
        valid_client._ws = AsyncMock()
        valid_client._ws.closed = False

        with pytest.raises(TypeError, match="subscription_id must be str"):
            await valid_client.unsubscribe(123)  # type: ignore


# ============================================================================
# Client Publishing Tests
# ============================================================================


@pytest.mark.unit
class TestClientPublishing:
    """Test Client event publishing."""

    @pytest.mark.asyncio
    async def test_publish_validates_event_type(self, valid_client: Client) -> None:
        """Test that publish validates event type."""
        valid_client._ws = AsyncMock()
        valid_client._ws.closed = False

        with pytest.raises(TypeError, match="event must be Event"):
            await valid_client.publish("not_an_event")  # type: ignore

    @pytest.mark.asyncio
    async def test_authenticate_validates_event_type(self, valid_client: Client) -> None:
        """Test that authenticate validates event type."""
        valid_client._ws = AsyncMock()
        valid_client._ws.closed = False

        with pytest.raises(TypeError, match="event must be Event"):
            await valid_client.authenticate("not_an_event")  # type: ignore

    @pytest.mark.asyncio
    async def test_authenticate_validates_event_kind(
        self, valid_client: Client, valid_event: Event
    ) -> None:
        """Test that authenticate validates event kind."""
        valid_client._ws = AsyncMock()
        valid_client._ws.closed = False

        # Event with wrong kind
        with pytest.raises(ValueError, match="Event kind must be 22242"):
            await valid_client.authenticate(valid_event)


# ============================================================================
# Client Async Context Manager Tests
# ============================================================================


@pytest.mark.unit
class TestClientAsyncContextManager:
    """Test Client async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager_connects_and_disconnects(self, valid_client: Client) -> None:
        """Test that context manager connects and disconnects."""
        with patch.object(valid_client, "connect", new_callable=AsyncMock):
            with patch.object(valid_client, "disconnect", new_callable=AsyncMock):
                async with valid_client:
                    pass

                valid_client.connect.assert_called_once()
                valid_client.disconnect.assert_called_once()


# ============================================================================
# Client Edge Cases Tests
# ============================================================================


@pytest.mark.unit
class TestClientEdgeCases:
    """Test Client edge cases and special scenarios."""

    def test_client_with_zero_timeout(self, valid_relay: Relay) -> None:
        """Test client with zero timeout."""
        # Zero timeout should be accepted (0 or greater allowed)
        client = Client(relay=valid_relay, timeout=0)
        assert client.timeout == 0

    def test_client_with_very_large_timeout(self, valid_relay: Relay) -> None:
        """Test client with very large timeout."""
        client = Client(relay=valid_relay, timeout=3600)  # 1 hour
        assert client.timeout == 3600

    def test_client_equality_based_on_relay(self, valid_relay: Relay) -> None:
        """Test that clients with same relay have same relay reference."""
        client1 = Client(relay=valid_relay, timeout=10)
        client2 = Client(relay=valid_relay, timeout=10)
        # While Client doesn't implement __eq__, relays should match
        assert client1.relay.url == client2.relay.url

    @pytest.mark.asyncio
    async def test_listen_events_validates_subscription_id_type(self, valid_client: Client) -> None:
        """Test that listen_events validates subscription_id type."""
        with pytest.raises(TypeError, match="subscription_id must be str"):
            async for _ in valid_client.listen_events(123):  # type: ignore
                pass

    @pytest.mark.asyncio
    async def test_listen_requires_connection(self, valid_relay: Relay) -> None:
        """Test that listen requires connection."""
        # Create a fresh client that's not connected
        client = Client(relay=valid_relay)
        with pytest.raises(ClientConnectionError):
            async for _ in client.listen():
                pass

    @pytest.mark.asyncio
    async def test_disconnect_when_not_connected(self, valid_client: Client) -> None:
        """Test that disconnect when not connected doesn't raise error."""
        await valid_client.disconnect()  # Should not raise

    @pytest.mark.asyncio
    async def test_multiple_disconnect_calls(self, valid_client: Client) -> None:
        """Test that multiple disconnect calls don't raise error."""
        await valid_client.disconnect()
        await valid_client.disconnect()  # Should not raise

    def test_client_with_ipv4_relay(self) -> None:
        """Test client with IPv4 relay."""
        relay = Relay(url="wss://192.168.1.1:7777")
        client = Client(relay=relay, timeout=10)
        assert client.is_valid

    def test_client_with_relay_with_path(self) -> None:
        """Test client with relay that has a path."""
        relay = Relay(url="wss://relay.example.com/nostr/v1")
        client = Client(relay=relay, timeout=10)
        assert client.is_valid


# ============================================================================
# Additional Client Coverage Tests
# ============================================================================


@pytest.mark.unit
class TestClientAdditionalCoverage:
    """Additional tests for improved Client coverage."""

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
        from aiohttp_socks import ProxyConnector

        # Use a valid v3 onion address (exactly 56 chars, a-z2-7 only)
        tor_relay = Relay(
            url="wss://abcdefghijklmnopqrstuvwxyz234567abcdefghijklmnopqrstuvwx.onion"
        )
        client = Client(relay=tor_relay,
                        socks5_proxy_url="socks5://localhost:9050")
        connector = client.connector()
        assert isinstance(connector, ProxyConnector)
        await connector.close()

    @pytest.mark.asyncio
    async def test_client_session_creation(self, valid_relay: Relay) -> None:
        """Test session creation."""
        from aiohttp import ClientSession

        client = Client(relay=valid_relay)
        session = client.session()
        assert isinstance(session, ClientSession)
        await session.close()

    @pytest.mark.asyncio
    async def test_client_session_with_custom_connector(self, valid_relay: Relay) -> None:
        """Test session with custom connector."""
        from aiohttp import ClientSession
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
        client._subscriptions = {
            "sub1": {"active": True}, "sub2": {"active": False}}
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
        """Test unsubscribe from nonexistent subscription raises SubscriptionError."""
        client = Client(relay=valid_relay)
        client._ws = AsyncMock()
        client._ws.closed = False
        with pytest.raises(ClientSubscriptionError, match="not found"):
            await client.unsubscribe("nonexistent")

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
