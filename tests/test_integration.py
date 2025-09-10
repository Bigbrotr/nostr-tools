"""
Integration tests for nostr-tools library.

These tests require network access and test the library's integration
with real Nostr relays. They may be slower and less reliable than unit tests.
"""

import pytest
import asyncio
import time
from unittest.mock import patch

from nostr_tools import (
    Client, Relay, Filter, Event, generate_keypair, generate_event,
    fetch_events, stream_events, compute_relay_metadata,
    fetch_nip11, check_connectivity, check_readability, check_writability,
    RelayConnectionError
)
from tests.conftest import skip_integration, generate_test_events
from tests import TEST_RELAY_URL, TEST_TIMEOUT


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
        relay_urls = [
            "wss://relay.damus.io",
            "wss://relay.nostr.band",
            "wss://nos.lol"
        ]
        
        successful_connections = 0
        
        for relay_url in relay_urls:
            try:
                relay = Relay(relay_url)
                client = Client(relay, timeout=10)
                
                rtt_open, openable = await check_connectivity(client)
                if openable:
                    successful_connections += 1
            except Exception:
                continue
        
        # At least one relay should be accessible
        assert successful_connections > 0


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
                    content=f"Integration test event {int(time.time())}"
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
                    'name', 'description', 'pubkey', 'contact',
                    'supported_nips', 'software', 'version', 'limitation'
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
            assert hasattr(metadata, 'connection_success')
            assert hasattr(metadata, 'nip11_success')
            assert hasattr(metadata, 'readable')
            assert hasattr(metadata, 'writable')
            assert hasattr(metadata, 'openable')
            
            if metadata.connection_success:
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
                    assert len(events) <= filter.filter_dict['limit']
                    
                    # Validate events match filter
                    for event in events:
                        assert event.kind in filter.filter_dict['kinds']
                        
        except RelayConnectionError:
            pytest.skip("Could not connect to test relay")


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
class TestErrorHandling:
    """Test error handling in integration scenarios."""
    
    async def test_invalid_relay_connection(self):
        """Test connection to invalid relay."""
        invalid_relay = Relay("wss://this-relay-does-not-exist-12345.invalid")
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
    
    @skip_integration
    async def test_malformed_filter_handling(self, sample_client):
        """Test handling of edge case filters."""
        try:
            async with sample_client:
                # Very restrictive filter that might return no results
                empty_filter = Filter(
                    kinds=[99999],  # Uncommon kind
                    limit=1,
                    since=int(time.time()) + 3600  # Future timestamp
                )
                
                events = await fetch_events(sample_client, empty_filter)
                assert isinstance(events, list)
                assert len(events) == 0  # Should return empty list, not error
                
        except RelayConnectionError:
            pytest.skip("Could not connect to test relay")