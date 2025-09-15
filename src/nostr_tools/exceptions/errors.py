"""
Custom exceptions for nostr_tools library.

This module defines custom exception classes used throughout the nostr-tools
library to provide specific error handling for Nostr protocol operations.
"""


class RelayConnectionError(Exception):
    """
    Custom exception for relay connection errors.

    Raised when there are issues connecting to, communicating with, or
    maintaining connections to Nostr relays.

    Args:
        message (str): Description of the connection error
    """

    pass
