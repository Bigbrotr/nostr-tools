"""
nostr-tools: A Python library for Nostr protocol interactions.

This library provides core components for working with the Nostr protocol,
including events, relays, WebSocket clients, and cryptographic utilities.

The main components include:
- Event: Nostr event representation and validation
- Relay: Nostr relay configuration
- RelayMetadata: Relay information and capabilities
- Client: WebSocket client for relay communication
- Filter: Event filtering for subscriptions
- Utility functions for key management, event signing, and more
- Custom exceptions for error handling
- High-level actions for common Nostr operations
"""

from .core.event import Event
from .core.relay import Relay
from .core.relay_metadata import RelayMetadata
from .core.client import Client
from .core.filter import Filter
from .actions import *
from .utils import *
from .exceptions.errors import RelayConnectionError

__version__ = "0.1.0"
__author__ = "Bigbrotr"
__email__ = "hello@bigbrotr.com"

__all__ = [
    # Core classes
    "Event",
    "Relay",
    "RelayMetadata",
    "Client",
    "Filter",
    # Utilities
    "find_websocket_relay_urls",
    "sanitize",
    "calc_event_id",
    "verify_sig",
    "sig_event_id",
    "generate_event",
    "test_keypair",
    "generate_keypair",
    "to_bech32",
    "to_hex",
    "TLDS",
    "URI_GENERIC_REGEX",
    "parse_nip11_response",
    "parse_connection_response",
    # Exceptions
    "RelayConnectionError",
    # Actions
    "fetch_events",
    "stream_events",
    "fetch_nip11",
    "check_connectivity",
    "check_readability",
    "check_writability",
    "fetch_connection",
    "compute_relay_metadata",
]
