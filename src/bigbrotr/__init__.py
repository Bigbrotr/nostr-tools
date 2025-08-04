"""
BigBrotr - A comprehensive Python library for NOSTR protocol and relay management

This library provides a complete toolkit for working with the NOSTR protocol,
including event management, relay operations, and PostgreSQL database integration.

Main Components:
- Bigbrotr: Main database interface for PostgreSQL operations
- Event: NOSTR event representation with validation
- Relay: NOSTR relay management with network detection
- RelayMetadata: Comprehensive relay metadata and performance tracking

Example Usage:
    >>> from bigbrotr import Bigbrotr, Event, Relay
    >>> 
    >>> # Initialize database connection
    >>> db = Bigbrotr("localhost", 5432, "user", "password", "bigbrotr_db")
    >>> db.connect()
    >>> 
    >>> # Create a relay
    >>> relay = Relay("wss://relay.nostr.com")
    >>> 
    >>> # Insert relay into database
    >>> db.insert_relay(relay)
    >>> 
    >>> # Create an event (example data)
    >>> event_data = {
    ...     "id": "a" * 64,
    ...     "pubkey": "b" * 64,
    ...     "created_at": 1234567890,
    ...     "kind": 1,
    ...     "tags": [["t", "test"]],
    ...     "content": "Hello NOSTR!",
    ...     "sig": "c" * 128
    ... }
    >>> event = Event.from_dict(event_data)
    >>> 
    >>> # Insert event into database
    >>> db.insert_event(event, relay)
    >>> 
    >>> db.close()
"""

from .bigbrotr import Bigbrotr
from .event import Event
from .relay import Relay
from .relay_metadata import RelayMetadata
from . import utils

__version__ = "0.1.0"
__author__ = "BigBrotr Team"
__email__ = "hello@bigbrotr.com"
__license__ = "MIT"

# Public API
__all__ = [
    "Bigbrotr",
    "Event", 
    "Relay",
    "RelayMetadata",
    "utils",
    "__version__",
]

# Version info
VERSION = (0, 1, 0)

def get_version():
    """Return the version string."""
    return __version__