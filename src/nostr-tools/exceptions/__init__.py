"""
Exceptions module for the Nostr library.

This module defines custom exceptions for error handling throughout
the nostr-tools library.
"""

from .errors import RelayConnectionError

__all__ = ["RelayConnectionError"]
