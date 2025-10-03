"""
Shared pytest fixtures for nostr-tools tests.

This module provides reusable fixtures for testing the nostr-tools library,
including mock data, keypairs, events, and client configurations.
"""

import time
from typing import Any
from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

# ============================================================================
# Test Data Fixtures
# ============================================================================


@pytest.fixture
def valid_keypair() -> tuple[str, str]:
    """Generate a valid keypair for testing."""
    from nostr_tools import generate_keypair

    return generate_keypair()


@pytest.fixture
def valid_private_key(valid_keypair: tuple[str, str]) -> str:
    """Provide a valid private key."""
    return valid_keypair[0]


@pytest.fixture
def valid_public_key(valid_keypair: tuple[str, str]) -> str:
    """Provide a valid public key."""
    return valid_keypair[1]


@pytest.fixture
def valid_event_dict(valid_private_key: str, valid_public_key: str) -> dict[str, Any]:
    """Generate a valid event dictionary for testing."""
    from nostr_tools import generate_event

    return generate_event(
        private_key=valid_private_key,
        public_key=valid_public_key,
        kind=1,
        tags=[["t", "test"]],
        content="Test event content",
        created_at=int(time.time()),
    )


@pytest.fixture
def valid_event(valid_event_dict: dict[str, Any]) -> Any:
    """Create a valid Event instance for testing."""
    from nostr_tools.core.event import Event

    return Event.from_dict(valid_event_dict)


@pytest.fixture
def valid_filter_dict() -> dict[str, Any]:
    """Provide a valid filter dictionary."""
    return {
        "ids": ["a" * 64],
        "authors": ["b" * 64],
        "kinds": [1, 2],
        "since": 1000000,
        "until": 2000000,
        "limit": 10,
        "tags": {"e": ["event1", "event2"]},
    }


@pytest.fixture
def valid_filter(valid_filter_dict: dict[str, Any]) -> Any:
    """Create a valid Filter instance for testing."""
    from nostr_tools.core.filter import Filter

    return Filter.from_dict(valid_filter_dict)


@pytest.fixture
def valid_relay_url() -> str:
    """Provide a valid relay URL."""
    return "wss://relay.damus.io"


@pytest.fixture
def valid_relay(valid_relay_url: str) -> Any:
    """Create a valid Relay instance for testing."""
    from nostr_tools.core.relay import Relay

    return Relay(url=valid_relay_url)


@pytest.fixture
def tor_relay_url() -> str:
    """Provide a valid Tor relay URL."""
    return "wss://oxtrdevav64z64yb7x6rjg4ntzqjhedm5b5zjqulugknhzr46ny2qbad.onion"


@pytest.fixture
def tor_relay(tor_relay_url: str) -> Any:
    """Create a valid Tor Relay instance for testing."""
    from nostr_tools.core.relay import Relay

    return Relay(url=tor_relay_url)


@pytest.fixture
def socks5_proxy_url() -> str:
    """Provide a SOCKS5 proxy URL for Tor testing."""
    return "socks5://localhost:9050"


@pytest.fixture
def valid_client(valid_relay: Any) -> Any:
    """Create a valid Client instance for testing."""
    from nostr_tools.core.client import Client

    return Client(relay=valid_relay, timeout=10)


@pytest.fixture
def tor_client(tor_relay: Any, socks5_proxy_url: str) -> Any:
    """Create a valid Tor Client instance for testing."""
    from nostr_tools.core.client import Client

    return Client(relay=tor_relay, timeout=10, socks5_proxy_url=socks5_proxy_url)


@pytest.fixture
def valid_nip11_dict() -> dict[str, Any]:
    """Provide a valid NIP-11 metadata dictionary."""
    return {
        "name": "Test Relay",
        "description": "A test relay for unit tests",
        "pubkey": "a" * 64,
        "contact": "test@example.com",
        "supported_nips": [1, 2, 11],
        "software": "test-relay",
        "version": "1.0.0",
        "limitation": {"max_message_length": 16384, "max_subscriptions": 20},
    }


@pytest.fixture
def valid_nip66_dict() -> dict[str, Any]:
    """Provide a valid NIP-66 metadata dictionary."""
    return {
        "openable": True,
        "readable": True,
        "writable": True,
        "rtt_open": 100,
        "rtt_read": 50,
        "rtt_write": 75,
    }


@pytest.fixture
def valid_relay_metadata_dict(
    valid_relay: Any, valid_nip11_dict: dict[str, Any], valid_nip66_dict: dict[str, Any]
) -> dict[str, Any]:
    """Provide a valid RelayMetadata dictionary."""
    return {
        "relay": valid_relay.to_dict(),
        "nip11": valid_nip11_dict,
        "nip66": valid_nip66_dict,
        "generated_at": int(time.time()),
    }


# ============================================================================
# Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_websocket() -> AsyncMock:
    """Create a mock WebSocket connection."""
    ws = AsyncMock()
    ws.closed = False
    ws.send_str = AsyncMock()
    ws.close = AsyncMock()
    ws.receive = AsyncMock()
    return ws


@pytest.fixture
def mock_session(mock_websocket: AsyncMock) -> AsyncMock:
    """Create a mock aiohttp session."""
    session = AsyncMock()
    session.ws_connect = AsyncMock(return_value=mock_websocket)
    session.close = AsyncMock()
    session.get = MagicMock()
    return session


# ============================================================================
# Async Test Utilities
# ============================================================================


# Event loop fixture removed - using pytest-asyncio default


# ============================================================================
# Test Markers Configuration
# ============================================================================


def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
