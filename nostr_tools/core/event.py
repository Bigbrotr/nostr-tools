"""Nostr event representation and validation."""

from typing import List, Dict, Any, Optional
from ..utils.crypto import calc_event_id, verify_sig
from ..utils.validation import validate_event
from ..exceptions.errors import EventValidationError
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
            EventValidationError: If validation fails
        """
        # Type validation
        if not isinstance(id, str):
            raise EventValidationError(f"id must be a str, not {type(id)}")
        if not isinstance(pubkey, str):
            raise EventValidationError(
                f"pubkey must be a str, not {type(pubkey)}")
        if not isinstance(created_at, int):
            raise EventValidationError(
                f"created_at must be an int, not {type(created_at)}")
        if not isinstance(kind, int):
            raise EventValidationError(
                f"kind must be an int, not {type(kind)}")
        if not isinstance(tags, list):
            raise EventValidationError(
                f"tags must be a list, not {type(tags)}")
        if not isinstance(content, str):
            raise EventValidationError(
                f"content must be a str, not {type(content)}")
        if not isinstance(sig, str):
            raise EventValidationError(f"sig must be a str, not {type(sig)}")

        # Validate tags structure
        for tag in tags:
            if not isinstance(tag, list):
                raise EventValidationError("tags must be a list of lists")
            for item in tag:
                if not isinstance(item, str):
                    raise EventValidationError("tag items must be strings")

        # Validate kind range
        if not (0 <= kind <= 65535):
            raise EventValidationError("kind must be between 0 and 65535")

        # Validate event ID
        expected_id = calc_event_id(pubkey, created_at, kind, tags, content)
        if id != expected_id:
            raise EventValidationError("Invalid event ID")

        # Validate signature
        if not verify_sig(id, pubkey, sig):
            raise EventValidationError("Invalid event signature")

        self.id = id
        self.pubkey = pubkey
        self.created_at = created_at
        self.kind = kind
        self.tags = tags
        self.content = content
        self.sig = sig

    def __repr__(self) -> str:
        """Return string representation of the Event."""
        return f"Event(id={self.id[:16]}..., kind={self.kind}, pubkey={self.pubkey[:16]}...)"

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
            raise EventValidationError(
                f"data must be a dict, not {type(data)}")

        required_fields = ["id", "pubkey", "created_at",
                           "kind", "tags", "content", "sig"]
        for field in required_fields:
            if field not in data:
                raise EventValidationError(f"Missing required field: {field}")

        return cls(
            id=data["id"],
            pubkey=data["pubkey"],
            created_at=data["created_at"],
            kind=data["kind"],
            tags=data["tags"],
            content=data["content"],
            sig=data["sig"]
        )

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

    def to_json(self) -> str:
        """Convert the Event to JSON string."""
        return json.dumps(self.to_dict())

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
