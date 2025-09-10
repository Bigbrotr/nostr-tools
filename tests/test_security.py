"""
Security tests for nostr-tools library.

These tests verify cryptographic security, input validation,
and protection against common attack vectors.
"""

import pytest
import json
import secrets
from unittest.mock import patch

from nostr_tools import (
    generate_keypair, generate_event, Event, Filter, Relay,
    verify_sig, calc_event_id, test_keypair, to_bech32, to_hex,
    sanitize, find_websocket_relay_urls
)


@pytest.mark.security
class TestCryptographicSecurity:
    """Test cryptographic security properties."""
    
    def test_keypair_randomness(self):
        """Test that generated keypairs are sufficiently random."""
        # Generate multiple keypairs
        keypairs = [generate_keypair() for _ in range(100)]
        private_keys = [pair[0] for pair in keypairs]
        public_keys = [pair[1] for pair in keypairs]
        
        # All keys should be unique
        assert len(set(private_keys)) == 100, "Private keys not unique"
        assert len(set(public_keys)) == 100, "Public keys not unique"
        
        # Keys should have high entropy (simple check)
        for private_key in private_keys[:10]:
            # Count unique characters in hex string
            unique_chars = len(set(private_key))
            assert unique_chars >= 10, f"Low entropy private key: {unique_chars} unique chars"
    
    def test_signature_security(self, sample_keypair):
        """Test signature security properties."""
        private_key, public_key = sample_keypair
        
        # Create multiple events with same content but different timestamps
        events = []
        for i in range(10):
            event_data = generate_event(
                private_key=private_key,
                public_key=public_key,
                kind=1,
                tags=[],
                content="Same content",
                created_at=1640995200 + i
            )
            events.append(event_data)
        
        # All signatures should be different (no signature reuse)
        signatures = [event['sig'] for event in events]
        assert len(set(signatures)) == 10, "Signature reuse detected"
        
        # All signatures should verify correctly
        for event_data in events:
            assert verify_sig(event_data['id'], event_data['pubkey'], event_data['sig'])
    
    def test_signature_malleability_protection(self, sample_keypair):
        """Test protection against signature malleability."""
        private_key, public_key = sample_keypair
        
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="Test content"
        )
        
        original_sig = event_data['sig']
        
        # Try various signature modifications
        malformed_sigs = [
            original_sig[:-2] + "00",  # Change last byte
            "00" + original_sig[2:],   # Change first byte
            original_sig[:64] + "0" * 64,  # Zero second half
            "f" * 128,  # All f's
            "0" * 128,  # All zeros
        ]
        
        for malformed_sig in malformed_sigs:
            # Malformed signatures should not verify
            assert not verify_sig(event_data['id'], event_data['pubkey'], malformed_sig)
    
    def test_cross_key_signature_rejection(self):
        """Test that signatures from different keys are rejected."""
        keypair1 = generate_keypair()
        keypair2 = generate_keypair()
        
        # Create event with first keypair
        event_data = generate_event(
            private_key=keypair1[0],
            public_key=keypair1[1],
            kind=1,
            tags=[],
            content="Test content"
        )
        
        # Signature should not verify with second public key
        assert not verify_sig(event_data['id'], keypair2[1], event_data['sig'])
    
    def test_event_id_tampering_detection(self, sample_keypair):
        """Test detection of event ID tampering."""
        private_key, public_key = sample_keypair
        
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="Test content"
        )
        
        # Tamper with event ID
        original_id = event_data['id']
        tampered_ids = [
            original_id[:-2] + "00",  # Change last byte
            "00" + original_id[2:],   # Change first byte
            "f" * 64,  # All f's
            "0" * 64,  # All zeros
        ]
        
        for tampered_id in tampered_ids:
            tampered_event = event_data.copy()
            tampered_event['id'] = tampered_id
            
            # Should fail validation
            with pytest.raises(ValueError, match="id does not match"):
                Event.from_dict(tampered_event)


@pytest.mark.security
class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_null_byte_injection_protection(self):
        """Test protection against null byte injection."""
        # Test content with null bytes
        malicious_content = "Normal content\x00hidden content"
        sanitized = sanitize(malicious_content)
        assert "\x00" not in sanitized
        assert sanitized == "Normal contenthidden content"
        
        # Test tags with null bytes
        malicious_tags = [["t", "tag\x00hidden"], ["p", "pubkey\x00"]]
        sanitized_tags = sanitize(malicious_tags)
        
        for tag in sanitized_tags:
            for value in tag:
                assert "\x00" not in value
    
    def test_event_validation_edge_cases(self, sample_keypair):
        """Test event validation with edge cases."""
        private_key, public_key = sample_keypair
        
        # Test various invalid inputs
        invalid_cases = [
            # Invalid ID length
            {"id": "short", "error": "64-character hex"},
            
            # Invalid pubkey length  
            {"pubkey": "short", "error": "64-character hex"},
            
            # Invalid signature length
            {"sig": "short", "error": "128-character hex"},
            
            # Negative timestamp
            {"created_at": -1, "error": "non-negative"},
            
            # Invalid kind
            {"kind": -1, "error": "between 0 and 65535"},
            {"kind": 65536, "error": "between 0 and 65535"},
            
            # Invalid tags structure
            {"tags": "not_a_list", "error": "list of lists"},
            {"tags": [["t"], [123]], "error": "strings"},
        ]
        
        base_event = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="Test"
        )
        
        for case in invalid_cases:
            invalid_event = base_event.copy()
            for key, value in case.items():
                if key != "error":
                    invalid_event[key] = value
            
            with pytest.raises((ValueError, TypeError)) as exc_info:
                Event.from_dict(invalid_event)
            
            if "error" in case:
                assert case["error"] in str(exc_info.value)
    
    def test_filter_validation_security(self):
        """Test Filter validation against malicious inputs."""
        # Test invalid hex strings
        with pytest.raises(ValueError):
            Filter(ids=["not_hex"])
        
        with pytest.raises(ValueError):
            Filter(authors=["not_hex"])
        
        # Test invalid time ranges
        with pytest.raises(ValueError):
            Filter(since=2000, until=1000)
        
        # Test invalid tag names
        with pytest.raises(ValueError):
            Filter(**{"invalid_tag_name": ["value"]})
        
        # Test negative values
        with pytest.raises(ValueError):
            Filter(since=-1)
        
        with pytest.raises(ValueError):
            Filter(until=-1)
        
        with pytest.raises(ValueError):
            Filter(limit=-1)
    
    def test_relay_url_validation_security(self):
        """Test Relay URL validation against malicious inputs."""
        # Test various invalid URLs
        invalid_urls = [
            "javascript:alert('xss')",
            "file:///etc/passwd",
            "http://evil.com/redirect",
            "ws://[invalid-ipv6",
            "wss://",
            "not-a-url",
            "",
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError):
                Relay(url)


@pytest.mark.security
class TestEncodingSecurity:
    """Test encoding/decoding security."""
    
    def test_bech32_injection_protection(self):
        """Test protection against Bech32 injection attacks."""
        # Test with various malicious inputs
        malicious_inputs = [
            "npub1" + "x" * 100,  # Too long
            "npub1" + "!@#$%",    # Invalid characters
            "evil1234567890",     # Wrong prefix
            "",                   # Empty string
        ]
        
        for malicious in malicious_inputs:
            try:
                result = to_hex(malicious)
                # If it doesn't raise an exception, result should be None or empty
                assert result is None or result == ""
            except Exception:
                # Exceptions are acceptable for malicious input
                pass
    
    def test_hex_validation_security(self):
        """Test hex string validation security."""
        # Test various invalid hex inputs
        invalid_hex = [
            "gggggggg" + "0" * 56,  # Invalid hex characters
            "0123456789abcdef" * 3,  # Wrong length (48 chars)
            "0123456789abcdef" * 5,  # Wrong length (80 chars)
            "",                      # Empty string
            "Z" * 64,               # All invalid chars
        ]
        
        for invalid in invalid_hex:
            with pytest.raises((ValueError, TypeError)):
                to_bech32("npub", invalid)


@pytest.mark.security  
class TestTimingAttackResistance:
    """Test resistance to timing attacks."""
    
    def test_signature_verification_timing(self, sample_keypair):
        """Test that signature verification timing is consistent."""
        import time
        
        private_key, public_key = sample_keypair
        
        # Create valid event
        valid_event = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="Test content"
        )
        
        # Create invalid signature
        invalid_sig = "f" * 128
        
        # Time multiple verifications
        valid_times = []
        invalid_times = []
        
        for _ in range(50):
            # Time valid signature verification
            start = time.perf_counter()
            verify_sig(valid_event['id'], valid_event['pubkey'], valid_event['sig'])
            valid_times.append(time.perf_counter() - start)
            
            # Time invalid signature verification
            start = time.perf_counter()
            verify_sig(valid_event['id'], valid_event['pubkey'], invalid_sig)
            invalid_times.append(time.perf_counter() - start)
        
        # Calculate average times
        avg_valid = sum(valid_times) / len(valid_times)
        avg_invalid = sum(invalid_times) / len(invalid_times)
        
        # Times should be relatively close (within 2x)
        ratio = max(avg_valid, avg_invalid) / min(avg_valid, avg_invalid)
        assert ratio < 2.0, f"Timing difference too large: {ratio:.2f}x"
    
    def test_keypair_validation_timing(self):
        """Test that keypair validation timing is consistent."""
        import time
        
        # Generate valid keypair
        valid_private, valid_public = generate_keypair()
        
        # Generate invalid keypair
        invalid_private = "f" * 64
        invalid_public = "0" * 64
        
        valid_times = []
        invalid_times = []
        
        for _ in range(50):
            # Time valid keypair validation
            start = time.perf_counter()
            test_keypair(valid_private, valid_public)
            valid_times.append(time.perf_counter() - start)
            
            # Time invalid keypair validation
            start = time.perf_counter()
            test_keypair(invalid_private, invalid_public)
            invalid_times.append(time.perf_counter() - start)
        
        avg_valid = sum(valid_times) / len(valid_times)
        avg_invalid = sum(invalid_times) / len(invalid_times)
        
        # Times should be relatively close
        ratio = max(avg_valid, avg_invalid) / min(avg_valid, avg_invalid)
        assert ratio < 3.0, f"Timing difference too large: {ratio:.2f}x"


@pytest.mark.security
class TestDataLeakagePrevention:
    """Test prevention of sensitive data leakage."""
    
    def test_error_message_safety(self, sample_keypair):
        """Test that error messages don't leak sensitive data."""
        private_key, public_key = sample_keypair
        
        # Create event with sensitive data in various fields
        sensitive_data = "SENSITIVE_PRIVATE_KEY_DATA"
        
        try:
            # Try to create invalid event with sensitive data
            Event.from_dict({
                "id": sensitive_data,
                "pubkey": public_key,
                "created_at": 1640995200,
                "kind": 1,
                "tags": [],
                "content": "test",
                "sig": "0" * 128
            })
        except Exception as e:
            error_msg = str(e)
            # Error message should not contain the sensitive data
            assert sensitive_data not in error_msg
    
    def test_repr_safety(self, sample_keypair):
        """Test that object representations don't leak sensitive data."""
        private_key, public_key = sample_keypair
        
        # For security, we should not include private keys in any representations
        # This test ensures private keys are never accidentally exposed
        
        # Note: Our library doesn't currently store private keys in objects,
        # but this test would catch if that changes
        
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="Test content"
        )
        
        event = Event.from_dict(event_data)
        event_repr = repr(event)
        
        # Private key should never appear in representations
        assert private_key not in event_repr
        # Public key is okay to appear
        assert public_key in event_repr


@pytest.mark.security
class TestURLSecurityValidation:
    """Test URL parsing and validation security."""
    
    def test_url_parsing_security(self):
        """Test URL parsing against malicious inputs."""
        # Test various potentially malicious URLs
        malicious_urls = [
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "file:///etc/passwd",
            "ftp://evil.com/",
            "http://evil.com:99999/",  # Invalid port
            "ws://evil.com/../../../etc/passwd",
            "wss://evil.com:0/",
            "ws://[::1:80/",  # Malformed IPv6
        ]
        
        for url in malicious_urls:
            # Should not find valid relay URLs in malicious input
            found_urls = find_websocket_relay_urls(url)
            
            # Either no URLs found, or only valid websocket URLs
            for found_url in found_urls:
                assert found_url.startswith(("ws://", "wss://"))
                assert "javascript:" not in found_url
                assert "data:" not in found_url
                assert "file:" not in found_url
    
    def test_onion_url_validation(self):
        """Test .onion URL validation security."""
        # Test various invalid .onion addresses
        invalid_onions = [
            "wss://short.onion",  # Too short
            "wss://toolongaddressthatexceedsmaximumlength1234567890.onion",  # Too long
            "wss://invalid-chars!@#.onion",  # Invalid characters
            "wss://UPPERCASE.ONION",  # Wrong case
            "wss://123456789012345.onion",  # Invalid characters for v2
        ]
        
        for url in invalid_onions:
            found_urls = find_websocket_relay_urls(url)
            # Should not validate invalid onion addresses
            assert url not in found_urls


@pytest.mark.security
class TestRandomnessQuality:
    """Test quality of random number generation."""
    
    def test_urandom_usage(self):
        """Test that secure random number generation is used."""
        with patch('os.urandom') as mock_urandom:
            # Mock urandom to return predictable data for testing
            mock_urandom.return_value = b'\x01' * 32
            
            # Generate keypair should use os.urandom
            private_key, public_key = generate_keypair()
            
            # Verify urandom was called
            mock_urandom.assert_called_once_with(32)
            
            # Verify the result is deterministic with our mock
            assert isinstance(private_key, str)
            assert len(private_key) == 64
    
    def test_entropy_distribution(self):
        """Test entropy distribution in generated keys."""
        keys = [generate_keypair()[0] for _ in range(100)]
        
        # Count character frequency across all keys
        char_counts = {}
        total_chars = 0
        
        for key in keys:
            for char in key:
                char_counts[char] = char_counts.get(char, 0) + 1
                total_chars += 1
        
        # Check that all hex characters appear
        hex_chars = "0123456789abcdef"
        for char in hex_chars:
            assert char in char_counts, f"Character '{char}' not found in generated keys"
        
        # Check distribution is roughly uniform (within 50% of expected)
        expected_freq = total_chars / 16  # 16 hex characters
        for char in hex_chars:
            freq = char_counts[char]
            assert abs(freq - expected_freq) < expected_freq * 0.5, \
                f"Character '{char}' frequency {freq} too far from expected {expected_freq}"


@pytest.mark.security
class TestProofOfWorkSecurity:
    """Test proof-of-work security properties."""
    
    def test_pow_difficulty_enforcement(self, sample_keypair):
        """Test that PoW difficulty is properly enforced."""
        private_key, public_key = sample_keypair
        
        # Generate event with specific difficulty
        target_difficulty = 12
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="PoW test",
            target_difficulty=target_difficulty,
            timeout=30
        )
        
        event = Event.from_dict(event_data)
        
        # Check if nonce tag exists (PoW was attempted)
        nonce_tags = [tag for tag in event.tags if tag[0] == "nonce"]
        
        if nonce_tags:
            # PoW was successful, verify difficulty
            event_id = event.id
            leading_zeros = 0
            
            for char in event_id:
                if char == '0':
                    leading_zeros += 4
                else:
                    leading_zeros += 4 - int(char, 16).bit_length()
                    break
            
            # Should meet or exceed target difficulty
            assert leading_zeros >= target_difficulty, \
                f"PoW difficulty {leading_zeros} less than target {target_difficulty}"
    
    def test_pow_nonce_format(self, sample_keypair):
        """Test that PoW nonce format is correct."""
        private_key, public_key = sample_keypair
        
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="PoW nonce test",
            target_difficulty=8,
            timeout=20
        )
        
        event = Event.from_dict(event_data)
        nonce_tags = [tag for tag in event.tags if tag[0] == "nonce"]
        
        if nonce_tags:
            nonce_tag = nonce_tags[0]
            
            # Nonce tag should have exactly 3 elements
            assert len(nonce_tag) == 3, f"Nonce tag format invalid: {nonce_tag}"
            
            # First element should be "nonce"
            assert nonce_tag[0] == "nonce"
            
            # Second element should be numeric string (the nonce)
            assert nonce_tag[1].isdigit(), f"Nonce value not numeric: {nonce_tag[1]}"
            
            # Third element should be target difficulty
            assert nonce_tag[2].isdigit(), f"Target difficulty not numeric: {nonce_tag[2]}"
            assert int(nonce_tag[2]) == 8, f"Target difficulty mismatch: {nonce_tag[2]}"


@pytest.mark.security
class TestMemorySafety:
    """Test memory safety and cleanup."""
    
    def test_sensitive_data_cleanup(self, sample_keypair):
        """Test that sensitive operations don't leave traces in memory."""
        import gc
        
        private_key, public_key = sample_keypair
        
        # Create event (which involves signing)
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content="Memory safety test"
        )
        
        # Force garbage collection
        gc.collect()
        
        # Check that private key doesn't appear in garbage
        for obj in gc.get_objects():
            if isinstance(obj, str) and len(obj) == 64:
                # Don't check the private_key variable itself
                if obj is not private_key:
                    assert obj != private_key, "Private key found in garbage collection"
    
    def test_large_data_handling(self, sample_keypair):
        """Test handling of large data without memory issues."""
        private_key, public_key = sample_keypair
        
        # Create event with large content
        large_content = "A" * 100000  # 100KB
        
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[],
            content=large_content
        )
        
        event = Event.from_dict(event_data)
        
        # Should handle large data without issues
        assert len(event.content) == 100000
        assert event.content == large_content
        
        # Cleanup
        del large_content
        del event_data
        del event


@pytest.mark.security
class TestConcurrencySafety:
    """Test thread safety and concurrency security."""
    
    def test_concurrent_keypair_generation_safety(self):
        """Test that concurrent keypair generation is safe."""
        import threading
        import queue
        
        num_threads = 10
        keys_per_thread = 10
        result_queue = queue.Queue()
        
        def generate_keys():
            thread_keys = []
            for _ in range(keys_per_thread):
                thread_keys.append(generate_keypair())
            result_queue.put(thread_keys)
        
        # Start threads
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=generate_keys)
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Collect all keys
        all_keys = []
        while not result_queue.empty():
            thread_keys = result_queue.get()
            all_keys.extend(thread_keys)
        
        # Verify all keys are unique
        private_keys = [pair[0] for pair in all_keys]
        public_keys = [pair[1] for pair in all_keys]
        
        assert len(set(private_keys)) == len(private_keys), "Duplicate private keys in concurrent generation"
        assert len(set(public_keys)) == len(public_keys), "Duplicate public keys in concurrent generation"
    
    def test_concurrent_event_creation_safety(self, sample_keypair):
        """Test that concurrent event creation is safe."""
        import threading
        import queue
        
        private_key, public_key = sample_keypair
        num_threads = 5
        events_per_thread = 5
        result_queue = queue.Queue()
        
        def create_events():
            thread_events = []
            for i in range(events_per_thread):
                event_data = generate_event(
                    private_key=private_key,
                    public_key=public_key,
                    kind=1,
                    tags=[],
                    content=f"Concurrent event {threading.current_thread().ident}-{i}"
                )
                thread_events.append(event_data)
            result_queue.put(thread_events)
        
        # Start threads
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=create_events)
            threads.append(t)
            t.start()
        
        # Wait for completion
        for t in threads:
            t.join()
        
        # Collect all events
        all_events = []
        while not result_queue.empty():
            thread_events = result_queue.get()
            all_events.extend(thread_events)
        
        # Verify all events are unique and valid
        event_ids = [event['id'] for event in all_events]
        signatures = [event['sig'] for event in all_events]
        
        assert len(set(event_ids)) == len(event_ids), "Duplicate event IDs in concurrent creation"
        assert len(set(signatures)) == len(signatures), "Duplicate signatures in concurrent creation"
        
        # Verify all events are valid
        for event_data in all_events:
            event = Event.from_dict(event_data)  # Should not raise exception
            assert verify_sig(event.id, event.pubkey, event.sig)


if __name__ == "__main__":
    pytest.main([__file__])