"""
nostr-tools: A comprehensive Python library for Nostr protocol interactions.

This library provides core components for working with the Nostr protocol,
including events, relays, WebSocket clients, and cryptographic utilities.

Features:
- Event creation, validation, and signing
- Relay communication and management
- WebSocket client for real-time interactions
- Cryptographic utilities (secp256k1, bech32)
- Async/await support throughout
- Type hints for better development experience
"""

import os
import sys
from typing import Any

# Core exports that are always available
from .exceptions.errors import ClientConnectionError
from .exceptions.errors import ClientError
from .exceptions.errors import ClientPublicationError
from .exceptions.errors import ClientSubscriptionError
from .exceptions.errors import ClientValidationError
from .exceptions.errors import EventError
from .exceptions.errors import EventValidationError
from .exceptions.errors import FilterError
from .exceptions.errors import FilterValidationError
from .exceptions.errors import Nip11Error
from .exceptions.errors import Nip11ValidationError
from .exceptions.errors import Nip66Error
from .exceptions.errors import Nip66ValidationError
from .exceptions.errors import NostrToolsError
from .exceptions.errors import RelayError
from .exceptions.errors import RelayMetadataError
from .exceptions.errors import RelayMetadataValidationError
from .exceptions.errors import RelayValidationError

__author__ = "Bigbrotr"
__email__ = "hello@bigbrotr.com"

# Version handling with setuptools-scm
try:
    # Try to get version from setuptools-scm generated file
    from ._version import version as __version__
except ImportError:
    try:
        # Fallback to setuptools-scm directly
        from importlib.metadata import version

        __version__ = version("nostr-tools")
    except ImportError:
        try:
            # Direct setuptools-scm fallback
            from setuptools_scm import get_version

            __version__ = get_version()
        except (ImportError, LookupError):
            # Final fallback
            __version__ = "1.0.0-dev"

# Detect documentation build environment
_BUILDING_DOCS = (
    "sphinx" in sys.modules
    or "sphinx.ext.autodoc" in sys.modules
    or os.environ.get("SPHINX_BUILD") == "1"
    or "sphinx-build" in " ".join(sys.argv)
    or "build_sphinx" in sys.argv
)

if _BUILDING_DOCS:
    # Direct imports for documentation - Sphinx needs real objects
    from .actions.actions import check_connectivity
    from .actions.actions import check_readability
    from .actions.actions import check_writability
    from .actions.actions import fetch_events
    from .actions.actions import fetch_nip11
    from .actions.actions import fetch_nip66
    from .actions.actions import fetch_relay_metadata
    from .actions.actions import stream_events
    from .core.client import Client
    from .core.event import Event
    from .core.filter import Filter
    from .core.relay import Relay
    from .core.relay_metadata import RelayMetadata
    from .utils.utils import TLDS
    from .utils.utils import URI_GENERIC_REGEX
    from .utils.utils import calc_event_id
    from .utils.utils import find_ws_urls
    from .utils.utils import generate_event
    from .utils.utils import generate_keypair
    from .utils.utils import sanitize
    from .utils.utils import sig_event_id
    from .utils.utils import to_bech32
    from .utils.utils import to_hex
    from .utils.utils import validate_keypair
    from .utils.utils import verify_sig

else:
    # Lazy loading for runtime - improves import performance
    _LAZY_IMPORTS: dict[str, tuple[str, str]] = {
        # Core classes
        "Event": ("nostr_tools.core.event", "Event"),
        "Relay": ("nostr_tools.core.relay", "Relay"),
        "RelayMetadata": ("nostr_tools.core.relay_metadata", "RelayMetadata"),
        "Client": ("nostr_tools.core.client", "Client"),
        "Filter": ("nostr_tools.core.filter", "Filter"),
        # Cryptographic utilities
        "generate_keypair": ("nostr_tools.utils.utils", "generate_keypair"),
        "generate_event": ("nostr_tools.utils.utils", "generate_event"),
        "calc_event_id": ("nostr_tools.utils.utils", "calc_event_id"),
        "verify_sig": ("nostr_tools.utils.utils", "verify_sig"),
        "sig_event_id": ("nostr_tools.utils.utils", "sig_event_id"),
        "validate_keypair": ("nostr_tools.utils.utils", "validate_keypair"),
        # Encoding utilities
        "to_bech32": ("nostr_tools.utils.utils", "to_bech32"),
        "to_hex": ("nostr_tools.utils.utils", "to_hex"),
        # Network and parsing utilities
        "find_ws_urls": ("nostr_tools.utils.utils", "find_ws_urls"),
        "sanitize": ("nostr_tools.utils.utils", "sanitize"),
        # Constants
        "TLDS": ("nostr_tools.utils.utils", "TLDS"),
        "URI_GENERIC_REGEX": ("nostr_tools.utils.utils", "URI_GENERIC_REGEX"),
        # High-level actions
        "fetch_events": ("nostr_tools.actions.actions", "fetch_events"),
        "stream_events": ("nostr_tools.actions.actions", "stream_events"),
        "fetch_nip11": ("nostr_tools.actions.actions", "fetch_nip11"),
        "check_connectivity": ("nostr_tools.actions.actions", "check_connectivity"),
        "check_readability": ("nostr_tools.actions.actions", "check_readability"),
        "check_writability": ("nostr_tools.actions.actions", "check_writability"),
        "fetch_nip66": ("nostr_tools.actions.actions", "fetch_nip66"),
        "fetch_relay_metadata": ("nostr_tools.actions.actions", "fetch_relay_metadata"),
    }

    # Cache for loaded modules to avoid repeated imports
    _module_cache: dict[str, Any] = {}

    class _LazyLoader:
        """Lazy loader that imports modules only when accessed."""

        def __init__(self, module_path: str, attr_name: str) -> None:
            self.module_path = module_path
            self.attr_name = attr_name

        def _get_attr(self) -> Any:
            """
            Import the module and get the attribute.

            This method implements lazy loading by importing the module only when
            the attribute is accessed. It uses caching to avoid repeated imports.

            Returns:
                Any: The requested attribute from the module

            Raises:
                ImportError: If the module or attribute cannot be imported
            """
            cache_key = f"{self.module_path}.{self.attr_name}"

            if cache_key in _module_cache:
                return _module_cache[cache_key]

            try:
                module = __import__(self.module_path, fromlist=[self.attr_name])
                attr = getattr(module, self.attr_name)
                _module_cache[cache_key] = attr
                return attr
            except (ImportError, AttributeError) as e:
                raise ImportError(
                    f"Cannot import {self.attr_name} from {self.module_path}: {e}"
                ) from e

    def __getattr__(name: str) -> Any:
        """
        Provide lazy loading for module attributes.

        This function implements lazy loading by only importing modules when
        their attributes are accessed. This improves startup performance
        by deferring imports until they're actually needed.

        Args:
            name: Name of the attribute to load

        Returns:
            Any: The requested attribute from the appropriate module

        Raises:
            AttributeError: If the attribute is not found in any module
        """
        if name in _LAZY_IMPORTS:
            module_path, attr_name = _LAZY_IMPORTS[name]
            return _LazyLoader(module_path, attr_name)._get_attr()

        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Public API - symbols available when importing the package
__all__ = [
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    # Core classes
    "Client",
    "Event",
    "Filter",
    "Relay",
    "RelayMetadata",
    # Exceptions
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
    # Cryptographic functions
    "calc_event_id",
    "generate_event",
    "generate_keypair",
    "sig_event_id",
    "validate_keypair",
    "verify_sig",
    # Encoding functions
    "to_bech32",
    "to_hex",
    # Utility functions
    "find_ws_urls",
    "sanitize",
    # Constants
    "TLDS",
    "URI_GENERIC_REGEX",
    # High-level actions
    "check_connectivity",
    "check_readability",
    "check_writability",
    "fetch_relay_metadata",
    "fetch_nip66",
    "fetch_events",
    "fetch_nip11",
    "stream_events",
]


def __dir__() -> list[str]:
    """
    Return available attributes for tab completion and introspection.

    This function provides the list of public symbols for the module,
    used by Python's dir() function and IDE auto-completion.

    Returns:
        list[str]: Sorted list of all public attribute names exported
            by the nostr_tools package.

    Examples:
        >>> import nostr_tools
        >>> attrs = dir(nostr_tools)
        >>> 'Event' in attrs
        True
        >>> 'generate_keypair' in attrs
        True
    """
    return sorted(__all__)


def get_info() -> dict[str, str]:
    """
    Get package metadata and version information.

    Returns comprehensive information about the nostr-tools package including
    name, version, author, and description.

    Returns:
        dict[str, str]: Dictionary containing package metadata with keys:
            - name: Package name ("nostr-tools")
            - version: Current package version
            - author: Package author
            - email: Author contact email
            - description: Brief package description

    Examples:
        >>> import nostr_tools
        >>> info = nostr_tools.get_info()
        >>> print(f"Using {info['name']} version {info['version']}")
        Using nostr-tools version 1.0.0

        >>> info = nostr_tools.get_info()
        >>> for key, value in info.items():
        ...     print(f"{key}: {value}")
    """
    return {
        "name": "nostr-tools",
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "description": "A comprehensive Python library for Nostr protocol interactions",
    }
