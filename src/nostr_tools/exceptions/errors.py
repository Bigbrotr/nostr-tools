"""
Custom exceptions for nostr_tools library.

This module defines custom exception classes used throughout the nostr-tools
library to provide specific error handling for Nostr protocol operations.
"""


class NostrToolsError(Exception):
    """
    Base exception for all nostr-tools errors.

    All custom exceptions in this library inherit from this base class,
    making it easy to catch any nostr-tools specific error.
    """

    pass


class RelayConnectionError(NostrToolsError):
    """
    Exception raised for relay connection errors.

    Raised when there are issues connecting to, communicating with, or
    maintaining connections to Nostr relays.

    Args:
        message (str): Description of the connection error

    Examples:
        >>> raise RelayConnectionError("Failed to connect to wss://relay.example.com")
    """

    pass


class EventValidationError(NostrToolsError):
    """
    Exception raised when event validation fails.

    Raised when an event fails validation checks such as:
    - Invalid signature
    - Incorrect event ID
    - Invalid field formats
    - Null characters in content

    Args:
        message (str): Description of the validation error

    Examples:
        >>> raise EventValidationError("sig is not a valid signature for the event")
    """

    pass


class KeyValidationError(NostrToolsError):
    """
    Exception raised when cryptographic key validation fails.

    Raised when:
    - Key format is invalid
    - Key pair doesn't match
    - Key length is incorrect

    Args:
        message (str): Description of the key validation error

    Examples:
        >>> raise KeyValidationError("private_key must be a 64-character hex string")
    """

    pass


class FilterValidationError(NostrToolsError):
    """
    Exception raised when filter validation fails.

    Raised when a subscription filter contains invalid parameters
    or values that don't conform to the Nostr protocol specification.

    Args:
        message (str): Description of the filter validation error

    Examples:
        >>> raise FilterValidationError("limit must be a positive integer")
    """

    pass


class RelayValidationError(NostrToolsError):
    """
    Exception raised when relay configuration validation fails.

    Raised when:
    - Relay URL is invalid or malformed
    - Network type doesn't match URL
    - Required configuration is missing

    Args:
        message (str): Description of the relay validation error

    Examples:
        >>> raise RelayValidationError("url must be a valid WebSocket URL")
    """

    pass


class SubscriptionError(NostrToolsError):
    """
    Exception raised for subscription-related errors.

    Raised when:
    - Subscription creation fails
    - Invalid subscription ID
    - Subscription already exists or doesn't exist

    Args:
        message (str): Description of the subscription error

    Examples:
        >>> raise SubscriptionError("Subscription not found: sub_123")
    """

    pass


class PublishError(NostrToolsError):
    """
    Exception raised when event publishing fails.

    Raised when an event cannot be published to a relay due to:
    - Connection issues
    - Relay rejection
    - Timeout

    Args:
        message (str): Description of the publish error

    Examples:
        >>> raise PublishError("Failed to publish event to relay")
    """

    pass


class EncodingError(NostrToolsError):
    """
    Exception raised for encoding/decoding errors.

    Raised when:
    - Bech32 encoding/decoding fails
    - Invalid hex string conversion
    - Unsupported encoding format

    Args:
        message (str): Description of the encoding error

    Examples:
        >>> raise EncodingError("Invalid bech32 string format")
    """

    pass
