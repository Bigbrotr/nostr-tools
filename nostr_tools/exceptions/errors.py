"""Custom exception classes for Nostr protocol operations."""


class NostrError(Exception):
    """Base exception for all Nostr-related errors."""
    pass


class EventValidationError(NostrError):
    """Raised when event validation fails."""
    pass


class RelayConnectionError(NostrError):
    """Raised when relay connection or communication fails."""
    pass


class CryptographicError(NostrError):
    """Raised when cryptographic operations fail."""
    pass


class SubscriptionError(NostrError):
    """Raised when subscription operations fail."""
    pass


class FilterError(NostrError):
    """Raised when event filters are invalid."""
    pass


class ProtocolError(NostrError):
    """Raised when protocol violations occur."""
    pass
