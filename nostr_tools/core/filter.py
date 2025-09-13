"""
Simple Nostr event filter following the protocol specification.

This module provides the Filter class for creating event filters according
to NIP-01 specification for querying Nostr relays.
"""

from typing import Any, Optional


class Filter:
    """
    Simple Nostr event filter following NIP-01 specification.

    This class creates filters for querying events from Nostr relays.
    Filters can specify event IDs, authors, kinds, time ranges, limits,
    and tag-based filtering.

    Attributes:
        filter_dict (Dict[str, Any]): Internal dictionary representation of the filter
    """

    def __init__(
        self,
        ids: Optional[list[str]] = None,
        authors: Optional[list[str]] = None,
        kinds: Optional[list[int]] = None,
        since: Optional[int] = None,
        until: Optional[int] = None,
        limit: Optional[int] = None,
        **tags: list[str],
    ):
        """
        Create a Nostr filter with specified criteria.

        Args:
            ids (Optional[List[str]]): List of event IDs (64-char hex strings)
            authors (Optional[List[str]]): List of author pubkeys (64-char hex strings)
            kinds (Optional[List[int]]): List of event kinds (0-65535)
            since (Optional[int]): Unix timestamp, events newer than this
            until (Optional[int]): Unix timestamp, events older than this
            limit (Optional[int]): Maximum number of events to return
            **tags: Tag filters (e.g., p=["pubkey"], e=["eventid"], t=["hashtag"])

        Raises:
            TypeError: If any argument is of incorrect type
            ValueError: If any argument has an invalid value
        """
        # Type validation
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

        # Validate list contents
        if not all(isinstance(id, str) for id in ids or []):
            raise TypeError("All ids must be strings")
        if not all(isinstance(author, str) for author in authors or []):
            raise TypeError("All authors must be strings")
        if not all(isinstance(kind, int) for kind in kinds or []):
            raise TypeError("All kinds must be integers")
        if not all(isinstance(tag_values, list) for tag_values in tags.values()):
            raise TypeError("All tag values must be lists")
        if not all(
            isinstance(tag_value, str)
            for tag_values in tags.values()
            for tag_value in tag_values
        ):
            raise TypeError("All tag values must be strings")

        # Value validation
        if not all(
            len(id) == 64 and all(c in "0123456789abcdef" for c in id)
            for id in ids or []
        ):
            raise ValueError("All ids must be 64-character hexadecimal strings")
        if not all(
            len(author) == 64 and all(c in "0123456789abcdef" for c in author)
            for author in authors or []
        ):
            raise ValueError("All authors must be 64-character hexadecimal strings")
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
        if not all(tag_name.isalpha() and len(tag_name) == 1 for tag_name in tags):
            raise ValueError(
                "Tag names must be single alphabetic characters a-z or A-Z"
            )

        # Build filter dictionary
        self.filter_dict: dict[str, Any] = {}

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

        # Add tag filters with # prefix
        for tag_name, tag_values in tags.items():
            self.filter_dict[f"#{tag_name}"] = tag_values

    def __repr__(self) -> str:
        """
        Return string representation of the Filter.

        Returns:
            str: String representation showing filter dictionary
        """
        return f"Filter({self.filter_dict})"

    def __eq__(self, other: object) -> bool:
        """
        Check equality with another Filter.

        Args:
            other: Object to compare with

        Returns:
            bool: True if filters are equal, False otherwise
        """
        if not isinstance(other, Filter):
            return NotImplemented
        return self.filter_dict == other.filter_dict

    def __ne__(self, other: object) -> bool:
        """
        Check inequality with another Filter.

        Args:
            other: Object to compare with

        Returns:
            bool: True if filters are not equal, False otherwise
        """
        return not self.__eq__(other)

    def __hash__(self):
        """
        Return hash of the Filter.

        Returns:
            int: Hash value for the filter
        """
        return hash(frozenset(self.filter_dict.items()))

    @classmethod
    def from_dict(cls, filter_dict: dict[str, Any]) -> "Filter":
        """
        Create a Filter instance from a dictionary.

        Args:
            filter_dict (Dict[str, Any]): Dictionary containing filter parameters

        Returns:
            Filter: New Filter instance
        """
        return cls(**filter_dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Return filter as dictionary that can be used with from_dict().

        This method converts the internal filter representation back to
        a format suitable for creating new Filter instances.

        Returns:
            Dict[str, Any]: Dictionary representation of the filter
        """
        result = {}
        for key, value in self.filter_dict.items():
            if key.startswith("#") and len(key) == 2:
                # Convert tag filters back to keyword arguments
                tag_name = key[1]
                result[tag_name] = value
            else:
                result[key] = value
        return result
