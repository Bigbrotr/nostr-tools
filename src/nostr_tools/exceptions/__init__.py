"""
Exceptions module for the Nostr library.

This module defines custom exceptions for error handling throughout
the nostr-tools library.

These exceptions are used exclusively by Core and Actions modules. The Utils
module uses standard Python exceptions (ValueError, TypeError, etc.) to maintain
independence and reusability.
"""

from .errors import ClientConnectionError
from .errors import ClientError
from .errors import ClientPublicationError
from .errors import ClientSubscriptionError
from .errors import ClientValidationError
from .errors import EventError
from .errors import EventValidationError
from .errors import FilterError
from .errors import FilterValidationError
from .errors import Nip11Error
from .errors import Nip11ValidationError
from .errors import Nip66Error
from .errors import Nip66ValidationError
from .errors import NostrToolsError
from .errors import RelayError
from .errors import RelayMetadataError
from .errors import RelayMetadataValidationError
from .errors import RelayValidationError

__all__ = [
    "NostrToolsError",
    # Generic error classes
    "EventError",
    "FilterError",
    "RelayError",
    "ClientError",
    "RelayMetadataError",
    "Nip11Error",
    "Nip66Error",
    # Specific error classes
    "ClientConnectionError",
    "ClientPublicationError",
    "ClientSubscriptionError",
    "ClientValidationError",
    "EventValidationError",
    "FilterValidationError",
    "RelayValidationError",
    "RelayMetadataValidationError",
    "Nip11ValidationError",
    "Nip66ValidationError",
]
