"""Nostr event representation and validation."""

from typing import List, Dict, Any, Optional
from ..utils import calc_event_id, verify_sig
import json


class Event:
    """
    Class to represent a NOSTR event.

    Attributes:
        id: str, id of the event
        pubkey: str, public key of the event
        created_at: int, timestamp of the event
        kind: int, kind of the event
        tags: List[List[str]], tags of the event
        content: str, content of the event
        sig: str, signature of the event
    """

    def __init__(
        self,
        id: str,
        pubkey: str,
        created_at: int,
        kind: int,
        tags: List[List[str]],
        content: str,
        sig: str
    ) -> None:
        """
        Initialize an Event object.

        Args:
            id: Event ID
            pubkey: Public key of the event author
            created_at: Unix timestamp
            kind: Event kind (0-65535)
            tags: List of tags (each tag is a list of strings)
            content: Event content
            sig: Event signature

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
            ("sig", sig, str)
        ]
        for name, value, expected_type in to_validate:
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"{name} must be a {expected_type.__name__}, not {type(value).__name__}")
        if not all(isinstance(tag, list) for tag in tags):
            raise TypeError("tags must be a list of lists")
        if not all(isinstance(item, str) for tag in tags for item in tag):
            raise TypeError("tag items must be strings")
        if len(id) != 64 or not all(c in '0123456789abcdef' for c in id):
            raise ValueError("id must be a 64-character hex string")
        if len(pubkey) != 64 or not all(c in '0123456789abcdef' for c in pubkey):
            raise ValueError("pubkey must be a 64-character hex string")
        if created_at < 0:
            raise ValueError("created_at must be a non-negative integer")
        if not (0 <= kind <= 65535):
            raise ValueError("kind must be between 0 and 65535")
        if "\\u0000" in json.dumps(tags):
            raise ValueError("tags cannot contain null characters")
        if "\\u0000" in content:
            raise ValueError("content cannot contain null characters")
        if len(sig) != 128 or not all(c in '0123456789abcdef' for c in sig):
            raise ValueError("sig must be a 128-character hex string")
        if calc_event_id(pubkey, created_at, kind, tags, content) != id:
            raise ValueError(f"id does not match the computed event id")
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
        """Return string representation of the Event."""
        return (f"Event(id={self.id}, pubkey={self.pubkey}, created_at={self.created_at}, "
                f"kind={self.kind}, tags={self.tags}, content={self.content}, sig={self.sig})")

    def __eq__(self, other):
        """Check equality of two Event objects."""
        if not isinstance(other, Event):
            return NotImplemented
        return (self.id == other.id and
                self.pubkey == other.pubkey and
                self.created_at == other.created_at and
                self.kind == other.kind and
                self.tags == other.tags and
                self.content == other.content and
                self.sig == other.sig)

    def __ne__(self, other):
        """Check inequality of two Event objects."""
        return not self.__eq__(other)

    def __hash__(self):
        """Return hash of the Event object."""
        return hash((self.id, self.pubkey, self.created_at, self.kind, tuple(tuple(tag) for tag in self.tags), self.content, self.sig))

    @classmethod
    def event_handler(cls, data: Dict[str, Any]) -> "Event":
        """
        Handle event creation from a dictionary, with escape sequence handling.
        Args:
            data: Dictionary containing event data
        Returns:
            Event object
        Raises:
            ValueError: If data is invalid
        """
        try:
            event = cls.from_dict(data)
        except ValueError:
            tags = []
            for tag in data['tags']:
                tag = [
                    t.replace(r'\n', '\n').replace(r'\"', '\"').replace(r'\\', '\\').replace(
                        r'\r', '\r').replace(r'\t', '\t').replace(r'\b', '\b').replace(r'\f', '\f')
                    for t in tag
                ]
                tags.append(tag)
            data['tags'] = tags
            data['content'] = data['content'].replace(r'\n', '\n').replace(r'\"', '\"').replace(
                r'\\', '\\').replace(r'\r', '\r').replace(r'\t', '\t').replace(r'\b', '\b').replace(r'\f', '\f')
            event = cls.from_dict(data)
        return event

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """
        Create an Event object from a dictionary.

        Args:
            data: Dictionary containing event data

        Returns:
            Event object

        Raises:
            EventValidationError: If data is invalid
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, not {type(data)}")
        for key in ["id", "pubkey", "created_at", "kind", "tags", "content", "sig"]:
            if key not in data:
                raise KeyError(f"data must contain key {key}")
        return cls(data["id"], data["pubkey"], data["created_at"], data["kind"], data["tags"], data["content"], data["sig"])

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Event object to a dictionary.

        Returns:
            Dictionary representation of the event
        """
        return {
            "id": self.id,
            "pubkey": self.pubkey,
            "created_at": self.created_at,
            "kind": self.kind,
            "tags": self.tags,
            "content": self.content,
            "sig": self.sig
        }

    def get_tag_values(self, tag_name: str) -> List[str]:
        """
        Get all values for a specific tag name.

        Args:
            tag_name: The tag name to search for

        Returns:
            List of values for the specified tag
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
            tag_name: The tag name to check for
            value: Optional specific value to check for

        Returns:
            True if the tag exists (and has the value if specified)
        """
        for tag in self.tags:
            if len(tag) > 0 and tag[0] == tag_name:
                if value is None:
                    return True
                elif len(tag) > 1 and value in tag[1:]:
                    return True
        return False
