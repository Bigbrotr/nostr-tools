"""
nostr-tools: A Python library for Nostr protocol interactions.

This library provides core components for working with the Nostr protocol,
including events, relays, WebSocket clients, and cryptographic utilities.
"""

import os
import sys
from typing import Any

# Core exports that are always available
from .exceptions.errors import RelayConnectionError

__version__ = "0.1.0"
__author__ = "Bigbrotr"
__email__ = "hello@bigbrotr.com"

# Detect if we're in a documentation build environment
_BUILDING_DOCS = (
    "sphinx" in sys.modules
    or "sphinx.ext.autodoc" in sys.modules
    or os.environ.get("SPHINX_BUILD") == "1"
    or "sphinx-build" in " ".join(sys.argv)
)

if _BUILDING_DOCS:
    # Direct imports for documentation - Sphinx can access real objects
    from .actions.actions import (
        check_connectivity,
        check_readability,
        check_writability,
        compute_relay_metadata,
        fetch_connection,
        fetch_events,
        fetch_nip11,
        stream_events,
    )
    from .core.client import Client
    from .core.event import Event
    from .core.filter import Filter
    from .core.relay import Relay
    from .core.relay_metadata import RelayMetadata
    from .utils.utils import (
        TLDS,
        URI_GENERIC_REGEX,
        calc_event_id,
        find_websocket_relay_urls,
        generate_event,
        generate_keypair,
        parse_connection_response,
        parse_nip11_response,
        sanitize,
        sig_event_id,
        to_bech32,
        to_hex,
        validate_keypair,
        verify_sig,
    )

else:
    # Lazy loading for runtime - your existing implementation
    _LAZY_IMPORTS = {
        # Core classes
        "Event": ("nostr_tools.core.event", "Event"),
        "Relay": ("nostr_tools.core.relay", "Relay"),
        "RelayMetadata": ("nostr_tools.core.relay_metadata", "RelayMetadata"),
        "Client": ("nostr_tools.core.client", "Client"),
        "Filter": ("nostr_tools.core.filter", "Filter"),
        # Utility functions - cryptographic
        "generate_keypair": ("nostr_tools.utils.utils", "generate_keypair"),
        "generate_event": ("nostr_tools.utils.utils", "generate_event"),
        "calc_event_id": ("nostr_tools.utils.utils", "calc_event_id"),
        "verify_sig": ("nostr_tools.utils.utils", "verify_sig"),
        "sig_event_id": ("nostr_tools.utils.utils", "sig_event_id"),
        "validate_keypair": ("nostr_tools.utils.utils", "validate_keypair"),
        # Utility functions - encoding
        "to_bech32": ("nostr_tools.utils.utils", "to_bech32"),
        "to_hex": ("nostr_tools.utils.utils", "to_hex"),
        # Utility functions - other
        "find_websocket_relay_urls": (
            "nostr_tools.utils.utils",
            "find_websocket_relay_urls",
        ),
        "sanitize": ("nostr_tools.utils.utils", "sanitize"),
        # Constants
        "TLDS": ("nostr_tools.utils.utils", "TLDS"),
        "URI_GENERIC_REGEX": ("nostr_tools.utils.utils", "URI_GENERIC_REGEX"),
        # Response parsing
        "parse_nip11_response": ("nostr_tools.utils.utils", "parse_nip11_response"),
        "parse_connection_response": (
            "nostr_tools.utils.utils",
            "parse_connection_response",
        ),
        # Action functions
        "fetch_events": ("nostr_tools.actions.actions", "fetch_events"),
        "stream_events": ("nostr_tools.actions.actions", "stream_events"),
        "fetch_nip11": ("nostr_tools.actions.actions", "fetch_nip11"),
        "check_connectivity": ("nostr_tools.actions.actions", "check_connectivity"),
        "check_readability": ("nostr_tools.actions.actions", "check_readability"),
        "check_writability": ("nostr_tools.actions.actions", "check_writability"),
        "fetch_connection": ("nostr_tools.actions.actions", "fetch_connection"),
        "compute_relay_metadata": (
            "nostr_tools.actions.actions",
            "compute_relay_metadata",
        ),
    }

    # Cache for loaded modules
    _module_cache: dict[str, Any] = {}

    class _LazyLoader:
        """A lazy loader that imports modules only when accessed."""

        def __init__(self, module_path: str, attr_name: str) -> None:
            self.module_path = module_path
            self.attr_name = attr_name

        def _get_attr(self) -> Any:
            """Get the actual attribute by importing the module."""
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

        This function is called when an attribute is not found in the module.
        It checks if the attribute is in the lazy imports and returns a lazy loader.
        This should rarely be called since lazy loaders are pre-populated.
        """
        if name in _LAZY_IMPORTS:
            module_path, attr_name = _LAZY_IMPORTS[name]
            return _LazyLoader(module_path, attr_name)._get_attr()

        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Backwards compatibility - these can be imported directly
__all__ = [
    "TLDS",
    "URI_GENERIC_REGEX",
    "Client",
    "Event",
    "Filter",
    "Relay",
    "RelayConnectionError",
    "RelayMetadata",
    "__author__",
    "__email__",
    "__version__",
    "calc_event_id",
    "check_connectivity",
    "check_readability",
    "check_writability",
    "compute_relay_metadata",
    "fetch_connection",
    "fetch_events",
    "fetch_nip11",
    "find_websocket_relay_urls",
    "generate_event",
    "generate_keypair",
    "parse_connection_response",
    "parse_nip11_response",
    "sanitize",
    "sig_event_id",
    "stream_events",
    "to_bech32",
    "to_hex",
    "validate_keypair",
    "verify_sig",
]


def __dir__():
    """
    Return list of available attributes for tab completion.

    Returns:
        list: List of available attributes
    """
    return sorted(__all__)
