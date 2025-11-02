"""
Nostr event representation and validation.

This module provides the Event dataclass for creating, validating, and
manipulating Nostr events according to the NIP-01 specification.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ..exceptions import EventValidationError
from ..utils import calc_event_id
from ..utils import verify_sig


@dataclass
class Event:
    """
    Nostr event representation following NIP-01 protocol specifications.

    This class handles validation, serialization, and manipulation of Nostr
    events according to the protocol specification. All events are validated
    for proper format, signature verification, and ID consistency. Events are
    automatically validated upon creation and escape sequences in content/tags
    are properly handled.

    Examples:
        Create an event from a dictionary:

        >>> event_data = {
        ...     "id": "a1b2c3...",
        ...     "pubkey": "d4e5f6...",
        ...     "created_at": 1234567890,
        ...     "kind": 1,
        ...     "tags": [["p", "abc123..."], ["e", "def456..."]],
        ...     "content": "Hello Nostr!",
        ...     "sig": "789abc..."
        ... }
        >>> event = Event.from_dict(event_data)

        Validate an event:

        >>> if event.is_valid:
        ...     print("Event is valid!")
        ... else:
        ...     print("Event validation failed")

        Convert event to dictionary:

        >>> event_dict = event.to_dict()
        >>> print(event_dict["kind"])
        1

    Raises:
        EventValidationError: If any attribute value is invalid, ID doesn't
            match computed hash, or signature verification fails.
    """

    #: Event ID as a 64-character lowercase hexadecimal string. This is the SHA-256 hash of the serialized event data.
    id: str
    #: Public key of the event author as a 64-character lowercase hexadecimal string.
    pubkey: str
    #: Unix timestamp (seconds since epoch) of when the event was created. Must be non-negative.
    created_at: int
    #: Event kind number (0-65535) defining the event type. Common kinds: 0=metadata, 1=text note, 3=contacts, 4=DM, etc.
    kind: int
    #: List of event tags. Each tag is a list of strings where the first element is the tag name. Example: [["e", "event_id"], ["p", "pubkey"]]
    tags: list[list[str]]
    #: The event content/message as a string. Cannot contain null bytes.
    content: str
    #: Schnorr signature of the event as a 128-character lowercase hexadecimal string.
    sig: str

    def __post_init__(self) -> None:
        """
        Validate and normalize the Event instance after initialization.

        This method is automatically called after the dataclass is created.
        It normalizes hex strings to lowercase and validates the event.
        If validation fails due to escape sequences, it attempts to unescape
        them and re-validates.

        Raises:
            EventValidationError: If validation fails after escape handling.
        """
        self.id = self.id.lower()
        self.pubkey = self.pubkey.lower()
        self.sig = self.sig.lower()
        try:
            self.validate()
        except EventValidationError:
            tags = []
            for tag in self.tags:
                tag = [
                    t.replace(r"\n", "\n")
                    .replace(r"\"", '"')
                    .replace(r"\\", "\\")
                    .replace(r"\r", "\r")
                    .replace(r"\t", "\t")
                    .replace(r"\b", "\b")
                    .replace(r"\f", "\f")
                    for t in tag
                ]
                tags.append(tag)
            self.tags = tags
            self.content = (
                self.content.replace(r"\n", "\n")
                .replace(r"\"", '"')
                .replace(r"\\", "\\")
                .replace(r"\r", "\r")
                .replace(r"\t", "\t")
                .replace(r"\b", "\b")
                .replace(r"\f", "\f")
            )
            self.validate()

    def validate(self) -> None:
        """
        Validate the Event instance against NIP-01 specifications.

        Performs comprehensive validation including:
        - Type checking for all attributes
        - Format validation (hex strings, timestamps, etc.)
        - Event ID verification against computed hash
        - Schnorr signature verification
        - Null byte checking in content and tags

        Raises:
            EventValidationError: If any attribute has an invalid value,
                including:
                - Invalid hex string formats
                - ID mismatch with computed event ID
                - Invalid signature
                - Presence of null bytes
                - Invalid kind range (must be 0-65535)

        Examples:
            >>> try:
            ...     event.validate()
            ...     print("Event is valid")
            ... except EventValidationError as e:
            ...     print(f"Validation failed: {e}")
        """
        # Type validation
        type_checks = [
            ("id", self.id, str),
            ("pubkey", self.pubkey, str),
            ("created_at", self.created_at, int),
            ("kind", self.kind, int),
            ("tags", self.tags, list),
            ("content", self.content, str),
            ("sig", self.sig, str),
        ]
        for field_name, field_value, expected_type in type_checks:
            if not isinstance(field_value, expected_type):
                raise EventValidationError(
                    f"{field_name} must be {expected_type.__name__}, got {type(field_value).__name__}"
                )

        if not all(
            isinstance(tag, list) and tag != [] and all(isinstance(t, str) for t in tag)
            for tag in self.tags
        ):
            raise EventValidationError("tags must be a list of lists (not empty) of strings")

        checks: list[tuple[Any, Callable[[Any], bool], str]] = [
            (
                self.id,
                lambda v: len(v) == 64 and all(c in "0123456789abcdef" for c in v),
                "id must be a 64-character hex string",
            ),
            (
                self.pubkey,
                lambda v: len(v) == 64 and all(c in "0123456789abcdef" for c in v),
                "pubkey must be a 64-character hex string",
            ),
            (
                self.created_at,
                lambda v: v >= 0,
                "created_at must be a non-negative integer",
            ),
            (
                self.kind,
                lambda v: 0 <= v <= 65535,
                "kind must be between 0 and 65535",
            ),
            (
                self.tags,
                lambda v: "\\u0000" not in json.dumps(v),
                "tags cannot contain null characters",
            ),
            (
                self.content,
                lambda v: "\\u0000" not in v,
                "content cannot contain null characters",
            ),
            (
                self.sig,
                lambda v: len(v) == 128 and all(c in "0123456789abcdef" for c in v),
                "sig must be a 128-character hex string",
            ),
        ]
        for field_value, check, error_message in checks:
            if not check(field_value):
                raise EventValidationError(error_message)

        # Verify event ID matches computed ID
        if (
            calc_event_id(self.pubkey, self.created_at, self.kind, self.tags, self.content)
            != self.id
        ):
            raise EventValidationError("id does not match the computed event id")

        # Verify signature
        if not verify_sig(self.id, self.pubkey, self.sig):
            raise EventValidationError("sig is not a valid signature for the event")

    @property
    def is_valid(self) -> bool:
        """
        Check if the Event is valid without raising exceptions.

        This property attempts validation and returns True if successful,
        False otherwise. Unlike validate(), this method does not raise
        exceptions, making it safe for conditional checks.

        Returns:
            bool: True if the event passes all validation checks,
                False if validation fails for any reason.

        Examples:
            >>> if event.is_valid:
            ...     # Process the valid event
            ...     publish_event(event)
            ... else:
            ...     # Handle invalid event
            ...     log_error("Invalid event detected")
        """
        try:
            self.validate()
            return True
        except EventValidationError:
            return False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        """
        Create an Event object from a dictionary representation.

        This class method constructs an Event instance from a dictionary,
        typically received from a Nostr relay or JSON deserialization.
        All required fields must be present in the dictionary.

        Args:
            data (dict[str, Any]): Dictionary containing event attributes.
                Required keys: id, pubkey, created_at, kind, tags, content, sig

        Returns:
            Event: A new Event instance created from the dictionary data.

        Raises:
            TypeError: If data is not a dictionary.
            KeyError: If any required key is missing from the dictionary.
            EventValidationError: If the resulting event fails validation.

        Examples:
            Parse an event from relay response:

            >>> relay_message = ["EVENT", "sub_id", {
            ...     "id": "a1b2c3d4...",
            ...     "pubkey": "e5f6g7h8...",
            ...     "created_at": 1234567890,
            ...     "kind": 1,
            ...     "tags": [["p", "i9j0k1l2..."]],
            ...     "content": "Hello Nostr!",
            ...     "sig": "m3n4o5p6..."
            ... }]
            >>> event = Event.from_dict(relay_message[2])
            >>> print(event.content)
            Hello Nostr!

            Parse from JSON:

            >>> import json
            >>> json_data = '{"id": "...", "pubkey": "...", ...}'
            >>> event_dict = json.loads(json_data)
            >>> event = Event.from_dict(event_dict)
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, got {type(data)}")

        return cls(
            id=data["id"],
            pubkey=data["pubkey"],
            created_at=data["created_at"],
            kind=data["kind"],
            tags=data["tags"],
            content=data["content"],
            sig=data["sig"],
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the Event object to a dictionary representation.

        This method serializes the Event instance into a dictionary format
        suitable for JSON encoding, relay transmission, or storage.

        Returns:
            dict[str, Any]: Dictionary containing all event fields with keys:
                - id: Event ID (str)
                - pubkey: Public key (str)
                - created_at: Timestamp (int)
                - kind: Event kind (int)
                - tags: Event tags (list[list[str]])
                - content: Event content (str)
                - sig: Signature (str)

        Examples:
            Convert event for relay publishing:

            >>> event_dict = event.to_dict()
            >>> publish_message = ["EVENT", event_dict]
            >>> await ws.send_str(json.dumps(publish_message))

            Serialize to JSON:

            >>> import json
            >>> json_str = json.dumps(event.to_dict())
            >>> print(json_str)
            {"id": "...", "pubkey": "...", ...}

            Store in database:

            >>> event_data = event.to_dict()
            >>> db.events.insert_one(event_data)
        """
        return {
            "id": self.id,
            "pubkey": self.pubkey,
            "created_at": self.created_at,
            "kind": self.kind,
            "tags": self.tags,
            "content": self.content,
            "sig": self.sig,
        }
