"""Validation utilities for Nostr protocol."""

import re
from typing import Dict, Any, List
from ..exceptions.errors import EventValidationError, RelayConnectionError


def validate_event(event_data: Dict[str, Any]) -> bool:
    """
    Validate event data structure.

    Args:
        event_data: Event data dictionary

    Returns:
        True if valid

    Raises:
        EventValidationError: If validation fails
    """
    if not isinstance(event_data, dict):
        raise EventValidationError("Event data must be a dictionary")

    required_fields = ["id", "pubkey", "created_at",
                       "kind", "tags", "content", "sig"]
    for field in required_fields:
        if field not in event_data:
            raise EventValidationError(f"Missing required field: {field}")

    # Validate field types
    if not isinstance(event_data["id"], str):
        raise EventValidationError("Event ID must be a string")
    if not isinstance(event_data["pubkey"], str):
        raise EventValidationError("Public key must be a string")
    if not isinstance(event_data["created_at"], int):
        raise EventValidationError("created_at must be an integer")
    if not isinstance(event_data["kind"], int):
        raise EventValidationError("Kind must be an integer")
    if not isinstance(event_data["tags"], list):
        raise EventValidationError("Tags must be a list")
    if not isinstance(event_data["content"], str):
        raise EventValidationError("Content must be a string")
    if not isinstance(event_data["sig"], str):
        raise EventValidationError("Signature must be a string")

    # Validate hex strings
    if not is_valid_hex(event_data["id"], 64):
        raise EventValidationError("Event ID must be 64-character hex string")
    if not is_valid_hex(event_data["pubkey"], 64):
        raise EventValidationError(
            "Public key must be 64-character hex string")
    if not is_valid_hex(event_data["sig"], 128):
        raise EventValidationError(
            "Signature must be 128-character hex string")

    # Validate kind range
    if not (0 <= event_data["kind"] <= 65535):
        raise EventValidationError("Kind must be between 0 and 65535")

    # Validate tags structure
    for i, tag in enumerate(event_data["tags"]):
        if not isinstance(tag, list):
            raise EventValidationError(f"Tag {i} must be a list")
        for j, item in enumerate(tag):
            if not isinstance(item, str):
                raise EventValidationError(f"Tag {i}[{j}] must be a string")

    return True


def validate_relay_url(url: str) -> bool:
    """
    Validate a relay URL.

    Args:
        url: URL to validate

    Returns:
        True if valid

    Raises:
        RelayConnectionError: If validation fails
    """
    if not isinstance(url, str):
        raise RelayConnectionError("URL must be a string")

    if not url.startswith(("ws://", "wss://")):
        raise RelayConnectionError("URL must start with ws:// or wss://")

    # Basic URL validation
    pattern = r'^wss?:\/\/[a-zA-Z0-9.-]+(?:\:[0-9]+)?(?:\/.*)?$'
    if not re.match(pattern, url):
        raise RelayConnectionError("Invalid URL format")

    return True


def is_valid_hex(value: str, expected_length: int = None) -> bool:
    """
    Check if a string is valid hexadecimal.

    Args:
        value: String to check
        expected_length: Expected length of hex string

    Returns:
        True if valid hex
    """
    if not isinstance(value, str):
        return False

    try:
        int(value, 16)
    except ValueError:
        return False

    if expected_length and len(value) != expected_length:
        return False

    return True


def is_valid_pubkey(pubkey: str) -> bool:
    """
    Check if a string is a valid Nostr public key.

    Args:
        pubkey: Public key to validate

    Returns:
        True if valid
    """
    return is_valid_hex(pubkey, 64)


def is_valid_event_id(event_id: str) -> bool:
    """
    Check if a string is a valid Nostr event ID.

    Args:
        event_id: Event ID to validate

    Returns:
        True if valid
    """
    return is_valid_hex(event_id, 64)


def is_valid_signature(signature: str) -> bool:
    """
    Check if a string is a valid Nostr signature.

    Args:
        signature: Signature to validate

    Returns:
        True if valid
    """
    return is_valid_hex(signature, 128)


def validate_tag(tag: List[str]) -> bool:
    """
    Validate a single tag.

    Args:
        tag: Tag to validate

    Returns:
        True if valid

    Raises:
        EventValidationError: If validation fails
    """
    if not isinstance(tag, list):
        raise EventValidationError("Tag must be a list")

    if len(tag) == 0:
        raise EventValidationError("Tag cannot be empty")

    for item in tag:
        if not isinstance(item, str):
            raise EventValidationError("Tag items must be strings")

    return True


def validate_kind(kind: int) -> bool:
    """
    Validate an event kind.

    Args:
        kind: Event kind to validate

    Returns:
        True if valid

    Raises:
        EventValidationError: If validation fails
    """
    if not isinstance(kind, int):
        raise EventValidationError("Kind must be an integer")

    if not (0 <= kind <= 65535):
        raise EventValidationError("Kind must be between 0 and 65535")

    return True
