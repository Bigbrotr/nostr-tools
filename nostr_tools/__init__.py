"""
nostr-tools: A Python library for Nostr protocol interactions.

This library provides core components for working with the Nostr protocol,
including events, relays, WebSocket clients, and cryptographic utilities.
"""

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
    "test_keypair": ("nostr_tools.utils.utils", "test_keypair"),
    
    # Utility functions - encoding
    "to_bech32": ("nostr_tools.utils.utils", "to_bech32"),
    "to_hex": ("nostr_tools.utils.utils", "to_hex"),
    
    # Utility functions - other
    "find_websocket_relay_urls": ("nostr_tools.utils.utils", "find_websocket_relay_urls"),
    "sanitize": ("nostr_tools.utils.utils", "sanitize"),
    
    # Constants
    "TLDS": ("nostr_tools.utils.utils", "TLDS"),
    "URI_GENERIC_REGEX": ("nostr_tools.utils.utils", "URI_GENERIC_REGEX"),
    
    # Response parsing
    "parse_nip11_response": ("nostr_tools.utils.utils", "parse_nip11_response"),
    "parse_connection_response": ("nostr_tools.utils.utils", "parse_connection_response"),
    
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
_module_cache = {}


def __getattr__(name: str) -> Any:
    """
    Lazy loading for heavy imports.
    
    This function is called when an attribute is not found in the module.
    It enables lazy loading of heavy dependencies to improve import performance.
    
    Args:
        name: The name of the attribute being accessed
        
    Returns:
        Any: The requested attribute
        
    Raises:
        AttributeError: If the attribute is not found
    """
    if name in _LAZY_IMPORTS:
        module_path, attr_name = _LAZY_IMPORTS[name]
        
        # Check cache first
        cache_key = f"{module_path}.{attr_name}"
        if cache_key in _module_cache:
            return _module_cache[cache_key]
        
        # Import and cache
        try:
            module = __import__(module_path, fromlist=[attr_name])
            attr = getattr(module, attr_name)
            _module_cache[cache_key] = attr
            return attr
        except ImportError as e:
            raise AttributeError(
                f"Failed to import {name} from {module_path}: {e}"
            ) from e
        except AttributeError as e:
            raise AttributeError(
                f"Module {module_path} has no attribute {attr_name}"
            ) from e
    
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def __dir__():
    """
    Return list of available attributes for tab completion.
    
    Returns:
        list: List of available attributes
    """
    # Combine regular attributes with lazy imports
    regular_attrs = [
        "__version__", "__author__", "__email__",
        "RelayConnectionError"
    ]
    
    lazy_attrs = list(_LAZY_IMPORTS.keys())
    
    return sorted(regular_attrs + lazy_attrs)


# Backwards compatibility - these can be imported directly
__all__ = [
    # Version info
    "__version__",
    "__author__", 
    "__email__",
    
    # Core classes
    "Event",
    "Relay", 
    "RelayMetadata",
    "Client",
    "Filter",
    
    # Cryptographic utilities
    "generate_keypair",
    "generate_event",
    "calc_event_id",
    "verify_sig",
    "sig_event_id",
    "test_keypair",
    
    # Encoding utilities
    "to_bech32",
    "to_hex",
    
    # Other utilities
    "find_websocket_relay_urls",
    "sanitize",
    
    # Constants
    "TLDS",
    "URI_GENERIC_REGEX",
    
    # Response parsing
    "parse_nip11_response",
    "parse_connection_response",
    
    # Exceptions
    "RelayConnectionError",
    
    # Actions
    "fetch_events",
    "stream_events",
    "fetch_nip11",
    "check_connectivity",
    "check_readability", 
    "check_writability",
    "fetch_connection",
    "compute_relay_metadata",
]