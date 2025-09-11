"""
Utility functions for Nostr protocol operations.

This module provides helper functions for various Nostr protocol operations
including WebSocket relay discovery, data sanitization, cryptographic 
operations, and encoding utilities.
"""

from .utils import (
    # WebSocket relay utilities
    find_websocket_relay_urls,

    # Data sanitization
    sanitize,

    # Event operations
    calc_event_id,
    verify_sig,
    sig_event_id,
    generate_event,

    # Key operations
    validate_keypair,
    generate_keypair,

    # Encoding utilities
    to_bech32,
    to_hex,

    # Constants
    TLDS,
    URI_GENERIC_REGEX,

    # Response parsing
    parse_nip11_response,
    parse_connection_response,
)

__all__ = [
    # WebSocket relay utilities
    "find_websocket_relay_urls",

    # Data sanitization
    "sanitize",

    # Event operations
    "calc_event_id",
    "verify_sig",
    "sig_event_id",
    "generate_event",

    # Key operations
    "validate_keypair",
    "generate_keypair",

    # Encoding utilities
    "to_bech32",
    "to_hex",

    # Constants
    "TLDS",
    "URI_GENERIC_REGEX",

    # Response parsing
    "parse_nip11_response",
    "parse_connection_response",
]
