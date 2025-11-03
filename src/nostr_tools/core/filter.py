"""
Simple Nostr event filter following the protocol specification.
"""

from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Optional
from typing import Union

from ..exceptions import FilterValidationError


@dataclass
class Filter:
    """
    Nostr event filter following NIP-01 subscription specification.

    This class creates filters for querying and subscribing to events from
    Nostr relays. Filters support multiple criteria including event IDs, authors,
    kinds, time ranges, result limits, and tag-based filtering. All filter
    criteria are optional and use AND logic when combined.

    Examples:
        Filter by event kind:

        >>> # Get last 10 text notes
        >>> filter = Filter(kinds=[1], limit=10)

        Filter by author:

        >>> # Get events from specific author
        >>> filter = Filter(authors=["abc123..."])

        Filter by time range:

        >>> import time
        >>> # Events from last hour
        >>> filter = Filter(
        ...     kinds=[1],
        ...     since=int(time.time()) - 3600
        ... )

        Filter by tags:

        >>> # Get replies to a specific event
        >>> filter = Filter(
        ...     kinds=[1],
        ...     e=["original_event_id"]  # Tag filter using kwargs
        ... )

        Complex filter:

        >>> # Reactions to my notes in last 24 hours
        >>> filter = Filter(
        ...     kinds=[7],  # Reactions
        ...     e=["my_note_id1", "my_note_id2"],
        ...     since=int(time.time()) - 86400,
        ...     limit=100
        ... )

        Create from dictionary:

        >>> filter_data = {
        ...     "kinds": [1],
        ...     "authors": ["abc123..."],
        ...     "limit": 10
        ... }
        >>> filter = Filter.from_dict(filter_data)

    Raises:
        FilterValidationError: If any attribute value is invalid (e.g.,
            invalid hex strings, negative timestamps, invalid tag names).
    """

    #: List of event IDs to match (64-char lowercase hex strings). Events matching any ID in the list will be returned.
    ids: Optional[list[str]] = None
    #: List of author public keys (64-char lowercase hex strings). Events from any author in the list will be returned.
    authors: Optional[list[str]] = None
    #: List of event kinds to match (0-65535). Events matching any kind in the list will be returned. Common kinds: 0=metadata, 1=text note, 3=contacts, 7=reaction
    kinds: Optional[list[int]] = None
    #: Unix timestamp (seconds). Only events created at or after this time will be returned. Must be >= 0.
    since: Optional[int] = None
    #: Unix timestamp (seconds). Only events created at or before this time will be returned. Must be >= 0.
    until: Optional[int] = None
    #: Maximum number of events to return. Must be >= 0. Relays may impose their own limits.
    limit: Optional[int] = None
    #: Tag-based filters. Keys are single alphabetic characters (a-z, A-Z), values are lists of strings. Example: {"e": ["event_id1", "event_id2"], "p": ["pubkey1"]}
    tags: Optional[dict[str, list[str]]] = field(default_factory=dict)

    def __init__(
        self,
        ids: Optional[list[str]] = None,
        authors: Optional[list[str]] = None,
        kinds: Optional[list[int]] = None,
        since: Optional[int] = None,
        until: Optional[int] = None,
        limit: Optional[int] = None,
        **tags: list[str],
    ) -> None:
        """
        Initialize Filter instance with subscription criteria.

        This constructor accepts standard filter parameters plus tag filters
        as keyword arguments. Tag filters use single-letter keys corresponding
        to tag names (e.g., e for event references, p for pubkey references).

        Args:
            ids (Optional[list[str]]): List of event IDs to match (64-char hex).
            authors (Optional[list[str]]): List of author pubkeys (64-char hex).
            kinds (Optional[list[int]]): List of event kinds (0-65535).
            since (Optional[int]): Unix timestamp for minimum event age (>= 0).
            until (Optional[int]): Unix timestamp for maximum event age (>= 0).
            limit (Optional[int]): Maximum number of events to return (>= 0).
            **tags (list[str]): Tag filters as keyword arguments.
                Single-letter keys only (a-z, A-Z).
                Example: e=['event_id'], p=['pubkey'], t=['hashtag']

        Examples:
            Basic filter:

            >>> filter = Filter(kinds=[1], limit=10)

            With tag filters:

            >>> filter = Filter(
            ...     kinds=[1],
            ...     e=['event_id_to_reply_to'],  # #e tag
            ...     p=['mentioned_pubkey']       # #p tag
            ... )

            Time-based filter:

            >>> filter = Filter(
            ...     kinds=[1],
            ...     since=1234567890,
            ...     until=1234567999
            ... )
        """
        self.ids = ids
        self.authors = authors
        self.kinds = kinds
        self.since = since
        self.until = until
        self.limit = limit
        self.tags = tags
        self.__post_init__()

    def __post_init__(self) -> None:
        """
        Validate and normalize filter after initialization.

        This method is automatically called after the dataclass is created.
        It normalizes empty collections to None, converts hex strings to
        lowercase, removes invalid tag filters, and validates all filter
        criteria.

        Raises:
            FilterValidationError: If validation fails after normalization.
        """
        # Normalize empty collections to None
        if self.ids == []:
            self.ids = None
        if self.authors == []:
            self.authors = None
        if self.kinds == []:
            self.kinds = None
        if self.tags == {}:
            self.tags = None

        # Normalize strings to lowercase
        def normalize(lst: Optional[list[str]]) -> Optional[list[str]]:
            """
            Normalize a list of strings by converting to lowercase and removing duplicates.

            Args:
                lst: List of strings to normalize, or None

            Returns:
                Normalized list with lowercase strings and duplicates removed, or None
            """
            if isinstance(lst, list):
                return list({item.lower() if isinstance(item, str) else item for item in lst})
            return lst

        self.ids = normalize(self.ids)
        self.authors = normalize(self.authors)
        # Normalize tags by removing empty lists and no single char keys
        if self.tags is not None:
            self.tags = {
                k: v for k, v in self.tags.items() if v != [] and (len(k) == 1) and k.isalpha()
            }
            if self.tags == {}:
                self.tags = None
        # Validate the data
        self.validate()

    def validate(self) -> None:
        """
        Validate the Filter instance.

        Raises:
            FilterValidationError: If any attribute has an invalid value
        """
        type_checks: list[tuple[str, Any, tuple[type, ...]]] = [
            ("ids", self.ids, (list, type(None))),
            ("authors", self.authors, (list, type(None))),
            ("kinds", self.kinds, (list, type(None))),
            ("since", self.since, (int, type(None))),
            ("until", self.until, (int, type(None))),
            ("limit", self.limit, (int, type(None))),
            ("tags", self.tags, (dict, type(None))),
        ]
        for field_name, field_value, expected_type in type_checks:
            if not isinstance(field_value, expected_type):
                raise FilterValidationError(
                    f"{field_name} must be {expected_type}, got {type(field_value)}"
                )

        elem_type_checks: list[
            tuple[str, Union[list[str], list[int], dict[str, list[str]], None], type]
        ] = [
            ("ids", self.ids, str),
            ("authors", self.authors, str),
            ("kinds", self.kinds, int),
        ]
        for field_name, field_value, expected_elem_type in elem_type_checks:
            if (
                field_value is not None
                and isinstance(field_value, list)
                and not all(isinstance(elem, expected_elem_type) for elem in field_value)
            ):
                raise FilterValidationError(
                    f"All elements in {field_name} must be of type {expected_elem_type}"
                )

        hex_checks: list[tuple[str, Optional[list[str]]]] = [
            ("ids", self.ids),
            ("authors", self.authors),
        ]
        for field_name, field_value in hex_checks:
            if field_value is not None and not all(
                len(elem) == 64 and all(c in "0123456789abcdef" for c in elem)
                for elem in field_value
            ):
                raise FilterValidationError(
                    f"All elements in {field_name} must be lower 64-character hexadecimal strings"
                )

        if self.kinds is not None:
            if not all(0 <= kind <= 65535 for kind in self.kinds):
                raise FilterValidationError("All elements in kinds must be between 0 and 65535")

        int_checks: list[tuple[str, Optional[int]]] = [
            ("since", self.since),
            ("until", self.until),
            ("limit", self.limit),
        ]
        for field_name, field_value in int_checks:
            if field_value is not None and field_value < 0:
                raise FilterValidationError(f"{field_name} must be a non-negative integer")
        if self.since is not None and self.until is not None and self.since > self.until:
            raise FilterValidationError("since must be less than or equal to until")

        if self.tags is not None:
            for tag_name, tag_values in self.tags.items():
                if not isinstance(tag_name, str):
                    raise FilterValidationError("Tag names must be strings")
                if isinstance(tag_name, str) and (len(tag_name) != 1 or not tag_name.isalpha()):
                    raise FilterValidationError(
                        "Tag names must be single alphabetic characters a-z or A-Z"
                    )
                if not isinstance(tag_values, list) or not all(
                    isinstance(tag_value, str) for tag_value in tag_values
                ):
                    raise FilterValidationError("All tag values must be lists of strings")

    @property
    def subscription_filter(self) -> dict[str, Any]:
        """
        Build the subscription filter dictionary for relay communication.

        Converts the Filter instance into a dictionary format suitable for
        sending to Nostr relays in REQ messages. Tag filters are converted
        to the #<tag_name> format required by the protocol.

        Returns:
            dict[str, Any]: Dictionary suitable for Nostr subscription filtering.
                Only includes non-None filter criteria. Tag filters are prefixed
                with # (e.g., {"#e": ["event_id"], "#p": ["pubkey"]}).

        Examples:
            Basic subscription filter:

            >>> filter = Filter(kinds=[1], limit=10)
            >>> print(filter.subscription_filter)
            {"kinds": [1], "limit": 10}

            With tag filters:

            >>> filter = Filter(kinds=[1], e=["event_id"], p=["pubkey"])
            >>> print(filter.subscription_filter)
            {"kinds": [1], "#e": ["event_id"], "#p": ["pubkey"]}

            Send to relay:

            >>> sub_filter = filter.subscription_filter
            >>> message = ["REQ", subscription_id, sub_filter]
            >>> await ws.send_str(json.dumps(message))
        """
        subscription_filter: dict[str, Any] = {}
        if self.ids is not None:
            subscription_filter["ids"] = self.ids
        if self.authors is not None:
            subscription_filter["authors"] = self.authors
        if self.kinds is not None:
            subscription_filter["kinds"] = self.kinds
        if self.since is not None:
            subscription_filter["since"] = self.since
        if self.until is not None:
            subscription_filter["until"] = self.until
        if self.limit is not None:
            subscription_filter["limit"] = self.limit
        if self.tags is not None:
            for tag_name, tag_values in self.tags.items():
                subscription_filter[f"#{tag_name}"] = tag_values
        return subscription_filter

    @property
    def is_valid(self) -> bool:
        """
        Check if the Filter is valid without raising exceptions.

        This property attempts validation and returns True if successful,
        False otherwise. Unlike validate(), this method does not raise
        exceptions, making it safe for conditional checks.

        Returns:
            bool: True if the filter passes all validation checks,
                False if validation fails for any reason.

        Examples:
            >>> filter = Filter(kinds=[1], limit=10)
            >>> if filter.is_valid:
            ...     events = await fetch_events(client, filter)
            ... else:
            ...     print("Invalid filter configuration")

            >>> # Check before using
            >>> filter = Filter(authors=["invalid"])
            >>> if not filter.is_valid:
            ...     print("Filter validation failed")
        """
        try:
            self.validate()
            return True
        except FilterValidationError:
            return False

    @classmethod
    def from_subscription_filter(cls, data: dict[str, Any]) -> "Filter":
        """
        Create Filter from subscription filter dictionary.

        This method converts a subscription filter dictionary (typically from
        a REQ message) into a Filter object. It handles the conversion of
        #-prefixed tag filters back to tag dictionary format.

        Args:
            data (dict[str, Any]): Dictionary containing subscription filter data.
                Can include standard filter fields and #-prefixed tag filters
                like {"#e": ["event_id"], "#p": ["pubkey"]}.

        Returns:
            Filter: An instance of Filter with all criteria properly converted.

        Raises:
            TypeError: If data is not a dictionary.
            FilterValidationError: If data contains invalid filter criteria.

        Examples:
            Parse REQ message filter:

            >>> req_filter = {
            ...     "kinds": [1],
            ...     "#e": ["abc123..."],
            ...     "#p": ["def456..."],
            ...     "limit": 10
            ... }
            >>> filter = Filter.from_subscription_filter(req_filter)
            >>> print(filter.tags)
            {'e': ['abc123...'], 'p': ['def456...']}

            Convert relay subscription:

            >>> relay_filter = {"kinds": [1, 3], "#t": ["nostr"]}
            >>> filter = Filter.from_subscription_filter(relay_filter)
            >>> # Use filter object with standard methods
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, got {type(data)}")

        data = {
            (key[1] if len(key) == 2 and key[0] == "#" and key[1].isalpha() else key): value
            for key, value in data.items()
        }
        return cls(**data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Filter":
        """
        Create Filter from dictionary representation.

        This method creates a Filter instance from a dictionary with standard
        Filter format (not subscription format). Tag filters should be provided
        in the "tags" dictionary field without # prefixes.

        Args:
            data (dict[str, Any]): Dictionary containing filter data with keys:
                - ids (Optional[list[str]]): Event IDs
                - authors (Optional[list[str]]): Author public keys
                - kinds (Optional[list[int]]): Event kinds
                - since (Optional[int]): Minimum timestamp
                - until (Optional[int]): Maximum timestamp
                - limit (Optional[int]): Maximum number of events
                - tags (Optional[dict]): Tag filters without # prefix

        Returns:
            Filter: An instance of Filter created from the dictionary.

        Raises:
            TypeError: If data is not a dictionary.
            FilterValidationError: If filter data is invalid.

        Examples:
            Create from stored configuration:

            >>> config = {
            ...     "kinds": [1],
            ...     "limit": 10,
            ...     "tags": {"e": ["event_id"], "p": ["pubkey"]}
            ... }
            >>> filter = Filter.from_dict(config)

            Parse from JSON:

            >>> import json
            >>> json_str = '{"kinds": [1], "authors": ["abc123..."], "limit": 50}'
            >>> filter_dict = json.loads(json_str)
            >>> filter = Filter.from_dict(filter_dict)

            Load from database:

            >>> filter_data = db.filters.find_one({"name": "my_filter"})
            >>> filter = Filter.from_dict(filter_data)
        """
        if not isinstance(data, dict):
            raise TypeError(f"data must be a dict, got {type(data)}")

        return cls(
            ids=data.get("ids"),
            authors=data.get("authors"),
            kinds=data.get("kinds"),
            since=data.get("since"),
            until=data.get("until"),
            limit=data.get("limit"),
            **data.get("tags", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert Filter to dictionary representation.

        This method serializes the Filter instance into a dictionary format
        suitable for JSON encoding, storage, or transmission. The output uses
        standard Filter format with tag filters in the "tags" dictionary field
        (not subscription format with # prefixes).

        Returns:
            dict[str, Any]: Dictionary representation of Filter with keys:
                - ids (Optional[list[str]]): Event IDs or None
                - authors (Optional[list[str]]): Author public keys or None
                - kinds (Optional[list[int]]): Event kinds or None
                - since (Optional[int]): Minimum timestamp or None
                - until (Optional[int]): Maximum timestamp or None
                - limit (Optional[int]): Maximum number of events or None
                - tags (Optional[dict]): Tag filters or None

        Examples:
            Serialize to JSON:

            >>> filter = Filter(kinds=[1], limit=10, e=["event_id"])
            >>> filter_dict = filter.to_dict()
            >>> import json
            >>> json_str = json.dumps(filter_dict)

            Store in database:

            >>> filter = Filter(kinds=[1], authors=["abc123..."])
            >>> filter_data = filter.to_dict()
            >>> db.filters.insert_one({"name": "my_filter", **filter_data})

            Create configuration:

            >>> filters_config = {
            ...     "notes": Filter(kinds=[1], limit=100).to_dict(),
            ...     "metadata": Filter(kinds=[0]).to_dict()
            ... }
        """
        return {
            "ids": self.ids,
            "authors": self.authors,
            "kinds": self.kinds,
            "since": self.since,
            "until": self.until,
            "limit": self.limit,
            "tags": self.tags,
        }
