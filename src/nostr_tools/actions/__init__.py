"""
Actions module for Nostr protocol operations.

This module provides high-level utility functions for interacting with
Nostr relays, including fetching events, streaming data, and testing
relay capabilities.
"""

from .actions import check_connectivity
from .actions import check_readability
from .actions import check_writability
from .actions import fetch_events
from .actions import fetch_nip11
from .actions import fetch_nip66
from .actions import fetch_relay_metadata
from .actions import stream_events

__all__ = [
    "check_connectivity",
    "check_readability",
    "check_writability",
    "fetch_relay_metadata",
    "fetch_nip66",
    "fetch_events",
    "fetch_nip11",
    "stream_events",
]
