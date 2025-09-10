"""
Pytest configuration and shared fixtures for nostr-tools tests.

This file contains pytest configuration, markers, and shared fixtures
that are used across multiple test files.
"""

import pytest
import asyncio
import time
from typing import Generator, Tuple
from unittest.mock import Mock, AsyncMock

from nostr_tools import (
    generate_keypair, generate_event, Event, Relay, Client, Filter
)
from tests import TEST_RELAY_URL, TEST_TIMEOUT, SKIP_INTEGRATION


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Fast unit tests")
    config.addinivalue_line("markers", "integration: Integration tests requiring network")
    config.addinivalue_line("markers", "slow: Slow tests that take time to complete")
    config.addinivalue_line("markers", "security: Security-focused tests")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add unit marker to non-integration tests
        if "test_integration" not in item.nodeid and "integration" not in item.keywords:
            item.add_marker(pytest.mark.unit)
        
        # Add slow marker to proof-of-work and network tests
        if any(keyword in item.name.lower() for keyword in ["pow", "proof_of_work", "stream", "network"]):
            item.add_marker(pytest.mark.slow)
        
        # Add security marker to cryptographic tests
        if any(keyword in item.name.lower() for keyword in ["key", "sign", "verify", "crypto"]):
            item.add_marker(pytest.mark.security)


# Skip integration tests if requested
skip_integration = pytest.mark.skipif(
    SKIP_INTEGRATION,
    reason="Integration tests skipped (NOSTR_SKIP_INTEGRATION=true)"
)


@pytest.fixture
def sample_keypair() -> Tuple[str, str]:
    """Generate a sample key pair for testing."""
    return generate_keypair()


@pytest.fixture
def sample_event_data(sample_keypair) -> dict:
    """Generate sample event data for testing."""
    private_key, public_key = sample_keypair
    return generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=1,
        tags=[["t", "test"]],
        content="Test event content"
    )


@pytest.fixture
def sample_event(sample_event_data) -> Event:
    """Create a sample Event object for testing."""
    return Event.from_dict(sample_event_data)


@pytest.fixture
def sample_relay() -> Relay:
    """Create a sample Relay object for testing."""
    return Relay(TEST_RELAY_URL)


@pytest.fixture
def sample_client(sample_relay) -> Client:
    """Create a sample Client object for testing."""
    return Client(sample_relay, timeout=TEST_TIMEOUT)


@pytest.fixture
def sample_filter() -> Filter:
    """Create a sample Filter object for testing."""
    return Filter(kinds=[1], limit=10)


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket for testing."""
    mock_ws = AsyncMock()
    mock_ws.closed = False
    mock_ws.receive = AsyncMock()
    mock_ws.send_str = AsyncMock()
    mock_ws.close = AsyncMock()
    return mock_ws


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session for testing."""
    mock_session = AsyncMock()
    mock_session.ws_connect = AsyncMock()
    mock_session.get = AsyncMock()
    mock_session.close = AsyncMock()
    return mock_session


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def fixed_time():
    """Provide a fixed timestamp for deterministic testing."""
    return 1640995200  # 2022-01-01 00:00:00 UTC


@pytest.fixture
def sample_metadata_event(sample_keypair, fixed_time) -> dict:
    """Generate a sample metadata event (kind 0)."""
    private_key, public_key = sample_keypair
    metadata = {
        "name": "Test User",
        "about": "A test user for nostr-tools",
        "picture": "https://example.com/avatar.jpg"
    }
    
    return generate_event(
        private_key=private_key,
        public_key=public_key,
        kind=0,
        tags=[],
        content=json.dumps(metadata),
        created_at=fixed_time
    )


@pytest.fixture
def sample_tags() -> list:
    """Provide sample tags for testing."""
    return [
        ["t", "nostr"],
        ["t", "python"],
        ["p", "0123456789abcdef" * 4],
        ["e", "fedcba9876543210" * 4]
    ]


@pytest.fixture
def invalid_event_data() -> dict:
    """Provide invalid event data for error testing."""
    return {
        "id": "invalid_id",
        "pubkey": "invalid_pubkey", 
        "created_at": -1,
        "kind": 999999,
        "tags": "invalid_tags",
        "content": "test content",
        "sig": "invalid_signature"
    }


# Utility functions for tests
import json


def create_mock_nip11_response():
    """Create a mock NIP-11 response for testing."""
    return {
        "name": "Test Relay",
        "description": "A test relay for nostr-tools",
        "pubkey": "0123456789abcdef" * 4,
        "contact": "test@example.com",
        "supported_nips": [1, 2, 9, 11, 12, 15, 16, 20, 22],
        "software": "test-relay",
        "version": "1.0.0",
        "limitation": {
            "max_message_length": 16384,
            "max_subscriptions": 20,
            "max_filters": 100,
            "max_limit": 5000,
            "max_subid_length": 100,
            "min_prefix": 4,
            "max_event_tags": 100,
            "max_content_length": 8196,
            "min_pow_difficulty": 0,
            "auth_required": False,
            "payment_required": False
        }
    }


# Performance testing utilities
@pytest.fixture
def performance_timer():
    """Utility for measuring test performance."""
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.perf_counter()
        
        def stop(self):
            self.end_time = time.perf_counter()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


# Test data generators
def generate_test_events(count: int, keypair: Tuple[str, str] = None) -> list:
    """Generate multiple test events."""
    if keypair is None:
        keypair = generate_keypair()
    
    private_key, public_key = keypair
    events = []
    
    for i in range(count):
        event_data = generate_event(
            private_key=private_key,
            public_key=public_key,
            kind=1,
            tags=[["t", f"test{i}"]],
            content=f"Test event {i}"
        )
        events.append(Event.from_dict(event_data))
    
    return events


def generate_hex_string(length: int) -> str:
    """Generate a hex string of specified length."""
    import secrets
    return secrets.token_hex(length // 2)


# Add module-level exports
__all__ = [
    "skip_integration",
    "create_mock_nip11_response", 
    "generate_test_events",
    "generate_hex_string"
]