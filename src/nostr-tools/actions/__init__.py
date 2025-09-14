"""
Actions module for Nostr protocol operations.

This module provides high-level utility functions for interacting with
Nostr relays, including fetching events, streaming data, and testing
relay capabilities.
"""

from .actions import (
    check_connectivity,
    check_readability,
    check_writability,
    compute_relay_metadata,
    fetch_connection,
    fetch_events,
    fetch_nip11,
    stream_events,
)

__all__ = [
    "check_connectivity",
    "check_readability",
    "check_writability",
    "compute_relay_metadata",
    "fetch_connection",
    "fetch_events",
    "fetch_nip11",
    "stream_events",
]
