"""
Custom exceptions for nostr_tools library.

This module defines custom exception classes used throughout the nostr-tools
library to provide specific error handling for Nostr protocol operations.

These exceptions are used exclusively by Core and Actions modules. The Utils
module uses standard Python exceptions (ValueError, TypeError, etc.) to maintain
independence and reusability.
"""


class NostrToolsError(Exception):
    """
    Base exception for all nostr-tools errors.

    All custom exceptions in this library inherit from this base class,
    making it easy to catch any nostr-tools specific error.
    """

    pass


# Generic error classes for different modules
class EventError(NostrToolsError):
    """
    Base exception for event-related errors.

    This is the base class for all errors related to event creation,
    validation, and processing in the nostr-tools library.
    """

    pass


class FilterError(NostrToolsError):
    """
    Base exception for filter-related errors.

    This is the base class for all errors related to subscription filter
    creation, validation, and processing in the nostr-tools library.
    """

    pass


class RelayError(NostrToolsError):
    """
    Base exception for relay-related errors.

    This is the base class for all errors related to relay configuration,
    validation, and processing in the nostr-tools library.
    """

    pass


class ClientError(NostrToolsError):
    """
    Base exception for client-related errors.

    This is the base class for all errors related to client operations,
    connections, subscriptions, and publications in the nostr-tools library.
    """

    pass


class RelayMetadataError(NostrToolsError):
    """
    Base exception for relay metadata-related errors.

    This is the base class for all errors related to relay metadata
    fetching, validation, and processing in the nostr-tools library.
    """

    pass


class Nip11Error(RelayMetadataError):
    """
    Base exception for NIP-11 related errors.

    This is the base class for all errors related to NIP-11 relay
    information fetching and validation in the nostr-tools library.
    """

    pass


class Nip66Error(RelayMetadataError):
    """
    Base exception for NIP-66 related errors.

    This is the base class for all errors related to NIP-66 relay
    monitoring data fetching and validation in the nostr-tools library.
    """

    pass


class ClientConnectionError(ClientError):
    """
    Exception raised for client connection errors.

    Raised when there are issues connecting to, communicating with, or
    maintaining connections to Nostr relays.

    Args:
        message (str): Description of the connection error

    Examples:
        >>> raise ClientConnectionError("Failed to connect to wss://relay.example.com")
    """

    pass


class EventValidationError(EventError):
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


class FilterValidationError(FilterError):
    """
    Exception raised when filter validation fails.

    Raised when a subscription filter contains invalid parameters
    or values that don't conform to the Nostr protocol specification.

    Args:
        message (str): Description of the filter validation error

    Examples:
        >>> raise FilterValidationError("limit must be a non-negative integer")
    """

    pass


class RelayValidationError(RelayError):
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


class ClientValidationError(ClientError):
    """
    Exception raised when client configuration validation fails.

    Raised when:
    - Invalid relay instance
    - Invalid timeout value
    - Missing SOCKS5 proxy for Tor relays
    - Type mismatches in client configuration

    Args:
        message (str): Description of the client validation error

    Examples:
        >>> raise ClientValidationError("timeout must be non-negative")
    """

    pass


class RelayMetadataValidationError(RelayMetadataError):
    """
    Exception raised when relay metadata validation fails.

    Raised when:
    - Invalid relay instance
    - Invalid timestamp
    - Type mismatches in metadata fields

    Args:
        message (str): Description of the metadata validation error

    Examples:
        >>> raise RelayMetadataValidationError("generated_at must be non-negative")
    """

    pass


class Nip11ValidationError(Nip11Error):
    """
    Exception raised when NIP-11 relay information validation fails.

    Raised when:
    - Invalid supported NIPs format
    - Invalid limitation fields
    - Non-JSON serializable extra fields
    - Type mismatches in NIP-11 fields

    Args:
        message (str): Description of the NIP-11 validation error

    Examples:
        >>> raise Nip11ValidationError("supported_nips must be a list of integers")
    """

    pass


class Nip66ValidationError(Nip66Error):
    """
    Exception raised when NIP-66 relay monitoring validation fails.

    Raised when:
    - Invalid boolean flags
    - Invalid RTT values
    - Inconsistent flag and RTT combinations
    - Type mismatches in NIP-66 fields

    Args:
        message (str): Description of the NIP-66 validation error

    Examples:
        >>> raise Nip66ValidationError("rtt_open must be provided when openable is True")
    """

    pass


class ClientSubscriptionError(ClientError):
    """
    Exception raised for client subscription-related errors.

    Raised when:
    - Subscription creation fails
    - Invalid subscription ID
    - Subscription already exists or doesn't exist

    Args:
        message (str): Description of the subscription error

    Examples:
        >>> raise ClientSubscriptionError("Subscription not found: sub_123")
    """

    pass


class ClientPublicationError(ClientError):
    """
    Exception raised when client event publishing fails.

    Raised when an event cannot be published to a relay due to:
    - Connection issues
    - Relay rejection
    - Timeout

    Args:
        message (str): Description of the publication error

    Examples:
        >>> raise ClientPublicationError("Failed to publish event to relay")
    """

    pass
