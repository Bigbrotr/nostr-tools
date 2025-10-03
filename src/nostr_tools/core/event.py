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
    Nostr event representation following protocol specifications.

    This class handles validation, serialization, and manipulation of Nostr
    events according to the protocol specification. All events are validated
    for proper format, signature verification, and ID consistency.

    Attributes:
        id: Event ID (64-character hex string)
        pubkey: Public key of the event author (64-character hex string)
        created_at: Unix timestamp of event creation
        kind: Event kind (0-65535)
        tags: List of event tags
        content: Event content
        sig: Event signature (128-character hex string)
    """

    id: str
    pubkey: str
    created_at: int
    kind: int
    tags: list[list[str]]
    content: str
    sig: str

    def __post_init__(self) -> None:
        """Validate the Event instance after initialization."""
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
        Validate the Event instance.

        Raises:
            TypeError: If any attribute is of incorrect type
            EventValidationError: If any attribute has an invalid value
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
                raise TypeError(
                    f"{field_name} must be {expected_type.__name__}, got {type(field_value).__name__}"
                )

        if not all(
            isinstance(tag, list) and tag != [] and all(isinstance(t, str) for t in tag)
            for tag in self.tags
        ):
            raise TypeError("tags must be a list of lists (not empty) of strings")

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
        Check if the Event is valid.

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            self.validate()
            return True
        except (TypeError, EventValidationError):
            return False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        """
        Create an Event object from a dictionary.

        Args:
            data: Dictionary containing event attributes

        Returns:
            Event: Event object created from the dictionary

        Raises:
            TypeError: If data is not a dictionary
            KeyError: If required keys are missing in the dictionary
            ValueError: If any attribute has an invalid value
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
        Convert the Event object to a dictionary.

        Returns:
            dict[str, Any]: Dictionary representation of the event
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
