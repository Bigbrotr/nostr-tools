"""
Actions module for Nostr protocol operations.

This module provides high-level utility functions for interacting with 
Nostr relays, including fetching events, streaming data, and testing 
relay capabilities.
"""

from .actions import (
    fetch_events,
    stream_events,
    fetch_nip11,
    check_connectivity,
    check_readability,
    check_writability,
    fetch_connection,
    compute_relay_metadata,
)

__all__ = [
    "fetch_events",
    "stream_events",
    "fetch_nip11",
    "check_connectivity",
    "check_readability",
    "check_writability",
    "fetch_connection",
    "compute_relay_metadata",
]
