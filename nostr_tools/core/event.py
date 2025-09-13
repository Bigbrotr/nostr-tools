"""
Nostr event representation and validation.

This module provides the Event class for creating, validating, and
manipulating Nostr events according to the NIP-01 specification.
"""

import json
from typing import Any, Optional

from ..utils import calc_event_id, verify_sig


class Event:
    """
    Class to represent a NOSTR event.

    This class handles validation, serialization, and manipulation of Nostr
    events according to the protocol specification. All events are validated
    for proper format, signature verification, and ID consistency.

    Attributes:
        id (str): Event ID (64-character hex string)
        pubkey (str): Public key of the event author (64-character hex string)
        created_at (int): Unix timestamp of event creation
        kind (int): Event kind (0-65535)
        tags (List[List[str]]): List of event tags
        content (str): Event content
        sig (str): Event signature (128-character hex string)
    """

    def __init__(
        self,
        id: str,
        pubkey: str,
        created_at: int,
        kind: int,
        tags: list[list[str]],
        content: str,
        sig: str,
    ) -> None:
        """
        Initialize an Event object with validation.

        Args:
            id (str): Event ID (64-character hex string)
            pubkey (str): Public key of the event author (64-character hex string)
            created_at (int): Unix timestamp of event creation
            kind (int): Event kind (0-65535)
            tags (List[List[str]]): List of event tags
            content (str): Event content
            sig (str): Event signature (128-character hex string)

        Raises:
            TypeError: If any argument is of incorrect type
            ValueError: If any argument has an invalid value
        """
        # Type validation
        to_validate = [
            ("id", id, str),
            ("pubkey", pubkey, str),
            ("created_at", created_at, int),
            ("kind", kind, int),
            ("tags", tags, list),
            ("content", content, str),
            ("sig", sig, str),
        ]
        for name, value, expected_type in to_validate:
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"{name} must be a {expected_type.__name__}, not {type(value).__name__}"
                )

        if not all(isinstance(tag, list) for tag in tags):
            raise TypeError("tags must be a list of lists")
        if not all(isinstance(item, str) for tag in tags for item in tag):
            raise TypeError("tag items must be strings")

        # Value validation
        if len(id) != 64 or not all(c in "0123456789abcdef" for c in id):
            raise ValueError("id must be a 64-character hex string")
        if len(pubkey) != 64 or not all(c in "0123456789abcdef" for c in pubkey):
            raise ValueError("pubkey must be a 64-character hex string")
        if created_at < 0:
            raise ValueError("created_at must be a non-negative integer")
        if not (0 <= kind <= 65535):
            raise ValueError("kind must be between 0 and 65535")
        if "\\u0000" in json.dumps(tags):
            raise ValueError("tags cannot contain null characters")
        if "\\u0000" in content:
            raise ValueError("content cannot contain null characters")
        if len(sig) != 128 or not all(c in "0123456789abcdef" for c in sig):
            raise ValueError("sig must be a 128-character hex string")

        # Verify event ID matches computed ID
        if calc_event_id(pubkey, created_at, kind, tags, content) != id:
            raise ValueError("id does not match the computed event id")

        # Verify signature
        if not verify_sig(id, pubkey, sig):
            raise ValueError("sig is not a valid signature for the event")

        self.id = id
        self.pubkey = pubkey
        self.created_at = created_at
        self.kind = kind
        self.tags = tags
        self.content = content
        self.sig = sig

    def __repr__(self) -> str:
        """
        Return string representation of the Event.

        Returns:
            str: String representation showing all event attributes
        """
        return (
            f"Event(id={self.id}, pubkey={self.pubkey}, created_at={self.created_at}, "
            f"kind={self.kind}, tags={self.tags}, content={self.content}, sig={self.sig})"
        )

    def __eq__(self, other):
        """
        Check equality of two Event objects.

        Args:
            other: Object to compare with

        Returns:
            bool: True if events are equal, False otherwise
        """
        if not isinstance(other, Event):
            return NotImplemented
        return (
            self.id == other.id
            and self.pubkey == other.pubkey
            and self.created_at == other.created_at
            and self.kind == other.kind
            and self.tags == other.tags
            and self.content == other.content
            and self.sig == other.sig
        )

    def __ne__(self, other):
        """
        Check inequality of two Event objects.

        Args:
            other: Object to compare with

        Returns:
            bool: True if events are not equal, False otherwise
        """
        return not self.__eq__(other)

    def __hash__(self):
        """
        Return hash of the Event object.

        Returns:
            int: Hash value for the event
        """
        return hash(
            (
                self.id,
                self.pubkey,
                self.created_at,
                self.kind,
                tuple(tuple(tag) for tag in self.tags),
                self.content,
                self.sig,
            )
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Event":
        """
        Create an Event object from a dictionary.

        Args:
            data (Dict[str, Any]): Dictionary containing event attributes
        Returns:
            Event: Event object created from the dictionary
        Raises:
            TypeError: If data is not a dictionary
            KeyError: If required keys are missing in the dictionary
            ValueError: If any attribute has an invalid value
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, not {type(data)}")
        required_keys = ["id", "pubkey", "created_at", "kind", "tags", "content", "sig"]
        for key in required_keys:
            if key not in data:
                raise KeyError(f"data must contain key {key}")
        try:
            event = cls(
                data["id"],
                data["pubkey"],
                data["created_at"],
                data["kind"],
                data["tags"],
                data["content"],
                data["sig"],
            )
        except ValueError:
            # Handle escape sequences in tags
            tags = []
            for tag in data["tags"]:
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
            data["tags"] = tags

            # Handle escape sequences in content
            data["content"] = (
                data["content"]
                .replace(r"\n", "\n")
                .replace(r"\"", '"')
                .replace(r"\\", "\\")
                .replace(r"\r", "\r")
                .replace(r"\t", "\t")
                .replace(r"\b", "\b")
                .replace(r"\f", "\f")
            )
            event = cls(
                data["id"],
                data["pubkey"],
                data["created_at"],
                data["kind"],
                data["tags"],
                data["content"],
                data["sig"],
            )
        return event

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the Event object to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the event
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

    def get_tag_values(self, tag_name: str) -> list[str]:
        """
        Get all values for a specific tag name.

        Args:
            tag_name (str): The tag name to search for

        Returns:
            List[str]: List of values for the specified tag
        """
        values = []
        for tag in self.tags:
            if len(tag) > 0 and tag[0] == tag_name:
                values.extend(tag[1:])
        return values

    def has_tag(self, tag_name: str, value: Optional[str] = None) -> bool:
        """
        Check if the event has a specific tag.

        Args:
            tag_name (str): The tag name to check for
            value (Optional[str]): Optional specific value to check for

        Returns:
            bool: True if the tag exists (and has the value if specified)
        """
        for tag in self.tags:
            if (
                len(tag) > 0
                and tag[0] == tag_name
                and (value is None or (len(tag) > 1 and value in tag[1:]))
            ):
                return True
        return False
