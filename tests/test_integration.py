"""
Integration tests for nostr-tools library.

These tests require network access and test the library's integration
with real Nostr relays. They may be slower and less reliable than unit tests.
"""

import time
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from nostr_tools import Client
from nostr_tools import Event
from nostr_tools import Filter
from nostr_tools import Relay
from nostr_tools import RelayConnectionError
from nostr_tools import check_connectivity
from nostr_tools import check_readability
from nostr_tools import check_writability
from nostr_tools import compute_relay_metadata
from nostr_tools import fetch_connection
from nostr_tools import fetch_events
from nostr_tools import fetch_nip11
from nostr_tools import generate_event
from nostr_tools import stream_events
from tests import TEST_RELAY_URL
from tests.conftest import skip_integration


@pytest.mark.integration
class TestRelayConnectivity:
    """Test basic relay connectivity."""

    @skip_integration
    async def test_relay_connection(self, sample_relay, sample_client):
        """Test basic relay connection."""
        try:
            async with sample_client:
                assert sample_client.is_connected
        except RelayConnectionError:
            pytest.skip("Test relay not accessible")

    @skip_integration
    async def test_connectivity_check(self, sample_client):
        """Test connectivity checking function."""
        try:
            rtt_open, openable = await check_connectivity(sample_client)

            if openable:
                assert rtt_open is not None
                assert rtt_open > 0
                assert isinstance(rtt_open, int)
            else:
                pytest.skip("Test relay not accessible")
        except Exception:
            pytest.skip("Connectivity test failed")

    @skip_integration
    async def test_multiple_relay_connections(self):
        """Test connecting to multiple relays."""
        relay_urls = ["wss://relay.damus.io", "wss://relay.nostr.band", "wss://nos.lol"]

        successful_connections = 0

        for relay_url in relay_urls:
            try:
                relay = Relay(relay_url)
                client = Client(relay, timeout=10)

                _, openable = await check_connectivity(client)
                if openable:
                    successful_connections += 1
            except Exception:
                continue

        # At least one relay should be accessible
        assert successful_connections > 0


@pytest.mark.integration
class TestClientOperations:
    """Test Client class operations with network connectivity."""

    @skip_integration
    async def test_client_context_manager(self, sample_client):
        """Test client as async context manager."""
        try:
            # Test entering and exiting context
            async with sample_client:
                assert sample_client.is_connected

            # Should be disconnected after exiting
            assert not sample_client.is_connected
        except RelayConnectionError:
            pytest.skip("Test relay not accessible")

    @skip_integration
    async def test_client_manual_connect_disconnect(self, sample_client):
        """Test manual connect and disconnect."""
        try:
            await sample_client.connect()
            assert sample_client.is_connected

            await sample_client.disconnect()
            assert not sample_client.is_connected
        except RelayConnectionError:
            pytest.skip("Test relay not accessible")

    @skip_integration
    async def test_client_already_connected(self, sample_client):
        """Test connecting when already connected."""
        try:
            async with sample_client:
                # Should not raise error when already connected
                await sample_client.connect()
                assert sample_client.is_connected
        except RelayConnectionError:
            pytest.skip("Test relay not accessible")

    @skip_integration
    async def test_client_send_message_not_connected(self, sample_client):
        """Test sending message when not connected."""
        with pytest.raises(RelayConnectionError, match="Not connected"):
            await sample_client.send_message(["REQ", "test", {}])

    @skip_integration
    async def test_client_listen_not_connected(self, sample_client):
        """Test listening when not connected."""
        with pytest.raises(RelayConnectionError, match="Not connected"):
            async for _ in sample_client.listen():
                pass

    @skip_integration
    async def test_client_subscription_management(self, sample_client):
        """Test subscription creation and management."""
        try:
            async with sample_client:
                filter = Filter(kinds=[1], limit=1)

                # Test subscription creation
                sub_id = await sample_client.subscribe(filter)
                assert isinstance(sub_id, str)
                assert len(sub_id) > 0

                # Test active subscriptions
                active_subs = sample_client.active_subscriptions
                assert sub_id in active_subs

                # Test unsubscription
                await sample_client.unsubscribe(sub_id)

                # Should still be in subscriptions but marked inactive
                assert sub_id in sample_client._subscriptions
                assert not sample_client._subscriptions[sub_id]["active"]
        except RelayConnectionError:
            pytest.skip("Test relay not accessible")

    @skip_integration
    async def test_client_custom_subscription_id(self, sample_client):
        """Test subscription with custom ID."""
        try:
            async with sample_client:
                filter = Filter(kinds=[1], limit=1)
                custom_id = "my_custom_subscription"

                sub_id = await sample_client.subscribe(filter, custom_id)
                assert sub_id == custom_id
        except RelayConnectionError:
            pytest.skip("Test relay not accessible")


@pytest.mark.integration
class TestEventOperations:
    """Test event publishing and fetching."""

    @skip_integration
    async def test_event_publishing(self, sample_client, sample_keypair):
        """Test publishing an event to a relay."""
        private_key, public_key = sample_keypair

        try:
            async with sample_client:
                # Create a test event
                event_data = generate_event(
                    private_key=private_key,
                    public_key=public_key,
                    kind=1,
                    tags=[["t", "integration_test"]],
                    content=f"Integration test event {int(time.time())}",
                )

                event = Event.from_dict(event_data)

                # Try to publish
                success = await sample_client.publish(event)

                # Note: success might be False if relay rejects the event
                # but this tests that the publish mechanism works
                assert isinstance(success, bool)

        except RelayConnectionError:
            pytest.skip("Could not connect to test relay")

    @skip_integration
    async def test_event_fetching(self, sample_client):
        """Test fetching events from a relay."""
        try:
            async with sample_client:
                filter = Filter(kinds=[1], limit=5)
                events = await fetch_events(sample_client, filter)

                assert isinstance(events, list)
                # There might be 0 events, which is valid

                for event in events:
                    assert isinstance(event, Event)
                    assert event.kind == 1
                    assert len(event.id) == 64
                    assert len(event.pubkey) == 64
                    assert len(event.sig) == 128

        except RelayConnectionError:
            pytest.skip("Could not connect to test relay")

    @skip_integration
    async def test_fetch_events_not_connected(self):
        """Test fetching events when client not connected."""
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)
        filter = Filter(kinds=[1], limit=1)

        with pytest.raises(RelayConnectionError, match="Client is not connected"):
            await fetch_events(client, filter)

    @skip_integration
    @pytest.mark.slow
    async def test_event_streaming(self, sample_client):
        """Test streaming events from a relay."""
        try:
            async with sample_client:
                filter = Filter(kinds=[1], limit=3)

                events_received = []
                stream_timeout = 30  # seconds
                start_time = time.time()

                async for event in stream_events(sample_client, filter):
                    events_received.append(event)

                    # Stop after 3 events or timeout
                    if len(events_received) >= 3 or (time.time() - start_time) > stream_timeout:
                        break

                # Validate received events
                for event in events_received:
                    assert isinstance(event, Event)
                    assert event.kind == 1

        except RelayConnectionError:
            pytest.skip("Could not connect to test relay")

    @skip_integration
    async def test_stream_events_not_connected(self):
        """Test streaming events when client not connected."""
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)
        filter = Filter(kinds=[1], limit=1)

        with pytest.raises(RelayConnectionError, match="Client is not connected"):
            async for _ in stream_events(client, filter):
                break


@pytest.mark.integration
class TestAuthenticationOperations:
    """Test NIP-42 authentication operations."""

    async def test_client_authenticate_invalid_kind(self, sample_client, sample_keypair):
        """Test authentication with invalid event kind."""
        private_key, public_key = sample_keypair

        # Create event with wrong kind
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,  # Wrong kind, should be 22242
            tags=[],
            content="Auth test",
        )
        event = Event.from_dict(event_data)

        with pytest.raises(ValueError, match="Event kind must be 22242"):
            await sample_client.authenticate(event)


@pytest.mark.integration
class TestRelayMetadata:
    """Test relay metadata and capabilities."""

    @skip_integration
    async def test_nip11_fetching(self, sample_client):
        """Test fetching NIP-11 relay information."""
        try:
            nip11_data = await fetch_nip11(sample_client)

            if nip11_data:
                # Validate NIP-11 structure
                assert isinstance(nip11_data, dict)

                # Check for common NIP-11 fields (all optional)
                expected_fields = [
                    "name",
                    "description",
                    "pubkey",
                    "contact",
                    "supported_nips",
                    "software",
                    "version",
                    "limitation",
                ]

                # At least some fields should be present
                present_fields = [field for field in expected_fields if field in nip11_data]
                assert len(present_fields) > 0

        except Exception:
            pytest.skip("NIP-11 not available or accessible")

    @skip_integration
    async def test_relay_capability_testing(self, sample_client, sample_keypair):
        """Test comprehensive relay capability testing."""
        private_key, public_key = sample_keypair

        try:
            metadata = await compute_relay_metadata(sample_client, private_key, public_key)

            # Validate metadata structure
            assert hasattr(metadata, "nip66_success")
            assert hasattr(metadata, "nip11_success")
            assert hasattr(metadata, "readable")
            assert hasattr(metadata, "writable")
            assert hasattr(metadata, "openable")

            if metadata.nip66_success:
                assert metadata.openable is True
                assert metadata.rtt_open is not None
                assert metadata.rtt_open > 0

        except Exception as e:
            pytest.skip(f"Relay metadata test failed: {e}")

    @skip_integration
    async def test_readability_check(self, sample_client):
        """Test relay readability checking."""
        try:
            async with sample_client:
                rtt_read, readable = await check_readability(sample_client)

                if readable:
                    assert rtt_read is not None
                    assert rtt_read > 0
                    assert isinstance(readable, bool)

        except RelayConnectionError:
            pytest.skip("Could not connect to test relay")

    @skip_integration
    async def test_readability_check_not_connected(self):
        """Test readability check when not connected."""
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        with pytest.raises(RelayConnectionError, match="Client is not connected"):
            await check_readability(client)

    @skip_integration
    async def test_writability_check(self, sample_client, sample_keypair):
        """Test relay writability checking."""
        private_key, public_key = sample_keypair

        try:
            async with sample_client:
                rtt_write, writable = await check_writability(
                    sample_client, private_key, public_key
                )

                # Writability check might fail (relay policy), but should not error
                assert isinstance(writable, bool)

                if writable and rtt_write:
                    assert rtt_write > 0

        except RelayConnectionError:
            pytest.skip("Could not connect to test relay")

    @skip_integration
    async def test_writability_check_not_connected(self, sample_keypair):
        """Test writability check when not connected."""
        private_key, public_key = sample_keypair
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        with pytest.raises(RelayConnectionError, match="Client is not connected"):
            await check_writability(client, private_key, public_key)

    @skip_integration
    async def test_fetch_connection_comprehensive(self, sample_keypair):
        """Test comprehensive connection fetching."""
        private_key, public_key = sample_keypair

        try:
            relay = Relay(TEST_RELAY_URL)
            client = Client(relay, timeout=15)

            result = await fetch_connection(client, private_key, public_key)

            if result:
                # Should contain all expected keys
                expected_keys = [
                    "rtt_open",
                    "rtt_read",
                    "rtt_write",
                    "openable",
                    "writable",
                    "readable",
                ]
                for key in expected_keys:
                    assert key in result

                # Type validation
                assert isinstance(result["openable"], bool)
                assert isinstance(result["writable"], bool)
                assert isinstance(result["readable"], bool)

        except Exception:
            pytest.skip("Connection test failed")

    async def test_fetch_connection_already_connected(self, sample_keypair):
        """Test fetch_connection when client already connected."""
        private_key, public_key = sample_keypair
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        # Simulate connected state
        client._ws = MagicMock()
        client._ws.closed = False

        with pytest.raises(RelayConnectionError, match="Client is already connected"):
            await fetch_connection(client, private_key, public_key)

    async def test_compute_relay_metadata_already_connected(self, sample_keypair):
        """Test compute_relay_metadata when client already connected."""
        private_key, public_key = sample_keypair
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        # Simulate connected state
        client._ws = MagicMock()
        client._ws.closed = False

        with pytest.raises(RelayConnectionError, match="Client is already connected"):
            await compute_relay_metadata(client, private_key, public_key)

    async def test_check_connectivity_already_connected(self):
        """Test check_connectivity when client already connected."""
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        # Simulate connected state
        client._ws = MagicMock()
        client._ws.closed = False

        with pytest.raises(RelayConnectionError, match="Client is already connected"):
            await check_connectivity(client)


@pytest.mark.integration
class TestFilteringAndSubscriptions:
    """Test event filtering and subscription management."""

    @skip_integration
    async def test_subscription_management(self, sample_client):
        """Test creating and managing subscriptions."""
        try:
            async with sample_client:
                filter = Filter(kinds=[1], limit=1)

                # Create subscription
                subscription_id = await sample_client.subscribe(filter)
                assert isinstance(subscription_id, str)
                assert len(subscription_id) > 0

                # Check active subscriptions
                active_subs = sample_client.active_subscriptions
                assert subscription_id in active_subs

                # Unsubscribe
                await sample_client.unsubscribe(subscription_id)

        except RelayConnectionError:
            pytest.skip("Could not connect to test relay")

    @skip_integration
    async def test_complex_filtering(self, sample_client):
        """Test complex event filtering."""
        try:
            async with sample_client:
                # Test different filter combinations
                filters_to_test = [
                    Filter(kinds=[0], limit=2),  # Metadata events
                    Filter(kinds=[1], limit=3),  # Text notes
                    Filter(kinds=[1, 3], limit=5),  # Multiple kinds
                ]

                for filter in filters_to_test:
                    events = await fetch_events(sample_client, filter)

                    assert isinstance(events, list)
                    assert len(events) <= filter.filter_dict["limit"]

                    # Validate events match filter
                    for event in events:
                        assert event.kind in filter.filter_dict["kinds"]

        except RelayConnectionError:
            pytest.skip("Could not connect to test relay")


@pytest.mark.integration
class TestClientErrorHandling:
    """Test client error handling scenarios."""

    @patch("nostr_tools.core.client.ClientSession")
    async def test_client_connection_session_error(self, mock_session_class):
        """Test client connection when session creation fails."""
        # Setup mock to raise exception
        mock_session_class.side_effect = Exception("Session creation failed")

        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        with pytest.raises(RelayConnectionError, match="Failed to connect"):
            await client.connect()

    @patch("aiohttp.ClientSession.ws_connect")
    async def test_client_websocket_connection_error(self, mock_ws_connect):
        """Test client when WebSocket connection fails."""
        # Setup mock to raise exception
        mock_ws_connect.side_effect = Exception("WebSocket connection failed")

        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        with pytest.raises(RelayConnectionError, match="Failed to connect"):
            await client.connect()

    async def test_client_send_message_websocket_error(self):
        """Test send_message when WebSocket send fails."""
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        # Create mock WebSocket that raises on send
        mock_ws = AsyncMock()
        mock_ws.send_str = AsyncMock(side_effect=Exception("Send failed"))
        client._ws = mock_ws

        with pytest.raises(RelayConnectionError, match="Failed to send message"):
            await client.send_message(["TEST", "message"])

    async def test_client_listen_websocket_error(self):
        """Test listen when WebSocket receive fails."""
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        # Create mock WebSocket that raises on receive
        mock_ws = AsyncMock()
        mock_ws.receive = AsyncMock(side_effect=Exception("Receive failed"))
        client._ws = mock_ws

        with pytest.raises(RelayConnectionError, match="Error listening to relay"):
            async for _ in client.listen():
                break

    async def test_client_listen_timeout(self):
        """Test listen with timeout."""
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay, timeout=1)  # Very short timeout

        # Create mock WebSocket that times out
        mock_ws = AsyncMock()
        import asyncio

        mock_ws.receive = AsyncMock(side_effect=asyncio.TimeoutError())
        client._ws = mock_ws

        # Should handle timeout gracefully
        messages = []
        async for message in client.listen():
            messages.append(message)

        assert len(messages) == 0  # Should exit gracefully on timeout

    from contextlib import asynccontextmanager

    async def test_client_listen_websocket_message_types(self):
        """Test listen with different WebSocket message types."""
        from contextlib import asynccontextmanager

        from aiohttp import WSMsgType

        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        # Create mock WebSocket with different message types
        mock_ws = AsyncMock()
        mock_msg_text = MagicMock()
        mock_msg_text.type = WSMsgType.TEXT
        mock_msg_text.data = '["TEST", "message"]'

        mock_msg_error = MagicMock()
        mock_msg_error.type = WSMsgType.ERROR
        mock_msg_error.data = "Error message"

        mock_msg_closed = MagicMock()
        mock_msg_closed.type = WSMsgType.CLOSED

        mock_msg_binary = MagicMock()
        mock_msg_binary.type = WSMsgType.BINARY

        @asynccontextmanager
        async def listen_context():
            """Context manager to properly close async generator."""
            listen_gen = client.listen()
            try:
                yield listen_gen
            finally:
                await listen_gen.aclose()

        # Test TEXT message (should yield)
        mock_ws.receive = AsyncMock(return_value=mock_msg_text)
        client._ws = mock_ws

        async with listen_context() as listen_gen:
            message = await listen_gen.__anext__()
            assert message == ["TEST", "message"]

        # Test ERROR message (should raise)
        mock_ws.receive = AsyncMock(return_value=mock_msg_error)
        with pytest.raises(RelayConnectionError, match="WebSocket error"):
            async with listen_context() as listen_gen:
                await listen_gen.__anext__()

        # Test CLOSED message (should exit gracefully)
        mock_ws.receive = AsyncMock(return_value=mock_msg_closed)
        async with listen_context() as listen_gen:
            messages = []
            try:
                async for message in listen_gen:
                    messages.append(message)
            except StopAsyncIteration:
                pass
            assert len(messages) == 0

        # Test unexpected message type (should raise)
        mock_ws.receive = AsyncMock(return_value=mock_msg_binary)
        with pytest.raises(RelayConnectionError, match="Unexpected message type"):
            async with listen_context() as listen_gen:
                await listen_gen.__anext__()


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Test performance characteristics with real relays."""

    @skip_integration
    async def test_connection_performance(self, sample_relay):
        """Test connection establishment performance."""
        client = Client(sample_relay, timeout=30)

        try:
            start_time = time.perf_counter()

            async with client:
                connection_time = time.perf_counter() - start_time

                # Connection should be reasonably fast (adjust as needed)
                assert connection_time < 10.0  # 10 seconds max

        except RelayConnectionError:
            pytest.skip("Could not connect to test relay")

    @skip_integration
    async def test_event_fetch_performance(self, sample_client):
        """Test event fetching performance."""
        try:
            async with sample_client:
                filter = Filter(kinds=[1], limit=50)

                start_time = time.perf_counter()
                events = await fetch_events(sample_client, filter)
                fetch_time = time.perf_counter() - start_time

                # Should fetch events reasonably quickly
                if events:
                    events_per_second = len(events) / fetch_time
                    assert events_per_second > 1  # At least 1 event per second

        except RelayConnectionError:
            pytest.skip("Could not connect to test relay")


@pytest.mark.integration
class TestActionsErrorHandling:
    """Test error handling in actions module."""

    async def test_invalid_relay_connection(self):
        """Test connection to invalid relay."""
        invalid_relay = Relay("wss://this-relay-does-not-exist-12345.com")
        client = Client(invalid_relay, timeout=5)

        with pytest.raises(RelayConnectionError):
            async with client:
                pass

    @skip_integration
    async def test_connection_timeout(self):
        """Test connection timeout handling."""
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay, timeout=1)  # Very short timeout

        try:
            async with client:
                # If connection succeeds despite short timeout, that's okay
                pass
        except RelayConnectionError:
            # If it times out, that's expected with short timeout
            pass

    @patch("nostr_tools.actions.actions.fetch_nip11")
    async def test_compute_relay_metadata_nip11_error(self, mock_fetch_nip11, sample_keypair):
        """Test compute_relay_metadata when NIP-11 fetch fails."""
        private_key, public_key = sample_keypair

        # Mock NIP-11 fetch to return None (failure)
        mock_fetch_nip11.return_value = None

        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        with patch("nostr_tools.actions.actions.fetch_connection") as mock_fetch_conn:
            mock_fetch_conn.return_value = None

            metadata = await compute_relay_metadata(client, private_key, public_key)

            # Should still return metadata object even if NIP-11 fails
            assert metadata.nip11_success is False
            assert metadata.nip66_success is False

    @patch("nostr_tools.actions.actions.fetch_connection")
    async def test_compute_relay_metadata_connection_error(self, mock_fetch_conn, sample_keypair):
        """Test compute_relay_metadata when connection test fails."""
        private_key, public_key = sample_keypair

        # Mock connection fetch to return None (failure)
        mock_fetch_conn.return_value = None

        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        metadata = await compute_relay_metadata(client, private_key, public_key)

        # Should still return metadata object even if connection fails
        assert metadata.nip66_success is False

    @patch("aiohttp.ClientSession.get")
    async def test_fetch_nip11_http_error(self, mock_get, sample_client):
        """Test fetch_nip11 when HTTP request fails."""
        from aiohttp import ClientError

        # Mock HTTP get to raise ClientError
        mock_get.side_effect = ClientError("HTTP request failed")

        result = await fetch_nip11(sample_client)
        assert result is None

    @patch("aiohttp.ClientSession.get")
    async def test_fetch_nip11_timeout_error(self, mock_get, sample_client):
        """Test fetch_nip11 when request times out."""
        from asyncio import TimeoutError

        # Mock HTTP get to raise TimeoutError
        mock_get.side_effect = TimeoutError("Request timed out")

        result = await fetch_nip11(sample_client)
        assert result is None

    @patch("aiohttp.ClientSession.get")
    async def test_fetch_nip11_unexpected_error(self, mock_get, sample_client):
        """Test fetch_nip11 when unexpected error occurs."""
        # Mock HTTP get to raise unexpected exception
        mock_get.side_effect = Exception("Unexpected error")

        result = await fetch_nip11(sample_client)
        assert result is None

    async def test_fetch_nip11_invalid_json_response(self, sample_client):
        """Test fetch_nip11 with non-JSON response."""
        with patch("aiohttp.ClientSession.get") as mock_get:
            # Create mock response with invalid JSON
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value="not a dict")

            mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
            mock_get.return_value.__aexit__ = AsyncMock(return_value=None)

            result = await fetch_nip11(sample_client)
            assert result == "not a dict"  # Should return whatever was returned

    async def test_check_readability_relay_error(self):
        """Test check_readability when relay returns error."""
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        # Create mock WebSocket and set connected state
        mock_ws = AsyncMock()
        mock_ws.closed = False
        client._ws = mock_ws

        # Mock subscription and listen to simulate error
        with patch.object(client, "subscribe", return_value="test_sub"):
            with patch.object(client, "listen") as mock_listen:
                # Simulate RelayConnectionError during listen
                mock_listen.side_effect = RelayConnectionError("Connection lost")

                rtt_read, readable = await check_readability(client)

                assert rtt_read is None
                assert readable is False

    async def test_check_writability_relay_error(self, sample_keypair):
        """Test check_writability when relay returns error."""
        private_key, public_key = sample_keypair
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        # Create mock WebSocket and set connected state
        mock_ws = AsyncMock()
        mock_ws.closed = False
        client._ws = mock_ws

        # Mock publish to simulate error
        with patch.object(client, "publish") as mock_publish:
            mock_publish.side_effect = RelayConnectionError("Publish failed")

            rtt_write, writable = await check_writability(client, private_key, public_key)

            assert rtt_write is None
            assert writable is False


@pytest.mark.integration
class TestActionsMockScenarios:
    """Test actions with various mock scenarios."""

    async def test_stream_events_parse_error(self, sample_client):
        """Test stream_events with event parsing errors."""
        filter = Filter(kinds=[1], limit=1)

        # Mock client to be connected
        mock_ws = AsyncMock()
        mock_ws.closed = False
        sample_client._ws = mock_ws

        with patch.object(sample_client, "subscribe", return_value="test_sub"):
            with patch.object(sample_client, "listen_events") as mock_listen:
                # Return malformed event data
                async def mock_listen_events(sub_id):
                    yield ["EVENT", "test_sub", {"invalid": "event_data"}]

                mock_listen.return_value = mock_listen_events("test_sub")

                events = []
                async for event in stream_events(sample_client, filter):
                    events.append(event)
                    break

                # Should handle parse errors gracefully
                assert len(events) == 0

    async def test_fetch_events_parse_error(self, sample_client):
        """Test fetch_events with event parsing errors."""
        filter = Filter(kinds=[1], limit=1)

        # Mock client to be connected
        mock_ws = AsyncMock()
        mock_ws.closed = False
        sample_client._ws = mock_ws

        with patch.object(sample_client, "subscribe", return_value="test_sub"):
            with patch.object(sample_client, "listen_events") as mock_listen:
                # Return malformed event data
                async def mock_listen_events(sub_id):
                    yield ["EVENT", "test_sub", {"invalid": "event_data"}]

                mock_listen.return_value = mock_listen_events("test_sub")

                with patch.object(sample_client, "unsubscribe"):
                    events = await fetch_events(sample_client, filter)

                # Should handle parse errors gracefully
                assert len(events) == 0

    async def test_check_readability_unexpected_error(self):
        """Test check_readability with unexpected error."""
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        # Create mock WebSocket and set connected state
        mock_ws = AsyncMock()
        mock_ws.closed = False
        client._ws = mock_ws

        # Mock subscription to raise unexpected error
        with patch.object(client, "subscribe") as mock_subscribe:
            mock_subscribe.side_effect = Exception("Unexpected error")

            rtt_read, readable = await check_readability(client)

            assert rtt_read is None
            assert readable is False

    async def test_check_writability_unexpected_error(self, sample_keypair):
        """Test check_writability with unexpected error."""
        private_key, public_key = sample_keypair
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        # Create mock WebSocket and set connected state
        mock_ws = AsyncMock()
        mock_ws.closed = False
        client._ws = mock_ws

        # Mock generate_event to raise error
        with patch("nostr_tools.actions.actions.generate_event") as mock_generate:
            mock_generate.side_effect = Exception("Event generation failed")

            rtt_write, writable = await check_writability(client, private_key, public_key)

            assert rtt_write is None
            assert writable is False

    async def test_compute_relay_metadata_pow_detection(self, sample_keypair):
        """Test compute_relay_metadata with proof-of-work detection."""
        private_key, public_key = sample_keypair
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        # Mock NIP-11 response with PoW requirement
        nip11_response = {"name": "Test Relay", "limitation": {"min_pow_difficulty": 16}}

        with patch("nostr_tools.actions.actions.fetch_nip11", return_value=nip11_response):
            with patch("nostr_tools.actions.actions.fetch_connection") as mock_fetch_conn:
                mock_fetch_conn.return_value = {
                    "rtt_open": 100,
                    "rtt_read": 150,
                    "rtt_write": 200,
                    "openable": True,
                    "writable": True,
                    "readable": True,
                }

                _ = await compute_relay_metadata(client, private_key, public_key)

                # Should have detected PoW requirement and passed it to fetch_connection
                mock_fetch_conn.assert_called_once()
                call_args = mock_fetch_conn.call_args

                # Check that target_difficulty=16 was passed
                assert call_args[0][3] == 16  # target_difficulty parameter

    async def test_compute_relay_metadata_invalid_pow(self, sample_keypair):
        """Test compute_relay_metadata with invalid PoW specification."""
        private_key, public_key = sample_keypair
        relay = Relay(TEST_RELAY_URL)
        client = Client(relay)

        # Mock NIP-11 response with invalid PoW requirement
        nip11_response = {
            "name": "Test Relay",
            "limitation": {
                "min_pow_difficulty": "invalid"  # Should be int
            },
        }

        with patch("nostr_tools.actions.actions.fetch_nip11", return_value=nip11_response):
            with patch("nostr_tools.actions.actions.fetch_connection") as mock_fetch_conn:
                mock_fetch_conn.return_value = None

                _ = await compute_relay_metadata(client, private_key, public_key)

                # Should pass None for target_difficulty due to invalid spec
                mock_fetch_conn.assert_called_once()
                call_args = mock_fetch_conn.call_args
                assert call_args[0][3] is None  # target_difficulty parameter
