"""
Actions module for Nostr protocol operations.

This module provides high-level utility functions for interacting with
Nostr relays, including fetching events, streaming data, and testing
relay capabilities.
"""

from .actions import check_connectivity
from .actions import check_readability
from .actions import check_writability
from .actions import compute_relay_metadata
from .actions import fetch_connection
from .actions import fetch_events
from .actions import fetch_nip11
from .actions import stream_events

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
