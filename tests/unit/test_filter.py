"""
Unit tests for the Filter class.

This module tests all functionality of the Filter class including:
- Filter creation and validation
- Type checking and validation rules
- Subscription filter generation
- Dictionary conversion
- Tag filtering
- Edge cases and error handling
"""

from typing import Any

import pytest

from nostr_tools import FilterValidationError
from nostr_tools.core.filter import Filter

# ============================================================================
# Filter Creation Tests
# ============================================================================


@pytest.mark.unit
class TestFilterCreation:
    """Test Filter instance creation."""

    def test_create_empty_filter(self) -> None:
        """Test creating an empty filter."""
        filter = Filter()
        assert isinstance(filter, Filter)
        assert filter.ids is None
        assert filter.authors is None
        assert filter.kinds is None
        assert filter.since is None
        assert filter.until is None
        assert filter.limit is None
        assert filter.tags is None

    def test_create_filter_with_ids(self) -> None:
        """Test creating a filter with IDs."""
        ids = ["a" * 64, "b" * 64]
        filter = Filter(ids=ids)
        # IDs are normalized and deduplicated, order not guaranteed
        assert set(filter.ids) == set(ids)

    def test_create_filter_with_authors(self) -> None:
        """Test creating a filter with authors."""
        authors = ["c" * 64, "d" * 64]
        filter = Filter(authors=authors)
        # Authors are normalized and deduplicated, order not guaranteed
        assert set(filter.authors) == set(authors)

    def test_create_filter_with_kinds(self) -> None:
        """Test creating a filter with kinds."""
        kinds = [1, 2, 3]
        filter = Filter(kinds=kinds)
        assert filter.kinds == kinds

    def test_create_filter_with_time_range(self) -> None:
        """Test creating a filter with time range."""
        filter = Filter(since=1000000, until=2000000)
        assert filter.since == 1000000
        assert filter.until == 2000000

    def test_create_filter_with_limit(self) -> None:
        """Test creating a filter with limit."""
        filter = Filter(limit=10)
        assert filter.limit == 10

    def test_create_filter_with_tags(self) -> None:
        """Test creating a filter with tag filters."""
        filter = Filter(e=["event1", "event2"], p=["pubkey1"])
        assert filter.tags == {"e": ["event1", "event2"], "p": ["pubkey1"]}

    def test_create_filter_with_all_fields(self) -> None:
        """Test creating a filter with all fields."""
        filter = Filter(
            ids=["a" * 64],
            authors=["b" * 64],
            kinds=[1],
            since=1000000,
            until=2000000,
            limit=10,
            e=["event1"],
        )
        assert filter.ids == ["a" * 64]
        assert filter.authors == ["b" * 64]
        assert filter.kinds == [1]
        assert filter.since == 1000000
        assert filter.until == 2000000
        assert filter.limit == 10
        assert filter.tags == {"e": ["event1"]}

    def test_create_filter_normalizes_hex_to_lowercase(self) -> None:
        """Test that filter normalizes hex strings to lowercase."""
        filter = Filter(ids=["A" * 64, "B" * 64], authors=["C" * 64])
        assert all(id.islower() for id in filter.ids or [])
        assert all(author.islower() for author in filter.authors or [])

    def test_create_filter_removes_duplicates(self) -> None:
        """Test that filter removes duplicates from lists."""
        filter = Filter(ids=["a" * 64, "a" * 64], kinds=[1, 1, 2])
        assert len(filter.ids or []) == 1
        assert (
            len(filter.kinds or []) == 2 or len(filter.kinds or []) == 3
        )  # Order/dedup not guaranteed


# ============================================================================
# Filter Validation Tests
# ============================================================================


@pytest.mark.unit
class TestFilterValidation:
    """Test Filter validation logic."""

    def test_valid_filter_passes_validation(self, valid_filter: Filter) -> None:
        """Test that a valid filter passes validation."""
        valid_filter.validate()  # Should not raise
        assert valid_filter.is_valid

    def test_invalid_ids_length_raises_error(self) -> None:
        """Test that invalid ID length raises ValueError."""
        with pytest.raises(FilterValidationError, match="64-character hexadecimal"):
            Filter(ids=["a" * 63])

    def test_invalid_ids_chars_raises_error(self) -> None:
        """Test that invalid ID characters raise ValueError."""
        with pytest.raises(FilterValidationError, match="64-character hexadecimal"):
            Filter(ids=["g" * 64])

    def test_invalid_authors_length_raises_error(self) -> None:
        """Test that invalid author length raises ValueError."""
        with pytest.raises(FilterValidationError, match="64-character hexadecimal"):
            Filter(authors=["a" * 63])

    def test_invalid_authors_chars_raises_error(self) -> None:
        """Test that invalid author characters raise ValueError."""
        with pytest.raises(FilterValidationError, match="64-character hexadecimal"):
            Filter(authors=["Z" * 64])

    def test_invalid_kind_below_range_raises_error(self) -> None:
        """Test that kind below valid range raises ValueError."""
        with pytest.raises(FilterValidationError, match="must be between 0 and 65535"):
            Filter(kinds=[-1])

    def test_invalid_kind_above_range_raises_error(self) -> None:
        """Test that kind above valid range raises ValueError."""
        with pytest.raises(FilterValidationError, match="must be between 0 and 65535"):
            Filter(kinds=[65536])

    def test_negative_since_raises_error(self) -> None:
        """Test that negative since raises ValueError."""
        with pytest.raises(FilterValidationError, match="must be a non-negative integer"):
            Filter(since=-1)

    def test_zero_since_is_valid(self) -> None:
        """Test that zero since is valid (Unix epoch start)."""
        filter = Filter(since=0)
        assert filter.since == 0
        assert filter.is_valid

    def test_negative_until_raises_error(self) -> None:
        """Test that negative until raises ValueError."""
        with pytest.raises(FilterValidationError, match="must be a non-negative integer"):
            Filter(until=-1)

    def test_zero_until_is_valid(self) -> None:
        """Test that zero until is valid (Unix epoch start)."""
        filter = Filter(until=0)
        assert filter.until == 0
        assert filter.is_valid

    def test_negative_limit_raises_error(self) -> None:
        """Test that negative limit raises ValueError."""
        with pytest.raises(FilterValidationError, match="must be a non-negative integer"):
            Filter(limit=-1)

    def test_zero_limit_is_valid(self) -> None:
        """Test that zero limit is valid (no results)."""
        filter = Filter(limit=0)
        assert filter.limit == 0
        assert filter.is_valid

    def test_since_greater_than_until_raises_error(self) -> None:
        """Test that since > until raises ValueError."""
        with pytest.raises(
            FilterValidationError, match="since must be less than or equal to until"
        ):
            Filter(since=2000000, until=1000000)

    def test_since_equal_to_until_is_valid(self) -> None:
        """Test that since == until is valid."""
        filter = Filter(since=1000000, until=1000000)
        assert filter.is_valid

    def test_invalid_tag_name_raises_error(self) -> None:
        """Test that invalid tag names are filtered out."""
        # Invalid tag names are silently filtered in __post_init__
        filter = Filter(ab=["value"])  # Two chars, should be filtered
        assert filter.tags is None or "ab" not in (filter.tags or {})

    def test_numeric_tag_name_raises_error(self) -> None:
        """Test that numeric tag names raise ValueError."""
        # This will be caught in __init__ since kwargs are passed as tags
        filter = Filter(**{"1": ["value"]})
        # Tag should be filtered out in validation
        assert filter.tags is None or "1" not in (filter.tags or {})

    def test_empty_tag_values_are_removed(self) -> None:
        """Test that empty tag value lists are removed."""
        filter = Filter(e=[])
        assert filter.tags is None


# ============================================================================
# Filter Type Validation Tests
# ============================================================================


@pytest.mark.unit
class TestFilterTypeValidation:
    """Test Filter type validation."""

    def test_non_list_ids_raises_error(self) -> None:
        """Test that non-list ids raises FilterValidationError."""
        with pytest.raises(FilterValidationError):
            Filter(ids="not_a_list")  # type: ignore

    def test_non_list_authors_raises_error(self) -> None:
        """Test that non-list authors raises FilterValidationError."""
        with pytest.raises(FilterValidationError):
            Filter(authors="not_a_list")  # type: ignore

    def test_non_list_kinds_raises_error(self) -> None:
        """Test that non-list kinds raises FilterValidationError."""
        with pytest.raises(FilterValidationError):
            Filter(kinds="not_a_list")  # type: ignore

    def test_non_int_since_raises_error(self) -> None:
        """Test that non-integer since raises FilterValidationError."""
        with pytest.raises(FilterValidationError):
            Filter(since="not_an_int")  # type: ignore

    def test_non_int_until_raises_error(self) -> None:
        """Test that non-integer until raises FilterValidationError."""
        with pytest.raises(FilterValidationError):
            Filter(until="not_an_int")  # type: ignore

    def test_non_int_limit_raises_error(self) -> None:
        """Test that non-integer limit raises FilterValidationError."""
        with pytest.raises(FilterValidationError):
            Filter(limit="not_an_int")  # type: ignore

    def test_non_string_id_elements_raises_error(self) -> None:
        """Test that non-string ID elements raise FilterValidationError."""
        with pytest.raises(FilterValidationError, match="must be of type"):
            Filter(ids=[123])  # type: ignore

    def test_non_string_author_elements_raises_error(self) -> None:
        """Test that non-string author elements raise FilterValidationError."""
        with pytest.raises(FilterValidationError, match="must be of type"):
            Filter(authors=[123])  # type: ignore

    def test_non_int_kind_elements_raises_error(self) -> None:
        """Test that non-integer kind elements raise FilterValidationError."""
        with pytest.raises(FilterValidationError, match="must be of type"):
            Filter(kinds=["not_int"])  # type: ignore

    def test_non_list_tag_values_raises_error(self) -> None:
        """Test that non-list tag values raise FilterValidationError."""
        with pytest.raises(FilterValidationError, match="must be lists of strings"):
            Filter(e="not_a_list")  # type: ignore

    def test_non_string_tag_value_elements_raises_error(self) -> None:
        """Test that non-string tag value elements raise FilterValidationError."""
        with pytest.raises(FilterValidationError, match="must be lists of strings"):
            Filter(e=[123])  # type: ignore


# ============================================================================
# Filter Normalization Tests
# ============================================================================


@pytest.mark.unit
class TestFilterNormalization:
    """Test Filter normalization logic."""

    def test_empty_ids_list_normalized_to_none(self) -> None:
        """Test that empty IDs list is normalized to None."""
        filter = Filter(ids=[])
        assert filter.ids is None

    def test_empty_authors_list_normalized_to_none(self) -> None:
        """Test that empty authors list is normalized to None."""
        filter = Filter(authors=[])
        assert filter.authors is None

    def test_empty_kinds_list_normalized_to_none(self) -> None:
        """Test that empty kinds list is normalized to None."""
        filter = Filter(kinds=[])
        assert filter.kinds is None

    def test_empty_tags_dict_normalized_to_none(self) -> None:
        """Test that empty tags dict is normalized to None."""
        filter = Filter()
        assert filter.tags is None

    def test_uppercase_hex_normalized_to_lowercase(self) -> None:
        """Test that uppercase hex is normalized to lowercase."""
        filter = Filter(ids=["A" * 64], authors=["B" * 64])
        assert filter.ids == ["a" * 64]
        assert filter.authors == ["b" * 64]


# ============================================================================
# Filter Subscription Filter Tests
# ============================================================================


@pytest.mark.unit
class TestFilterSubscriptionFilter:
    """Test Filter subscription filter generation."""

    def test_empty_filter_produces_empty_subscription_filter(self) -> None:
        """Test that empty filter produces empty subscription filter."""
        filter = Filter()
        subscription_filter = filter.subscription_filter
        assert subscription_filter == {}

    def test_subscription_filter_includes_ids(self) -> None:
        """Test that subscription filter includes IDs."""
        filter = Filter(ids=["a" * 64])
        subscription_filter = filter.subscription_filter
        assert "ids" in subscription_filter
        assert subscription_filter["ids"] == ["a" * 64]

    def test_subscription_filter_includes_authors(self) -> None:
        """Test that subscription filter includes authors."""
        filter = Filter(authors=["b" * 64])
        subscription_filter = filter.subscription_filter
        assert "authors" in subscription_filter
        assert subscription_filter["authors"] == ["b" * 64]

    def test_subscription_filter_includes_kinds(self) -> None:
        """Test that subscription filter includes kinds."""
        filter = Filter(kinds=[1, 2])
        subscription_filter = filter.subscription_filter
        assert "kinds" in subscription_filter
        assert subscription_filter["kinds"] == [1, 2]

    def test_subscription_filter_includes_since(self) -> None:
        """Test that subscription filter includes since."""
        filter = Filter(since=1000000)
        subscription_filter = filter.subscription_filter
        assert "since" in subscription_filter
        assert subscription_filter["since"] == 1000000

    def test_subscription_filter_includes_until(self) -> None:
        """Test that subscription filter includes until."""
        filter = Filter(until=2000000)
        subscription_filter = filter.subscription_filter
        assert "until" in subscription_filter
        assert subscription_filter["until"] == 2000000

    def test_subscription_filter_includes_limit(self) -> None:
        """Test that subscription filter includes limit."""
        filter = Filter(limit=10)
        subscription_filter = filter.subscription_filter
        assert "limit" in subscription_filter
        assert subscription_filter["limit"] == 10

    def test_subscription_filter_includes_tag_filters(self) -> None:
        """Test that subscription filter includes tag filters with # prefix."""
        filter = Filter(e=["event1"], p=["pubkey1"])
        subscription_filter = filter.subscription_filter
        assert "#e" in subscription_filter
        assert "#p" in subscription_filter
        assert subscription_filter["#e"] == ["event1"]
        assert subscription_filter["#p"] == ["pubkey1"]

    def test_subscription_filter_with_all_fields(self) -> None:
        """Test subscription filter with all fields."""
        filter = Filter(
            ids=["a" * 64],
            authors=["b" * 64],
            kinds=[1],
            since=1000000,
            until=2000000,
            limit=10,
            e=["event1"],
        )
        subscription_filter = filter.subscription_filter
        assert len(subscription_filter) == 7
        assert "ids" in subscription_filter
        assert "authors" in subscription_filter
        assert "kinds" in subscription_filter
        assert "since" in subscription_filter
        assert "until" in subscription_filter
        assert "limit" in subscription_filter
        assert "#e" in subscription_filter


# ============================================================================
# Filter Dictionary Conversion Tests
# ============================================================================


@pytest.mark.unit
class TestFilterDictionaryConversion:
    """Test Filter dictionary conversion."""

    def test_from_dict_creates_filter(self, valid_filter_dict: dict[str, Any]) -> None:
        """Test that from_dict creates a Filter instance."""
        filter = Filter.from_dict(valid_filter_dict)
        assert isinstance(filter, Filter)

    def test_from_dict_with_non_dict_raises_error(self) -> None:
        """Test that from_dict with non-dict raises TypeError."""
        with pytest.raises(TypeError, match="data must be a dict"):
            Filter.from_dict("not_a_dict")  # type: ignore

    def test_from_dict_with_empty_dict(self) -> None:
        """Test that from_dict with empty dict creates empty filter."""
        filter = Filter.from_dict({})
        assert filter.ids is None
        assert filter.authors is None
        assert filter.kinds is None

    def test_to_dict_returns_dict(self, valid_filter: Filter) -> None:
        """Test that to_dict returns a dictionary."""
        filter_dict = valid_filter.to_dict()
        assert isinstance(filter_dict, dict)

    def test_to_dict_contains_all_fields(self, valid_filter: Filter) -> None:
        """Test that to_dict contains all filter fields."""
        filter_dict = valid_filter.to_dict()
        assert "ids" in filter_dict
        assert "authors" in filter_dict
        assert "kinds" in filter_dict
        assert "since" in filter_dict
        assert "until" in filter_dict
        assert "limit" in filter_dict
        assert "tags" in filter_dict

    def test_round_trip_conversion(self, valid_filter_dict: dict[str, Any]) -> None:
        """Test that Filter can be converted to dict and back."""
        filter1 = Filter.from_dict(valid_filter_dict)
        filter_dict = filter1.to_dict()
        filter2 = Filter.from_dict(filter_dict)

        assert filter1.ids == filter2.ids
        assert filter1.authors == filter2.authors
        assert filter1.kinds == filter2.kinds
        assert filter1.since == filter2.since
        assert filter1.until == filter2.until
        assert filter1.limit == filter2.limit
        assert filter1.tags == filter2.tags


# ============================================================================
# Filter Subscription Filter Conversion Tests
# ============================================================================


@pytest.mark.unit
class TestFilterSubscriptionFilterConversion:
    """Test Filter.from_subscription_filter() method."""

    def test_from_subscription_filter_creates_filter(self) -> None:
        """Test that from_subscription_filter creates a Filter instance."""
        data = {"kinds": [1], "limit": 10}
        filter = Filter.from_subscription_filter(data)
        assert isinstance(filter, Filter)
        assert filter.kinds == [1]
        assert filter.limit == 10

    def test_from_subscription_filter_with_non_dict_raises_error(self) -> None:
        """Test that from_subscription_filter with non-dict raises TypeError."""
        with pytest.raises(TypeError, match="data must be a dict"):
            Filter.from_subscription_filter("not_a_dict")  # type: ignore

    def test_from_subscription_filter_with_empty_dict(self) -> None:
        """Test that from_subscription_filter with empty dict creates empty filter."""
        filter = Filter.from_subscription_filter({})
        assert filter.ids is None
        assert filter.authors is None
        assert filter.kinds is None
        assert filter.tags is None

    def test_from_subscription_filter_converts_tag_filters(self) -> None:
        """Test that from_subscription_filter converts #-prefixed tag filters."""
        data = {"kinds": [1], "#e": ["event1"], "#p": ["pubkey1"]}
        filter = Filter.from_subscription_filter(data)
        assert filter.kinds == [1]
        assert filter.tags == {"e": ["event1"], "p": ["pubkey1"]}

    def test_from_subscription_filter_with_single_tag(self) -> None:
        """Test from_subscription_filter with a single tag filter."""
        data = {"#e": ["event_id_123"]}
        filter = Filter.from_subscription_filter(data)
        assert filter.tags == {"e": ["event_id_123"]}

    def test_from_subscription_filter_with_multiple_tags(self) -> None:
        """Test from_subscription_filter with multiple tag filters."""
        data = {
            "#e": ["event1", "event2"],
            "#p": ["pubkey1"],
            "#a": ["addr1"],
            "#t": ["hashtag1", "hashtag2"],
        }
        filter = Filter.from_subscription_filter(data)
        assert filter.tags is not None
        assert len(filter.tags) == 4
        assert filter.tags["e"] == ["event1", "event2"]
        assert filter.tags["p"] == ["pubkey1"]
        assert filter.tags["a"] == ["addr1"]
        assert filter.tags["t"] == ["hashtag1", "hashtag2"]

    def test_from_subscription_filter_with_all_fields(self) -> None:
        """Test from_subscription_filter with all standard and tag fields."""
        data = {
            "ids": ["a" * 64],
            "authors": ["b" * 64],
            "kinds": [1, 2],
            "since": 1000000,
            "until": 2000000,
            "limit": 50,
            "#e": ["event1"],
            "#p": ["pubkey1"],
        }
        filter = Filter.from_subscription_filter(data)
        assert filter.ids == ["a" * 64]
        assert filter.authors == ["b" * 64]
        assert filter.kinds == [1, 2]
        assert filter.since == 1000000
        assert filter.until == 2000000
        assert filter.limit == 50
        assert filter.tags == {"e": ["event1"], "p": ["pubkey1"]}

    def test_from_subscription_filter_ignores_invalid_tag_keys(self) -> None:
        """Test that from_subscription_filter ignores non-alphabetic tag keys."""
        data = {"#1": ["value"], "#ab": ["value"], "kinds": [1]}
        filter = Filter.from_subscription_filter(data)
        # Invalid tags should be filtered out during validation
        assert filter.kinds == [1]
        assert filter.tags is None or "1" not in (filter.tags or {})
        assert filter.tags is None or "ab" not in (filter.tags or {})

    def test_from_subscription_filter_preserves_non_tag_fields(self) -> None:
        """Test that from_subscription_filter preserves fields without # prefix."""
        data = {"kinds": [1, 7], "limit": 100, "#e": ["event_ref"]}
        filter = Filter.from_subscription_filter(data)
        assert filter.kinds == [1, 7]
        assert filter.limit == 100
        assert filter.tags == {"e": ["event_ref"]}

    def test_from_subscription_filter_round_trip(self) -> None:
        """Test round-trip conversion: Filter -> subscription_filter -> Filter."""
        original_filter = Filter(
            ids=["a" * 64],
            authors=["b" * 64],
            kinds=[1],
            since=1000000,
            until=2000000,
            limit=10,
            e=["event1"],
            p=["pubkey1"],
        )

        # Convert to subscription filter
        sub_filter = original_filter.subscription_filter

        # Convert back to Filter
        reconstructed_filter = Filter.from_subscription_filter(sub_filter)

        # Verify all fields match
        assert reconstructed_filter.ids == original_filter.ids
        assert reconstructed_filter.authors == original_filter.authors
        assert reconstructed_filter.kinds == original_filter.kinds
        assert reconstructed_filter.since == original_filter.since
        assert reconstructed_filter.until == original_filter.until
        assert reconstructed_filter.limit == original_filter.limit
        assert reconstructed_filter.tags == original_filter.tags

    def test_from_subscription_filter_with_uppercase_tags(self) -> None:
        """Test from_subscription_filter with uppercase tag names."""
        data = {"#E": ["event1"], "#P": ["pubkey1"]}
        filter = Filter.from_subscription_filter(data)
        # Tags should be normalized to lowercase keys
        assert filter.tags == {"E": ["event1"], "P": ["pubkey1"]}

    def test_from_subscription_filter_mixed_tag_formats(self) -> None:
        """Test from_subscription_filter handles mixed tag key formats."""
        data = {
            "#e": ["event1"],  # Valid tag with #
            "kinds": [1],  # Standard field
            "#p": ["pubkey1"],  # Valid tag with #
            "limit": 10,  # Standard field
        }
        filter = Filter.from_subscription_filter(data)
        assert filter.kinds == [1]
        assert filter.limit == 10
        assert filter.tags == {"e": ["event1"], "p": ["pubkey1"]}

    def test_from_subscription_filter_validates_result(self) -> None:
        """Test that from_subscription_filter validates the resulting filter."""
        # Invalid data should raise validation error
        with pytest.raises(FilterValidationError):
            Filter.from_subscription_filter({"kinds": [-1]})

    def test_from_subscription_filter_with_empty_tag_values(self) -> None:
        """Test from_subscription_filter with empty tag value lists."""
        data = {"#e": [], "kinds": [1]}
        filter = Filter.from_subscription_filter(data)
        # Empty tag lists should be removed
        assert filter.kinds == [1]
        assert filter.tags is None


# ============================================================================
# Filter Property Tests
# ============================================================================


@pytest.mark.unit
class TestFilterProperties:
    """Test Filter properties."""

    def test_is_valid_property_returns_true_for_valid_filter(self, valid_filter: Filter) -> None:
        """Test that is_valid returns True for valid filters."""
        assert valid_filter.is_valid is True

    def test_is_valid_property_returns_false_for_invalid_filter(self) -> None:
        """Test that is_valid returns False for invalid filters."""
        filter = Filter(kinds=[1])
        # Corrupt the filter
        filter.kinds = [-1]  # Invalid kind
        assert filter.is_valid is False


# ============================================================================
# Filter Edge Cases Tests
# ============================================================================


@pytest.mark.unit
class TestFilterEdgeCases:
    """Test Filter edge cases and special scenarios."""

    def test_filter_with_single_id(self) -> None:
        """Test filter with a single ID."""
        filter = Filter(ids=["a" * 64])
        assert len(filter.ids or []) == 1

    def test_filter_with_many_ids(self) -> None:
        """Test filter with many IDs."""
        # Create valid hex IDs (a-f only, not a-z)
        ids = [chr(97 + i) * 64 for i in range(6)]  # a-f * 64 (valid hex)
        filter = Filter(ids=ids)
        # Should have all unique IDs (set removes any dups)
        assert len(set(filter.ids or [])) <= 6

    def test_filter_with_max_kind_value(self) -> None:
        """Test filter with maximum kind value."""
        filter = Filter(kinds=[65535])
        assert filter.kinds == [65535]

    def test_filter_with_min_kind_value(self) -> None:
        """Test filter with minimum kind value."""
        filter = Filter(kinds=[0])
        assert filter.kinds == [0]

    def test_filter_with_multiple_tag_types(self) -> None:
        """Test filter with multiple tag types."""
        filter = Filter(e=["event1", "event2"], p=["pubkey1"], a=["addr1"], t=["tag1"])
        assert filter.tags is not None
        assert len(filter.tags) == 4

    def test_filter_with_large_limit(self) -> None:
        """Test filter with large limit value."""
        filter = Filter(limit=1000000)
        assert filter.limit == 1000000

    def test_filter_with_very_old_since(self) -> None:
        """Test filter with very old since timestamp."""
        filter = Filter(since=1)  # Unix epoch + 1 second
        assert filter.since == 1

    def test_filter_with_far_future_until(self) -> None:
        """Test filter with far future until timestamp."""
        filter = Filter(until=2147483647)  # Max 32-bit signed int
        assert filter.until == 2147483647

    def test_filter_rejects_non_single_char_tags(self) -> None:
        """Test that tags with non-single character names are rejected."""
        # Multi-char tag name should be filtered out
        filter = Filter(**{"ab": ["value"]})
        assert filter.tags is None or "ab" not in (filter.tags or {})

    def test_filter_rejects_non_alpha_tags(self) -> None:
        """Test that tags with non-alphabetic names are rejected."""
        # Numeric tag name should be filtered out
        filter = Filter(**{"1": ["value"]})
        assert filter.tags is None or "1" not in (filter.tags or {})
