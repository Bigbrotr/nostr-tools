"""Simple Nostr event filter following the protocol specification."""

from typing import Dict, List, Optional, Any


class Filter:
    """
    Simple Nostr event filter following NIP-01 specification.
    """

    def __init__(
        self,
        ids: Optional[List[str]] = None,
        authors: Optional[List[str]] = None,
        kinds: Optional[List[int]] = None,
        since: Optional[int] = None,
        until: Optional[int] = None,
        limit: Optional[int] = None,
        **tags: List[str]
    ):
        """
        Create a Nostr filter.

        Args:
            ids: List of event IDs
            authors: List of author pubkeys
            kinds: List of event kinds
            since: Unix timestamp, events newer than this
            until: Unix timestamp, events older than this
            limit: Maximum number of events
            **tags: Tag filters (e.g., p=["pubkey"], e=["eventid"], t=["hashtag"])
        """
        # type validation
        to_validate = [
            ("ids", ids, (list, type(None))),
            ("authors", authors, (list, type(None))),
            ("kinds", kinds, (list, type(None))),
            ("since", since, (int, type(None))),
            ("until", until, (int, type(None))),
            ("limit", limit, (int, type(None))),
        ]
        for name, value, types in to_validate:
            if not isinstance(value, types):
                raise TypeError(f"{name} must be of type {types}")
        if not all(isinstance(id, str) for id in ids or []):
            raise TypeError("All ids must be strings")
        if not all(isinstance(author, str) for author in authors or []):
            raise TypeError("All authors must be strings")
        if not all(isinstance(kind, int) for kind in kinds or []):
            raise TypeError("All kinds must be integers")
        if not all(isinstance(tag_values, list) for tag_values in tags.values()):
            raise TypeError("All tag values must be lists")
        if not all(isinstance(tag_value, str) for tag_values in tags.values() for tag_value in tag_values):
            raise TypeError("All tag values must be strings")

        # value validation
        if not all(len(id) == 64 and all(c in '0123456789abcdef' for c in id) for id in ids or []):
            raise ValueError(
                "All ids must be 64-character hexadecimal strings")
        if not all(len(author) == 64 and all(c in '0123456789abcdef' for c in author) for author in authors or []):
            raise ValueError(
                "All authors must be 64-character hexadecimal strings")
        if not all(0 <= kind <= 65535 for kind in kinds or []):
            raise ValueError("All kinds must be integers between 0 and 65535")
        if since is not None and since <= 0:
            raise ValueError("since must be a non-negative integer")
        if until is not None and until <= 0:
            raise ValueError("until must be a non-negative integer")
        if limit is not None and limit <= 0:
            raise ValueError("limit must be a positive integer")
        if since is not None and until is not None and since > until:
            raise ValueError("since must be less than or equal to until")
        if not all(tag_name.isalpha() and len(tag_name) == 1 for tag_name in tags.keys()):
            raise ValueError(
                "Tag names must be single alphabetic characters a-z or A-Z")

        self.filter_dict: Dict[str, Any] = {}

        if ids is not None:
            self.filter_dict["ids"] = ids
        if authors is not None:
            self.filter_dict["authors"] = authors
        if kinds is not None:
            self.filter_dict["kinds"] = kinds
        if since is not None:
            self.filter_dict["since"] = since
        if until is not None:
            self.filter_dict["until"] = until
        if limit is not None:
            self.filter_dict["limit"] = limit

        # Add tag filters
        for tag_name, tag_values in tags.items():
            self.filter_dict[f"#{tag_name}"] = tag_values

    def __repr__(self) -> str:
        return f"Filter({self.filter_dict})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Filter):
            return NotImplemented
        return self.filter_dict == other.filter_dict

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self):
        return hash(frozenset(self.filter_dict.items()))

    @classmethod
    def from_dict(cls, filter_dict: Dict[str, Any]) -> "Filter":
        """Create a Filter instance from a dictionary."""
        return cls(**filter_dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return filter as dictionary that can be used with from_dict()."""
        result = {}
        for key, value in self.filter_dict.items():
            if key.startswith("#") and len(key) == 2:
                tag_name = key[1]
                result[tag_name] = value
            else:
                result[key] = value
        return result
