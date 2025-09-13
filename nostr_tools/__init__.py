"""
nostr-tools: A Python library for Nostr protocol interactions.

This library provides core components for working with the Nostr protocol,
including events, relays, WebSocket clients, and cryptographic utilities.
"""

import sys
from typing import Any

__version__ = "0.1.0"
__author__ = "Bigbrotr"
__email__ = "hello@bigbrotr.com"

# Core exports that are always available
from .exceptions.errors import RelayConnectionError

# Lazy loading mapping for heavy imports
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
    "compute_relay_metadata": ("nostr_tools.actions.actions", "compute_relay_metadata"),
}

# Cache for loaded modules
_module_cache: dict[str, Any] = {}


class _LazyLoader:
    """A lazy loader that imports modules only when accessed."""

    def __init__(self, module_path: str, attr_name: str):
        self.module_path = module_path
        self.attr_name = attr_name
        self._loaded = None

    def __call__(self, *args, **kwargs):
        """Allow the lazy loader to be called like the actual function/class."""
        return self._get_attr()(*args, **kwargs)

    def __getattr__(self, name):
        """Delegate attribute access to the loaded module."""
        return getattr(self._get_attr(), name)

    def _get_attr(self):
        """Load and return the actual attribute."""
        if self._loaded is None:
            cache_key = f"{self.module_path}.{self.attr_name}"
            if cache_key in _module_cache:
                self._loaded = _module_cache[cache_key]
            else:
                try:
                    module = __import__(self.module_path, fromlist=[self.attr_name])
                    self._loaded = getattr(module, self.attr_name)
                    _module_cache[cache_key] = self._loaded

                    # Replace the lazy loader with the actual object in the module
                    current_module = sys.modules[__name__]
                    for name, (mod_path, attr) in _LAZY_IMPORTS.items():
                        if mod_path == self.module_path and attr == self.attr_name:
                            setattr(current_module, name, self._loaded)
                            break

                except ImportError as e:
                    raise AttributeError(
                        f"Failed to import {self.attr_name} from {self.module_path}: {e}"
                    ) from e
                except AttributeError as e:
                    raise AttributeError(
                        f"Module {self.module_path} has no attribute {self.attr_name}"
                    ) from e

        return self._loaded


# Populate the module namespace with lazy loaders
# This ensures 'from module import name' works immediately
_current_module = sys.modules[__name__]
for name, (module_path, attr_name) in _LAZY_IMPORTS.items():
    setattr(_current_module, name, _LazyLoader(module_path, attr_name))


def __getattr__(name: str) -> Any:
    """
    Fallback for any remaining lazy loading needs.

    This should rarely be called since lazy loaders are pre-populated.
    """
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        return _LazyLoader(module_path, attr_name)._get_attr()

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__():
    """
    Return list of available attributes for tab completion.

    Returns:
        list: List of available attributes
    """
    # Combine regular attributes with lazy imports
    regular_attrs = ["__version__", "__author__", "__email__", "RelayConnectionError"]

    lazy_attrs = list(_LAZY_IMPORTS.keys())

    return sorted(regular_attrs + lazy_attrs)


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
