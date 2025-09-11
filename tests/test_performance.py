"""
Performance tests for nostr-tools library.

These tests measure performance characteristics and ensure the library
meets performance requirements for key operations.
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor

from nostr_tools import (
    generate_keypair, generate_event, Event, Filter,
    calc_event_id, verify_sig, to_bech32, to_hex
)

@pytest.mark.slow
class TestCryptographicPerformance:
    """Test performance of cryptographic operations."""
    
    def test_keypair_generation_performance(self, performance_timer):
        """Test key pair generation performance."""
        iterations = 100
        
        performance_timer.start()
        for _ in range(iterations):
            generate_keypair()
        performance_timer.stop()
        
        avg_time = performance_timer.elapsed / iterations
        
        # Should generate at least 10 keypairs per second
        assert avg_time < 0.1, f"Keypair generation too slow: {avg_time:.4f}s per keypair"
        
        print(f"Keypair generation: {1/avg_time:.1f} pairs/second")
    
    def test_event_signing_performance(self, sample_keypair, performance_timer):
        """Test event signing performance."""
        private_key, public_key = sample_keypair
        iterations = 100
        
        # Pre-generate event data
        events_data = []
        for i in range(iterations):
            events_data.append({
                'content': f"Test event {i}",
                'kind': 1,
                'tags': [["t", f"test{i}"]]
            })
        
        performance_timer.start()
        for data in events_data:
            generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=data['kind'],
                tags=data['tags'],
                content=data['content']
            )
        performance_timer.stop()
        
        avg_time = performance_timer.elapsed / iterations
        
        # Should sign at least 20 events per second
        assert avg_time < 0.05, f"Event signing too slow: {avg_time:.4f}s per event"
        
        print(f"Event signing: {1/avg_time:.1f} events/second")
    
    def test_signature_verification_performance(self, sample_keypair, performance_timer):
        """Test signature verification performance."""
        private_key, public_key = sample_keypair
        iterations = 100
        
        # Pre-generate signed events
        events = []
        for i in range(iterations):
            event_data = generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=1,
                tags=[],
                content=f"Test event {i}"
            )
            events.append(event_data)
        
        performance_timer.start()
        for event_data in events:
            verify_sig(event_data['id'], event_data['pubkey'], event_data['sig'])
        performance_timer.stop()
        
        avg_time = performance_timer.elapsed / iterations
        
        # Should verify at least 50 signatures per second
        assert avg_time < 0.02, f"Signature verification too slow: {avg_time:.4f}s per verification"
        
        print(f"Signature verification: {1/avg_time:.1f} verifications/second")
    
    def test_event_id_calculation_performance(self, sample_keypair, performance_timer):
        """Test event ID calculation performance."""
        private_key, public_key = sample_keypair
        iterations = 1000
        
        # Pre-generate event parameters
        event_params = []
        for i in range(iterations):
            event_params.append({
                'pubkey': public_key,
                'created_at': int(time.time()) + i,
                'kind': 1,
                'tags': [["t", f"test{i}"]],
                'content': f"Test event {i}"
            })
        
        performance_timer.start()
        for params in event_params:
            calc_event_id(
                params['pubkey'],
                params['created_at'],
                params['kind'],
                params['tags'],
                params['content']
            )
        performance_timer.stop()
        
        avg_time = performance_timer.elapsed / iterations
        
        # Should calculate at least 200 IDs per second
        assert avg_time < 0.005, f"Event ID calculation too slow: {avg_time:.4f}s per ID"
        
        print(f"Event ID calculation: {1/avg_time:.1f} IDs/second")


@pytest.mark.slow
class TestEncodingPerformance:
    """Test performance of encoding operations."""
    
    def test_bech32_encoding_performance(self, performance_timer):
        """Test Bech32 encoding performance."""
        iterations = 1000
        test_hex = "0123456789abcdef" * 4  # 64 char hex
        
        performance_timer.start()
        for _ in range(iterations):
            to_bech32("npub", test_hex)
        performance_timer.stop()
        
        avg_time = performance_timer.elapsed / iterations
        
        # Should encode at least 500 per second
        assert avg_time < 0.002, f"Bech32 encoding too slow: {avg_time:.4f}s per encoding"
        
        print(f"Bech32 encoding: {1/avg_time:.1f} encodings/second")
    
    def test_bech32_decoding_performance(self, performance_timer):
        """Test Bech32 decoding performance."""
        iterations = 1000
        test_bech32 = to_bech32("npub", "0123456789abcdef" * 4)
        
        performance_timer.start()
        for _ in range(iterations):
            to_hex(test_bech32)
        performance_timer.stop()
        
        avg_time = performance_timer.elapsed / iterations
        
        # Should decode at least 500 per second
        assert avg_time < 0.002, f"Bech32 decoding too slow: {avg_time:.4f}s per decoding"
        
        print(f"Bech32 decoding: {1/avg_time:.1f} decodings/second")


@pytest.mark.slow
class TestEventProcessingPerformance:
    """Test performance of event processing operations."""
    
    def test_event_creation_performance(self, sample_keypair, performance_timer):
        """Test Event object creation performance."""
        private_key, public_key = sample_keypair
        iterations = 100
        
        # Pre-generate event data
        events_data = []
        for i in range(iterations):
            event_data = generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=1,
                tags=[["t", f"test{i}"]],
                content=f"Test event {i}"
            )
            events_data.append(event_data)
        
        performance_timer.start()
        for event_data in events_data:
            Event.from_dict(event_data)
        performance_timer.stop()
        
        avg_time = performance_timer.elapsed / iterations
        
        # Should create at least 200 Event objects per second
        assert avg_time < 0.005, f"Event creation too slow: {avg_time:.4f}s per event"
        
        print(f"Event object creation: {1/avg_time:.1f} events/second")
    
    def test_event_serialization_performance(self, sample_keypair, performance_timer):
        """Test Event serialization performance."""
        private_key, public_key = sample_keypair
        iterations = 100
        
        # Pre-create Event objects
        events = []
        for i in range(iterations):
            event_data = generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=1,
                tags=[["t", f"test{i}"]],
                content=f"Test event {i}"
            )
            events.append(Event.from_dict(event_data))
        
        performance_timer.start()
        for event in events:
            event.to_dict()
        performance_timer.stop()
        
        avg_time = performance_timer.elapsed / iterations
        
        # Should serialize at least 500 events per second
        assert avg_time < 0.002, f"Event serialization too slow: {avg_time:.4f}s per event"
        
        print(f"Event serialization: {1/avg_time:.1f} events/second")
    
    def test_tag_operations_performance(self, sample_keypair, performance_timer):
        """Test tag operations performance."""
        private_key, public_key = sample_keypair
        
        # Create event with many tags
        tags = []
        for i in range(100):
            tags.append(["t", f"tag{i}"])
            tags.append(["p", f"pubkey{i:016x}" + "0" * 48])
            tags.append(["e", f"event{i:016x}" + "0" * 48])
        
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=tags,
            content="Event with many tags"
        )
        
        event = Event.from_dict(event_data)
        iterations = 1000
        
        performance_timer.start()
        for _ in range(iterations):
            event.get_tag_values("t")
            event.get_tag_values("p")
            event.has_tag("t", "tag50")
            event.has_tag("nonexistent")
        performance_timer.stop()
        
        avg_time = performance_timer.elapsed / (iterations * 4)  # 4 operations per iteration
        
        # Should perform at least 1000 tag operations per second
        assert avg_time < 0.001, f"Tag operations too slow: {avg_time:.4f}s per operation"
        
        print(f"Tag operations: {1/avg_time:.1f} operations/second")


@pytest.mark.slow
class TestFilterPerformance:
    """Test performance of filter operations."""
    
    def test_filter_creation_performance(self, sample_keypair, performance_timer):
        """Test Filter creation performance."""
        private_key, public_key = sample_keypair
        iterations = 1000
        
        performance_timer.start()
        for i in range(iterations):
            Filter(
                kinds=[1, 3, 6, 7],
                authors=[public_key],
                since=int(time.time()) - 3600,
                until=int(time.time()),
                limit=50,
                t=[f"tag{i % 10}"],
                p=[public_key]
            )
        performance_timer.stop()
        
        avg_time = performance_timer.elapsed / iterations
        
        # Should create at least 500 filters per second
        assert avg_time < 0.002, f"Filter creation too slow: {avg_time:.4f}s per filter"
        
        print(f"Filter creation: {1/avg_time:.1f} filters/second")
    
    def test_filter_validation_performance(self, sample_keypair, performance_timer):
        """Test Filter validation performance."""
        private_key, public_key = sample_keypair
        iterations = 100
        
        # Create filters with various validation requirements
        filter_params = []
        for i in range(iterations):
            filter_params.append({
                'ids': [f"{i:064x}"],
                'authors': [public_key],
                'kinds': [1, 3, 6, 7],
                'since': int(time.time()) - 3600,
                'until': int(time.time()),
                'limit': 50 + i,
                't': [f"tag{i}"],
                'p': [public_key]
            })
        
        performance_timer.start()
        for params in filter_params:
            Filter(**params)
        performance_timer.stop()
        
        avg_time = performance_timer.elapsed / iterations
        
        # Should validate at least 200 complex filters per second
        assert avg_time < 0.005, f"Filter validation too slow: {avg_time:.4f}s per filter"
        
        print(f"Filter validation: {1/avg_time:.1f} filters/second")


@pytest.mark.slow
class TestProofOfWorkPerformance:
    """Test proof-of-work performance."""
    
    def test_low_difficulty_pow(self, sample_keypair, performance_timer):
        """Test low difficulty proof-of-work performance."""
        private_key, public_key = sample_keypair
        
        performance_timer.start()
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="PoW test event",
            target_difficulty=8,  # 8 leading zero bits
            timeout=30
        )
        performance_timer.stop()
        
        # Should complete within reasonable time
        assert performance_timer.elapsed < 10, f"PoW too slow: {performance_timer.elapsed:.2f}s"
        
        # Verify the event has the nonce tag
        event = Event.from_dict(event_data)
        nonce_tags = [tag for tag in event.tags if tag[0] == "nonce"]
        assert len(nonce_tags) > 0, "PoW event should have nonce tag"
        
        print(f"PoW (difficulty 8): {performance_timer.elapsed:.2f}s")
    
    def test_pow_timeout_handling(self, sample_keypair, performance_timer):
        """Test proof-of-work timeout handling."""
        private_key, public_key = sample_keypair
        
        performance_timer.start()
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="PoW timeout test",
            target_difficulty=20,  # Very high difficulty
            timeout=2  # Short timeout
        )
        performance_timer.stop()
        
        # Should respect timeout
        assert performance_timer.elapsed <= 3, f"PoW timeout not respected: {performance_timer.elapsed:.2f}s"
        
        # Event should still be valid (without PoW if timed out)
        event = Event.from_dict(event_data)
        assert event.content == "PoW timeout test"
        
        print(f"PoW timeout test: {performance_timer.elapsed:.2f}s")


@pytest.mark.slow
class TestConcurrencyPerformance:
    """Test performance under concurrent operations."""
    
    def test_concurrent_keypair_generation(self, performance_timer):
        """Test concurrent key pair generation."""
        iterations = 50
        threads = 4
        
        def generate_keypairs_batch():
            for _ in range(iterations // threads):
                generate_keypair()
        
        performance_timer.start()
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(generate_keypairs_batch) for _ in range(threads)]
            for future in futures:
                future.result()
        performance_timer.stop()
        
        avg_time = performance_timer.elapsed / iterations
        
        # Concurrent generation should still be reasonably fast
        assert avg_time < 0.2, f"Concurrent keypair generation too slow: {avg_time:.4f}s per keypair"
        
        print(f"Concurrent keypair generation: {1/avg_time:.1f} pairs/second")
    
    def test_concurrent_event_creation(self, sample_keypair, performance_timer):
        """Test concurrent event creation."""
        private_key, public_key = sample_keypair
        iterations = 50
        threads = 4
        
        def create_events_batch():
            for i in range(iterations // threads):
                generate_event(
                    private_key=private_key,
                    public_key=public_key,
                    kind=1,
                    tags=[["t", f"concurrent{i}"]],
                    content=f"Concurrent event {i}"
                )
        
        performance_timer.start()
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(create_events_batch) for _ in range(threads)]
            for future in futures:
                future.result()
        performance_timer.stop()
        
        avg_time = performance_timer.elapsed / iterations
        
        # Concurrent event creation should be reasonably fast
        assert avg_time < 0.1, f"Concurrent event creation too slow: {avg_time:.4f}s per event"
        
        print(f"Concurrent event creation: {1/avg_time:.1f} events/second")


@pytest.mark.slow
class TestMemoryPerformance:
    """Test memory usage and garbage collection performance."""
    
    def test_event_memory_usage(self, sample_keypair):
        """Test memory usage of event creation."""
        import gc
        import sys
        
        private_key, public_key = sample_keypair
        
        # Force garbage collection
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Create many events
        events = []
        for i in range(1000):
            event_data = generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=1,
                tags=[["t", f"memory{i}"]],
                content=f"Memory test event {i}"
            )
            events.append(Event.from_dict(event_data))
        
        # Check object count
        after_objects = len(gc.get_objects())
        objects_created = after_objects - initial_objects
        
        # Clean up
        del events
        gc.collect()
        
        # Should not create excessive objects
        objects_per_event = objects_created / 1000
        assert objects_per_event < 50, f"Too many objects created per event: {objects_per_event}"
        
        print(f"Objects per event: {objects_per_event:.1f}")
    
    def test_large_event_handling(self, sample_keypair, performance_timer):
        """Test handling of large events."""
        private_key, public_key = sample_keypair
        
        # Create event with large content
        large_content = "x" * 10000  # 10KB content
        large_tags = []
        for i in range(100):
            large_tags.append(["t", f"largetag{i}" * 10])
        
        performance_timer.start()
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=large_tags,
            content=large_content
        )
        
        event = Event.from_dict(event_data)
        serialized = event.to_dict()
        performance_timer.stop()
        
        # Should handle large events reasonably fast
        assert performance_timer.elapsed < 1.0, f"Large event processing too slow: {performance_timer.elapsed:.2f}s"
        
        # Verify data integrity
        assert len(serialized['content']) == 10000
        assert len(serialized['tags']) == 100
        
        print(f"Large event processing: {performance_timer.elapsed:.2f}s")


@pytest.mark.slow
class TestBenchmarkComparison:
    """Benchmark tests for comparison across versions."""
    
    def test_comprehensive_benchmark(self, sample_keypair, performance_timer):
        """Comprehensive benchmark of core operations."""
        private_key, public_key = sample_keypair
        
        results = {}
        
        # Keypair generation benchmark
        performance_timer.start()
        for _ in range(10):
            generate_keypair()
        performance_timer.stop()
        results['keypair_generation'] = performance_timer.elapsed / 10
        
        # Event creation benchmark
        performance_timer.start()
        for i in range(50):
            generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=1,
                tags=[["t", f"bench{i}"]],
                content=f"Benchmark event {i}"
            )
        performance_timer.stop()
        results['event_creation'] = performance_timer.elapsed / 50
        
        # Signature verification benchmark
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="Verification test"
        )
        
        performance_timer.start()
        for _ in range(100):
            verify_sig(event_data['id'], event_data['pubkey'], event_data['sig'])
        performance_timer.stop()
        results['signature_verification'] = performance_timer.elapsed / 100
        
        # Bech32 encoding benchmark
        performance_timer.start()
        for _ in range(100):
            to_bech32("npub", public_key)
        performance_timer.stop()
        results['bech32_encoding'] = performance_timer.elapsed / 100
        
        # Print benchmark results
        print("\nBenchmark Results:")
        print(f"Keypair generation: {results['keypair_generation']*1000:.2f}ms")
        print(f"Event creation: {results['event_creation']*1000:.2f}ms")
        print(f"Signature verification: {results['signature_verification']*1000:.2f}ms")
        print(f"Bech32 encoding: {results['bech32_encoding']*1000:.2f}ms")
        
        # Assert reasonable performance thresholds
        assert results['keypair_generation'] < 0.1, "Keypair generation too slow"
        assert results['event_creation'] < 0.05, "Event creation too slow"
        assert results['signature_verification'] < 0.02, "Signature verification too slow"
        assert results['bech32_encoding'] < 0.001, "Bech32 encoding too slow"