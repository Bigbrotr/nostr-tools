"""
nostr-tools: A Python library for Nostr protocol interactions.

This library provides core components for working with the Nostr protocol,
including events, relays, WebSocket clients, and cryptographic utilities.
"""

from .core.event import Event
from .core.relay import Relay
from .core.relay_metadata import RelayMetadata
from .client.websocket_client import NostrWebSocketClient
from .client.event_fetcher import fetch_events
from .utils.crypto import (
    calc_event_id,
    verify_sig,
    generate_event,
    test_keypair,
    to_bech32,
    to_hex,
)
from .utils.network import find_websocket_relay_urls, sanitize
from .utils.validation import validate_event, validate_relay_url
from .exceptions.errors import (
    NostrError,
    EventValidationError,
    RelayConnectionError,
    CryptographicError,
)

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    # Core classes
    "Event",
    "Relay",
    "RelayMetadata",
    # Client classes
    "NostrWebSocketClient",
    "fetch_events",
    # Crypto utilities
    "calc_event_id",
    "verify_sig",
    "generate_event",
    "test_keypair",
    "to_bech32",
    "to_hex",
    # Network utilities
    "find_websocket_relay_urls",
    "sanitize",
    # Validation utilities
    "validate_event",
    "validate_relay_url",
    # Exceptions
    "NostrError",
    "EventValidationError",
    "RelayConnectionError",
    "CryptographicError",
]
